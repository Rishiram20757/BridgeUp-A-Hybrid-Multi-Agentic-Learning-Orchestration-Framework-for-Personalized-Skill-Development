from typing import List
import requests
from .schemas import TutorialResource


class TutorialAPIClient:

    BASE_URL = "https://dev.to/api/articles"

    def _devto_tutorials(self, skill: str) -> List[TutorialResource]:

        tag = skill.replace(" ", "").lower()
        params = {
            "tag": tag,
            "per_page": 30
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)

            if response.status_code != 200:
                return []

            data = response.json()

        except Exception:
            return []

        tutorials = []

        for article in data:

            tutorials.append(
                TutorialResource(
                    title=article.get("title"),
                    platform="dev.to",
                    skill_tags=[skill],
                    url=article.get("url")
                )
            )

        return tutorials

    # -----------------------------
    # Query by skill
    # -----------------------------
    def query_by_skill(self, skill: str) -> List[TutorialResource]:

        return self._devto_tutorials(skill)

    # -----------------------------
    # Query by role
    # -----------------------------
    def query_by_role(self, role: str) -> List[TutorialResource]:

        return self._devto_tutorials(role)