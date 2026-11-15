
import cv2
import json
import sqlite3
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

IMAGE_DIR = BASE_DIR / "dataset" / "images"
MASK_DIR = BASE_DIR / "dataset" / "masks"
DB_FILE = BASE_DIR / "outputs" / "floorplan.db"
OUTPUT_DIR = BASE_DIR / "outputs" / "room_contours"

MIN_AREA = 500
COLOR_TOLERANCE = 8


def find_mask(plan_id):
    matches = [
        path for path in MASK_DIR.glob("*.png")
        if path.stem.split()[0].isdigit()
        and int(path.stem.split()[0]) == plan_id
    ]

    return matches[0] if len(matches) == 1 else None


def get_room_color(plan_id):

    if not DB_FILE.exists():
        raise FileNotFoundError(f"Database not found: {DB_FILE}")

    with sqlite3.connect(DB_FILE) as connection:
        row = connection.execute(
            """
            SELECT mapping_json
            FROM semantic_mappings
            WHERE plan_id = ?
            """,
            (plan_id,)
        ).fetchone()

    if not row:
        raise ValueError(
            f"No semantic mapping found for plan {plan_id}"
        )

    mapping = json.loads(row[0])
    color = mapping["room"]

    return tuple(int(value) for value in color)


def visualize(plan_id):

    image_path = IMAGE_DIR / f"{plan_id}.png"
    mask_path = find_mask(plan_id)

    if not image_path.exists() or mask_path is None:
        print(f"Missing or ambiguous image/mask for plan {plan_id}")
        return

    original = cv2.imread(str(image_path))
    mask_bgr = cv2.imread(str(mask_path))

    if original is None or mask_bgr is None:
        print(f"Could not read plan {plan_id}")
        return

    if original.shape[:2] != mask_bgr.shape[:2]:
        print(f"Image and mask dimensions differ for plan {plan_id}")
        return

    room_rgb = get_room_color(plan_id)
    mask_rgb = cv2.cvtColor(mask_bgr, cv2.COLOR_BGR2RGB)

    target = np.array(room_rgb, dtype=np.int16)

    difference = np.abs(
        mask_rgb.astype(np.int16) - target
    )

    room_mask = (
        np.all(difference <= COLOR_TOLERANCE, axis=2) * 255
    ).astype(np.uint8)

    count, labels, stats, centroids = (
        cv2.connectedComponentsWithStats(
            room_mask,
            connectivity=8
        )
    )

    result = original.copy()
    region_number = 0

    for component_id in range(1, count):

        area = stats[component_id, cv2.CC_STAT_AREA]

        if area < MIN_AREA:
            continue

        component = (
            np.uint8(labels == component_id) * 255
        )

        contours, _ = cv2.findContours(
            component,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            continue

        region_number += 1

        cv2.drawContours(
            result,
            contours,
            -1,
            (0, 0, 255),
            2
        )

        cx, cy = centroids[component_id]

        cv2.putText(
            result,
            f"Region {region_number}",
            (int(cx), int(cy)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 255),
            2
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / f"plan_{plan_id}_rooms.png"

    if not cv2.imwrite(str(output_path), result):
        raise IOError(f"Could not save: {output_path}")

    print(f"Plan {plan_id}: {region_number} candidate regions")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    for plan_id in (1, 2, 3):
        visualize(plan_id)
