#!/usr/bin/env python3

import os
import subprocess
import sys
import argparse


def build(clean=False, debug=False, output_name="actionman"):
    """
    Build a standalone executable using PyInstaller.

    Args:
        clean (bool): Whether to clean before building
        debug (bool): Whether to include debug information
        output_name (str): Name of the output executable
    """
    print("Building standalone executable for ActionMan...")

    # Clean if requested
    if clean and os.path.exists("dist"):
        print("Cleaning previous build...")
        import shutil

        shutil.rmtree("dist", ignore_errors=True)
        shutil.rmtree("build", ignore_errors=True)
        for file in os.listdir("."):
            if file.endswith(".spec"):
                os.remove(file)

    # Ensure PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Build the executable
    build_command = [
        "pyinstaller",
        "--onefile",
        "--name",
        output_name,
        "--collect-all=actionman",
        "-m",
        "actionman",
        "actionman/cli.py",
    ]

    # Add debug flag if requested
    if debug:
        build_command.insert(1, "--debug")

    subprocess.check_call(build_command)

    # Check if build was successful
    executable_path = os.path.join("dist", output_name)
    if os.path.exists(executable_path) or os.path.exists(executable_path + ".exe"):
        print(
            f"\nBuild successful! Executable created at: {os.path.abspath(os.path.join('dist', output_name))}"
        )
    else:
        print("\nBuild failed. Check the output above for errors.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build ActionMan executable")
    parser.add_argument("--clean", action="store_true", help="Clean before building")
    parser.add_argument(
        "--debug", action="store_true", help="Include debug information"
    )
    parser.add_argument(
        "--name", default="actionman", help="Name of the output executable"
    )

    args = parser.parse_args()
    build(clean=args.clean, debug=args.debug, output_name=args.name)
