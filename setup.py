#!/usr/bin/env python3

from cx_Freeze import setup, Executable
import os
import sys
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

# Get output name from environment variable or use default
output_name = os.environ.get("ACTIONMAN_OUTPUT_NAME", "actionman")

# Check if debug mode is enabled
debug_mode = os.environ.get("ACTIONMAN_DEBUG", "") == "1"

# Get long description from README.md
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    long_description = "ActionMan - Build and run management tool for C++ projects"

# Determine the base for the executable
base = None
if sys.platform == "win32":
    base = "Console"  # Use "Win32GUI" for Windows GUI applications

# Define the executable
executable = Executable(
    script="actionman/cli.py",
    target_name=output_name,
    base=base,
)

# Define build options
build_options = {
    "packages": ["actionman"],
    "excludes": [],
    "include_files": [],
    "optimize": 0 if debug_mode else 2,  # Optimization level (0-2 with 0 for debug)
    "build_exe": "dist",  # Output directory
}

setup(
    name="actionman",
    version=version,
    description="Build and run management tool for C++ projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="zer0cell",
    author_email="mannie@inherent.design",
    url="https://github.com/inherent-design/actionman.py",
    packages=["actionman", "actionman.modules"],
    options={"build_exe": build_options},
    executables=[executable],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
    ],
)
