import random
import string
from typing import Tuple

import cv2
import numpy as np
import pytest

from dicom_img_anon.east import CHECKPOINT_PATH, EAST, blackout_pixels


def get_rand_string(N: int = 4) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=N))


@pytest.fixture
def test_image(
    rows: int = 256,
    cols: int = 256,
    font_scale: int = 1,
    thickness: int = 1,
    line_type: int = 1,
    font_color: Tuple[int, int, int] = (256, 256, 256),
    text: str = get_rand_string(),
):
    image = np.zeros((rows, cols, 3), dtype=np.uint8)
    rand_coords = tuple(random.randint(0, c // 2) for c in [rows, cols])
    cv2.putText(image, text, rand_coords, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_color, thickness, line_type)
    return np.array(image)


def test_EAST(test_image):
    east = EAST(CHECKPOINT_PATH)

    assert test_image.sum() != 0

    for box in east(test_image):
        blackout_pixels(test_image, box)

    assert test_image.sum() == 0
