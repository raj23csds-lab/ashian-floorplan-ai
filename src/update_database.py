
import sqlite3
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "outputs" / "floorplan.db"
CSV_FILE = BASE_DIR / "outputs" / "extracted_data" / "components.csv"


def update_database():

    if not DB_FILE.exists():
        raise FileNotFoundError(f"Database not found: {DB_FILE}")

    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")

    required_fields = [
        "mask", "class_id", "color", "element_type",
        "area_pixels", "x", "y", "width", "height",
        "centroid_x", "centroid_y"
    ]

    with open(
        CSV_FILE, "r", newline="", encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames or not set(required_fields).issubset(
            reader.fieldnames
        ):
            raise ValueError(
                "CSV is missing required columns."
            )

        rows = list(reader)

    connection = sqlite3.connect(DB_FILE)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mask TEXT,
                class_id INTEGER,
                color TEXT,
                element_type TEXT,
                area_pixels INTEGER,
                x INTEGER,
                y INTEGER,
                width INTEGER,
                height INTEGER,
                centroid_x REAL,
                centroid_y REAL
            )
        """)

        # Replace old component records without dropping the table
        cursor.execute("DELETE FROM components")

        insert_sql = """
            INSERT INTO components (
                mask, class_id, color, element_type, area_pixels,
                x, y, width, height,
                centroid_x, centroid_y
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        data = [
            (
                row["mask"],
                int(row["class_id"]),
                row["color"],
                row["element_type"],
                int(row["area_pixels"]),
                int(row["x"]),
                int(row["y"]),
                int(row["width"]),
                int(row["height"]),
                float(row["centroid_x"]),
                float(row["centroid_y"])
            )
            for row in rows
        ]

        cursor.executemany(insert_sql, data)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_components_mask
            ON components(mask)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_components_class
            ON components(class_id)
        """)

        cursor.execute(
            "SELECT COUNT(*) FROM components"
        )
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT class_id, COUNT(*), SUM(area_pixels)
            FROM components
            GROUP BY class_id
            ORDER BY class_id
        """)

        summary = cursor.fetchall()

        connection.commit()

        print("\nDATABASE UPDATED SUCCESSFULLY")
        print("Total components:", total)
        print("\nCLASS SUMMARY")

        for class_id, count, area in summary:
            print(
                f"Class {class_id}: "
                f"{count} components, {area} pixels"
            )

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    update_database()
