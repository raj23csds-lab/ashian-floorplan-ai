
from pathlib import Path
import re
import cv2

BASE_DIR = Path(__file__).resolve().parent.parent

IMAGE_DIR = BASE_DIR / "dataset" / "images"
MASK_DIR = BASE_DIR / "dataset" / "masks"


def get_number(filename):
    match = re.match(r"(\d+)", filename.stem)
    return int(match.group(1)) if match else None


def load_dataset():

    if not IMAGE_DIR.exists():
        raise FileNotFoundError(f"Image directory not found: {IMAGE_DIR}")

    if not MASK_DIR.exists():
        raise FileNotFoundError(f"Mask directory not found: {MASK_DIR}")

    images = {}
    masks = {}

    for file in sorted(IMAGE_DIR.glob("*.png")):
        plan_id = get_number(file)
        if plan_id is not None:
            images.setdefault(plan_id, file)

    for file in sorted(MASK_DIR.glob("*.png")):
        plan_id = get_number(file)
        if plan_id is not None:
            masks.setdefault(plan_id, file)

    print("Original images:", len(images))
    print("Segmentation masks:", len(masks))

    common_ids = sorted(set(images) & set(masks))

    print("\nMatching floor plans:")

    valid_pairs = []

    for image_id in common_ids:
        image = cv2.imread(str(images[image_id]))
        mask = cv2.imread(str(masks[image_id]))

        if image is None or mask is None:
            print(f"Plan {image_id}: Loading failed")
            continue

        if image.shape[:2] != mask.shape[:2]:
            print(f"Plan {image_id}: Dimension mismatch")
            continue

        valid_pairs.append(
            (image_id, images[image_id], masks[image_id])
        )

    print("\nValid image-mask pairs:", len(valid_pairs))

    return valid_pairs


if __name__ == "__main__":
    load_dataset()
