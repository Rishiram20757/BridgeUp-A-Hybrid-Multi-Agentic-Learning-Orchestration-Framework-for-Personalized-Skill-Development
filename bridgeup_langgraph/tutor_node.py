from learning_tutor import LearningTutor

# ✅ Persistent tutor (IMPORTANT for memory)
tutor = LearningTutor()


def tutor_node(state: dict) -> dict:
    """
    Injects LearningTutor into LangGraph flow
    """

    current_task = state.get("current_task")

    if not current_task:
        print("[tutor_node] No current task found")
        return state

    task_title = current_task["title"]
    skill = current_task["skill"]
    level = current_task["level"]
    goal = current_task["goal"]

    user_input = state.get("user_input")

    print(f"\n[tutor_node] Teaching: {task_title} ({skill})")

    # --------------------------------------
    # FIRST LOAD (NO USER INPUT)
    # --------------------------------------
    if not user_input:

        lesson = tutor.generate_contextual_lesson(
            task_title=task_title,
            skill=skill,
            level=level
        )

        return {
            "tutor_output": {
                "mode": "teach",
                "message": lesson.explanation,
                "structured": lesson
            }
        }

    # --------------------------------------
    # INTERACTIVE CHAT
    # --------------------------------------

    response = tutor.chat(
        user_input=user_input,
        skill=skill,
        level=level,
        goal=goal
    )

    return {
        "tutor_output": response
    }