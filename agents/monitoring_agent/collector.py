# agents/monitoring_agent/collector.py

import json
import statistics
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

from .models import TaskSignal, SessionSignal


# -----------------------------
# Utilities
# -----------------------------

def _dt(dt_str: str) -> datetime:
    return datetime.fromisoformat(dt_str)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


# -----------------------------
# Collector
# -----------------------------

class MonitoringCollector:

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.sessions_path = self.base_path / "sessions"
        self.sessions_path.mkdir(parents=True, exist_ok=True)

    # ==========================================================
    # EVENT INGESTION
    # ==========================================================

    def record_task_event(self, event: Dict) -> None:

        session_id = event["session_id"]
        task_id = event["task_id"]
        event_type = event["event_type"]
        timestamp = _dt(event["timestamp"])
        payload = event.get("payload", {})

        tasks = self._load_tasks(session_id)

        task = tasks.get(task_id)

        # -------------------------
        # TASK CREATED
        # -------------------------
        if event_type == "TASK_CREATED":

            if task is not None:
                return  # idempotent

            tasks[task_id] = {
                "task_id": task_id,
                "session_id": session_id,
                "strategy_type": payload["strategy_type"],
                "created_at": event["timestamp"],
                "scheduled_start": payload["scheduled_start"],
                "deadline": payload["deadline"],
                "started_at": None,
                "completed_at": None,
                "status": "pending",
                "reschedule_count": 0,
                "delay_duration_seconds": 0.0,
                "execution_duration_seconds": None,
                "was_early": False,
            }

        # -------------------------
        # TASK STARTED
        # -------------------------
        elif event_type == "TASK_STARTED":

            if task and task["started_at"] is None:
                task["started_at"] = event["timestamp"]
                task["status"] = "in_progress"

        # -------------------------
        # TASK COMPLETED
        # -------------------------
        elif event_type == "TASK_COMPLETED":

            if task and task["completed_at"] is None:

                task["completed_at"] = event["timestamp"]
                task["status"] = "completed"

                deadline = _dt(task["deadline"])
                delay = (timestamp - deadline).total_seconds()
                task["delay_duration_seconds"] = max(0.0, delay)
                task["was_early"] = timestamp < deadline

                if task["started_at"]:
                    start = _dt(task["started_at"])
                    task["execution_duration_seconds"] = (
                        timestamp - start
                    ).total_seconds()

        # -------------------------
        # TASK MISSED
        # -------------------------
        elif event_type == "TASK_MISSED":

            if task and task["status"] != "completed":
                task["status"] = "missed"

        # -------------------------
        # TASK RESCHEDULED
        # -------------------------
        elif event_type == "TASK_RESCHEDULED":

            if task:
                new_deadline = payload["new_deadline"]
                if new_deadline != task["deadline"]:
                    task["deadline"] = new_deadline
                    task["reschedule_count"] += 1

        self._save_tasks(session_id, tasks)

    # ==========================================================
    # SNAPSHOT BUILDER
    # ==========================================================

    def build_session_snapshot(
        self,
        session_id: str,
        weekly_hours_allocated: float = 0.0,
        planned_days: int = 7,
    ) -> SessionSignal:

        tasks = self._load_tasks(session_id)

        if not tasks:
            raise ValueError("No tasks found for session")

        task_list = list(tasks.values())

        strategy_type = task_list[0]["strategy_type"]

        total_tasks = len(task_list)
        completed = [t for t in task_list if t["status"] == "completed"]
        missed = [t for t in task_list if t["status"] == "missed"]
        pending = [t for t in task_list if t["status"] == "pending"]

        total_reschedules = sum(t["reschedule_count"] for t in task_list)

        # Weekly Hours Used
        total_exec_seconds = sum(
            t["execution_duration_seconds"] or 0 for t in completed
        )
        weekly_hours_used = total_exec_seconds / 3600

        # Active Days
        activity_dates = set()
        completion_times = []

        for t in completed:
            if t["started_at"]:
                activity_dates.add(_dt(t["started_at"]).date())
            activity_dates.add(_dt(t["completed_at"]).date())
            completion_times.append(_dt(t["completed_at"]))

        active_days = len(activity_dates)

        # Inactivity Periods (>48h)
        inactivity_periods = 0
        completion_times.sort()
        for i in range(1, len(completion_times)):
            gap = completion_times[i] - completion_times[i - 1]
            if gap > timedelta(hours=48):
                inactivity_periods += 1

        # Early Completions
        early_completions = sum(1 for t in completed if t["was_early"])

        # Average Delay
        if completed:
            avg_delay = sum(
                t["delay_duration_seconds"] for t in completed
            ) / len(completed)
        else:
            avg_delay = 0.0

        # Task Interval Stddev
        if len(completion_times) > 1:
            intervals = [
                (completion_times[i] - completion_times[i - 1]).total_seconds()
                for i in range(1, len(completion_times))
            ]
            stddev = statistics.pstdev(intervals)
        else:
            stddev = 0.0

        snapshot = SessionSignal(
            session_id=session_id,
            strategy_type=strategy_type,
            total_tasks=total_tasks,
            completed_tasks=len(completed),
            missed_tasks=len(missed),
            pending_tasks=len(pending),
            total_reschedules=total_reschedules,
            weekly_hours_allocated=weekly_hours_allocated,
            weekly_hours_used=weekly_hours_used,
            active_days=active_days,
            planned_days=planned_days,
            inactivity_periods=inactivity_periods,
            early_completions=early_completions,
            average_delay_seconds=avg_delay,
            task_interval_stddev=stddev,
            snapshot_timestamp=datetime.utcnow(),
        )

        self._save_snapshot(session_id, snapshot)

        return snapshot

    # ==========================================================
    # ACCESSORS
    # ==========================================================

    def get_latest_session_snapshot(self, session_id: str) -> SessionSignal:

        snapshots = self._load_snapshots(session_id)

        if not snapshots:
            raise ValueError("No session snapshots found")

        latest = snapshots[-1]

        return self._dict_to_session_signal(latest)

    # ==========================================================
    # STORAGE
    # ==========================================================

    def _session_dir(self, session_id: str) -> Path:
        path = self.sessions_path / session_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _load_tasks(self, session_id: str) -> Dict:
        path = self._session_dir(session_id) / "tasks.json"
        if not path.exists():
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def _save_tasks(self, session_id: str, tasks: Dict) -> None:
        path = self._session_dir(session_id) / "tasks.json"
        with open(path, "w") as f:
            json.dump(tasks, f, indent=2)

    def _save_snapshot(self, session_id: str, snapshot: SessionSignal):
        path = self._session_dir(session_id) / "session_snapshots.json"

        snapshots = []
        if path.exists():
            with open(path, "r") as f:
                snapshots = json.load(f)

        snapshots.append(snapshot.__dict__)

        with open(path, "w") as f:
            json.dump(snapshots, f, indent=2, default=str)

    def _load_snapshots(self, session_id: str) -> List[Dict]:
        path = self._session_dir(session_id) / "session_snapshots.json"
        if not path.exists():
            return []
        with open(path, "r") as f:
            return json.load(f)

    def _dict_to_session_signal(self, data: Dict) -> SessionSignal:
        data["snapshot_timestamp"] = _dt(data["snapshot_timestamp"])
        return SessionSignal(**data)