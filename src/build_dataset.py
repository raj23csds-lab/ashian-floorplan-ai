"""Build a queryable floor-plan database from extracted components."""

import re
import sqlite3
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from semantic_mapping import infer_mapping


BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "outputs" / "floorplan.db"

def plan_number(mask_name: str) -> int:
    match = re.match(r"(\d+)", mask_name)
    if not match:
        raise ValueError(f"Cannot determine plan number from {mask_name!r}")
    return int(match.group(1))


def boxes_touch(first: tuple[int, int, int, int], second: tuple[int, int, int, int]) -> bool:
    """Return whether two component boxes overlap or are within 20 pixels."""
    x1, y1, w1, h1 = first
    x2, y2, w2, h2 = second
    gap = 20
    return not (
        x1 + w1 + gap < x2
        or x2 + w2 + gap < x1
        or y1 + h1 + gap < y2
        or y2 + h2 + gap < y1
    )


def build_database() -> None:
    if not DB_FILE.exists():
        raise FileNotFoundError(
            f"{DB_FILE} does not exist. Run src.extract_components first."
        )

    with sqlite3.connect(DB_FILE) as connection:
        connection.executescript(
            """
            DROP TABLE IF EXISTS element_links;
            DROP TABLE IF EXISTS elements;
            DROP TABLE IF EXISTS semantic_mappings;
            DROP TABLE IF EXISTS plans;

            CREATE TABLE plans (
                plan_id INTEGER PRIMARY KEY,
                mask TEXT NOT NULL UNIQUE,
                image TEXT NOT NULL
            );

            CREATE TABLE semantic_mappings (
                plan_id INTEGER PRIMARY KEY REFERENCES plans(plan_id),
                mapping_json TEXT NOT NULL,
                method TEXT NOT NULL
            );

            CREATE TABLE elements (
                id INTEGER PRIMARY KEY,
                plan_id INTEGER NOT NULL REFERENCES plans(plan_id),
                source_component_id INTEGER NOT NULL UNIQUE,
                element_type TEXT NOT NULL,
                class_id INTEGER NOT NULL,
                color TEXT NOT NULL,
                area_pixels INTEGER NOT NULL,
                x INTEGER NOT NULL,
                y INTEGER NOT NULL,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                centroid_x REAL NOT NULL,
                centroid_y REAL NOT NULL
            );

            CREATE TABLE element_links (
                element_id INTEGER NOT NULL REFERENCES elements(id),
                room_id INTEGER NOT NULL REFERENCES elements(id),
                relation TEXT NOT NULL,
                PRIMARY KEY (element_id, room_id, relation)
            );
            """
        )

        components = connection.execute(
            """
            SELECT id, mask, class_id, color, element_type, area_pixels,
                   x, y, width, height,
                   centroid_x, centroid_y
            FROM components
            ORDER BY mask, id
            """
        ).fetchall()
        if not components:
            raise RuntimeError("The components table is empty.")

        masks = sorted({row[1] for row in components}, key=plan_number)
        connection.executemany(
            "INSERT INTO plans(plan_id, mask, image) VALUES (?, ?, ?)",
            [(plan_number(mask), mask, f"{plan_number(mask)}.png") for mask in masks],
        )

        connection.executemany(
            """
            INSERT INTO elements(
                id, plan_id, source_component_id, element_type, class_id, color,
                area_pixels, x, y, width, height, centroid_x, centroid_y
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row[0],
                    plan_number(row[1]),
                    row[0],
                    row[4],
                    row[2],
                    row[3],
                    *row[5:],
                )
                for row in components
            ],
        )

        rooms_by_plan: dict[int, list[tuple[int, tuple[int, int, int, int]]]] = {}
        for row in connection.execute(
            "SELECT id, plan_id, x, y, width, height FROM elements WHERE element_type='room'"
        ):
            rooms_by_plan.setdefault(row[1], []).append((row[0], row[2:]))

        links = []
        for row in connection.execute(
            """
            SELECT id, plan_id, element_type, x, y, width, height
            FROM elements
            WHERE element_type IN ('door', 'window')
            """
        ):
            element_id, plan_id, element_type = row[:3]
            box = row[3:]
            links.extend(
                (element_id, room_id, f"{element_type}_near_room")
                for room_id, room_box in rooms_by_plan.get(plan_id, [])
                if boxes_touch(box, room_box)
            )
        connection.executemany(
            "INSERT INTO element_links(element_id, room_id, relation) VALUES (?, ?, ?)",
            links,
        )
        mappings = []
        for mask in masks:
            mapping = infer_mapping(BASE_DIR / "dataset" / "masks" / mask)
            mappings.append(
                (plan_number(mask), json.dumps(mapping["roles"]), mapping["method"])
            )
        connection.executemany(
            """
            INSERT INTO semantic_mappings(plan_id, mapping_json, method)
            VALUES (?, ?, ?)
            """,
            mappings,
        )
        connection.commit()


if __name__ == "__main__":
    build_database()
    print(f"Built normalized database at {DB_FILE}")
