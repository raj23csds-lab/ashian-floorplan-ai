
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

IMAGE_DIR = BASE_DIR / "dataset" / "images"
MASK_DIR = BASE_DIR / "dataset" / "masks"


def verify_dataset():

    if not IMAGE_DIR.exists():
        raise FileNotFoundError(f"Images folder not found: {IMAGE_DIR}")

    if not MASK_DIR.exists():
        raise FileNotFoundError(f"Masks folder not found: {MASK_DIR}")

    image_files = sorted(IMAGE_DIR.glob("*.png"))
    mask_files = sorted(MASK_DIR.glob("*.png"))

    print("Original images:", len(image_files))
    print("Segmentation masks:", len(mask_files))

    print("\nFirst 10 image files:")
    for file in image_files[:10]:
        print(file.name)

    print("\nFirst 10 mask files:")
    for file in mask_files[:10]:
        print(file.name)

    if len(image_files) == len(mask_files):
        print("\nImage and mask counts match.")
    else:
        print("\nWARNING: Image and mask counts do not match.")

    print("\nDataset verification completed!")


if __name__ == "__main__":
    verify_dataset()
