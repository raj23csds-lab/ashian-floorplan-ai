
import sys
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retrieval_engine import retrieve_data

DB_FILE = ROOT / "outputs" / "floorplan.db"


def reference_answer(question):
    """Calculate a reference result directly from SQLite."""
    q = question.lower()

    with sqlite3.connect(DB_FILE) as conn:
        if "average" in q:
            sql = """
                SELECT ROUND(AVG(room_count), 2)
                FROM (
                    SELECT plan_id, COUNT(*) AS room_count
                    FROM elements
                    WHERE element_type = 'room'
                    GROUP BY plan_id
                )
            """
            return conn.execute(sql).fetchall()

        if "more than 3 doors" in q:
            sql = """
                SELECT plan_id, COUNT(*)
                FROM elements
                WHERE element_type = 'door'
                GROUP BY plan_id
                HAVING COUNT(*) > 3
                ORDER BY plan_id
            """
            return conn.execute(sql).fetchall()

        if "floor plans" in q:
            return conn.execute(
                "SELECT COUNT(*) FROM plans"
            ).fetchall()

        if "components" in q and "dataset" in q:
            return conn.execute(
                "SELECT COUNT(*) FROM elements"
            ).fetchall()

        import re
        match = re.search(r"plan\s+(\d+)", q)
        if not match:
            return None

        plan_id = int(match.group(1))

        if "largest room" in q:
            sql = """
                SELECT id, area_pixels, x, y, width, height
                FROM elements
                WHERE plan_id = ? AND element_type = 'room'
                ORDER BY area_pixels DESC
                LIMIT 1
            """
            return conn.execute(sql, (plan_id,)).fetchall()

        if "no windows" in q:
            sql = """
                SELECT r.id, r.area_pixels, r.x, r.y, r.width, r.height
                FROM elements AS r
                WHERE r.plan_id = ? AND r.element_type = 'room'
                AND NOT EXISTS (
                    SELECT 1 FROM element_links AS l
                    WHERE l.room_id = r.id
                    AND l.relation = 'window_near_room'
                )
                ORDER BY r.id
            """
            return conn.execute(sql, (plan_id,)).fetchall()

        for element_type in ["room", "window", "door", "wall"]:
            if element_type in q:
                sql = """
                    SELECT COUNT(*) FROM elements
                    WHERE plan_id = ? AND element_type = ?
                """
                return conn.execute(
                    sql, (plan_id, element_type)
                ).fetchall()

    return None


QUESTIONS = [
    "How many rooms does plan 1 have?",
    "How many windows does plan 1 have?",
    "How many doors does plan 1 have?",
    "How many walls does plan 1 have?",
    "What is the largest room in plan 1?",
    "Which room in plan 1 has no windows?",
    "How many rooms does plan 2 have?",
    "How many windows does plan 2 have?",
    "How many doors does plan 2 have?",
    "How many walls does plan 2 have?",
    "What is the largest room in plan 2?",
    "Which room in plan 2 has no windows?",
    "How many rooms does plan 3 have?",
    "How many windows does plan 3 have?",
    "How many doors does plan 3 have?",
    "How many walls does plan 3 have?",
    "What is the average number of rooms across all plans?",
    "Which plans have more than 3 doors?",
    "How many floor plans are in the dataset?",
    "How many components are in the dataset?",
]


def test_evaluation_accuracy():
    passed = 0
    failures = []

    for question in QUESTIONS:
        actual = retrieve_data(question)
        expected = reference_answer(question)

        if actual is not None and expected is not None and actual["evidence"] == expected:
            passed += 1
        else:
            failures.append(question)

    accuracy = passed / len(QUESTIONS) * 100

    print(f"\nEvaluation questions: {len(QUESTIONS)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(failures)}")
    print(f"SQL consistency score: {accuracy:.2f}%")

    if failures:
        print("Failed questions:")
        for question in failures:
            print("-", question)

    assert not failures, "Some retrieval results differ from reference SQL."

