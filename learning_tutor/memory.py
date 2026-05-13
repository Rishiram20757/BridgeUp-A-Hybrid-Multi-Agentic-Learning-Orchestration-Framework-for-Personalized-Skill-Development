from collections import deque


class TutorMemory:
    def __init__(self, max_history: int = 3):
        self.history = deque(maxlen=max_history)

    def add(self, user_input: str, tutor_response: dict):
        self.history.append({
            "user": user_input,
            "tutor": tutor_response
        })

    def get_context(self) -> str:
        if not self.history:
            return "No previous context."

        context = ""
        for i, item in enumerate(self.history):
            context += f"\nInteraction {i+1}:\n"
            context += f"User: {item['user']}\n"
            context += f"Tutor: {item['tutor']['explanation']}\n"

        return context.strip()