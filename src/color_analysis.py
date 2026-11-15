
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MASK_PATH = BASE_DIR / "dataset" / "masks" / "1 (2).png"

mask = cv2.imread(str(MASK_PATH))

if mask is None:
    raise FileNotFoundError(f"Mask not found: {MASK_PATH}")

mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

colors, counts = np.unique(
    mask.reshape(-1, 3),
    axis=0,
    return_counts=True
)

sorted_indices = np.argsort(counts)[::-1]

print("DOMINANT COLORS IN MASK 1\n")

for index in sorted_indices[:7]:
    color = colors[index]
    count = counts[index]
    print(f"RGB: {tuple(color)} | Pixels: {count}")

print("\nAnalysis completed.")
