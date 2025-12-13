#!/usr/bin/env python3
"""Setup script for Minmatar Rebellion"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="minmatar-rebellion",
    version="2.0.0",
    author="James Young, AreteLabs",
    description="A top-down arcade space shooter inspired by EVE Online",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AreteDriver/EVE_Rebellion",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Arcade",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "minmatar-rebellion=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["data/**/*.json"],
    },
)
