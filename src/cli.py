
"""Command-line interface for the floor-plan assistant."""

from assistant import answer_question


def main() -> None:
    print("Ask your floor-plan assistant (type 'exit' to stop).")

    while True:
        question = input("\nQuestion: ").strip()

        if question.lower() == "exit":
            print("Goodbye!")
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            result = answer_question(question)

            print(f"\nAnswer: {result['answer']}")
            print(f"\nSQL: {result['sql']}")
            print(f"Evidence: {result['evidence']}")

        except Exception as error:
            print(f"Error processing question: {error}")


if __name__ == "__main__":
    main()
