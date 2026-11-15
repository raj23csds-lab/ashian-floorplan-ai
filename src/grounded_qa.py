
import sqlite3
from pathlib import Path
from gemini_client import ask_gemini

DB_FILE = (
    Path(__file__).resolve().parent.parent
    / "outputs"
    / "floorplan.db"
)


def get_database_context():

    if not DB_FILE.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_FILE}"
        )

    with sqlite3.connect(DB_FILE) as connection:

        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(DISTINCT mask) FROM floorplan_features"
        )
        plans = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM floorplan_features"
        )
        records = cursor.fetchone()[0]

        cursor.execute("""
            SELECT color, SUM(pixels)
            FROM floorplan_features
            GROUP BY color
            ORDER BY SUM(pixels) DESC
        """)

        colors = cursor.fetchall()

    context = f"""
Verified dataset facts:

Total floor plans: {plans}
Total feature records: {records}

Aggregated color pixel counts:
{colors}

Important limitations:
- Colors have not been reliably mapped to room types.
- Bedroom, kitchen, door and window counts are not verified.
- Pixel counts must not be treated as object counts.
- Do not invent measurements or object counts.
"""

    return context


def answer_question(question):

    if not question or not question.strip():
        return "Please enter a valid question."

    question_lower = question.lower()

    supported_topics = [
        "floor plan",
        "floor plans",
        "plan",
        "plans",
        "records",
        "dominant colors",
        "dominant colours",
        "pixel",
        "colour",
        "color",
        "dataset"
    ]

    if not any(
        topic in question_lower
        for topic in supported_topics
    ):
        return (
            "I cannot answer this question because the "
            "required information is not available "
            "in the verified dataset."
        )

    try:
        context = get_database_context()

        prompt = f"""
You are a floor-plan data assistant.

Answer the user's question using ONLY the verified
database facts provided below.

Rules:
1. Never invent information.
2. Do not infer room types from RGB colors.
3. If evidence is insufficient, say so clearly.
4. Keep answers concise.
5. Distinguish pixel counts from object counts.
6. Do not claim that a color represents a room
   unless verified data supports it.

VERIFIED DATA:
{context}

USER QUESTION:
{question.strip()}
"""

        return ask_gemini(prompt)

    except Exception as error:
        return f"Unable to retrieve verified data: {error}"


if __name__ == "__main__":

    while True:

        question = input(
            "\nAsk a floor-plan question (exit to stop): "
        ).strip()

        if question.lower() == "exit":
            break

        print("\nAI Answer:")
        print(answer_question(question))
