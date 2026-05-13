import os
import json
import re
from typing import Type

from openai import OpenAI
from openai import OpenAIError
from pydantic import BaseModel, ValidationError


class LLMClient:

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,
        max_tokens: int = 500,
    ):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set.")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Deterministic cache for experiments
        self._cache = {}

    # -----------------------------------------------------
    # JSON Extraction
    # -----------------------------------------------------

    def _extract_json(self, text: str) -> str:
        """
        Extract JSON object from model output safely.
        Handles cases where the LLM wraps JSON with text or markdown.
        """

        text = text.strip()

        text = text.replace("```json", "")
        text = text.replace("```", "")

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            return match.group(0)

        return text

    # -----------------------------------------------------
    # LLM Call
    # -----------------------------------------------------

    def _call_llm(self, prompt: str) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You MUST return ONLY valid JSON. "
                        "The JSON MUST match the required schema exactly. "
                        "Do not wrap inside additional keys."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        return response.choices[0].message.content

    # -----------------------------------------------------
    # Structured Generation (Robust)
    # -----------------------------------------------------

    def generate_structured(
        self,
        prompt: str,
        schema: Type[BaseModel],
    ) -> BaseModel:

        # ------------------------------
        # Cache
        # ------------------------------

        if prompt in self._cache:
            return self._cache[prompt]

        attempts = 2

        for attempt in range(attempts):

            try:

                content = self._call_llm(prompt)

                try:
                    parsed = json.loads(content)

                except json.JSONDecodeError:

                    cleaned = self._extract_json(content)
                    parsed = json.loads(cleaned)

                result = schema(**parsed)

                self._cache[prompt] = result

                return result

            except (json.JSONDecodeError, ValidationError):
                continue

            except OpenAIError as e:
                raise RuntimeError(f"OpenAI API error: {e}")

        # -------------------------------------------------
        # SAFE SCHEMA-AWARE FALLBACK
        # -------------------------------------------------

        try:

            fallback_data = {}

            for field_name, field_info in schema.model_fields.items():

                annotation = field_info.annotation

                # If the field expects a list → return empty list
                if getattr(annotation, "__origin__", None) is list:
                    fallback_data[field_name] = []

                # Otherwise return None
                else:
                    fallback_data[field_name] = None

            fallback = schema(**fallback_data)

            self._cache[prompt] = fallback

            return fallback

        except Exception as e:

            raise RuntimeError(
                f"Schema validation failed after retries: {e}"
            )