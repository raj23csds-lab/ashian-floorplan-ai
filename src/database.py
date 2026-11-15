
import sqlite3
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_FILE = BASE_DIR / "outputs" / "extracted_data" / "color_features.csv"
DB_FILE = BASE_DIR / "outputs" / "floorplan.db"


def create_database():
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")

    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    inserted = 0
    skipped = 0

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        required_columns = {
            "mask", "color", "pixels", "percentage", "regions"
        }

        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError("CSV is missing required columns.")

        with sqlite3.connect(DB_FILE) as connection:
            cursor = connection.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS floorplan_features (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mask TEXT,
                    color TEXT,
                    pixels INTEGER,
                    percentage REAL,
                    regions INTEGER
                )
            """)

            for row in reader:
                exists = cursor.execute("""
                    SELECT 1 FROM floorplan_features
                    WHERE mask = ? AND color = ?
                    LIMIT 1
                """, (row["mask"], row["color"])).fetchone()

                if exists:
                    skipped += 1
                    continue

                cursor.execute("""
                    INSERT INTO floorplan_features
                    (mask, color, pixels, percentage, regions)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    row["mask"],
                    row["color"],
                    int(row["pixels"]),
                    float(row["percentage"]),
                    int(row["regions"])
                ))

                inserted += 1

            count = cursor.execute(
                "SELECT COUNT(*) FROM floorplan_features"
            ).fetchone()[0]

    print("Database operation completed!")
    print("New records inserted:", inserted)
    print("Existing records skipped:", skipped)
    print("Total records:", count)


if __name__ == "__main__":
    create_database()
