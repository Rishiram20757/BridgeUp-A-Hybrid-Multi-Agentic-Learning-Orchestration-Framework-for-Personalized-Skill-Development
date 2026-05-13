from learning_tutor import LearningTutor


def run_test():
    tutor = LearningTutor()

    print("\n=== SESSION START ===")

    inputs = [
        "What is a list?",
        "Give example",
        "I tried creating one",
        "Test me"
    ]

    for user_input in inputs:

        res = tutor.chat(
            user_input=user_input,
            skill="Python Lists",
            level="beginner",
            goal="Understand list basics"
        )

        print("\n---------------------------")
        print("User:", user_input)
        print("Mode:", res["mode"])
        print("\nMessage:\n", res["message"])

        if res["mode"] != "quiz":
            s = res["structured"]
            print("\n[Structured]")
            print("Explanation:", s.explanation)
            print("Example:", s.example)
            print("Task:", s.practice_task)
            print("Question:", s.follow_up_question)
        else:
            q = res["structured"]
            print("\n[Quiz]")
            print("Q:", q.question)
            print("Options:", q.options)
            print("Answer:", q.answer)


if __name__ == "__main__":
    run_test()