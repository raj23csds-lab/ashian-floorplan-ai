
import re
import sqlite3
from pathlib import Path

from gemini_client import generate_sql, ask_gemini
from retrieval_engine import retrieve_data


DB_FILE = (
    Path(__file__).resolve().parent.parent
    / "outputs"
    / "floorplan.db"
)

ALLOWED_TABLES = {"plans", "elements", "element_links"}
MAX_ROWS = 5000


def execute_readonly_sql(sql):
    sql = sql.strip()

    if not sql:
        raise ValueError("SQL query is empty.")

    if not re.match(r"^SELECT\b", sql, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed.")

    if ";" in sql.rstrip(";"):
        raise ValueError("Multiple SQL statements are not allowed.")

    if not DB_FILE.exists():
        raise FileNotFoundError("Floor-plan database not found.")

    connection = sqlite3.connect(
        DB_FILE.resolve().as_uri() + "?mode=ro",
        uri=True
    )

    def authorizer(action, arg1, arg2, database, trigger):
        if action in (
            sqlite3.SQLITE_SELECT,
            sqlite3.SQLITE_FUNCTION
        ):
            return sqlite3.SQLITE_OK

        if action == sqlite3.SQLITE_READ:
            if arg1 in ALLOWED_TABLES:
                return sqlite3.SQLITE_OK
            return sqlite3.SQLITE_DENY

        return sqlite3.SQLITE_DENY

    try:
        connection.set_authorizer(authorizer)

        cursor = connection.execute(sql)

        columns = [
            description[0]
            for description in (cursor.description or [])
        ]

        rows = cursor.fetchmany(MAX_ROWS + 1)

        if len(rows) > MAX_ROWS:
            raise ValueError(
                "Query result exceeds the maximum allowed rows."
            )

        return columns, rows

    finally:
        connection.close()


def local_answer(question, evidence):
    q = question.lower()

    plan_match = re.search(r"\bplan\s+(\d+)\b", q)
    plan_id = plan_match.group(1) if plan_match else "unknown"

    if "average" in q:
        return (
            "The average number of rooms across all plans is "
            f"{evidence[0][0]}."
        )

    if "more than" in q and "door" in q:
        threshold_match = re.search(r"more than\s+(\d+)", q)
        threshold = (
            threshold_match.group(1)
            if threshold_match
            else "the specified threshold"
        )

        return (
            f"{len(evidence)} plans have more than {threshold} doors. "
            "Plan IDs: "
            + ", ".join(str(row[0]) for row in evidence)
        )

    if "largest room" in q:
        room_id = evidence[0][0]
        area = evidence[0][1]

        return (
            f"The largest room in plan {plan_id} is room ID "
            f"{room_id}, with an area of {area} pixels."
        )

    if "no window" in q or "without window" in q:
        room_ids = [str(row[0]) for row in evidence]

        return (
            f"Rooms in plan {plan_id} with no windows: "
            + ", ".join(room_ids)
        )

    if "window" in q and ("how many" in q or "count" in q):
        return (
            f"Plan {plan_id} has {evidence[0][0]} windows."
        )

    if "door" in q and ("how many" in q or "count" in q):
        return (
            f"Plan {plan_id} has {evidence[0][0]} doors."
        )

    if "wall" in q and ("how many" in q or "count" in q):
        return (
            f"Plan {plan_id} has {evidence[0][0]} walls."
        )

    if "room" in q and ("how many" in q or "count" in q):
        return (
            f"Plan {plan_id} has {evidence[0][0]} rooms."
        )

    return f"Database returned: {evidence}"


def answer_question(question):

    if not question.strip():
        return {
            "answer": "Please enter a question.",
            "sql": "No query executed",
            "evidence": []
        }

    # Decline questions outside the available database.
    if "rent" in question.lower():
        return {
            "answer": (
                "Rent information is not available in the database."
            ),
            "sql": "No query executed",
            "evidence": []
        }

    sql = None
    columns = []
    evidence = []

    # First try Gemini-generated SQL.
    try:
        sql = generate_sql(question)

        if not sql or sql.strip().upper() == "UNSUPPORTED":
            return {
                "answer": (
                    "This question is not supported by the "
                    "available database."
                ),
                "sql": "No query executed",
                "evidence": []
            }

        columns, evidence = execute_readonly_sql(sql)

    except Exception:
        # If Gemini SQL generation fails, use local retrieval.
        result = retrieve_data(question)

        if not result:
            return {
                "answer": (
                    "This question cannot be answered using "
                    "the available data."
                ),
                "sql": "No query executed",
                "evidence": []
            }

        sql = result["sql"]
        evidence = result["evidence"]

    if not evidence:
        return {
            "answer": (
                "The database query returned no matching records."
            ),
            "sql": sql,
            "evidence": []
        }

    # Ask Gemini to explain only the database evidence.
    try:
        prompt = f"""
Answer using ONLY the database evidence below.

Question: {question}
SQL: {sql}
Columns: {columns}
Evidence: {evidence}

Do not invent information.
Give a concise answer.
"""

        answer = ask_gemini(prompt)

        # Detect Gemini API failures and use local explanation.
        if not answer or any(
            error in answer.lower()
            for error in [
                "gemini api error",
                "gemini api request failed",
                "429",
                "too many requests",
                "rate limit",
                "quota",
                "resource_exhausted"
            ]
        ):
            answer = local_answer(question, evidence)

    except Exception:
        answer = local_answer(question, evidence)

    return {
        "answer": answer,
        "sql": sql,
        "evidence": evidence
    }


if __name__ == "__main__":

    print("Ask your floor-plan assistant (type 'exit' to stop).")

    while True:
        question = input("\nQuestion: ").strip()

        if question.lower() == "exit":
            break

        result = answer_question(question)

        print("\nAnswer:", result["answer"])
        print("\nSQL:", result["sql"])
        print("\nEvidence:", result["evidence"])
