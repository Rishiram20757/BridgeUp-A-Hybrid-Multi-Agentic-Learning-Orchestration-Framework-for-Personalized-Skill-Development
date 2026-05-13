from typing import Optional, Dict
from .schema import TutorResponse, QuizResponse
from .memory import TutorMemory
from agents.llm_agent.llm_client import LLMClient


class LearningTutor:

    def __init__(self):
        self.llm = LLMClient()
        self.memory = TutorMemory()

        # conversational state
        self.chat_history = []
        self.current_mode = "teach"

        # topic context
        self.skill = None
        self.level = None
        self.goal = None

    # --------------------------------------------------
    # MODE DETECTION
    # --------------------------------------------------

    def _detect_mode(self, user_input: str) -> str:

        text = user_input.lower()

        if any(word in text for word in ["quiz", "test", "mcq", "question me"]):
            return "quiz"

        if any(word in text for word in ["i tried", "my answer", "check", "solve"]):
            return "practice"

        return "teach"

    # --------------------------------------------------
    # CONTEXT BUILDER
    # --------------------------------------------------

    def _build_chat_context(self) -> str:
        return "\n".join(self.chat_history[-5:]) if self.chat_history else "No previous conversation."

    # --------------------------------------------------
    # PROMPT BUILDER
    # --------------------------------------------------

    def _build_chat_prompt(self, user_input: str, context: str) -> str:

        return f"""
You are a PERSONAL AI TUTOR.

Mode: {self.current_mode}

STRICT RULES:
- Stay ONLY within topic: {self.skill}
- Teach step-by-step
- Keep explanation simple
- Give EXACTLY one example
- Give EXACTLY one practice task
- Ask EXACTLY one follow-up question
- Do NOT go off-topic

User Level: {self.level}
Goal: {self.goal}

Conversation History:
{context}

User Input:
{user_input}

Return JSON:
explanation, example, practice_task, follow_up_question, difficulty_level
"""

    # --------------------------------------------------
    # CHAT METHOD
    # --------------------------------------------------

    def chat(
        self,
        user_input: str,
        skill: Optional[str] = None,
        level: Optional[str] = None,
        goal: Optional[str] = None
    ) -> Dict:

        # set context
        if skill:
            self.skill = skill
        if level:
            self.level = level
        if goal:
            self.goal = goal

        # detect mode
        self.current_mode = self._detect_mode(user_input)

        # build context
        context = self._build_chat_context()

        # -----------------------------
        # QUIZ MODE
        # -----------------------------
        if self.current_mode == "quiz":

            quiz = self.generate_quiz(self.skill, self.level)

            message = (
                "Great, let's check your understanding 👇\n\n"
                f"{quiz.question}"
            )

            self.chat_history.append(f"User: {user_input}")
            self.chat_history.append(f"Tutor: {quiz.question}")

            return {
                "message": message,
                "structured": quiz,
                "mode": "quiz"
            }

        # -----------------------------
        # TEACH / PRACTICE
        # -----------------------------

        prompt = self._build_chat_prompt(user_input, context)

        response: TutorResponse = self.llm.generate_structured(
            prompt,
            TutorResponse
        )

        message = (
            f"{response.explanation}\n\n"
            f"Example:\n{response.example}\n\n"
            f"Try this:\n{response.practice_task}\n\n"
            f"{response.follow_up_question}"
        )

        self.chat_history.append(f"User: {user_input}")
        self.chat_history.append(f"Tutor: {response.explanation}")

        return {
            "message": message,
            "structured": response,
            "mode": self.current_mode
        }

    # --------------------------------------------------
    # CONTEXTUAL LESSON (✅ FIXED POSITION)
    # --------------------------------------------------

    def generate_contextual_lesson(
        self,
        task_title: str,
        skill: str,
        level: str,
        goal: str = ""
    ) -> TutorResponse:

        prompt = f"""
You are a PERSONAL AI TUTOR.

Your job is to teach ONLY the given task in a structured way.

STRICT RULES:
- Stay ONLY within this task: {task_title}
- Do NOT go beyond the topic
- Keep explanation simple and step-by-step
- Give EXACTLY one example
- Give EXACTLY one practice task
- Ask EXACTLY one follow-up question

Skill: {skill}
Level: {level}
Goal: {goal}

Return JSON:
explanation, example, practice_task, follow_up_question, difficulty_level
"""

        return self.llm.generate_structured(
            prompt,
            TutorResponse
        )

    # --------------------------------------------------
    # QUIZ METHOD
    # --------------------------------------------------

    def generate_quiz(
        self,
        skill: str,
        level: str
    ) -> QuizResponse:

        prompt = f"""
Create a multiple choice question to test understanding.

Skill: {skill}
Level: {level}

Rules:
- One clear question
- 4 options
- One correct answer
- No explanation
- Stay strictly within topic

Return JSON:
question, options, answer
"""

        return self.llm.generate_structured(
            prompt,
            QuizResponse
        )

    # --------------------------------------------------
    # RESET SESSION
    # --------------------------------------------------

    def reset_session(self):
        self.chat_history = []
        self.current_mode = "teach"
        self.memory = TutorMemory()
        self.skill = None
        self.level = None
        self.goal = None