
import cv2
import csv
import numpy as np
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MASK_DIR = BASE_DIR / "dataset" / "masks"
OUTPUT_DIR = BASE_DIR / "outputs" / "extracted_data"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COLORS = [
    (0, 0, 0),
    (0, 142, 142),
    (175, 216, 248),
    (246, 189, 15),
    (255, 142, 70),
    (214, 70, 70),
    (139, 186, 0)
]


def get_plan_number(path):
    match = re.match(r"(\d+)", path.stem)

    if not match:
        raise ValueError(f"Invalid filename: {path.name}")

    return int(match.group(1))


def extract_features(mask_path):

    image = cv2.imread(str(mask_path))

    if image is None:
        print(f"Skipping unreadable mask: {mask_path}")
        return []

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    height, width = image.shape[:2]
    results = []

    for color in COLORS:

        color_array = np.array(color, dtype=np.int16)

        lower = np.clip(color_array - 5, 0, 255).astype(np.uint8)
        upper = np.clip(color_array + 5, 0, 255).astype(np.uint8)

        binary = cv2.inRange(image, lower, upper)

        count, labels, stats, centroids = (
            cv2.connectedComponentsWithStats(
                binary,
                connectivity=8
            )
        )

        pixel_count = int(np.count_nonzero(binary))

        regions = sum(
            1 for area in stats[1:, cv2.CC_STAT_AREA]
            if area >= 100
        )

        results.append({
            "plan_id": get_plan_number(mask_path),
            "mask": mask_path.name,
            "color": str(color),
            "pixels": pixel_count,
            "percentage": round(
                pixel_count / (height * width) * 100, 2
            ),
            "regions": regions
        })

    return results


def main():

    if not MASK_DIR.exists():
        raise FileNotFoundError(f"Mask directory not found: {MASK_DIR}")

    mask_files = sorted(
        MASK_DIR.glob("*.png"),
        key=get_plan_number
    )

    if not mask_files:
        raise FileNotFoundError("No PNG masks found.")

    all_results = []

    for mask_path in mask_files:
        all_results.extend(extract_features(mask_path))

    output_file = OUTPUT_DIR / "color_features.csv"

    fields = [
        "plan_id", "mask", "color",
        "pixels", "percentage", "regions"
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_results)

    print("\nCOLOR FEATURE EXTRACTION")
    print("------------------------")
    print("Floor plans processed:", len(mask_files))
    print("Feature records:", len(all_results))
    print("Saved:", output_file)


if __name__ == "__main__":
    main()
