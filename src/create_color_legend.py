
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs" / "visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Plan 1 inferred semantic mapping
classes = [
    ("Background", (0, 0, 0)),
    ("Room", (0, 142, 142)),
    ("Wall", (175, 216, 248)),
    ("Window", (246, 189, 15)),
    ("Door", (255, 142, 70)),
    ("Opening", (214, 70, 70)),
    ("Furniture", (139, 186, 0))
]

legend = np.zeros((540, 850, 3), dtype=np.uint8)

cv2.putText(
    legend, "PLAN 1 - INFERRED COLOR LEGEND",
    (30, 35), cv2.FONT_HERSHEY_SIMPLEX,
    0.8, (255, 255, 255), 2
)

for i, (name, rgb) in enumerate(classes):
    y = 65 + i * 65

    bgr = (rgb[2], rgb[1], rgb[0])
    legend[y:y+45, 30:100] = bgr

    cv2.putText(
        legend,
        f"{name} | RGB: {rgb}",
        (130, y + 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

output = OUTPUT_DIR / "color_legend.png"
cv2.imwrite(str(output), legend)

print("Color legend saved:", output)
