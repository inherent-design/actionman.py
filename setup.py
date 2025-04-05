from setuptools import setup, find_packages
import os

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
    name="actionman",
    version=version,
    packages=find_packages(),
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
            "pyinstaller>=5.6.2",
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
        ],
    },
    python_requires=">=3.6",
    author="Fabric Engine Team",
    author_email="",
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
    url="https://github.com/fabric-engine/actionman",
)
