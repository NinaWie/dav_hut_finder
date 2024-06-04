"""Package installer."""
import os
from setuptools import setup
from setuptools import find_packages

LONG_DESCRIPTION = ""
if os.path.exists("README.md"):
    with open("README.md") as fp:
        LONG_DESCRIPTION = fp.read()

scripts = []

setup(
    name="airbnbpt",
    version="0.0.1",
    description="Public Transport filtering for Airbnb",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Mäuschens",
    license="MIT",
    url="https://github.com/NinaWie/public_transport_airbnb",
    install_requires=[
        "numpy",
        "geopandas",
        "matplotlib",
        "beautifulsoup4",
        "pyrosm"
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages("."),
    python_requires=">=3.8"
)
