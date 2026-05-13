# bridgeup/agents/action_agent/models.py

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict
from typing import Optional


# -----------------------------
# Task Status Enum
# -----------------------------

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MISSED = "missed"


# -----------------------------
# Task Model
# -----------------------------

@dataclass(frozen=True)
class Task:
    """
    Atomic executable unit derived from a RoadmapStep resource.

    Immutable to guarantee deterministic behavior.
    """
    task_id: str
    roadmap_step_id: str
    title: str
    description: str
    estimated_minutes: int

    # Optional resource linkage
    resource_id: Optional[str] = None

    # Scheduling metadata (assigned later by scheduler)
    deadline: Optional[datetime] = None


# -----------------------------
# Schedule Block
# -----------------------------

@dataclass(frozen=True)
class ScheduleBlock:
    """
    Represents a fixed study time allocation.
    Deterministically created by scheduler.
    """
    block_id: str
    task_id: str
    start_time: datetime
    end_time: datetime


# -----------------------------
# Execution State
# -----------------------------

@dataclass
class ExecutionState:
    """
    Mutable execution tracking layer.

    Holds runtime state.
    Must be externally persisted by orchestrator.
    """
    task_id: str
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None


# -----------------------------
# Progress Snapshot
# -----------------------------

@dataclass(frozen=True)
class ProgressSnapshot:
    """
    Immutable summary exposed to Orchestrator.

    Deterministic aggregation of execution states.
    """
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    missed_tasks: int

    completion_percentage: float

    generated_at: datetime