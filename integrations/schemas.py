from dataclasses import dataclass
from typing import List, Optional

from dataclasses import dataclass
from typing import List


@dataclass
class AggregatedResources:

    skill: str

    jobs: List
    projects: List
    courses: List
    tutorials: List

@dataclass
class JobPosting:
    title: str
    company: str
    location: Optional[str]
    salary_range: Optional[str]
    required_skills: List[str]
    url: str
    source: str


@dataclass
class CourseResource:
    title: str
    provider: str
    difficulty: Optional[str]
    duration_hours: Optional[float]
    cost: Optional[str]
    url: str
    skills: List[str]


@dataclass
class ProjectResource:
    name: str
    description: str
    stars: int
    primary_language: Optional[str]
    skills: List[str]
    repo_url: str


@dataclass
class TutorialResource:
    title: str
    platform: str
    skill_tags: List[str]
    url: str