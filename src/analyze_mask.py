
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

MASK_PATH = BASE / "dataset" / "masks" / "1 (2).png"
OUTPUT_DIR = BASE / "outputs" / "visualizations"

COLORS = [
    (0, 142, 142),
    (175, 216, 248),
    (246, 189, 15),
    (255, 142, 70),
    (214, 70, 70),
    (139, 186, 0)
]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

mask = cv2.imread(str(MASK_PATH))

if mask is None:
    raise FileNotFoundError(f"Mask not found: {MASK_PATH}")

mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

fig, axes = plt.subplots(2, 3, figsize=(12, 8))

for ax, color in zip(axes.flat, COLORS):
    difference = np.abs(
        mask.astype(np.int16) -
        np.array(color, dtype=np.int16)
    )

    selected = np.all(difference <= 8, axis=2)

    ax.imshow(selected, cmap="gray")
    ax.set_title(f"RGB: {color}")
    ax.axis("off")

plt.tight_layout()

output_path = OUTPUT_DIR / "mask_analysis.png"
plt.savefig(output_path, dpi=200, bbox_inches="tight")
plt.show()
plt.close()

print(f"Saved: {output_path}")
