#!/usr/bin/env python3

"""
Test operations for the ActionMan build tool.

This module contains functionality for testing C++ projects built with CMake.
"""

import os
import subprocess
import sys
import time

from ..utils import (
    colorize,
    print_separator,
    run_command,
    handle_errors,
    CMAKE_BUILD_MAP,
)
from .build_operations import BuildOperations


class TestOperations:
    """Handles test operations for C++ projects using CMake.

    This class provides methods for testing C++ projects.
    """

    def __init__(self, build_ops: BuildOperations):
        """Initialize the TestOperations.

        Args:
            build_ops (BuildOperations): Build operations instance to use for building if needed.
        """
        self.build_ops = build_ops
        self.build_dir = build_ops.build_dir

    @handle_errors
    def test(self, build_type: str = "debug", test_filter: str = "") -> None:
        """Run tests for the specified build type.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            test_filter (str, optional): Filter to run specific tests. Defaults to "".

        Raises:
            SystemExit: If tests fail or build type is invalid
        """
        try:
            # Ensure the build exists
            if not os.path.exists(self.build_dir):
                print(f"Build directory not found. Building {build_type}...")
                self.build_ops.build(build_type)

            print_separator(f"BEGIN TEST OUTPUT ({build_type.upper()})", "cyan")
            start_time = time.time()

            cmd = ["ctest", "--output-on-failure"]
            if test_filter:
                cmd.extend(["-R", test_filter])

            print(f"Running: {' '.join(cmd)}")
            returncode, stdout, stderr = run_command(cmd, cwd=self.build_ops.cwd)

            if stdout:
                print(stdout)
            if stderr:
                print(colorize(stderr, "red" if returncode != 0 else "yellow"))

            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)

            elapsed = time.time() - start_time
            print_separator(
                f"END TEST OUTPUT ({build_type.upper()}) - {elapsed:.2f}s", "green"
            )
        except subprocess.CalledProcessError as e:
            print(colorize(f"Test execution failed: {e}", "red"))
            raise

    def test_all(self) -> None:
        """Run tests for all configurations."""
        success = True
        results = []

        for build_type in CMAKE_BUILD_MAP.keys():
            print(f"\nTesting {build_type} configuration...")
            start_time = time.time()
            try:
                self.test(build_type)
                elapsed = time.time() - start_time
                results.append((build_type, True, elapsed))
            except SystemExit:
                elapsed = time.time() - start_time
                results.append((build_type, False, elapsed))
                success = False

        # Print summary
        print_separator("TEST SUMMARY", "bold")
        for build_type, result, elapsed in results:
            status = (
                colorize("SUCCESS", "green") if result else colorize("FAILED", "red")
            )
            print(f"{build_type.ljust(10)}: {status} ({elapsed:.2f}s)")

        if not success:
            sys.exit(1)
