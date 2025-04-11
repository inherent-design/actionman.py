#!/usr/bin/env python3

"""
Build operations for the ActionMan build tool.

This module contains functionality for configuring and building C++ projects with CMake.
"""

import os
import subprocess
import sys
import shutil
import time
from typing import List, Optional

from ..utils import (
    colorize,
    print_separator,
    run_command,
    handle_errors,
    CMAKE_BUILD_MAP,
)


class BuildOperations:
    """Handles build operations for C++ projects using CMake.

    This class provides methods for configuring and building C++ projects.
    """

    def __init__(self, cwd: Optional[str] = None, build_dir: Optional[str] = None):
        """Initialize the BuildOperations.

        Args:
            cwd (Optional[str]): Current working directory. Defaults to os.getcwd().
            build_dir (Optional[str]): Build directory. Defaults to os.path.join(cwd, "build").
        """
        self.cwd = cwd or os.getcwd()
        if build_dir is not None:
            if os.path.isabs(build_dir):
                self.build_dir = build_dir
            else:
                self.build_dir = os.path.join(self.cwd, build_dir)
        else:
            self.build_dir = os.path.join(self.cwd, "build")

    def configure(self, build_type: str = "debug", flags: List[str] = []) -> None:
        """Configure the build environment using CMake.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            flags (List[str], optional): Additional CMake flags. Defaults to empty list.

        Raises:
            SystemExit: If configuration fails or build type is invalid
        """

        @handle_errors
        def _configure(self, build_type: str, flags: List[str]):
            # Create build directory if it doesn't exist
            os.makedirs(self.build_dir, exist_ok=True)

            print_separator(f"BEGIN CONFIGURE ({build_type.upper()})", "cyan")

            # Determine generator based on platform
            generator = "Ninja"
            if shutil.which("ninja") is None:
                if os.name == "nt":
                    generator = "Visual Studio 17 2022"
                else:
                    generator = "Unix Makefiles"

            start_time = time.time()

            cmd = [
                "cmake",
                "-G",
                generator,
                "-S",
                ".",
                "-B",
                self.build_dir,
                f"-DCMAKE_BUILD_TYPE={CMAKE_BUILD_MAP[build_type]}",
            ] + flags

            print(f"Running: {' '.join(cmd)}")
            returncode, stdout, stderr = run_command(cmd, cwd=self.cwd)

            if stdout:
                print(stdout)
            if stderr:
                print(colorize(stderr, "red"))

            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)

            elapsed = time.time() - start_time
            print_separator(
                f"END CONFIGURE ({build_type.upper()}) - {elapsed:.2f}s", "green"
            )

        _configure(self, build_type, flags)

    def build(self, build_type: str = "debug", flags: List[str] = []) -> None:
        """Build the specified configuration.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            flags (List[str], optional): Additional CMake flags. Defaults to empty list.

        Raises:
            SystemExit: If build fails or build type is invalid
        """

        @handle_errors
        def _build(self, build_type: str, flags: List[str]):
            self.configure(build_type, flags)

            print_separator(f"BEGIN BUILD OUTPUT ({build_type.upper()})", "cyan")
            start_time = time.time()

            # Determine number of CPU cores for parallel builds
            cpu_count = os.cpu_count() or 4

            cmd = ["cmake", "--build", ".", f"-j{cpu_count}"]
            print(f"Running: {' '.join(cmd)}")

            returncode, stdout, stderr = run_command(cmd, self.build_dir)

            if stdout:
                print(stdout)
            if stderr and returncode != 0:
                print(colorize(stderr, "red"))

            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)

            elapsed = time.time() - start_time
            print_separator(
                f"END BUILD OUTPUT ({build_type.upper()}) - {elapsed:.2f}s", "green"
            )

        _build(self, build_type, flags)

    def build_all(self) -> None:
        """Build all configurations (debug, profile, release)."""
        success = True
        results = []

        for build_type in CMAKE_BUILD_MAP.keys():
            print(f"\nBuilding {build_type} configuration...")
            start_time = time.time()
            try:
                self.build(build_type)
                elapsed = time.time() - start_time
                results.append((build_type, True, elapsed))
            except SystemExit:
                elapsed = time.time() - start_time
                results.append((build_type, False, elapsed))
                success = False

        # Print summary
        print_separator("BUILD SUMMARY", "bold")
        for build_type, result, elapsed in results:
            status = (
                colorize("SUCCESS", "green") if result else colorize("FAILED", "red")
            )
            print(f"{build_type.ljust(10)}: {status} ({elapsed:.2f}s)")

        if not success:
            sys.exit(1)

    def install(self, build_type: str = "debug", prefix: Optional[str] = None) -> None:
        """Install the built application.

        Args:
            build_type (str, optional): Build type to install. Defaults to "debug".
            prefix (Optional[str], optional): Installation prefix. Defaults to None.

        Raises:
            SystemExit: If installation fails
        """

        @handle_errors
        def _install(self, build_type: str, prefix: Optional[str]):
            # Ensure the build exists
            if not os.path.exists(self.build_dir):
                print(f"Build directory not found. Building {build_type}...")
                self.build(build_type)

            print_separator(f"BEGIN INSTALL ({build_type.upper()})", "cyan")
            start_time = time.time()

            cmd = ["cmake", "--install", "."]
            if prefix:
                if not os.path.isabs(prefix):
                    prefix = os.path.join(self.cwd, prefix)
                cmd.extend(["--prefix", prefix])

            print(f"Running: {' '.join(cmd)}")
            returncode, stdout, stderr = run_command(cmd, self.build_dir)

            if stdout:
                print(stdout)
            if stderr:
                print(colorize(stderr, "red" if returncode != 0 else "yellow"))

            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)

            elapsed = time.time() - start_time
            print_separator(
                f"END INSTALL ({build_type.upper()}) - {elapsed:.2f}s", "green"
            )

            # Verify installed executable
            install_bin_dir = os.path.join(prefix or "/usr/local", "bin")
            # Look for any installed executable in the bin directory
            if os.path.exists(install_bin_dir):
                installed_files = os.listdir(install_bin_dir)
                if installed_files:
                    # Get the first executable file for verification
                    installed_exe = os.path.join(install_bin_dir, installed_files[0])

                    # Ensure executable permissions
                    try:
                        os.chmod(installed_exe, 0o755)
                        print(colorize(f"Set executable permissions: {installed_exe}", "cyan"))

                        # Basic version check
                        returncode, stdout, stderr = run_command(
                            [installed_exe, "--version"], install_bin_dir
                        )
                        if returncode == 0:
                            print(colorize(f"Installation verified: {stdout.strip()}", "green"))
                        else:
                            print(colorize(f"Version check failed: {stderr}", "yellow"))
                    except Exception as e:
                        print(colorize(f"Post-install verification failed: {e}", "yellow"))
                else:
                    print(colorize(f"No installed files found in {install_bin_dir}, but directory exists", "yellow"))
            else:
                print(colorize(f"Install directory {install_bin_dir} not found, skipping verification", "yellow"))

            # The code below is now handled in the conditional blocks above

        _install(self, build_type, prefix)

    def clean_directory(self, directory: str) -> None:
        """Remove all files and subdirectories in the specified directory.

        Args:
            directory (str): Directory to clean
        """
        @handle_errors
        def _clean_directory(self, directory: str):
            if not os.path.isabs(directory):
                directory = os.path.join(self.cwd, directory)
            if not os.path.exists(directory):
                print(f"Directory {directory} does not exist. Nothing to clean.")
                return

            try:
                print(f"Cleaning {os.path.basename(directory)} directory...")
                shutil.rmtree(directory, ignore_errors=True)
                print(
                    colorize(f"Cleaned {os.path.basename(directory)} directory.", "green")
                )
            except Exception as e:
                print(
                    colorize(
                        f"An error occurred during cleaning {os.path.basename(directory)}: {e}",
                        "red",
                    )
                )
        
        _clean_directory(self, directory)

    def clean(self) -> None:
        """Clean the build directory."""
        @handle_errors
        def _clean(self):
            self.clean_directory(self.build_dir)
            
        _clean(self)
