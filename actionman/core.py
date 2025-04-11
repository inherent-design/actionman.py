#!/usr/bin/env python3

"""Core functionality for the ActionMan build tool.

This module serves as a facade for the various build operations modules.
It provides a unified interface for configuring, building, testing,
and running C++ projects built with CMake.
"""

import os
from typing import List, Optional

from .modules.build_operations import BuildOperations
from .modules.run_operations import RunOperations
from .modules.test_operations import TestingOperations
from .modules.system_operations import SystemOperations


class BuildManager:
    """Manages the build process for C++ projects using CMake.

    This class serves as a facade for the various specialized operation classes,
    providing a unified interface for all build-related operations.
    """

    def __init__(self, cwd: Optional[str] = None):
        """Initialize the BuildManager.

        Args:
            cwd (Optional[str]): Current working directory. Defaults to os.getcwd().
        """
        if cwd:
            if not os.path.exists(cwd):
                raise ValueError(f"Specified working directory does not exist: {cwd}")
            if not os.path.isdir(cwd):
                raise ValueError(f"Specified path is not a directory: {cwd}")
        self.cwd = os.path.abspath(cwd) if cwd else os.getcwd()
        self.build_dir = os.path.join(self.cwd, "build")

        # Initialize operation modules
        self.build_ops = BuildOperations(cwd=self.cwd, build_dir=self.build_dir)
        self.run_ops = RunOperations(self.build_ops)
        self.test_ops = TestingOperations(self.build_ops)
        self.system_ops = SystemOperations()

    def configure(self, build_type: str = "debug", flags: List[str] = []) -> None:
        """Configure the build environment using CMake.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            flags (List[str], optional): Additional CMake flags. Defaults to empty list.

        Raises:
            SystemExit: If configuration fails or build type is invalid
        """
        self.build_ops.configure(build_type, flags)

    def build(self, build_type: str = "debug", flags: List[str] = []) -> None:
        """Build the specified configuration.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            flags (List[str], optional): Additional CMake flags. Defaults to empty list.

        Raises:
            SystemExit: If build fails or build type is invalid
        """
        self.build_ops.build(build_type, flags)

    def run(self, build_type: str = "debug", execution_params: List[str] = []) -> None:
        """Run the executable for the specified build type.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            execution_params (List[str], optional): Parameters to pass to the executable. Defaults to empty list.

        Raises:
            SystemExit: If execution fails or build type is invalid
        """
        self.run_ops.run(build_type, execution_params)

    def clean_directory(self, directory: str) -> None:
        """Remove all files and subdirectories in the specified directory.

        Args:
            directory (str): Directory to clean
        """
        self.build_ops.clean_directory(directory)

    def clean(self) -> None:
        """Clean the build directory."""
        self.build_ops.clean()

    def build_all(self) -> None:
        """Build all configurations (debug, profile, release)."""
        self.build_ops.build_all()

    def test(self, build_type: str = "debug", test_filter: str = "") -> None:
        """Run tests for the specified build type.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            test_filter (str, optional): Filter to run specific tests. Defaults to "".

        Raises:
            SystemExit: If tests fail or build type is invalid
        """
        self.test_ops.test(build_type, test_filter)

    def test_all(self) -> None:
        """Run tests for all configurations."""
        self.test_ops.test_all()

    def install(self, build_type: str = "debug", prefix: Optional[str] = None) -> None:
        """Install the built application.

        Args:
            build_type (str, optional): Build type to install. Defaults to "debug".
            prefix (Optional[str], optional): Installation prefix. Defaults to None.

        Raises:
            SystemExit: If installation fails
        """
        self.build_ops.install(build_type, prefix)

    def system_info(self) -> None:
        """Display system information relevant to the build."""
        self.system_ops.system_info()

    def print_help(self) -> None:
        """Print the help message with available commands."""
        self.system_ops.print_help()
