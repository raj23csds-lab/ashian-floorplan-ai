
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs" / "visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

colors = [
    (0, 0, 0),
    (0, 142, 142),
    (175, 216, 248),
    (246, 189, 15),
    (255, 142, 70),
    (214, 70, 70),
    (139, 186, 0)
]

labels = [
    "Black", "Teal", "Light Blue", "Yellow",
    "Orange", "Red", "Green"
]

counts = [
    2595172, 857763, 124524, 29896,
    10466, 4569, 3858
]

legend_items = []

for color, label, count in zip(colors, labels, counts):
    normalized = tuple(c / 255 for c in color)

    legend_items.append(
        Patch(
            facecolor=normalized,
            label=f"{label} - {count:,} pixels"
        )
    )

plt.figure(figsize=(9, 5))

plt.legend(
    handles=legend_items,
    loc="center",
    fontsize=12,
    title="Plan 1 Segmentation Mask Color Legend"
)

plt.axis("off")
plt.tight_layout()

output_path = OUTPUT_DIR / "color_legend.png"
plt.savefig(output_path, dpi=200, bbox_inches="tight")
plt.show()

print(f"Color legend saved: {output_path}")
