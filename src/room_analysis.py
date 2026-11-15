
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MASK_PATH = BASE_DIR / "dataset" / "masks" / "1 (2).png"
OUTPUT_DIR = BASE_DIR / "outputs" / "visualizations"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def analyze_rooms():

    if not MASK_PATH.exists():
        raise FileNotFoundError(
            f"Mask not found: {MASK_PATH}"
        )

    mask = cv2.imread(str(MASK_PATH))

    if mask is None:
        raise ValueError("Unable to read segmentation mask.")

    mask = cv2.cvtColor(mask, cv2.COLOR_BGR2RGB)

    # Detect teal regions
    teal = np.array([0, 142, 142], dtype=np.int16)

    difference = np.abs(
        mask.astype(np.int16) - teal
    )

    binary = np.all(
        difference <= 5,
        axis=2
    ).astype(np.uint8)

    # Connected components
    count, labels, stats, centroids = (
        cv2.connectedComponentsWithStats(
            binary,
            connectivity=8
        )
    )

    # Create component visualization
    output = np.zeros(
        (labels.shape[0], labels.shape[1], 3),
        dtype=np.uint8
    )

    np.random.seed(42)

    for i in range(1, count):
        color = np.random.randint(50, 255, 3)
        output[labels == i] = color

    # Display results
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    axes[0].imshow(binary, cmap="gray")
    axes[0].set_title("Teal Binary Mask")

    axes[1].imshow(output)
    axes[1].set_title("Connected Components")

    for ax in axes:
        ax.axis("off")

    plt.tight_layout()

    output_file = OUTPUT_DIR / "room_analysis.png"

    plt.savefig(
        output_file,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close(fig)

    print("Connected components:", count - 1)
    print("Analysis saved:", output_file)


if __name__ == "__main__":
    analyze_rooms()
