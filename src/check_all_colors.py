
import cv2
import numpy as np
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
MASK_DIR = BASE_DIR / "dataset" / "masks"

color_counts = Counter()
mask_files = sorted(MASK_DIR.glob("*.png"))

for mask_path in mask_files:
    image = cv2.imread(str(mask_path))

    if image is None:
        print(f"Skipped: {mask_path.name}")
        continue

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    pixels = image.reshape(-1, 3).astype(np.uint32)

    packed = (
        (pixels[:, 0] << 16)
        | (pixels[:, 1] << 8)
        | pixels[:, 2]
    )

    values, counts = np.unique(
        packed, return_counts=True
    )

    for value, count in zip(values, counts):
        if count >= 20:
            r = int(value >> 16)
            g = int((value >> 8) & 255)
            b = int(value & 255)

            color_counts[(r, g, b)] += int(count)

print("\nTOP 15 COLORS ACROSS ALL MASKS\n")

for color, count in color_counts.most_common(15):
    print(f"RGB: {color} | Pixels: {count}")

print("\nMasks analyzed:", len(mask_files))
print("Unique colors:", len(color_counts))
