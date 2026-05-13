# agents/monitoring_agent/metrics.py

from datetime import datetime
from .models import SessionSignal, MetricSnapshot


class MetricsEngine:

    METRIC_VERSION = "v1.0"

    @staticmethod
    def compute(session_signal: SessionSignal) -> MetricSnapshot:

        total = session_signal.total_tasks
        completed = session_signal.completed_tasks
        missed = session_signal.missed_tasks

        # Completion Rate
        completion_rate = completed / total if total > 0 else 0.0

        # Delay Index
        delay_index = session_signal.average_delay_seconds

        # Workload Utilization
        if session_signal.weekly_hours_allocated > 0:
            workload_utilization = (
                session_signal.weekly_hours_used
                / session_signal.weekly_hours_allocated
            )
        else:
            workload_utilization = 0.0

        workload_utilization = min(workload_utilization, 2.0)

        # Stability Score
        stability_score = 1 / (1 + session_signal.task_interval_stddev)

        # Dropoff Risk
        dropoff_risk_score = missed / total if total > 0 else 0.0

        # Consistency
        if session_signal.planned_days > 0:
            consistency_score = (
                session_signal.active_days
                / session_signal.planned_days
            )
        else:
            consistency_score = 0.0

        consistency_score = min(consistency_score, 1.0)

        return MetricSnapshot(
            session_id=session_signal.session_id,
            completion_rate=completion_rate,
            delay_index=delay_index,
            workload_utilization=workload_utilization,
            stability_score=stability_score,
            dropoff_risk_score=dropoff_risk_score,
            consistency_score=consistency_score,
            computed_at=datetime.utcnow(),
            metric_version=MetricsEngine.METRIC_VERSION,
        )