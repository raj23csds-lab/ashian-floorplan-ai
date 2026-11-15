
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MASK_PATH = BASE_DIR / "dataset" / "masks" / "1 (2).png"


def inspect_mask():

    if not MASK_PATH.exists():
        raise FileNotFoundError(
            f"Mask not found: {MASK_PATH}"
        )

    mask = cv2.imread(str(MASK_PATH))

    if mask is None:
        raise ValueError("Unable to read the mask image.")

    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

    colors, counts = np.unique(
        mask.reshape(-1, 3),
        axis=0,
        return_counts=True
    )

    indices = np.argsort(counts)[::-1]

    print("\nTOP 15 DOMINANT COLORS\n")

    for i in indices[:15]:
        color = tuple(colors[i].tolist())

        print(
            f"RGB: {color} | Pixels: {counts[i]}"
        )

    print("\nTotal unique colors:", len(colors))
    print("Image dimensions:", mask.shape)


if __name__ == "__main__":
    inspect_mask()
