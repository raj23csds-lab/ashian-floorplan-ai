
import cv2
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MASK_PATH = BASE_DIR / "dataset" / "masks" / "1 (2).png"
OUTPUT_DIR = BASE_DIR / "outputs" / "visualizations"

COLORS = [
    (0, 142, 142),
    (175, 216, 248),
    (246, 189, 15),
    (255, 142, 70),
    (214, 70, 70),
    (139, 186, 0)
]

NAMES = [
    "Class 1 - Teal",
    "Class 2 - Light Blue",
    "Class 3 - Yellow",
    "Class 4 - Orange",
    "Class 5 - Red",
    "Class 6 - Green"
]


def visualize_classes():

    if not MASK_PATH.exists():
        raise FileNotFoundError(f"Mask not found: {MASK_PATH}")

    image = cv2.imread(str(MASK_PATH))

    if image is None:
        raise ValueError("Unable to read segmentation mask.")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    if len(COLORS) != len(NAMES):
        raise ValueError("Colors and names must have equal lengths.")

    height, width = image.shape[:2]

    # Preserve aspect ratio
    scale = min(350 / width, 300 / height)
    new_width = int(width * scale)
    new_height = int(height * scale)

    tiles = []

    for color, name in zip(COLORS, NAMES):

        lower = np.maximum(np.array(color) - 8, 0).astype(np.uint8)
        upper = np.minimum(np.array(color) + 8, 255).astype(np.uint8)

        binary = cv2.inRange(image, lower, upper)

        binary = cv2.resize(
            binary,
            (new_width, new_height),
            interpolation=cv2.INTER_NEAREST
        )

        tile = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

        cv2.putText(
            tile, name, (10, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6, (0, 0, 255), 2
        )

        tile = cv2.copyMakeBorder(
            tile,
            0, 300 - new_height,
            0, 350 - new_width,
            cv2.BORDER_CONSTANT,
            value=(255, 255, 255)
        )

        tiles.append(tile)

    row1 = np.hstack(tiles[:3])
    row2 = np.hstack(tiles[3:])

    montage = np.vstack((row1, row2))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / "class_visualization.png"

    if not cv2.imwrite(str(output_path), montage):
        raise IOError("Failed to save class visualization.")

    print("Class visualizations generated!")
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    visualize_classes()
