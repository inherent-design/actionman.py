#!/usr/bin/env python3

import os
import subprocess
import argparse
from actionman.utils import ensure_virtualenv


def build(clean=False, debug=False, output_name="actionman"):
    """
    Build a standalone executable using cx_Freeze.

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

    # Ensure we're using a virtualenv
    python_exe = ensure_virtualenv()

    # Ensure cx_Freeze is installed
    try:
        # Try to import from the current environment
        import cx_Freeze
    except ImportError:
        print("cx_Freeze not found. Installing...")
        subprocess.check_call([python_exe, "-m", "pip", "install", "cx_Freeze==8.1.0"])

    # Build the executable
    build_command = [
        python_exe,
        "setup.py",
        "build_exe",
    ]

    # Set environment variables for build options
    env = os.environ.copy()
    env["ACTIONMAN_OUTPUT_NAME"] = output_name

    # Add debug flag if requested
    if debug:
        env["ACTIONMAN_DEBUG"] = "1"

    subprocess.check_call(build_command, env=env)

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
