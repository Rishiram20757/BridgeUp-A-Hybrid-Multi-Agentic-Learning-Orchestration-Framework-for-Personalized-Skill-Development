from typing import List
from math import ceil
from .models import Task


# Deterministic chunk size (in minutes)
CHUNK_MINUTES = 120  # 2-hour segments


def generate_tasks_from_roadmap(learning_roadmap) -> List[Task]:
    """
    Deterministically converts a LearningRoadmap into
    a granular ordered list of executable micro-tasks.

    Each resource is split into fixed-size chunks to enable
    meaningful behavioral simulation and monitoring metrics.

    No scheduling logic here.
    No state mutation.
    """

    tasks: List[Task] = []

    # Orchestrator injects this dynamically
    roadmap_id = getattr(learning_roadmap, "roadmap_id", "unknown")

    for step in learning_roadmap.steps:

        step_id = step.order  # Planning Agent uses 'order'

        for resource in step.resources:

            total_minutes = int(resource.duration_hours * 60)

            # Determine number of chunks
            num_chunks = ceil(total_minutes / CHUNK_MINUTES)

            for chunk_index in range(num_chunks):

                start_minute = chunk_index * CHUNK_MINUTES
                remaining = total_minutes - start_minute
                chunk_minutes = min(CHUNK_MINUTES, remaining)

                task_id = (
                    f"{roadmap_id}:{step_id}:"
                    f"{resource.resource_id}:{chunk_index}"
                )

                task = Task(
                    task_id=task_id,
                    roadmap_step_id=step_id,
                    title=f"Learn {step.skill_name} (Part {chunk_index + 1})",
                    description=(
                        f"Complete resource {resource.resource_id} "
                        f"[Segment {chunk_index + 1}/{num_chunks}] "
                        f"for skill {step.skill_name}"
                    ),
                    estimated_minutes=chunk_minutes,
                    resource_id=resource.resource_id,
                    deadline=None  # assigned by scheduler
                )

                tasks.append(task)

    return tasks