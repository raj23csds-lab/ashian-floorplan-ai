
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

IMAGE_PATH = BASE_DIR / "dataset" / "images" / "1.png"
MASK_PATH = BASE_DIR / "dataset" / "masks" / "1 (2).png"

OUTPUT_DIR = BASE_DIR / "outputs" / "visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

original = cv2.imread(str(IMAGE_PATH))
mask = cv2.imread(str(MASK_PATH))

if original is None:
    raise FileNotFoundError(f"Original image not found: {IMAGE_PATH}")

if mask is None:
    raise FileNotFoundError(f"Mask not found: {MASK_PATH}")

height = 900
width = int(original.shape[1] * height / original.shape[0])

original = cv2.resize(original, (width, height))
mask_display = cv2.resize(
    mask,
    (width, height),
    interpolation=cv2.INTER_NEAREST
)

comparison = np.hstack((original, mask_display))

cv2.putText(
    comparison, "Original Floor Plan",
    (20, 35), cv2.FONT_HERSHEY_SIMPLEX,
    0.8, (0, 0, 255), 2
)

cv2.putText(
    comparison, "Segmentation Mask",
    (width + 20, 35), cv2.FONT_HERSHEY_SIMPLEX,
    0.8, (0, 0, 255), 2
)

output = OUTPUT_DIR / "plan_1_comparison.png"
cv2.imwrite(str(output), comparison)

print("Comparison saved:", output)
