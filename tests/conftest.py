#!/usr/bin/env python3

"""
Test fixtures for ActionMan tests.

This module provides fixtures that can be used across all test modules.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator, Dict, Any

import pytest

from actionman.core import BuildManager
from actionman.modules.build_operations import BuildOperations
from actionman.modules.run_operations import RunOperations
from actionman.modules.test_operations import TestingOperations
from actionman.modules.system_operations import SystemOperations


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """
    Create a temporary directory for tests.

    Yields:
        str: Path to the temporary directory
    """
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_build_dir(temp_dir: str) -> str:
    """
    Create a mock build directory structure.

    Args:
        temp_dir (str): Temporary directory path

    Returns:
        str: Path to the mock build directory
    """
    build_dir = os.path.join(temp_dir, "build")
    os.makedirs(build_dir, exist_ok=True)

    # Create mock build type directories
    for build_type in ["Debug", "RelWithDebInfo", "Release"]:
        build_type_dir = os.path.join(build_dir, build_type)
        os.makedirs(build_type_dir, exist_ok=True)

        # Create a mock executable
        bin_dir = os.path.join(build_type_dir, "bin")
        os.makedirs(bin_dir, exist_ok=True)

        executable_path = os.path.join(bin_dir, "test_executable")
        with open(executable_path, "w") as f:
            f.write('#!/bin/sh\necho "Mock executable for {build_type}"')

        # Make it executable
        os.chmod(executable_path, 0o755)

    return build_dir


@pytest.fixture
def build_operations(temp_dir: str, mock_build_dir: str) -> BuildOperations:
    """
    Create a BuildOperations instance with a mock build directory.

    Args:
        temp_dir (str): Temporary directory path
        mock_build_dir (str): Mock build directory path

    Returns:
        BuildOperations: Configured BuildOperations instance
    """
    return BuildOperations(cwd=temp_dir, build_dir=mock_build_dir)


@pytest.fixture
def run_operations(build_operations: BuildOperations) -> RunOperations:
    """
    Create a RunOperations instance.

    Args:
        build_operations (BuildOperations): BuildOperations instance

    Returns:
        RunOperations: Configured RunOperations instance
    """
    return RunOperations(build_operations)


@pytest.fixture
def test_operations(build_operations: BuildOperations) -> TestingOperations:
    """
    Create a TestingOperations instance.

    Args:
        build_operations (BuildOperations): BuildOperations instance

    Returns:
        TestingOperations: Configured TestingOperations instance
    """
    return TestingOperations(build_operations)


@pytest.fixture
def system_operations() -> SystemOperations:
    """
    Create a SystemOperations instance.

    Returns:
        SystemOperations: Configured SystemOperations instance
    """
    return SystemOperations()


@pytest.fixture
def build_manager(temp_dir: str) -> BuildManager:
    """
    Create a BuildManager instance.

    Args:
        temp_dir (str): Temporary directory path

    Returns:
        BuildManager: Configured BuildManager instance
    """
    return BuildManager(cwd=temp_dir)


@pytest.fixture
def mock_command_runner(monkeypatch) -> Dict[str, Any]:
    """
    Mock the run_command function to avoid executing real commands.

    Args:
        monkeypatch: pytest's monkeypatch fixture

    Returns:
        Dict[str, Any]: Dictionary with mock command history and configuration
    """
    command_history = []

    def mock_run_command(cmd, cwd=None):
        command_history.append({"cmd": cmd, "cwd": cwd})
        # Default successful return
        return 0, "Mock command output", ""

    # Store the original function for selective use in tests
    import actionman.utils
    import actionman.modules.build_operations
    import actionman.modules.run_operations
    import actionman.modules.test_operations
    import actionman.modules.system_operations

    original_run_command = actionman.utils.run_command

    # Apply the mock to all modules that use run_command
    monkeypatch.setattr(actionman.utils, "run_command", mock_run_command)
    monkeypatch.setattr(
        actionman.modules.build_operations, "run_command", mock_run_command
    )
    monkeypatch.setattr(
        actionman.modules.run_operations, "run_command", mock_run_command
    )
    monkeypatch.setattr(
        actionman.modules.test_operations, "run_command", mock_run_command
    )
    monkeypatch.setattr(
        actionman.modules.system_operations, "run_command", mock_run_command
    )

    return {"history": command_history, "original_run_command": original_run_command}
