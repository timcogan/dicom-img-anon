from pathlib import Path
from typing import Final, List, Union

import pydicom
from numpy import ndarray
from pydicom.uid import ExplicitVRLittleEndian

from dicom_img_anon.east import EAST, blackout_pixels

TARGET_MODALITIES: Final[List[str]] = ["US"]
EAST_INSTANCE: Final[EAST] = EAST()


def has_dicm_prefix(filename: Union[str, Path]) -> bool:
    """DICOM files have a 128 byte preamble followed by bytes 'DICM'."""
    with open(filename, "rb") as f:
        f.seek(128)
        return f.read(4) == b"DICM"


def anon_dicom(dicom: Path) -> None:
    if dicom.is_file() and has_dicm_prefix(dicom):
        ds = pydicom.dcmread(dicom)

        if ds.get("Modality", "") in TARGET_MODALITIES:
            image = anon_image(ds.pixel_array)
            ds.PixelData = image.tobytes()
            ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
            ds.save_as(dicom)


def anon_image(image: ndarray) -> ndarray:
    for box in EAST_INSTANCE(image):
        blackout_pixels(image, box)
    return image
