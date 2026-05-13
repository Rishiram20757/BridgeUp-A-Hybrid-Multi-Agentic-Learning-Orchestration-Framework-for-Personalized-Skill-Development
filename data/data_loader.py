"""
Mock Data Loader for BridgeUp
Used only for orchestration testing.

Fully aligned with models.py
"""

from typing import Dict, List

from agents.planning_agent.models import (
    JobSkillRequirement,
    Skill,
    SkillPrerequisite,
    LearningResource,
)


# -------------------------
# Mock Skills
# -------------------------

def load_all_skills() -> Dict[str, Skill]:
    return {
        "python": Skill(
            skill_id="python",
            skill_name="Python",
            domain="programming",
            parent_skill=None,
            level=1,
            description="Python programming language"
        ),
        "dsa": Skill(
            skill_id="dsa",
            skill_name="Data Structures & Algorithms",
            domain="computer_science",
            parent_skill=None,
            level=2,
            description="Core data structures and algorithms"
        ),
    }


# -------------------------
# Mock Prerequisites
# -------------------------

def load_prerequisites() -> List[SkillPrerequisite]:
    return [
        SkillPrerequisite(
            skill_id="dsa",
            prerequisite_skill_id="python",
            dependency_type="hard",
        )
    ]


# -------------------------
# Mock Resources
# -------------------------

def load_resources() -> List[LearningResource]:
    return [
        LearningResource(
            resource_id="r1",
            title="Python Basics Course",
            provider="MockProvider",
            domain="programming",
            skill_tags=["python"],
            difficulty="beginner",
            duration_hours=10.0,
            cost_type="free",
            url="https://example.com/python"
        ),
        LearningResource(
            resource_id="r2",
            title="DSA Crash Course",
            provider="MockProvider",
            domain="computer_science",
            skill_tags=["dsa"],
            difficulty="intermediate",
            duration_hours=15.0,
            cost_type="free",
            url="https://example.com/dsa"
        ),
    ]


# -------------------------
# Mock Job Requirement
# -------------------------

def load_job_requirement(role_name: str) -> JobSkillRequirement:

    if role_name == "Backend Developer":
        return JobSkillRequirement(
            job_role_id="backend_dev",
            job_role_name="Backend Developer",
            required_skills=["python", "dsa"],
            skill_weightage=[0.7, 0.6],
            domain="software_engineering",
        )

    raise ValueError(f"Unknown job role: {role_name}")