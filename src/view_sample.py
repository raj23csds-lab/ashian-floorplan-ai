
import cv2
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

IMAGE_PATH = BASE_DIR / "dataset" / "images" / "1.png"
MASK_PATH = BASE_DIR / "dataset" / "masks" / "1 (2).png"


def view_sample():

    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Original image not found: {IMAGE_PATH}")

    if not MASK_PATH.exists():
        raise FileNotFoundError(f"Segmentation mask not found: {MASK_PATH}")

    floor_plan = cv2.imread(str(IMAGE_PATH))
    mask = cv2.imread(str(MASK_PATH))

    if floor_plan is None:
        raise ValueError("Unable to read original floor plan.")

    if mask is None:
        raise ValueError("Unable to read segmentation mask.")

    floor_plan = cv2.cvtColor(floor_plan, cv2.COLOR_BGR2RGB)
    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

    print("Floor plan shape:", floor_plan.shape)
    print("Mask shape:", mask.shape)

    if floor_plan.shape[:2] != mask.shape[:2]:
        print("WARNING: Image and mask dimensions do not match.")

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.imshow(floor_plan)
    plt.title("Original Floor Plan")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(mask)
    plt.title("Segmentation Mask")
    plt.axis("off")

    plt.tight_layout()
    plt.show()
    plt.close()


if __name__ == "__main__":
    view_sample()
