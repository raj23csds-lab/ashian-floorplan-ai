
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MASK_PATH = BASE_DIR / "dataset" / "masks" / "1 (2).png"

mask = cv2.imread(str(MASK_PATH))

if mask is None:
    raise FileNotFoundError(f"Mask not found: {MASK_PATH}")

mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

print("Mask dimensions:", mask.shape)

colors, counts = np.unique(
    mask.reshape(-1, 3),
    axis=0,
    return_counts=True
)

print("Unique colors:", len(colors))
print("\nTop 7 colors:")

for i in np.argsort(counts)[::-1][:7]:
    print(f"RGB: {colors[i].tolist()} | Pixels: {counts[i]}")
