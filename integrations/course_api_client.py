from typing import List
import requests
from .schemas import CourseResource


class CourseAPIClient:

    BASE_URL = "https://serpapi.com/search.json"
    SERPAPI_KEY = "2fd2a2fcb1442bada5714ce879932b9768d3645ebafdbd2863c496937745fc10"

    def query_by_skill(self, skill: str) -> List[CourseResource]:

        params = {
            "engine": "google",
            "q": f"{skill} online course",
            "hl": "en",
            "gl": "us",
            "api_key": self.SERPAPI_KEY
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)

            if response.status_code != 200:
                return []

            data = response.json()

        except Exception:
            return []

        courses = []

        # Parse organic search results
        for result in data.get("organic_results", []):

            courses.append(
                CourseResource(
                    title=result.get("title"),
                    provider=result.get("source"),
                    difficulty=None,
                    duration_hours=None,
                    cost=None,
                    url=result.get("link"),
                    skills=[skill]
                )
            )

        return courses

    def query_by_role(self, role: str):
        return self.query_by_skill(role)