import uuid
from datetime import datetime
from bridgeup_langgraph.graph import build_graph


def run_bridgeup(goal, skills, hours):

    graph = build_graph()

    initial_state = {
        "session_id": str(uuid.uuid4()),
        "user_goal": goal,
        "known_skills": skills,
        "weekly_hours": hours,
        "start_date": datetime.now(),

        "selected_strategy": "",
        "strategy_rationale": "",
        "roadmap": None,
        "tasks": [],
        "schedule_blocks": [],
        "metric_snapshot": None,
        "risk_profile": None,
        "execution_summary": None,
        "decision_action": "",
        "decision_reason": "",
        "adaptation_cycles": 0,
        "_session_state": None,
        "_monitor": None,
    }

    return graph.invoke(initial_state)