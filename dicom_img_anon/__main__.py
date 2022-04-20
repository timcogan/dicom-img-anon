import argparse
from pathlib import Path

from tqdm import tqdm

from dicom_img_anon.anon import anon_dicom


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove PHI from DICOM images")
    parser.add_argument("folder", help="root folder with DICOMs to be anonymized")
    return parser.parse_args()


def main(args: argparse.Namespace):
    filenames = list(Path(args.folder).rglob("*"))

    for filename in tqdm(filenames):
        try:
            anon_dicom(filename)
        except:
            pass


if __name__ == "__main__":
    main(parse_args())
