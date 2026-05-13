from typing import List
import requests
from .schemas import ProjectResource


class GitHubAPIClient:

    BASE_URL = "https://api.github.com/search/repositories"

    def _search_repositories(self, query: str) -> List[ProjectResource]:

        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 30
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)

            if response.status_code != 200:
                return []

            data = response.json()

        except Exception:
            return []

        projects = []

        for repo in data.get("items", []):

            projects.append(
                ProjectResource(
                    name=repo.get("name"),
                    description=repo.get("description"),
                    stars=repo.get("stargazers_count"),
                    primary_language=repo.get("language"),
                    skills=[query],
                    repo_url=repo.get("html_url")
                )
            )

        return projects

    # --------------------------------
    # Query by skill
    # --------------------------------
    def query_by_skill(self, skill: str) -> List[ProjectResource]:

        query = f"{skill} project"

        return self._search_repositories(query)

    # --------------------------------
    # Query by role
    # --------------------------------
    def query_by_role(self, role: str) -> List[ProjectResource]:

        query = f"{role} project"

        return self._search_repositories(query)