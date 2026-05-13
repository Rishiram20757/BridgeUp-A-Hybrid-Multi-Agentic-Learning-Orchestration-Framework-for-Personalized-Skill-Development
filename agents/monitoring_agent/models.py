# agents/monitoring_agent/models.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


# -----------------------------
# Task Level
# -----------------------------

@dataclass
class TaskSignal:
    task_id: str
    session_id: str
    strategy_type: str

    created_at: datetime
    scheduled_start: datetime
    deadline: datetime

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    status: str = "pending"
    reschedule_count: int = 0

    delay_duration_seconds: float = 0.0
    execution_duration_seconds: Optional[float] = None
    was_early: bool = False


# -----------------------------
# Session Level
# -----------------------------

@dataclass
class SessionSignal:
    session_id: str
    strategy_type: str

    total_tasks: int
    completed_tasks: int
    missed_tasks: int
    pending_tasks: int

    total_reschedules: int
    weekly_hours_allocated: float
    weekly_hours_used: float

    active_days: int
    planned_days: int
    inactivity_periods: int
    early_completions: int

    average_delay_seconds: float
    task_interval_stddev: float

    snapshot_timestamp: datetime


# -----------------------------
# Metrics
# -----------------------------

@dataclass
class MetricSnapshot:
    session_id: str

    completion_rate: float
    delay_index: float
    workload_utilization: float
    stability_score: float
    dropoff_risk_score: float
    consistency_score: float

    computed_at: datetime
    metric_version: str


# -----------------------------
# Risk Profile
# -----------------------------

@dataclass
class RiskProfile:
    session_id: str

    risk_level: str
    primary_issue: str
    contributing_factors: List[str]
    confidence: float
    recommended_action: str

    analyzed_at: datetime
    analyzer_version: str


# -----------------------------
# Execution Summary
# -----------------------------

@dataclass
class ExecutionSummary:
    session_id: str
    strategy_type: str

    completion_rate: float
    risk_level: str
    key_insight: str
    progress_status: str

    summary_generated_at: datetime