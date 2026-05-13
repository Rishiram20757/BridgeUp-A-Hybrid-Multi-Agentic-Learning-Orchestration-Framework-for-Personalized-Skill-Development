# agents/monitoring_agent/analyzer.py

from datetime import datetime
from .models import (
    SessionSignal,
    MetricSnapshot,
    RiskProfile,
    ExecutionSummary,
)


class MonitoringAnalyzer:

    ANALYZER_VERSION = "v1.0"

    @staticmethod
    def analyze(
        session_signal: SessionSignal,
        metric_snapshot: MetricSnapshot,
    ) -> RiskProfile:

        issues = []
        weight = 0

        # Low Engagement
        low_engagement = (
            metric_snapshot.completion_rate < 0.4
            and metric_snapshot.consistency_score < 0.5
        )
        if low_engagement:
            issues.append("low_engagement")
            weight += 2

        # Overload
        overload = metric_snapshot.workload_utilization > 1.5
        if overload:
            issues.append("overload")
            weight += 2

        # Chronic Delay
        chronic_delay = (
            metric_snapshot.delay_index > 12 * 3600
            and metric_snapshot.completion_rate > 0.5
        )
        if chronic_delay:
            issues.append("chronic_delay")
            weight += 2

        # Unstable Execution
        unstable = metric_snapshot.stability_score < 0.4
        if unstable:
            issues.append("unstable_execution")
            weight += 1

        # Strategy Mismatch
        strategy_mismatch = False
        if session_signal.strategy_type == "FAST":
            if metric_snapshot.dropoff_risk_score > 0.3:
                strategy_mismatch = True

        if strategy_mismatch:
            issues.append("strategy_mismatch")
            weight += 1

        # Risk Level
        if weight >= 4:
            risk_level = "high"
        elif weight >= 2:
            risk_level = "medium"
        else:
            risk_level = "low"

        primary_issue = issues[0] if issues else "none"

        # Recommendation
        recommendation_map = {
            "chronic_delay": "reduce_weekly_load",
            "overload": "reduce_weekly_load",
            "low_engagement": "increase_structure",
            "unstable_execution": "increase_structure",
            "strategy_mismatch": "review_strategy",
            "none": "maintain_plan",
        }

        recommended_action = recommendation_map.get(
            primary_issue, "maintain_plan"
        )

        confidence = min(1.0, len(issues) / 5)

        return RiskProfile(
            session_id=session_signal.session_id,
            risk_level=risk_level,
            primary_issue=primary_issue,
            contributing_factors=issues,
            confidence=confidence,
            recommended_action=recommended_action,
            analyzed_at=datetime.utcnow(),
            analyzer_version=MonitoringAnalyzer.ANALYZER_VERSION,
        )

    @staticmethod
    def build_execution_summary(
        session_signal: SessionSignal,
        metric_snapshot: MetricSnapshot,
        risk_profile: RiskProfile,
    ) -> ExecutionSummary:

        if risk_profile.risk_level == "high":
            status = "at_risk"
        elif risk_profile.risk_level == "medium":
            status = "struggling"
        else:
            status = "stable"

        key_insight = f"Primary issue: {risk_profile.primary_issue}"

        return ExecutionSummary(
            session_id=session_signal.session_id,
            strategy_type=session_signal.strategy_type,
            completion_rate=metric_snapshot.completion_rate,
            risk_level=risk_profile.risk_level,
            key_insight=key_insight,
            progress_status=status,
            summary_generated_at=datetime.utcnow(),
        )