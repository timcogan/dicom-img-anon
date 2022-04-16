from typing import Dict, Final, List

from setuptools import find_packages, setup

from util import write_version_info

package_name: Final[str] = "dicom_img_anon"


requirements: Final[List[str]] = [
    "matplotlib",
    "numpy",
    "opencv-python",
    "Pillow",
    "pydicom",
]

extras: Final[Dict[str, List[str]]] = {
    "dev": ["pytest", "black", "flake8", "autoflake", "autopep8", "isort", "coverage"]
}

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name=package_name,
    version=write_version_info(package_name),
    packages=find_packages(),
    install_requires=requirements,
    extras_require=extras,
    python_requires=">=3.8.0",
    long_description=long_description,
)
