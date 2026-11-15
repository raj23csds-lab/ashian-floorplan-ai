
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

IMAGE_PATH = BASE_DIR / "dataset" / "images" / "1.png"
MASK_PATH = BASE_DIR / "dataset" / "masks" / "1 (2).png"

OUTPUT_DIR = BASE_DIR / "outputs" / "visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

image = cv2.imread(str(IMAGE_PATH))
mask = cv2.imread(str(MASK_PATH))

if image is None or mask is None:
    raise FileNotFoundError("Image or mask not found.")

height = 700
width = int(image.shape[1] * height / image.shape[0])

image = cv2.resize(image, (width, height))
mask = cv2.resize(
    mask,
    (width, height),
    interpolation=cv2.INTER_NEAREST
)

comparison = np.hstack((image, mask))

output = OUTPUT_DIR / "sample_comparison.png"

cv2.imwrite(str(output), comparison)

print("Comparison image saved:", output)
