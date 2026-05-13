"""
BridgeUp – Planning Agent
Core planning logic (with multi-strategy support)
"""

# =========================
# Imports
# =========================

from typing import List, Dict

from .models import (
    JobSkillRequirement,
    Skill,
    SkillPrerequisite,
    LearningResource,
    SkillNode,
    ResourceAssignment,
    RoadmapStep,
    LearningRoadmap,
    WeeklyPlan,
    ExplainabilityNote,
    MasteryLevel,
    PlanStrategy,
)

# =========================
# Basic Validation Helpers
# =========================

def _ensure_non_empty_list(value, name: str):
    if not value:
        raise ValueError(f"{name} must not be empty")


def _ensure_non_negative(value, name: str):
    if value < 0:
        raise ValueError(f"{name} must be non-negative")

# =========================
# STEP 2 — Skill Gap Computation
# =========================

def compute_skill_gaps(
    job_requirement: JobSkillRequirement,
    known_skills: List[str],
) -> Dict[str, float]:
    skill_gaps: Dict[str, float] = {}

    for skill_id, weight in zip(
        job_requirement.required_skills,
        job_requirement.skill_weightage,
    ):
        if skill_id not in known_skills:
            skill_gaps[skill_id] = weight

    return skill_gaps

# =========================
# STEP 3 — Dependency Graph
# =========================

def build_skill_dependency_graph(
    missing_skills: Dict[str, float],
    all_skills: Dict[str, Skill],
    prerequisites: List[SkillPrerequisite],
    known_skills: List[str],
) -> Dict[str, SkillNode]:

    skill_nodes: Dict[str, SkillNode] = {}

    for skill_id, weight in missing_skills.items():
        skill = all_skills[skill_id]

        skill_nodes[skill_id] = SkillNode(
            skill_id=skill.skill_id,
            skill_name=skill.skill_name,
            domain=skill.domain,
            weight=weight,
            hard_prerequisites=[],
            soft_prerequisites=[],
            is_known=False,
        )

    for prereq in prerequisites:
        if prereq.skill_id not in skill_nodes:
            continue

        if prereq.prerequisite_skill_id in known_skills:
            continue

        node = skill_nodes[prereq.skill_id]

        if prereq.dependency_type == "hard":
            node.hard_prerequisites.append(prereq.prerequisite_skill_id)
        elif prereq.dependency_type == "soft":
            node.soft_prerequisites.append(prereq.prerequisite_skill_id)

    return skill_nodes

# =========================
# STEP 4 — Ordering
# =========================

def order_skills_with_constraints(
    skill_nodes: Dict[str, SkillNode]
) -> List[str]:

    ordered: List[str] = []
    remaining = dict(skill_nodes)

    while remaining:
        available = [
            node for node in remaining.values()
            if all(
                prereq not in remaining
                for prereq in node.hard_prerequisites
            )
        ]

        if not available:
            raise ValueError("Hard prerequisite cycle detected")

        available.sort(
            key=lambda n: (
                -n.weight,
                len([
                    p for p in n.soft_prerequisites
                    if p in remaining
                ])
            )
        )

        chosen = available[0]
        ordered.append(chosen.skill_id)
        del remaining[chosen.skill_id]

    return ordered

# =========================
# STEP 5 — Resource Selection
# =========================

def select_resources_for_skills(
    ordered_skills: List[str],
    all_resources: List[LearningResource],
) -> Dict[str, List[ResourceAssignment]]:

    skill_resources: Dict[str, List[ResourceAssignment]] = {}

    for skill_id in ordered_skills:
        matched = [
            r for r in all_resources
            if skill_id in r.skill_tags
        ]

        matched.sort(key=lambda r: r.duration_hours)

        skill_resources[skill_id] = [
            ResourceAssignment(
                resource_id=r.resource_id,
                skill_id=skill_id,
                duration_hours=r.duration_hours,
            )
            for r in matched
        ]

    return skill_resources

# =========================
# Mastery Logic (Strategy-aware)
# =========================

def determine_mastery_level(
    weight: float,
    strategy: PlanStrategy,
) -> MasteryLevel:

    if strategy == PlanStrategy.FAST:
        if weight >= 0.6:
            return MasteryLevel.MEDIUM
        return MasteryLevel.LOW

    if strategy == PlanStrategy.DEEP:
        if weight >= 0.3:
            return MasteryLevel.HIGH
        return MasteryLevel.MEDIUM

    # BALANCED
    if weight >= 0.6:
        return MasteryLevel.HIGH
    elif weight >= 0.3:
        return MasteryLevel.MEDIUM
    return MasteryLevel.LOW

# =========================
# STEP 6 — Roadmap Assembly
# =========================

