
from pathlib import Path
import sys
import cv2
import numpy as np

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))

from semantic_mapping import infer_mapping

IMAGES = BASE / "dataset" / "images"
MASKS = BASE / "dataset" / "masks"
OUT = BASE / "outputs" / "improved_overlays"

MIN_AREA = 1000
MIN_DIMENSION = 25


def get_mask_path(plan_id):
    matches = [
        p for p in MASKS.glob("*.png")
        if p.stem.split()[0].isdigit()
        and int(p.stem.split()[0]) == plan_id
    ]

    return matches[0] if len(matches) == 1 else None


def color_mask(mask, color, tolerance=8):
    target = np.array(color, dtype=np.int16)
    difference = np.abs(mask.astype(np.int16) - target)

    return (
        np.all(difference <= tolerance, axis=2) * 255
    ).astype(np.uint8)


def extract_regions(mask, roles):

    room_mask = color_mask(mask, roles["room"])

    # Remove isolated noise.
    room_mask = cv2.morphologyEx(
        room_mask,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (3, 3)
        )
    )

    count, labels, stats, centroids = (
        cv2.connectedComponentsWithStats(
            room_mask,
            connectivity=8
        )
    )

    regions = []

    for i in range(1, count):

        x, y, width, height, area = stats[i]

        if area < MIN_AREA:
            continue

        if width < MIN_DIMENSION or height < MIN_DIMENSION:
            continue

        component = (
            (labels == i).astype(np.uint8) * 255
        )

        contours, _ = cv2.findContours(
            component,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            continue

        contour = max(contours, key=cv2.contourArea)

        if cv2.contourArea(contour) < MIN_AREA:
            continue

        regions.append({
            "area": int(area),
            "bbox": (int(x), int(y), int(width), int(height)),
            "contour": contour,
            "centroid": (
                int(centroids[i][0]),
                int(centroids[i][1])
            )
        })

    return regions


def render(plan_ids=(1, 2, 3)):

    OUT.mkdir(parents=True, exist_ok=True)

    for plan_id in plan_ids:

        image_path = IMAGES / f"{plan_id}.png"
        mask_path = get_mask_path(plan_id)

        if not image_path.exists() or mask_path is None:
            print(f"Missing files for plan {plan_id}")
            continue

        image = cv2.imread(str(image_path))
        mask_bgr = cv2.imread(str(mask_path))

        if image is None or mask_bgr is None:
            print(f"Could not read plan {plan_id}")
            continue

        if image.shape[:2] != mask_bgr.shape[:2]:
            print(f"Dimension mismatch: plan {plan_id}")
            continue

        mask = cv2.cvtColor(
            mask_bgr,
            cv2.COLOR_BGR2RGB
        )

        mapping = infer_mapping(mask_path)

        regions = extract_regions(
            mask,
            mapping["roles"]
        )

        result = image.copy()

        for number, region in enumerate(regions, 1):

            cv2.drawContours(
                result,
                [region["contour"]],
                -1,
                (0, 0, 255),
                2
            )

            cx, cy = region["centroid"]

            cv2.putText(
                result,
                f"R{number}",
                (cx, cy),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1,
                cv2.LINE_AA
            )

        output = OUT / f"plan_{plan_id}_improved.png"

        if not cv2.imwrite(str(output), result):
            print(f"Could not save Plan {plan_id}")
            continue

        print(
            f"Plan {plan_id}: "
            f"{len(regions)} candidate regions"
        )
        print(f"Saved: {output}")


if __name__ == "__main__":
    render()
