from pathlib import Path
from typing import Final, List

import pydicom
from numpy import ndarray

from dicom_img_anon.east import EAST, blackout_pixels

TARGET_MODALITIES: Final[List[str]] = ["US"]
EAST_INSTANCE: Final[EAST] = EAST()


def anon_dicom(dicom: Path) -> None:
    ds = pydicom.dcmread(dicom)

    if ds.get("Modality", "") in ["US"]:
        image = anon_image(ds.pixel_array)
        ds.PixelData = image.tobytes()
        ds.save_as(dicom)


def anon_image(image: ndarray) -> ndarray:
    for box in EAST_INSTANCE(image):
        blackout_pixels(image, box)
    return image
