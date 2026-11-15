
"""Independently evaluate the floor-plan assistant using 20 test questions."""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from retrieval_engine import DB_FILE, retrieve_data


QUESTIONS = [
    "How many rooms does plan 12 have?",
    "What is the largest room in plan 7?",
    "Which plans have more than 3 doors?",
    "Which room in plan 4 has no windows?",
    "What is the average number of rooms across all plans?",
    "How many rooms does plan 1 have?",
    "How many doors does plan 4 have?",
    "How many windows does plan 7 have?",
    "How many walls does plan 12 have?",
    "How many rooms does plan 4 have?",
    "What is the largest room in plan 4?",
    "How many rooms does plan 7 have?",
    "What is the largest room in plan 12?",
    "How many windows does plan 12 have?",
    "How many doors does plan 12 have?",
    "How many walls does plan 7 have?",
    "How many floor plans are in the dataset?",
    "How many components are in the dataset?",
    "How many rooms does plan 20 have?",
    "How many doors does plan 20 have?",
]


def _rooms_without_windows(connection, plan_id):
    """Find rooms that have no linked windows."""

    rooms = connection.execute(
        """
        SELECT id, area_pixels, x, y, width, height
        FROM elements
        WHERE plan_id = ? AND element_type = 'room'
        """,
        (plan_id,),
    ).fetchall()

    window_room_ids = {
        row[0]
        for row in connection.execute(
            """
            SELECT DISTINCT room_id
            FROM element_links
            WHERE relation = 'window_near_room'
            """
        )
    }

    return [
        room for room in rooms
        if room[0] not in window_room_ids
    ]


