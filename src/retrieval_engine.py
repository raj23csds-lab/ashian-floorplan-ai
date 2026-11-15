
"""Deterministic, evidence-first retrieval for floor-plan questions."""

import re
import sqlite3
from pathlib import Path
from typing import Any

DB_FILE = (
    Path(__file__).resolve().parent.parent
    / "outputs"
    / "floorplan.db"
)


def _plan_id(question: str) -> int | None:
    match = re.search(r"\bplan\s+(\d+)\b", question.lower())
    return int(match.group(1)) if match else None


def _result(sql, parameters, rows):
    return {
        "sql": sql.strip(),
        "parameters": parameters,
        "evidence": rows
    }


def retrieve_data(question: str) -> dict[str, Any] | None:

    if not question or not question.strip():
        return None

    if not DB_FILE.exists():
        raise FileNotFoundError(
            f"Floor-plan database not found: {DB_FILE}"
        )

    normalized = question.lower().strip()
    plan_id = _plan_id(normalized)

    # Open database in read-only mode
    connection = sqlite3.connect(
        f"{DB_FILE.as_uri()}?mode=ro",
        uri=True
    )

    try:
        # Average number of rooms across all plans
        if "average" in normalized and "room" in normalized:

            sql = """
                SELECT ROUND(AVG(room_count), 2)
                FROM (
                    SELECT p.plan_id, COUNT(e.id) AS room_count
                    FROM plans AS p
                    LEFT JOIN elements AS e
                      ON e.plan_id = p.plan_id
                      AND e.element_type = 'room'
                    GROUP BY p.plan_id
                )
            """

            return _result(
                sql,
                (),
                connection.execute(sql).fetchall()
            )

        # Plans having more than N doors
        if "more than" in normalized and "door" in normalized:

            match = re.search(
                r"more than\s+(\d+)\s+doors?",
                normalized
            )

            if not match:
                return None

            threshold = int(match.group(1))

            sql = """
                SELECT plan_id, COUNT(*) AS door_count
                FROM elements
                WHERE element_type = 'door'
                GROUP BY plan_id
                HAVING COUNT(*) > ?
                ORDER BY plan_id
            """

            return _result(
                sql,
                (threshold,),
                connection.execute(
                    sql, (threshold,)
                ).fetchall()
            )

        # Questions that do not specify a particular plan
        if plan_id is None:

            if (
                "floor plans" in normalized
                or "how many plans" in normalized
            ):

                sql = "SELECT COUNT(*) FROM plans"

                return _result(
                    sql,
                    (),
                    connection.execute(sql).fetchall()
                )

            if (
                "total components" in normalized
                or "how many components" in normalized
            ):

                sql = "SELECT COUNT(*) FROM elements"

                return _result(
                    sql,
                    (),
                    connection.execute(sql).fetchall()
                )

            return None

        # Verify that the requested plan exists
        plan_exists = connection.execute(
            "SELECT 1 FROM plans WHERE plan_id = ?",
            (plan_id,)
        ).fetchone()

        if not plan_exists:
            return _result(
                "SELECT 1 FROM plans WHERE plan_id = ?",
                (plan_id,),
                []
            )

        # Largest room
        if "largest room" in normalized:

            sql = """
                SELECT id, area_pixels, x, y, width, height
                FROM elements
                WHERE plan_id = ?
                  AND element_type = 'room'
                ORDER BY area_pixels DESC
                LIMIT 1
            """

            return _result(
                sql,
                (plan_id,),
                connection.execute(
                    sql, (plan_id,)
                ).fetchall()
            )

        # Rooms without windows
        if (
            "no window" in normalized
            or "without window" in normalized
        ):

            sql = """
                SELECT r.id, r.area_pixels, r.x, r.y,
                       r.width, r.height
                FROM elements AS r
                WHERE r.plan_id = ?
                  AND r.element_type = 'room'
                  AND NOT EXISTS (
                      SELECT 1
                      FROM element_links AS l
                      WHERE l.room_id = r.id
                        AND l.relation = 'window_near_room'
                  )
                ORDER BY r.id
            """

            return _result(
                sql,
                (plan_id,),
                connection.execute(
                    sql, (plan_id,)
                ).fetchall()
            )

        # Count elements by type
        element_type = next(
            (
                kind
                for kind in ("room", "door", "window", "wall")
                if kind in normalized
            ),
            None
        )

        if element_type and (
            "how many" in normalized or "count" in normalized
        ):

            sql = """
                SELECT COUNT(*)
                FROM elements
                WHERE plan_id = ?
                  AND element_type = ?
            """

            parameters = (plan_id, element_type)

            return _result(
                sql,
                parameters,
                connection.execute(
                    sql, parameters
                ).fetchall()
            )

        return None

    finally:
        connection.close()
