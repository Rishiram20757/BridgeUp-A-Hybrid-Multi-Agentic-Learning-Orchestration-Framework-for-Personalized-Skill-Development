from datetime import datetime, timedelta
from typing import List, Tuple

from .models import Task, ScheduleBlock


STUDY_DAYS_PER_WEEK = 5


def generate_schedule(
    tasks: List[Task],
    weekly_capacity_minutes: int,
    start_date: datetime
) -> Tuple[List[ScheduleBlock], List[Task]]:
    """
    Deterministically allocate tasks into schedule blocks.
    Returns:
        - List of ScheduleBlocks
        - Updated Task list with deadlines assigned
    """

    if weekly_capacity_minutes <= 0:
        raise ValueError("weekly_capacity_minutes must be > 0")

    daily_capacity = weekly_capacity_minutes // STUDY_DAYS_PER_WEEK
    if daily_capacity <= 0:
        raise ValueError("Weekly capacity too low for daily allocation")

    schedule_blocks: List[ScheduleBlock] = []
    updated_tasks: List[Task] = []

    current_day = start_date
    remaining_daily_capacity = daily_capacity

    for task in tasks:
        remaining_task_minutes = task.estimated_minutes
        last_block_end = None

        while remaining_task_minutes > 0:
            if remaining_daily_capacity == 0:
                current_day += timedelta(days=1)
                remaining_daily_capacity = daily_capacity

            allocation = min(remaining_task_minutes, remaining_daily_capacity)

            block_start = current_day
            block_end = current_day + timedelta(minutes=allocation)

            block = ScheduleBlock(
                block_id=f"{task.task_id}:{len(schedule_blocks)}",
                task_id=task.task_id,
                start_time=block_start,
                end_time=block_end
            )

            schedule_blocks.append(block)

            remaining_task_minutes -= allocation
            remaining_daily_capacity -= allocation
            last_block_end = block_end

            # Move current time forward within the day
            current_day = block_end

        # Assign deadline to task
        updated_task = Task(
            task_id=task.task_id,
            roadmap_step_id=task.roadmap_step_id,
            title=task.title,
            description=task.description,
            estimated_minutes=task.estimated_minutes,
            resource_id=task.resource_id,
            deadline=last_block_end
        )

        updated_tasks.append(updated_task)

    return schedule_blocks, updated_tasks


def reschedule(
    incomplete_tasks: List[Task],
    weekly_capacity_minutes: int,
    new_start_date: datetime
) -> Tuple[List[ScheduleBlock], List[Task]]:
    """
    Full deterministic recompute from new anchor date.
    """
    return generate_schedule(
        tasks=incomplete_tasks,
        weekly_capacity_minutes=weekly_capacity_minutes,
        start_date=new_start_date
    )