def expected_answers():
    """Generate expected results using independent SQL queries."""

    with sqlite3.connect(DB_FILE) as connection:

        expected = [
            # 1. Rooms in plan 12
            [(
                connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM elements
                    WHERE plan_id = 12 AND element_type = 'room'
                    """
                ).fetchone()[0],
            )],

            # 2. Largest room in plan 7
            connection.execute(
                """
                SELECT id, area_pixels, x, y, width, height
                FROM elements
                WHERE plan_id = 7 AND element_type = 'room'
                ORDER BY area_pixels DESC
                LIMIT 1
                """
            ).fetchall(),

            # 3. Plans with more than 3 doors
            connection.execute(
                """
                SELECT plan_id, COUNT(*)
                FROM elements
                WHERE element_type = 'door'
                GROUP BY plan_id
                HAVING COUNT(*) > 3
                ORDER BY plan_id
                """
            ).fetchall(),

            # 4. Rooms without windows in plan 4
            _rooms_without_windows(connection, 4),

            # 5. Average number of rooms
            [(
                connection.execute(
                    """
                    SELECT ROUND(AVG(room_count), 2)
                    FROM (
                        SELECT p.plan_id, COUNT(e.id) AS room_count
                        FROM plans p
                        LEFT JOIN elements e
                            ON e.plan_id = p.plan_id
                            AND e.element_type = 'room'
                        GROUP BY p.plan_id
                    )
                    """
                ).fetchone()[0],
            )],
        ]

        # Additional count questions
        count_questions = [
            (1, "room"),
            (4, "door"),
            (7, "window"),
            (12, "wall"),
            (4, "room"),
        ]

        for plan_id, element_type in count_questions:
            result = connection.execute(
                """
                SELECT COUNT(*)
                FROM elements
                WHERE plan_id = ? AND element_type = ?
                """,
                (plan_id, element_type),
            ).fetchone()[0]

            expected.append([(result,)])

        # 11. Largest room in plan 4
        expected.append(
            connection.execute(
                """
                SELECT id, area_pixels, x, y, width, height
                FROM elements
                WHERE plan_id = 4 AND element_type = 'room'
                ORDER BY area_pixels DESC
                LIMIT 1
                """
            ).fetchall()
        )

        # 12. Rooms in plan 7
        expected.append([(
            connection.execute(
                """
                SELECT COUNT(*)
                FROM elements
                WHERE plan_id = 7 AND element_type = 'room'
                """
            ).fetchone()[0],
        )])

        # 13. Largest room in plan 12
        expected.append(
            connection.execute(
                """
                SELECT id, area_pixels, x, y, width, height
                FROM elements
                WHERE plan_id = 12 AND element_type = 'room'
                ORDER BY area_pixels DESC
                LIMIT 1
                """
            ).fetchall()
        )

        # 14, 15 and 16. Additional counts
        for plan_id, element_type in [
            (12, "window"),
            (12, "door"),
            (7, "wall"),
        ]:
            result = connection.execute(
                """
                SELECT COUNT(*)
                FROM elements
                WHERE plan_id = ? AND element_type = ?
                """,
                (plan_id, element_type),
            ).fetchone()[0]

            expected.append([(result,)])

        # 17. Total floor plans
        expected.append([(
            connection.execute(
                "SELECT COUNT(*) FROM plans"
            ).fetchone()[0],
        )])

        # 18. Total components
        expected.append([(
            connection.execute(
                "SELECT COUNT(*) FROM elements"
            ).fetchone()[0],
        )])

        # 19. Rooms in plan 20
        expected.append([(
            connection.execute(
                """
                SELECT COUNT(*)
                FROM elements
                WHERE plan_id = 20 AND element_type = 'room'
                """
            ).fetchone()[0],
        )])

        # 20. Doors in plan 20
        expected.append([(
            connection.execute(
                """
                SELECT COUNT(*)
                FROM elements
                WHERE plan_id = 20 AND element_type = 'door'
                """
            ).fetchone()[0],
        )])

    return expected


def run():
    """Run all evaluation questions and generate a report."""

    expected = expected_answers()

    if len(expected) != len(QUESTIONS):
        raise ValueError(
            "Question and expected-answer counts do not match."
        )

    failures = []

    print("\nFLOOR-PLAN ASSISTANT EVALUATION")
    print("=" * 45)

    for index, (question, reference) in enumerate(
        zip(QUESTIONS, expected, strict=True), start=1
    ):

        try:
            actual = retrieve_data(question)
            actual_rows = (
                [] if actual is None
                else actual.get("evidence", [])
            )

            if actual_rows == reference:
                print(f"[PASS] Q{index}: {question}")
            else:
                print(f"[FAIL] Q{index}: {question}")

                failures.append(
                    f"- **{question}**\n"
                    f"  - Expected: `{reference}`\n"
                    f"  - Actual: `{actual_rows}`"
                )

        except Exception as error:
            print(f"[ERROR] Q{index}: {error}")

            failures.append(
                f"- **{question}**\n"
                f"  - Error: `{error}`"
            )

    # Check unsupported questions
    unsupported_question = "What is the rent for plan 1?"

    try:
        unsupported = retrieve_data(unsupported_question)

        unsupported_declined = unsupported is None

    except Exception:
        unsupported_declined = False

    if not unsupported_declined:
        failures.append(
            "- Unsupported question was not declined: "
            f"`{unsupported_question}`"
        )

    passed = len(QUESTIONS) - sum(
        1 for failure in failures
        if not failure.startswith(
            "- Unsupported question was not declined:"
        )
    )

    accuracy = passed / len(QUESTIONS) * 100

    print("\n" + "=" * 45)
    print(f"Passed: {passed}/{len(QUESTIONS)}")
    print(f"Accuracy: {accuracy:.1f}%")
    print(f"Unsupported question declined: {unsupported_declined}")

    # Generate evaluation report
    report = [
        "# Part 3A - Evaluation Report",
        "",
        "## Evaluation Summary",
        "",
        f"- Total questions: **{len(QUESTIONS)}**",
        f"- Passed: **{passed}**",
        f"- Failed: **{len(QUESTIONS) - passed}**",
        f"- Accuracy: **{accuracy:.1f}%**",
        f"- Unsupported question declined: **{unsupported_declined}**",
        "",
        "## Test Questions",
        "",
    ]

    for index, question in enumerate(QUESTIONS, start=1):
        report.append(f"{index}. {question}")

    report.extend([
        "",
        "## Failures",
        "",
        *(failures or ["None. All evaluation questions passed."]),
        "",
        "## Unsupported Question Test",
        "",
        f"Question: `{unsupported_question}`",
        "",
        f"Declined successfully: **{unsupported_declined}**",
        "",
        "## Evaluation Method",
        "",
        "Expected answers were generated using independent SQLite "
        "reference queries and compared with the retrieval engine's "
        "database evidence.",
        "",
        "## Limitations",
        "",
        "- Evaluation measures database question-answering accuracy.",
        "- It does not establish that computer-vision room labels "
        "are perfect architectural ground truth.",
        "- Room and component classifications are based on "
        "heuristic segmentation mappings.",
        "- Pixel area is not equivalent to real-world square footage.",
        "",
    ])

    output = DB_FILE.parent / "evaluation_report.md"
    output.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print(f"\nEvaluation report saved: {output}")

    return passed, failures


if __name__ == "__main__":
    passed, failures = run()

    if passed != len(QUESTIONS) or failures:
        raise SystemExit(1)
