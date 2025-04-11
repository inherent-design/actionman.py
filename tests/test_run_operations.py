#!/usr/bin/env python3

"""
Tests for the RunOperations class.

This module contains tests for the RunOperations class, which handles
running C++ executables built with CMake.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from actionman.modules.run_operations import RunOperations
from actionman.utils import CMAKE_BUILD_MAP


class TestRunOperations:
    """Tests for the RunOperations class."""

    def test_init(self, build_operations):
        """Test RunOperations initialization."""
        run_ops = RunOperations(build_operations)
        assert run_ops.build_ops == build_operations
        assert run_ops.build_dir == build_operations.build_dir

    def test_find_executable(self, run_operations, mock_build_dir):
        """Test _find_executable method."""
        # Test finding executable for debug build
        executable = run_operations._find_executable("debug")
        assert executable is not None
        assert os.path.exists(executable)
        assert os.path.isfile(executable)
        assert os.access(executable, os.X_OK)

        # Verify the executable is in the correct directory
        assert os.path.join(mock_build_dir, "Debug") in executable

        # Test finding executable for release build
        executable = run_operations._find_executable("release")
        assert executable is not None
        assert os.path.exists(executable)
        assert os.path.join(mock_build_dir, "Release") in executable

    def test_find_executable_not_found(self, run_operations, temp_dir):
        """Test _find_executable method when executable is not found."""
        # Create a new RunOperations with an empty build directory
        empty_build_dir = os.path.join(temp_dir, "empty_build")
        os.makedirs(empty_build_dir, exist_ok=True)

        from actionman.modules.build_operations import BuildOperations

        build_ops = BuildOperations(cwd=temp_dir, build_dir=empty_build_dir)
        run_ops = RunOperations(build_ops)

        # Expect FileNotFoundError when trying to find executable
        with pytest.raises(FileNotFoundError):
            run_ops._find_executable("debug")

    def test_run(self, run_operations, mock_command_runner):
        """Test run method."""
        # Test with default build type
        run_operations.run()

        # Verify that the executable was run
        assert len(mock_command_runner["history"]) > 0
        last_command = mock_command_runner["history"][-1]
        assert "test_executable" in last_command["cmd"][0]

        # Test with specific build type
        mock_command_runner["history"].clear()
        run_operations.run("release")

        # Verify that the correct executable was run
        assert len(mock_command_runner["history"]) > 0
        last_command = mock_command_runner["history"][-1]
        assert "test_executable" in last_command["cmd"][0]

        # Test with execution parameters
        mock_command_runner["history"].clear()
        execution_params = ["--verbose", "--option=value"]
        run_operations.run("debug", execution_params)

        # Verify that the executable was run with the correct parameters
        assert len(mock_command_runner["history"]) > 0
        last_command = mock_command_runner["history"][-1]
        assert "test_executable" in last_command["cmd"][0]
        assert last_command["cmd"][1:] == execution_params

    def test_run_build_if_not_found(self, run_operations, mock_command_runner):
        """Test run method builds the executable if not found."""
        # Mock _find_executable to raise FileNotFoundError on first call, then return a path
        original_find_executable = run_operations._find_executable
        call_count = 0

        def mock_find_executable(build_type):
            nonlocal call_count
            if call_count == 0:
                call_count += 1
                raise FileNotFoundError("Executable not found")
            return original_find_executable(build_type)

        with patch.object(
            run_operations, "_find_executable", side_effect=mock_find_executable
        ):
            # Mock the build method to track calls
            with patch.object(run_operations.build_ops, "build") as mock_build:
                run_operations.run("debug")

                # Verify that build was called
                mock_build.assert_called_once_with("debug")

                # Verify that the executable was run after building
                assert len(mock_command_runner["history"]) > 0
                last_command = mock_command_runner["history"][-1]
                assert "test_executable" in last_command["cmd"][0]
