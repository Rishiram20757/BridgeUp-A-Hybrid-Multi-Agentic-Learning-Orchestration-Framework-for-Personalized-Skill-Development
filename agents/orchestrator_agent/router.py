from typing import Dict
from .state import SessionState


class WorkflowRouter:

    @staticmethod
    def resolve_workflow(request: Dict, state: SessionState) -> str:
        request_type = request.get("request_type", "generate_plan")

        if request_type == "generate_plan":
            return "planning_only"

        if request_type == "full_pipeline":
            return "planning_action_monitor"

        if request_type == "replan":
            return "replanning"

        if request_type == "execute_plan":
            return "execution_only"

        if request_type == "monitor_progress":
            return "monitoring_only"

        return "planning_only"
