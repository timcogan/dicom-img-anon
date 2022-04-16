import argparse
from pathlib import Path
from dicom_img_anon.anon import anon_dicom


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove PHI from DICOM images")
    parser.add_argument("folder", help="root folder with DICOMs to be anonymized")
    return parser.parse_args()


def main(args: argparse.Namespace):
    for filename in Path(args.folder).rglob("*"):
        try:
            anon_dicom(filename)
        except:
            pass  # We don't care if the file is not a valid DICOM (e.g. txt file)


if __name__ == "__main__":
    main(parse_args())
