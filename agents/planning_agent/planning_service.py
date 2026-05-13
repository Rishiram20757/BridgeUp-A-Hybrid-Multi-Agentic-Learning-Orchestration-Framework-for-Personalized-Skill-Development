"""
Planning Service Layer
This is the ONLY public entry for Orchestrator.
Handles dataset loading and domain conversion internally.
"""

from typing import Dict, Any

from .planner import (
    generate_multiple_learning_plans,
    schedule_roadmap_weekwise,
    generate_explainability_notes,
)

from .models import JobSkillRequirement
from .data_loader import load_all_skills, load_prerequisites, load_resources


def run_planning_pipeline(
    job_role_name: str,
    known_skills: list,
    weekly_time_hours: float,
) -> Dict[str, Any]:

    # Convert role name → JobSkillRequirement
    job_requirement = JobSkillRequirement.from_role_name(job_role_name)

    # Load datasets
    all_skills = load_all_skills()
    prerequisites = load_prerequisites()
    resources = load_resources()

    # Generate multi-strategy plans
    plans = generate_multiple_learning_plans(
        job_requirement=job_requirement,
        known_skills=known_skills,
        all_skills=all_skills,
        prerequisites=prerequisites,
        resources=resources,
        weekly_time_hours=weekly_time_hours,
    )

    # Generate weekly schedules per strategy
    schedules = {
        strategy: schedule_roadmap_weekwise(plan)
        for strategy, plan in plans.items()
    }

    # Generate explainability per strategy
    explainability = {
        strategy: generate_explainability_notes(
            ordered_skills=[step.skill_id for step in plan.steps],
            skill_graph=None  # If needed, modify planner to expose graph
        )
        for strategy, plan in plans.items()
    }

    return {
        "roadmap_options": plans,
        "weekly_schedules": schedules,
        "explainability": explainability,
    }