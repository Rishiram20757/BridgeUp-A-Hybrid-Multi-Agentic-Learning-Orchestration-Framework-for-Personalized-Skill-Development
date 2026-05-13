from typing import Dict, Any
import uuid
import time
from pathlib import Path
from datetime import datetime
from integrations.resource_aggregator import ResourceAggregator
from agents.monitoring_agent import MonitoringAgent
#from api.resource_aggregator import ResourceAggregator
from agents.llm_agent.reasoning_engine import LLMReasoningEngine

# 🔷 Unified Event System
from events.schema import EventType
from events.emitter import emit_orchestrator_event

# 🔥 LLM Advisory Layer
from agents.llm_agent.reasoning_engine import LLMReasoningEngine

from .state import (
    SessionState,
    WorkflowStage,
    PlanningStatus,
    ExecutionStatus,
    MonitoringStatus,
    ErrorRecord,
)


# =========================
# AGENT PROTOCOL
# =========================

class AgentRequest:
    def __init__(self, agent_name: str, session_id: str, input_payload: Dict[str, Any]):
        self.agent_name = agent_name
        self.session_id = session_id
        self.correlation_id = str(uuid.uuid4())
        self.input_payload = input_payload
        self.timestamp = time.time()


class AgentResponse:
    def __init__(
        self,
        agent_name: str,
        correlation_id: str,
        status: str,
        output_payload: Dict[str, Any] = None,
        error: Exception = None,
    ):
        self.agent_name = agent_name
        self.correlation_id = correlation_id
        self.status = status
        self.output_payload = output_payload
        self.error = error


# =========================
# PLANNING AGENT ADAPTER
# =========================

class PlanningAgentAdapter:

    def invoke(self, request: AgentRequest) -> AgentResponse:
        try:
            from agents.planning_agent.planner import (
                generate_multiple_learning_plans,
                schedule_roadmap_weekwise,
            )

            from data.data_loader import (
                load_all_skills,
                load_prerequisites,
                load_resources,
                load_job_requirement,
            )

            payload = request.input_payload

            all_skills = load_all_skills()
            prerequisites = load_prerequisites()
            resources = load_resources()
            job_requirement = load_job_requirement(payload["job_requirement"])

            plans = generate_multiple_learning_plans(
                job_requirement=job_requirement,
                known_skills=payload["known_skills"],
                all_skills=all_skills,
                prerequisites=prerequisites,
                resources=resources,
                weekly_time_hours=payload["weekly_time_hours"],
            )

            schedules = {
                strategy: schedule_roadmap_weekwise(plan)
                for strategy, plan in plans.items()
            }

            return AgentResponse(
                agent_name="planning",
                correlation_id=request.correlation_id,
                status="SUCCESS",
                output_payload={
                    "roadmap_options": plans,
                    "weekly_schedule": schedules,
                },
            )

        except Exception as e:
            return AgentResponse(
                agent_name="planning",
                correlation_id=request.correlation_id,
                status="FAILURE",
                error=e,
            )


# =========================
# ACTION AGENT ADAPTER
# =========================

class ActionAgentAdapter:

    def invoke(self, request: AgentRequest) -> AgentResponse:
        try:
            from agents.action_agent.executor import generate_tasks_from_roadmap
            from agents.action_agent.scheduler import generate_schedule
            from agents.action_agent.tracker import TaskTracker

            payload = request.input_payload

            roadmap = payload["learning_roadmap"]
            weekly_capacity_minutes = payload["weekly_capacity_minutes"]
            start_date = payload["start_date"]

            tasks = generate_tasks_from_roadmap(roadmap)

            schedule_blocks, updated_tasks = generate_schedule(
                tasks,
                weekly_capacity_minutes,
                start_date,
            )

            tracker = TaskTracker(updated_tasks)
            snapshot = tracker.generate_progress_snapshot()

            return AgentResponse(
                agent_name="action",
                correlation_id=request.correlation_id,
                status="SUCCESS",
                output_payload={
                    "tasks": updated_tasks,
                    "schedule_blocks": schedule_blocks,
                    "progress_snapshot": snapshot,
                },
            )

        except Exception as e:
            return AgentResponse(
                agent_name="action",
                correlation_id=request.correlation_id,
                status="FAILURE",
                error=e,
            )


# =========================
# ORCHESTRATOR ENGINE
# =========================

