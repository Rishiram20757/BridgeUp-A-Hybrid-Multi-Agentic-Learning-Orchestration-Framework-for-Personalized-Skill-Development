from datetime import datetime
from typing import Dict, List

from .models import ExecutionState, TaskStatus, ProgressSnapshot, Task


class TaskTracker:
    def __init__(self, tasks: List[Task]):
        self._states: Dict[str, ExecutionState] = {
            task.task_id: ExecutionState(task_id=task.task_id)
            for task in tasks
        }

    # -------------------------
    # State Transitions
    # -------------------------

    def mark_task_started(self, task_id: str):
        if task_id not in self._states:
            raise ValueError(f"Unknown task_id: {task_id}")

        state = self._states[task_id]

        if state.status == TaskStatus.PENDING:
            now = datetime.utcnow()
            state.status = TaskStatus.IN_PROGRESS
            state.started_at = now
            state.last_updated = now

    def mark_task_completed(self, task_id: str):
        if task_id not in self._states:
            raise ValueError(f"Unknown task_id: {task_id}")

        state = self._states[task_id]

        if state.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS):
            now = datetime.utcnow()
            state.status = TaskStatus.COMPLETED
            state.completed_at = now
            state.last_updated = now

    def mark_task_missed(self, task_id: str):
        if task_id not in self._states:
            raise ValueError(f"Unknown task_id: {task_id}")

        state = self._states[task_id]

        if state.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS):
            now = datetime.utcnow()
            state.status = TaskStatus.MISSED
            state.last_updated = now

    # -------------------------
    # Query Methods
    # -------------------------

    def get_execution_state(self, task_id: str) -> ExecutionState:
        if task_id not in self._states:
            raise ValueError(f"Unknown task_id: {task_id}")

        return self._states[task_id]

    def all_states(self) -> List[ExecutionState]:
        return list(self._states.values())

    # -------------------------
    # Progress Snapshot
    # -------------------------

    def generate_progress_snapshot(self) -> ProgressSnapshot:
        total = len(self._states)

        completed = sum(
            1 for s in self._states.values()
            if s.status == TaskStatus.COMPLETED
        )

        in_progress = sum(
            1 for s in self._states.values()
            if s.status == TaskStatus.IN_PROGRESS
        )

        pending = sum(
            1 for s in self._states.values()
            if s.status == TaskStatus.PENDING
        )

        missed = sum(
            1 for s in self._states.values()
            if s.status == TaskStatus.MISSED
        )

        completion_percentage = (
            (completed / total) * 100 if total > 0 else 0.0
        )

        return ProgressSnapshot(
            total_tasks=total,
            completed_tasks=completed,
            in_progress_tasks=in_progress,
            pending_tasks=pending,
            missed_tasks=missed,
            completion_percentage=round(completion_percentage, 2),
            generated_at=datetime.utcnow()
        )