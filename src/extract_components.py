
import cv2
import numpy as np
import csv
import re
from pathlib import Path
import sys

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
MASK_DIR = BASE_DIR / "dataset" / "masks"
OUTPUT_DIR = BASE_DIR / "outputs" / "extracted_data"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from semantic_mapping import infer_mapping, ROLE_IDS


def get_plan_number(path):
    match = re.match(r"(\d+)", path.stem)

    if not match:
        raise ValueError(f"Invalid mask filename: {path.name}")

    return int(match.group(1))


def extract_components(mask_path):
    image = cv2.imread(str(mask_path))

    if image is None:
        print(f"Skipping unreadable mask: {mask_path}")
        return []

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    records = []

    mapping = infer_mapping(mask_path)["roles"]

    for element_type, color_values in mapping.items():

        if element_type not in ROLE_IDS:
            continue

        class_id = ROLE_IDS[element_type]

        color = np.array(color_values, dtype=np.int16)

        lower = np.clip(color - 8, 0, 255).astype(np.uint8)
        upper = np.clip(color + 8, 0, 255).astype(np.uint8)

        binary = cv2.inRange(image, lower, upper)

        count, labels, stats, centroids = (
            cv2.connectedComponentsWithStats(
                binary,
                connectivity=8
            )
        )

        for i in range(1, count):

            x, y, w, h, area = stats[i]

            minimum_area = 100 if element_type == "room" else 20

            if area < minimum_area:
                continue

            cx, cy = centroids[i]

            records.append({
                "plan_id": get_plan_number(mask_path),
                "mask": mask_path.name,
                "class_id": class_id,
                "color": str(tuple(color_values)),
                "element_type": element_type,
                "area_pixels": int(area),
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),
                "centroid_x": round(float(cx), 2),
                "centroid_y": round(float(cy), 2)
            })

    return records


def main():

    if not MASK_DIR.exists():
        raise FileNotFoundError(f"Mask directory not found: {MASK_DIR}")

    mask_files = sorted(
        MASK_DIR.glob("*.png"),
        key=get_plan_number
    )

    if not mask_files:
        raise FileNotFoundError("No PNG masks found.")

    all_records = []

    for mask_path in mask_files:
        records = extract_components(mask_path)
        all_records.extend(records)

    output_file = OUTPUT_DIR / "components.csv"

    fields = [
        "plan_id",
        "mask",
        "class_id",
        "color",
        "element_type",
        "area_pixels",
        "x",
        "y",
        "width",
        "height",
        "centroid_x",
        "centroid_y"
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_records)

    print("\nEXTRACTION SUMMARY")
    print("------------------")
    print("Masks processed:", len(mask_files))
    print("Components extracted:", len(all_records))
    print("Saved to:", output_file)

    print("\nComponents by element type:")

    for element_type in sorted(set(r["element_type"] for r in all_records)):
        count = sum(
            1 for r in all_records
            if r["element_type"] == element_type
        )
        print(f"{element_type}: {count}")


if __name__ == "__main__":
    main()
