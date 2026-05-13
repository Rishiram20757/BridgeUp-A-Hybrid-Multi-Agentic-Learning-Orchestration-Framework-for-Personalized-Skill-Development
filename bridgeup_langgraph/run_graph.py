"""
BridgeUp LangGraph Runner (Interactive CLI — FIXED)
--------------------------------------------------
Graph runs once. Tutor handles interaction loop.
"""

import uuid
from datetime import datetime
from pathlib import Path
import shutil

from bridgeup_langgraph.graph import build_graph, BridgeUpGraphState
from learning_tutor.tutor import LearningTutor   # ✅ NEW


# =============================================================================
# Helpers
# =============================================================================

def reset_monitoring_state(session_id: str) -> None:
    session_dir = Path("data/monitoring_logs/sessions") / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir)


def print_summary(final_state: BridgeUpGraphState) -> None:
    print("\n" + "=" * 60)
    print("BRIDGEUP LANGGRAPH — RUN SUMMARY")
    print("=" * 60)
    print(f"  Session ID          : {final_state['session_id']}")
    print(f"  User Goal           : {final_state['user_goal']}")
    print(f"  Final Strategy      : {final_state['selected_strategy']}")
    print(f"  Strategy Rationale  : {final_state['strategy_rationale']}")
    print(f"  Adaptation Cycles   : {final_state['adaptation_cycles']}")
    print(f"  Final Decision      : {final_state['decision_action']}")
    print(f"  Decision Reason     : {final_state['decision_reason']}")

    metric = final_state.get("metric_snapshot")
    if metric:
        print(f"  Completion Rate     : {metric.completion_rate:.2f}")
        print(f"  Dropoff Risk        : {metric.dropoff_risk_score:.2f}")
        print(f"  Stability Score     : {metric.stability_score:.2f}")

    tasks = final_state.get("tasks") or []
    print(f"  Total Tasks         : {len(tasks)}")
    print("=" * 60)


def display_tutor_output(lesson):
    print("\n" + "=" * 50)
    print("📘 Tutor")
    print("=" * 50)

    print("\n🧠 Explanation:\n")
    print(lesson.explanation)

    print("\n💻 Example:\n")
    print(lesson.example)

    print("\n🧪 Practice Task:\n")
    print(lesson.practice_task)

    print("\n❓ Question:\n")
    print(lesson.follow_up_question)

    print("\n" + "=" * 50)


# =============================================================================
# Entry point
# =============================================================================

def run() -> BridgeUpGraphState:

    session_id = str(uuid.uuid4())
    reset_monitoring_state(session_id)

    # --------------------------------------------------
    # INITIAL STATE
    # --------------------------------------------------
    initial_state: BridgeUpGraphState = {
        "session_id": session_id,
        "user_goal": "Backend Developer",
        "known_skills": ["Python"],
        "weekly_hours": 10,
        "start_date": datetime(2026, 1, 1),

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

        "current_task": None,
        "current_task_index": 0,
    }

    print("\n" + "=" * 60)
    print("BRIDGEUP — INTERACTIVE LEARNING SESSION")
    print(f"Session : {session_id}")
    print("=" * 60)

    graph = build_graph()

    # --------------------------------------------------
    # RUN GRAPH ONCE
    # --------------------------------------------------
    state = graph.invoke(initial_state)

    tutor = LearningTutor()

    current_task = state["current_task"]

    # FIRST LESSON
    lesson = tutor.generate_contextual_lesson(
        task_title=current_task["title"],
        skill=current_task["skill"],
        level=current_task["level"]
    )

    display_tutor_output(lesson)

    print("\n💡 Type 'exit' to quit")
    print("💡 Type 'complete' to finish task\n")

    # --------------------------------------------------
    # INTERACTION LOOP (NO GRAPH CALLS)
    # --------------------------------------------------
    while True:

        user_input = input("\nYou: ").strip()

        # EXIT
        if user_input.lower() in ["exit", "quit"]:
            print("\nSession ended.")
            break

        # --------------------------------------------------
        # COMPLETE TASK
        # --------------------------------------------------
        if "complete" in user_input.lower():

            print("\n✅ Task marked as complete.")

            tasks = state["tasks"]
            idx = state["current_task_index"] + 1

            if idx >= len(tasks):
                print("\n🎉 All tasks completed!")
                break

            # move to next task
            state["current_task_index"] = idx
            state["current_task"] = tasks[idx]

            tutor.reset_session()

            next_task = state["current_task"]

            print("\n➡ Moving to next task...\n")

            lesson = tutor.generate_contextual_lesson(
                task_title=next_task["title"],
                skill=next_task["skill"],
                level=next_task["level"]
            )

            display_tutor_output(lesson)
            continue

        # --------------------------------------------------
        # NORMAL CHAT (DIRECT TUTOR)
        # --------------------------------------------------
        current_task = state["current_task"]

        response = tutor.chat(
            user_input=user_input,
            skill=current_task["skill"],
            level=current_task["level"],
            goal=current_task["goal"]
        )

        display_tutor_output(response["structured"])

    # --------------------------------------------------
    # FINAL SUMMARY
    # --------------------------------------------------
    print_summary(state)

    return state


if __name__ == "__main__":
    run()