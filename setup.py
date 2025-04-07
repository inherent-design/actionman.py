from setuptools import setup, find_packages
import os
import sys
import subprocess
from pathlib import Path
from actionman.utils import ensure_virtualenv


# Ensure we're using a virtualenv
python_exe = ensure_virtualenv()

# Get version from __init__.py
with open(os.path.join("actionman", "__init__.py"), "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip("\"'")
            break
    else:
        version = "0.1.0"

# Get long description from README.md
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    long_description = "ActionMan - Build and run management tool for C++ projects"

setup(
    packages=find_packages(),
    package_dir={"": "."},
    name="actionman",
    version=version,
    entry_points={
        "console_scripts": [
            "actionman=actionman.cli:main",
        ],
    },
    install_requires=[
        # No external dependencies required for core functionality
    ],
    extras_require={
        "dev": [
            "pyinstaller>=6.12.0",
            "pytest>=8.3.5",
            "black>=25.1.0",
            "isort>=6.0.1",
            "ruff>=0.11.4",
        ],
    },
    python_requires=">=3.6",
    author="zer0cell",
    author_email="mannie@inherent.design",
    description="Build and run management tool for C++ projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
    ],
    url="https://github.com/inherent-design/actionman.py",
)
