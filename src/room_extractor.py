
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MASK_PATH = BASE_DIR / "dataset" / "masks" / "1 (2).png"

TOLERANCE = 5
MINIMUM_AREA = 1000


def extract_rooms():

    if not MASK_PATH.exists():
        raise FileNotFoundError(f"Mask not found: {MASK_PATH}")

    mask = cv2.imread(str(MASK_PATH))

    if mask is None:
        raise ValueError("Unable to read segmentation mask.")

    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

    # Teal represents candidate room regions
    teal = np.array([0, 142, 142], dtype=np.int16)

    difference = np.abs(
        mask.astype(np.int16) - teal
    )

    binary = np.all(
        difference <= TOLERANCE,
        axis=2
    ).astype(np.uint8)

    # Detect connected components
    count, labels, stats, centroids = (
        cv2.connectedComponentsWithStats(
            binary,
            connectivity=8
        )
    )

    rooms = []

    for i in range(1, count):

        x, y, w, h, area = stats[i]

        if area < MINIMUM_AREA:
            continue

        center_x, center_y = centroids[i]

        rooms.append({
            "component_id": i,
            "area_pixels": int(area),
            "x": int(x),
            "y": int(y),
            "width": int(w),
            "height": int(h),
            "centroid_x": round(float(center_x), 2),
            "centroid_y": round(float(center_y), 2)
        })

    print("\nROOM EXTRACTION RESULTS")
    print("-----------------------")
    print("Candidate regions detected:", count - 1)
    print("Regions after area filtering:", len(rooms))

    for number, room in enumerate(rooms, start=1):

        print(f"\nCandidate Room {number}")
        print("Area:", room["area_pixels"], "pixels")
        print("Position:", (room["x"], room["y"]))
        print(
            "Dimensions:",
            (room["width"], room["height"])
        )
        print(
            "Center:",
            (room["centroid_x"], room["centroid_y"])
        )

    print("\nRoom candidate extraction completed!")

    return rooms


if __name__ == "__main__":
    extract_rooms()
