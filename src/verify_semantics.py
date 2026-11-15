
"""Write an auditable semantic-colour verification report."""

import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "outputs" / "floorplan.db"
OUTPUT = BASE_DIR / "outputs" / "semantic_mapping_report.md"


def main() -> None:

    if not DB_FILE.exists():
        raise FileNotFoundError(f"Database not found: {DB_FILE}")

    with sqlite3.connect(DB_FILE) as connection:
        rows = connection.execute("""
            SELECT
                s.plan_id,
                s.mapping_json,
                COUNT(CASE WHEN e.element_type = 'room' THEN 1 END),
                COUNT(CASE WHEN e.element_type = 'door' THEN 1 END),
                COUNT(CASE WHEN e.element_type = 'window' THEN 1 END),
                COUNT(CASE WHEN e.element_type = 'wall' THEN 1 END)
            FROM semantic_mappings AS s
            LEFT JOIN elements AS e
                ON e.plan_id = s.plan_id
            GROUP BY s.plan_id, s.mapping_json
            ORDER BY s.plan_id
        """).fetchall()

    lines = [
        "# Semantic Colour Verification",
        "",
        "The mask files do not provide a machine-readable legend. "
        "Semantic roles are inferred using colour and geometric heuristics. "
        "These mappings should be treated as candidate classifications, "
        "not independently verified ground truth.",
        "",
        "The applied heuristic rules are:",
        "",
        "- Light blue is treated as the wall class.",
        "- Yellow is treated as the window class.",
        "- The dominant remaining filled colour is treated as the room class.",
        "- The remaining colour with the most small components is treated "
        "as the door class.",
        "- Leftover colours are retained as opening/furniture candidates.",
        "",
        "The mappings are persisted in the `semantic_mappings` table.",
        "",
        "| Plan | Room colour | Window colour | Door colour | "
        "Walls | Rooms | Doors | Windows |",
        "|---:|---|---|---|---:|---:|---:|---:|"
    ]

    for plan_id, mapping_json, rooms, doors, windows, walls in rows:

        mapping = json.loads(mapping_json)

        def colour(role):
            return str(tuple(mapping[role]))

        lines.append(
            f"| {plan_id} | {colour('room')} | "
            f"{colour('window')} | {colour('door')} | "
            f"{walls} | {rooms} | {doors} | {windows} |"
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    print(f"Semantic verification report saved: {OUTPUT}")
    print("Plans reported:", len(rows))


if __name__ == "__main__":
    main()