def assemble_learning_roadmap(
    ordered_skills: List[str],
    skill_resources: Dict[str, List[ResourceAssignment]],
    skill_graph: Dict[str, SkillNode],
    weekly_time_hours: float,
    target_job_role: str,
    strategy: PlanStrategy,
) -> LearningRoadmap:

    steps: List[RoadmapStep] = []

    for index, skill_id in enumerate(ordered_skills, start=1):
        resources = skill_resources.get(skill_id, [])

        skill_weight = skill_graph[skill_id].weight
        mastery = determine_mastery_level(skill_weight, strategy)

        coverage_ratio = {
            MasteryLevel.HIGH: 1.0,
            MasteryLevel.MEDIUM: 0.7,
            MasteryLevel.LOW: 0.4,
        }[mastery]

        full_hours = sum(r.duration_hours for r in resources)
        planned_hours = full_hours * coverage_ratio

        steps.append(
            RoadmapStep(
                order=index,
                skill_id=skill_id,
                skill_name=skill_id,
                mastery_level=mastery,
                resources=resources,
                total_hours=planned_hours,
            )
        )

    return LearningRoadmap(
        target_job_role=target_job_role,
        weekly_time_hours=weekly_time_hours,
        steps=steps,
    )

# =========================
# Single Plan Entry
# =========================

def generate_learning_roadmap(
    *,
    job_requirement,
    known_skills: List[str],
    all_skills: Dict[str, Skill],
    prerequisites: List[SkillPrerequisite],
    resources: List[LearningResource],
    weekly_time_hours: float,
    strategy: PlanStrategy = PlanStrategy.BALANCED,
) -> LearningRoadmap:

    _ensure_non_empty_list(
        job_requirement.required_skills,
        "job_requirement.required_skills",
    )
    _ensure_non_negative(
        weekly_time_hours,
        "weekly_time_hours",
    )

    missing_skills = compute_skill_gaps(
        job_requirement=job_requirement,
        known_skills=known_skills,
    )

    if not missing_skills:
        return LearningRoadmap(
            target_job_role=job_requirement.job_role_name,
            weekly_time_hours=weekly_time_hours,
            steps=[],
        )

    skill_graph = build_skill_dependency_graph(
        missing_skills=missing_skills,
        all_skills=all_skills,
        prerequisites=prerequisites,
        known_skills=known_skills,
    )

    ordered_skills = order_skills_with_constraints(skill_graph)

    skill_resources = select_resources_for_skills(
        ordered_skills=ordered_skills,
        all_resources=resources,
    )

    return assemble_learning_roadmap(
        ordered_skills=ordered_skills,
        skill_resources=skill_resources,
        skill_graph=skill_graph,
        weekly_time_hours=weekly_time_hours,
        target_job_role=job_requirement.job_role_name,
        strategy=strategy,
    )

# =========================
# Multiple Plan Generator
# =========================

def generate_multiple_learning_plans(
    *,
    job_requirement,
    known_skills,
    all_skills,
    prerequisites,
    resources,
    weekly_time_hours,
):

    plans = {}

    for strategy in [
        PlanStrategy.FAST,
        PlanStrategy.BALANCED,
        PlanStrategy.DEEP,
    ]:
        plans[strategy.value] = generate_learning_roadmap(
            job_requirement=job_requirement,
            known_skills=known_skills,
            all_skills=all_skills,
            prerequisites=prerequisites,
            resources=resources,
            weekly_time_hours=weekly_time_hours,
            strategy=strategy,
        )

    return plans

# =========================
# Weekly Scheduling
# =========================

def schedule_roadmap_weekwise(
    roadmap: LearningRoadmap,
) -> List[WeeklyPlan]:

    weekly_plan: List[WeeklyPlan] = []

    current_week = 1
    remaining_week_hours = roadmap.weekly_time_hours

    for step in roadmap.steps:
        remaining_skill_hours = step.total_hours

        while remaining_skill_hours > 0:
            if remaining_week_hours == 0:
                current_week += 1
                remaining_week_hours = roadmap.weekly_time_hours

            allocated = min(
                remaining_skill_hours,
                remaining_week_hours,
            )

            weekly_plan.append(
                WeeklyPlan(
                    week_number=current_week,
                    skill_id=step.skill_id,
                    allocated_hours=allocated,
                    resources=[r.resource_id for r in step.resources],
                )
            )

            remaining_skill_hours -= allocated
            remaining_week_hours -= allocated

    return weekly_plan

# =========================
# Explainability
# =========================

def generate_explainability_notes(
    ordered_skills: List[str],
    skill_graph: Dict[str, SkillNode],
) -> List[ExplainabilityNote]:

    notes: List[ExplainabilityNote] = []

    for index, skill_id in enumerate(ordered_skills):
        node = skill_graph[skill_id]
        reasons: List[str] = []

        reasons.append(
            f"Skill has job importance weight {node.weight}"
        )

        if node.hard_prerequisites:
            reasons.append(
                f"Has {len(node.hard_prerequisites)} hard prerequisite(s)"
            )

        if node.soft_prerequisites:
            reasons.append(
                f"Has {len(node.soft_prerequisites)} soft prerequisite(s)"
            )

        if index == 0:
            reasons.append("Scheduled early due to high priority")
        else:
            reasons.append("Scheduled after prerequisites were satisfied")

        notes.append(
            ExplainabilityNote(
                skill_id=skill_id,
                reasons=reasons,
            )
        )

    return notes
