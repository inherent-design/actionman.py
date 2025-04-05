#!/usr/bin/env python3

"""
Run operations for the ActionMan build tool.

This module contains functionality for running C++ executables built with CMake.
"""

import os
import subprocess
import sys
import time
from typing import List

from ..utils import colorize, print_separator, run_command, CMAKE_BUILD_MAP
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

    def run(self, build_type: str = "debug", execution_params: List[str] = []) -> None:
        """Run the executable for the specified build type.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            execution_params (List[str], optional): Parameters to pass to the executable. Defaults to empty list.

        Raises:
            SystemExit: If execution fails or build type is invalid
        """
        try:
            executable = os.path.join(self.build_dir, "bin", "Fabric")
            if os.name == "nt":
                executable += ".exe"

            if not os.path.exists(executable):
                print(f"Executable not found. Building {build_type}...")
                self.build_ops.build(build_type)

            print(
                colorize(f"Running with arguments: {execution_params}", "cyan")
                if execution_params
                else colorize("Running without arguments", "cyan")
            )

            print_separator(f"BEGIN FABRIC OUTPUT ({build_type.upper()})", "cyan")
            start_time = time.time()

            cmd = [executable] + execution_params
            returncode, stdout, stderr = run_command(cmd)

            if stdout:
                print(stdout)
            if stderr:
                print(colorize(stderr, "red" if returncode != 0 else "yellow"))

            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)

            elapsed = time.time() - start_time
            print_separator(
                f"END FABRIC OUTPUT ({build_type.upper()}) - {elapsed:.2f}s", "green"
            )
        except subprocess.CalledProcessError as e:
            print(colorize(f"Execution failed: {e}", "red"))
            sys.exit(1)
        except KeyError:
            print(colorize(f"Invalid build type: {build_type}", "red"))
            print(f"Available build types: {', '.join(CMAKE_BUILD_MAP.keys())}")
            sys.exit(1)
