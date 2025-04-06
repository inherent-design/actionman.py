#!/usr/bin/env python3

"""
Run operations for the ActionMan build tool.

This module contains functionality for running C++ executables built with CMake.
"""

import os
import subprocess
import time
from typing import List
import glob

from ..utils import (
    colorize,
    print_separator,
    run_command,
    handle_errors,
    CMAKE_BUILD_MAP,
)
from .build_operations import BuildOperations


class RunOperations:
    """Handles run operations for C++ projects using CMake.

    This class provides methods for running C++ executables.
    """

    def __init__(self, build_ops: BuildOperations):
        """Initialize the RunOperations.

        Args:
            build_ops (BuildOperations): Build operations instance to use for building if needed.
        """
        self.build_ops = build_ops
        self.build_dir = build_ops.build_dir

    @handle_errors
    def _find_executable(self, build_type: str) -> str:
        """Locates the built executable in platform-specific build directories."""
        base_path = os.path.join(self.build_dir, CMAKE_BUILD_MAP[build_type])
        patterns = [
            os.path.join(base_path, "bin", "*"),
            os.path.join(base_path, "**", "*"),
            os.path.join(self.build_dir, "bin", CMAKE_BUILD_MAP[build_type], "*"),
            os.path.join(self.build_dir, "**", "*"),
        ]

        for pattern in patterns:
            for match in glob.glob(pattern):
                if os.path.isfile(match) and os.access(match, os.R_OK):
                    return match
        raise FileNotFoundError(
            f"Could not find built executable for {build_type} configuration. Searched:\n"
            f"{chr(10).join(patterns)}"
        )

    @handle_errors
    def run(self, build_type: str = "debug", execution_params: List[str] = []) -> None:
        """Run the executable for the specified build type.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            execution_params (List[str], optional): Parameters to pass to the executable. Defaults to empty list.

        Raises:
            SystemExit: If execution fails or build type is invalid
        """
        try:
            # First try to find the executable
            try:
                executable = self._find_executable(build_type)
            except FileNotFoundError:
                # If not found, build it first
                print(f"Executable not found. Building {build_type}...")
                self.build_ops.build(build_type)
                # Try to find it again after building
                executable = self._find_executable(build_type)

            # Ensure it's executable
            if not os.access(executable, os.X_OK):
                os.chmod(executable, 0o755)

            print(
                colorize(f"Running with arguments: {execution_params}", "cyan")
                if execution_params
                else colorize("Running without arguments", "cyan")
            )

            print_separator(f"BEGIN PROGRAM OUTPUT ({build_type.upper()})", "cyan")
            start_time = time.time()

            cmd = [executable] + execution_params
            returncode, stdout, stderr = run_command(cmd, cwd=self.build_ops.cwd)

            if stdout:
                print(stdout)
            if stderr:
                print(colorize(stderr, "red" if returncode != 0 else "yellow"))

            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)

            elapsed = time.time() - start_time
            print_separator(
                f"END PROGRAM OUTPUT ({build_type.upper()}) - {elapsed:.2f}s", "green"
            )
        except subprocess.CalledProcessError as e:
            print(colorize(f"Execution failed: {e}", "red"))
