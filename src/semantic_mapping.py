
"""Infer semantic roles from the palette used by each individual mask.

Room and door roles are heuristic estimates, not ground-truth labels.
Mappings and statistics are returned for auditing.
"""

from pathlib import Path
from typing import Any

import cv2
import numpy as np


PALETTE = (
    (0, 142, 142),
    (175, 216, 248),
    (246, 189, 15),
    (255, 142, 70),
    (214, 70, 70),
    (139, 186, 0),
)

ROLE_IDS = {
    "room": 1,
    "window": 2,
    "door": 3,
    "wall": 4,
    "opening": 5,
    "furniture": 6,
}

TOLERANCE = 8


def _mask_for_color(
    image: np.ndarray,
    color: tuple[int, int, int]
) -> np.ndarray:

    target = np.asarray(color, dtype=np.int16)

    difference = np.abs(
        image.astype(np.int16) - target
    )

    return (
        np.all(difference <= TOLERANCE, axis=2)
    ).astype(np.uint8) * 255


def infer_mapping(mask_path: Path) -> dict[str, Any]:

    mask_path = Path(mask_path)

    if not mask_path.exists():
        raise FileNotFoundError(
            f"Mask not found: {mask_path}"
        )

    image = cv2.imread(str(mask_path))

    if image is None:
        raise ValueError(
            f"Unable to read mask: {mask_path}"
        )

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    stats = {}

    # Calculate statistics for each palette colour
    for color in PALETTE:

        binary = _mask_for_color(image, color)

        count, labels, component_stats, centroids = (
            cv2.connectedComponentsWithStats(
                binary,
                connectivity=8
            )
        )

        areas = component_stats[1:, cv2.CC_STAT_AREA]

        stats[color] = {
            "pixels": int(np.count_nonzero(binary)),
            "components": int(
                np.sum(areas >= 20)
            ),
            "small_components": int(
                np.sum(
                    (areas >= 20) &
                    (areas <= 20000)
                )
            ),
        }

    # Stable colour assumptions from the dataset
    wall = (175, 216, 248)
    window = (246, 189, 15)

    # Check that stable classes are present
    if stats[wall]["pixels"] == 0:
        raise ValueError(
            "Expected wall colour not found in mask."
        )

    if stats[window]["pixels"] == 0:
        raise ValueError(
            "Expected window colour not found in mask."
        )

    # Infer room colour from dominant remaining colour
    room_candidates = [
        color for color in PALETTE
        if color not in (wall, window)
    ]

    room = max(
        room_candidates,
        key=lambda color: stats[color]["pixels"]
    )

    # Infer door colour using small component count
    door_candidates = [
        color for color in room_candidates
        if color != room
    ]

    door = max(
        door_candidates,
        key=lambda color: stats[color]["small_components"]
    )

    # Assign remaining colours
    remaining = [
        color for color in door_candidates
        if color != door
    ]

    remaining.sort(
        key=lambda color: stats[color]["pixels"],
        reverse=True
    )

    if len(remaining) != 2:
        raise ValueError(
            "Unable to assign opening and furniture colours."
        )

    mapping = {
        "room": room,
        "window": window,
        "door": door,
        "wall": wall,
        "opening": remaining[0],
        "furniture": remaining[1],
    }

    return {
        "roles": {
            role: list(color)
            for role, color in mapping.items()
        },
        "role_ids": ROLE_IDS.copy(),
        "statistics": {
            ".".join(map(str, color)): values
            for color, values in stats.items()
        },
        "method": (
            "Heuristic mapping: stable wall/window colours; "
            "dominant remaining colour for room; "
            "small-component count for door; "
            "remaining colours assigned by pixel count."
        ),
        "limitations": (
            "Room and door assignments are heuristic estimates "
            "and have not been independently verified."
        )
    }


if __name__ == "__main__":

    BASE_DIR = Path(__file__).resolve().parent.parent
    MASK_PATH = BASE_DIR / "dataset" / "masks" / "1 (2).png"

    result = infer_mapping(MASK_PATH)

    print("\nSEMANTIC MAPPING")
    print("----------------")

    for role, color in result["roles"].items():
        print(f"{role}: {color}")

    print("\nMAPPING STATISTICS")

    for color, values in result["statistics"].items():
        print(color, values)

    print("\nMethod:", result["method"])
    print("Limitations:", result["limitations"])
