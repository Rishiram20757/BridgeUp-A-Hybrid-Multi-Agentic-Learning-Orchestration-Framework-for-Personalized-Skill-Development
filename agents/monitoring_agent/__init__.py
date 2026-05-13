# agents/monitoring_agent/__init__.py

from pathlib import Path
from .collector import MonitoringCollector
from .metrics import MetricsEngine
from .analyzer import MonitoringAnalyzer


class MonitoringAgent:

    def __init__(self, base_path: Path):
        self.collector = MonitoringCollector(base_path)

    def get_session_metrics(self, session_id: str):
        session_signal = self.collector.get_latest_session_snapshot(
            session_id
        )
        return MetricsEngine.compute(session_signal)

    def get_risk_profile(self, session_id: str):
        session_signal = self.collector.get_latest_session_snapshot(
            session_id
        )
        metrics = MetricsEngine.compute(session_signal)
        return MonitoringAnalyzer.analyze(session_signal, metrics)

    def get_execution_summary(self, session_id: str):
        session_signal = self.collector.get_latest_session_snapshot(
            session_id
        )
        metrics = MetricsEngine.compute(session_signal)
        risk = MonitoringAnalyzer.analyze(session_signal, metrics)

        return MonitoringAnalyzer.build_execution_summary(
            session_signal,
            metrics,
            risk,
        )