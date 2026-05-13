from typing import List
import requests
from .schemas import JobPosting


class JobAPIClient:

    # -----------------------------
    # API Endpoints
    # -----------------------------
    REMOTIVE_URL = "https://remotive.com/api/remote-jobs"

    # Replace with your real Adzuna credentials
    ADZUNA_APP_ID = "41a2e920"
    ADZUNA_APP_KEY = "d0476c0966b92a818f4fa408df74b0cd"

    # -----------------------------
    # Remotive API
    # -----------------------------
    def _remotive_jobs(self, skill: str) -> List[JobPosting]:

        params = {
            "search": skill,
            "limit": 50
        }

        try:
            response = requests.get(self.REMOTIVE_URL, params=params, timeout=10)

            if response.status_code != 200:
                return []

            data = response.json()

        except Exception:
            return []

        jobs = []

        for job in data.get("jobs", []):

            jobs.append(
                JobPosting(
                    title=job.get("title"),
                    company=job.get("company_name"),
                    location=job.get("candidate_required_location"),
                    salary_range=job.get("salary"),
                    required_skills=[skill],
                    url=job.get("url"),
                    source="remotive"
                )
            )

        return jobs

    # -----------------------------
    # Adzuna API
    # -----------------------------
    def _adzuna_jobs(self, skill: str) -> List[JobPosting]:

        url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

        params = {
            "app_id": self.ADZUNA_APP_ID,
            "app_key": self.ADZUNA_APP_KEY,
            "what": skill
        }

        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code != 200:
                return []

            data = response.json()

        except Exception:
            return []

        jobs = []

        for job in data.get("results", []):

            salary = None

            if job.get("salary_min") and job.get("salary_max"):
                salary = f"{job['salary_min']} - {job['salary_max']}"

            jobs.append(
                JobPosting(
                    title=job.get("title"),
                    company=job.get("company", {}).get("display_name"),
                    location=job.get("location", {}).get("display_name"),
                    salary_range=salary,
                    required_skills=[skill],
                    url=job.get("redirect_url"),
                    source="adzuna"
                )
            )

        return jobs

    # -----------------------------
    # Combined Query
    # -----------------------------
    def query_by_skill(self, skill: str) -> List[JobPosting]:

        jobs = []

        # Fetch from both APIs
        jobs.extend(self._remotive_jobs(skill))
        jobs.extend(self._adzuna_jobs(skill))

        # Deduplicate by URL
        unique = {}

        for job in jobs:
            if job.url:
                unique[job.url] = job

        return list(unique.values())

    # -----------------------------
    # Role Query
    # -----------------------------
    def query_by_role(self, role: str) -> List[JobPosting]:
        return self.query_by_skill(role)