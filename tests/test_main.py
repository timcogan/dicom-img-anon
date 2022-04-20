import runpy
import sys
from pathlib import Path

import numpy as np
import pydicom
from numpy import ndarray
from pydicom.data import get_testdata_file
from test_east import test_image as _test_image

test_image = _test_image


def save_dicom(folder: Path, image: ndarray, modality: str):
    ds = get_testdata_file("MR_small_padded.dcm", read=True)
    assert isinstance(ds, pydicom.Dataset)
    rows, cols = image.shape
    ds.PixelData = image.astype(np.uint8).tobytes()
    ds.Rows = rows
    ds.Columns = cols
    ds.BitsAllocated = 8
    ds.BitsStored = ds.BitsAllocated
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.Modality = modality
    ds.PixelRepresentation = 0
    test_filepath = folder / f"{modality}.dcm"
    ds.save_as(test_filepath)
    return test_filepath


def test_main(tmpdir, test_image):  # noqa
    Path(tmpdir / "should_be_ignored.txt").touch()
    anon_filepath = save_dicom(tmpdir, test_image[:, :, 0], "US")
    no_anon_filepath = save_dicom(tmpdir, test_image[:, :, 0], "MG")
    sys.argv = [sys.argv[0], str(tmpdir)]
    runpy.run_module("dicom_img_anon", run_name="__main__", alter_sys=False)

    ds = pydicom.dcmread(anon_filepath)
    assert ds.pixel_array.sum() == 0

    ds = pydicom.dcmread(no_anon_filepath)
    assert ds.pixel_array.sum() != 0
