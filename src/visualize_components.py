
import cv2
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

IMAGE = BASE_DIR / "dataset" / "images" / "1.png"
CSV_FILE = BASE_DIR / "outputs" / "extracted_data" / "components.csv"
OUTPUT = BASE_DIR / "outputs" / "visualizations" / "components_overlay.png"

COLORS = {
    1: (0, 255, 0),
    2: (255, 0, 0),
    3: (0, 255, 255),
    4: (255, 165, 0),
    5: (0, 0, 255),
    6: (255, 0, 255)
}


def visualize_components():

    if not IMAGE.exists():
        raise FileNotFoundError(f"Image not found: {IMAGE}")

    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_FILE}")

    image = cv2.imread(str(IMAGE))

    if image is None:
        raise ValueError("Unable to read original floor plan.")

    image_height, image_width = image.shape[:2]
    component_count = 0

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        required = {
            "mask", "x", "y", "width", "height", "class_id"
        }

        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV is missing required columns.")

        for row in reader:

            if row["mask"] != "1 (2).png":
                continue

            class_id = int(row["class_id"])

            if class_id not in COLORS:
                continue

            x = int(row["x"])
            y = int(row["y"])
            w = int(row["width"])
            h = int(row["height"])

            if w <= 0 or h <= 0:
                continue

            # Skip boxes outside the image
            if x < 0 or y < 0 or x + w > image_width or y + h > image_height:
                continue

            color = COLORS[class_id]

            cv2.rectangle(
                image,
                (x, y),
                (x + w - 1, y + h - 1),
                color,
                2
            )

            component_count += 1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if not cv2.imwrite(str(OUTPUT), image):
        raise IOError("Failed to save component overlay.")

    print("Overlay generated successfully!")
    print("Components drawn:", component_count)
    print("Saved:", OUTPUT)


if __name__ == "__main__":
    visualize_components()
