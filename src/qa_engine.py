
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "outputs" / "floorplan.db"


def answer_question(question):

    if not question or not question.strip():
        return "Please enter a valid question."

    question = question.lower().strip()

    if not DB_FILE.exists():
        return "Database file not found."

    try:
        with sqlite3.connect(DB_FILE) as connection:

            cursor = connection.cursor()

            if "how many floor plans" in question:

                cursor.execute("""
                    SELECT COUNT(DISTINCT mask)
                    FROM floorplan_features
                """)

                result = cursor.fetchone()[0]
                answer = f"The dataset contains {result} floor plans."

            elif "how many records" in question:

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM floorplan_features
                """)

                result = cursor.fetchone()[0]
                answer = (
                    f"The database contains {result} feature records."
                )

            elif "dominant colors" in question or "dominant colours" in question:

                cursor.execute("""
                    SELECT color, SUM(pixels) AS total
                    FROM floorplan_features
                    GROUP BY color
                    ORDER BY total DESC
                """)

                rows = cursor.fetchall()

                if not rows:
                    answer = "No colour records found."

                else:
                    answer = "Dominant colors and pixel counts:\n"

                    for color, pixels in rows:
                        answer += f"{color}: {pixels} pixels\n"

            else:
                answer = (
                    "I cannot answer this question using the "
                    "currently available extracted data."
                )

            return answer

    except sqlite3.Error as error:
        return f"Database error: {error}"


if __name__ == "__main__":

    while True:

        question = input(
            "\nAsk about the floor plans (type exit to stop): "
        ).strip()

        if question.lower() == "exit":
            break

        print("\nAnswer:")
        print(answer_question(question))
