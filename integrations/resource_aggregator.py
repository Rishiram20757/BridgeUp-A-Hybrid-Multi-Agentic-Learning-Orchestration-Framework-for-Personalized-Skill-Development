from .job_api_client import JobAPIClient
from .github_api_client import GitHubAPIClient
from .tutorial_api_client import TutorialAPIClient
from .course_api_client import CourseAPIClient
from .schemas import AggregatedResources


class ResourceAggregator:

    def __init__(self):

        self.job_client = JobAPIClient()
        self.github_client = GitHubAPIClient()
        self.tutorial_client = TutorialAPIClient()
        self.course_client = CourseAPIClient()

    # --------------------------------------------------
    # Demo Fallback Resources
    # --------------------------------------------------

    def _fallback_jobs(self):
        return [
            {"title": "Backend Developer (Python)"},
            {"title": "Junior Backend Engineer"},
            {"title": "Python API Developer"},
        ]

    def _fallback_projects(self):
        return [
            {"title": "Build a REST API with FastAPI"},
            {"title": "Django Blog Backend"},
            {"title": "Microservices Backend Architecture"},
        ]

    def _fallback_courses(self):
        return [
            {"title": "Backend Development with Python"},
            {"title": "Django REST Framework Masterclass"},
            {"title": "System Design Fundamentals"},
        ]

    def _fallback_tutorials(self):
        return [
            {"title": "Python Backend Tutorial"},
            {"title": "REST API Design Guide"},
            {"title": "Building APIs with FastAPI"},
        ]

    # --------------------------------------------------
    # Collect by Skill
    # --------------------------------------------------

    def collect_by_skill(self, skill: str) -> AggregatedResources:

        jobs = self.job_client.query_by_skill(skill)
        projects = self.github_client.query_by_skill(skill)
        tutorials = self.tutorial_client.query_by_skill(skill)
        courses = self.course_client.query_by_skill(skill)

        # 🔥 Demo fallback if APIs return nothing
        if not jobs:
            jobs = self._fallback_jobs()

        if not projects:
            projects = self._fallback_projects()

        if not courses:
            courses = self._fallback_courses()

        if not tutorials:
            tutorials = self._fallback_tutorials()

        return AggregatedResources(
            skill=skill,
            jobs=jobs,
            projects=projects,
            courses=courses,
            tutorials=tutorials
        )

    # --------------------------------------------------
    # Collect by Role
    # --------------------------------------------------

    def collect_by_role(self, role: str) -> AggregatedResources:

        jobs = self.job_client.query_by_role(role)
        projects = self.github_client.query_by_role(role)
        tutorials = self.tutorial_client.query_by_role(role)
        courses = self.course_client.query_by_role(role)

        # 🔥 Demo fallback
        if not jobs:
            jobs = self._fallback_jobs()

        if not projects:
            projects = self._fallback_projects()

        if not courses:
            courses = self._fallback_courses()

        if not tutorials:
            tutorials = self._fallback_tutorials()

        return AggregatedResources(
            skill=role,
            jobs=jobs,
            projects=projects,
            courses=courses,
            tutorials=tutorials
        )