class Orchestrator:

    def __init__(self):
        self.agent_registry = {
            "planning": PlanningAgentAdapter(),
            "action": ActionAgentAdapter(),
        }

        self.monitor = MonitoringAgent(
            base_path=Path("data/monitoring_logs")
        )

        # 🔥 LLM Advisory Layer (Suggest-Only)
        self.llm_engine = LLMReasoningEngine()
        self.resource_aggregator = ResourceAggregator()
        self.resource_aggregator = ResourceAggregator()
        self.reasoning_engine = LLMReasoningEngine()

    # =========================
    # ENTRY POINT
    # =========================

    def handle_request(self, request: Dict[str, Any], state: SessionState) -> Dict[str, Any]:

        try:
            self._validate_request(request)

            emit_orchestrator_event(
                EventType.SESSION_STARTED,
                state.session_id,
                payload={"user_id": request.get("user_id", "anonymous")}
            )

            state.current_stage = WorkflowStage.VALIDATED
            state.update_timestamp()

            state.request_history.append({
                "request_id": str(uuid.uuid4()),
                "request_type": request.get("request_type", "generate_plan"),
                "timestamp": time.time(),
            })

            if request.get("request_type") == "generate_plan_and_execute":
                return self._execute_full_pipeline(request, state)

            return self._execute_planning_workflow(request, state)

        except Exception as e:
            emit_orchestrator_event(
                EventType.ERROR,
                state.session_id,
                payload={"error_message": str(e)}
            )
            raise

    # =========================
    # PLANNING WORKFLOW
    # =========================

    def _execute_planning_workflow(self, request: Dict[str, Any], state: SessionState):

        state.current_stage = WorkflowStage.PLANNING
        state.planning_state.planning_status = PlanningStatus.IN_PROGRESS
        state.planning_state.input_payload = request
        state.update_timestamp()

        # =====================================
        # 🔥 LLM Advisory Suggestion (Non-Blocking)
        # =====================================
        try:
            llm_suggestion = self.llm_engine.suggest_strategy(
                user_goal=request["job_requirement"],
                weekly_hours=request["weekly_time_hours"],
                known_skills=request["known_skills"],
            )

            state.planning_state.explainability_notes = {
                "llm_strategy_suggestion": llm_suggestion.model_dump()
            }

        except Exception as e:
            state.planning_state.explainability_notes = {
                "llm_strategy_suggestion_error": str(e)
            }

        agent = self.agent_registry["planning"]

        agent_request = AgentRequest(
            agent_name="planning",
            session_id=state.session_id,
            input_payload=request,
        )

        response = agent.invoke(agent_request)

        if response.status != "SUCCESS":
            state.current_stage = WorkflowStage.ERROR
            state.planning_state.planning_status = PlanningStatus.FAILED
            return {
                "session_id": state.session_id,
                "state": "ERROR",
                "error": str(response.error),
            }

        state.planning_state.roadmap_options = response.output_payload["roadmap_options"]
        state.planning_state.weekly_schedule = response.output_payload["weekly_schedule"]
        state.planning_state.selected_strategy = request.get("strategy", "balanced")
        state.planning_state.planning_status = PlanningStatus.COMPLETED

        try:
            selected_strategy = state.planning_state.selected_strategy
            roadmap = state.planning_state.roadmap_options[selected_strategy]
            explanation = self.llm_engine.explain_roadmap(roadmap)

            state.planning_state.explainability_notes["roadmap_explanation"] = (
                explanation.model_dump()
            )

        except Exception as e:
            state.planning_state.explainability_notes["roadmap_explanation_error"] = str(e)

        # =====================================
        # 🔥 RESOURCE INTELLIGENCE LAYER
        # =====================================

        try:
            skill = request["job_requirement"]
            aggregated_resources = self.resource_aggregator.collect_by_skill(skill)

            ranked_resources = self.llm_engine.rank_resources(
                aggregated_resources
            )

            learning_plan = self.llm_engine.generate_learning_plan(
                aggregated_resources,
                ranked_resources
            )

            if state.planning_state.explainability_notes is None:
                state.planning_state.explainability_notes = {}

            state.planning_state.explainability_notes["resource_intelligence"] = {
                "skill": aggregated_resources.skill,
                "ranked_resources": ranked_resources.model_dump(),
                "learning_plan": learning_plan.model_dump()
            }

        except Exception as e:
            if state.planning_state.explainability_notes is None:
                state.planning_state.explainability_notes = {}

            state.planning_state.explainability_notes["resource_intelligence_error"] = str(e)

        state.current_stage = WorkflowStage.PLAN_READY
        state.update_timestamp()

        plan_id = f"{state.session_id}:{state.planning_state.selected_strategy}"

        total_tasks = 0
        selected_plan = state.planning_state.roadmap_options[state.planning_state.selected_strategy]

        for step in selected_plan.steps:
            total_tasks += len(step.resources)

        emit_orchestrator_event(
            EventType.PLAN_READY,
            state.session_id,
            payload={
                "plan_id": plan_id,
                "total_tasks": total_tasks
            }
        )

        return {
            "session_id": state.session_id,
            "state": state.current_stage.value,
            "roadmap_options": state.planning_state.roadmap_options,
            "weekly_schedule": state.planning_state.weekly_schedule,
            "llm_advisory": state.planning_state.explainability_notes,
        }

    # =========================
    # FULL PIPELINE WORKFLOW
    # =========================

    def _execute_full_pipeline(self, request: Dict[str, Any], state: SessionState):

        planning_result = self._execute_planning_workflow(request, state)

        if state.current_stage != WorkflowStage.PLAN_READY:
            return planning_result

        selected_strategy = state.planning_state.selected_strategy
        roadmap = state.planning_state.roadmap_options[selected_strategy]

        # ====================================
        # RESOURCE INTELLIGENCE STAGE
        # ====================================

        skills = [step.skill_name for step in roadmap.steps]

        aggregated_resources = []
        ranked_resources = []
        learning_plans = []

        for skill in skills:

            resources = self.resource_aggregator.collect_by_skill(skill)

            aggregated_resources.append(resources)

            ranked = self.reasoning_engine.rank_resources(resources)

            ranked_resources.append(ranked)

            learning_plan = self.reasoning_engine.generate_learning_plan(
                resources,
                ranked
            )

            learning_plans.append(learning_plan)

        state.llm_ranked_resources = ranked_resources
        state.llm_learning_plan = learning_plans

        roadmap_id = f"{state.session_id}:{selected_strategy}"
        setattr(roadmap, "roadmap_id", roadmap_id)

        emit_orchestrator_event(
            EventType.EXECUTION_STARTED,
            state.session_id,
            payload={"plan_id": roadmap_id}
        )

        action_agent = self.agent_registry["action"]

        action_request = AgentRequest(
            agent_name="action",
            session_id=state.session_id,
            input_payload={
                "learning_roadmap": roadmap,
                "weekly_capacity_minutes": request["weekly_time_hours"] * 60,
                "start_date": request.get("start_date"),
            },
        )

        action_response = action_agent.invoke(action_request)

        if action_response.status != "SUCCESS":
            state.current_stage = WorkflowStage.ERROR
            return {
                "session_id": state.session_id,
                "state": "ERROR",
                "error": str(action_response.error),
            }

        state.execution_state.tasks = action_response.output_payload["tasks"]
        state.execution_state.schedule_blocks = action_response.output_payload["schedule_blocks"]
        state.execution_state.progress_snapshot = action_response.output_payload["progress_snapshot"]
        state.execution_state.execution_status = ExecutionStatus.ACTIVE

        session_id = state.session_id
        strategy = selected_strategy
        weekly_hours = request["weekly_time_hours"]
        planned_days = 5

        for task in state.execution_state.tasks:

            first_block = next(
                (b for b in state.execution_state.schedule_blocks if b.task_id == task.task_id),
                None
            )

            event = {
                "event_type": "TASK_CREATED",
                "task_id": task.task_id,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {
                    "strategy_type": strategy,
                    "scheduled_start": first_block.start_time.isoformat() if first_block else None,
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                    "new_deadline": None,
                },
            }

            self.monitor.collector.record_task_event(event)

        self.monitor.collector.build_session_snapshot(
            session_id=session_id,
            weekly_hours_allocated=weekly_hours,
            planned_days=planned_days
        )

        metrics = self.monitor.get_session_metrics(session_id)
        risk = self.monitor.get_risk_profile(session_id)
        summary = self.monitor.get_execution_summary(session_id)

        state.monitoring_state.performance_metrics = metrics
        state.monitoring_state.monitoring_report = {
            "risk_profile": risk,
            "execution_summary": summary,
        }

        try:
            monitoring_feedback = self.llm_engine.generate_monitoring_feedback(
                metrics=metrics,
                risk_profile=risk,
            )

            state.monitoring_state.monitoring_report["llm_feedback"] = (
                monitoring_feedback.model_dump()
            )

        except Exception as e:
            state.monitoring_state.monitoring_report["llm_feedback_error"] = str(e)

        try:
            reflection = self.llm_engine.generate_reflection_feedback(
                metrics=metrics,
                risk_profile=risk,
                execution_summary=summary,
            )

            state.monitoring_state.monitoring_report["reflection"] = (
                reflection.model_dump()
            )

        except Exception as e:
            state.monitoring_state.monitoring_report["reflection_error"] = str(e)

        state.monitoring_state.monitoring_status = MonitoringStatus.RUNNING

        state.current_stage = WorkflowStage.EXECUTION_ACTIVE
        state.update_timestamp()

        return {
            "session_id": state.session_id,
            "state": state.current_stage.value,
            "schedule": state.execution_state.schedule_blocks,
            "progress_snapshot": state.execution_state.progress_snapshot,
            "monitoring": state.monitoring_state.monitoring_report,
            "ranked_resources": state.llm_ranked_resources,
            "learning_plan": state.llm_learning_plan
        }

    # =========================
    # VALIDATION
    # =========================

    def _validate_request(self, request: Dict[str, Any]):

        required_fields = ["job_requirement", "known_skills", "weekly_time_hours"]

        for field in required_fields:
            if field not in request:
                raise ValueError(f"Missing required field: {field}")

        if not isinstance(request["known_skills"], list):
            raise ValueError("known_skills must be a list")

        if request["weekly_time_hours"] <= 0:
            raise ValueError("weekly_time_hours must be > 0")