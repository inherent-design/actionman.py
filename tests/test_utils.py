#!/usr/bin/env python3

"""
Tests for utility functions.

This module contains tests for the utility functions used across the ActionMan package.
"""

import os
import platform
import sys
import subprocess
import pytest
from unittest.mock import patch, MagicMock

from actionman.utils import (
    colorize,
    print_separator,
    run_command,
    handle_errors,
    get_system_info,
    is_executable,
    find_executable,
    CMAKE_BUILD_MAP,
)


class TestUtils:
    """Tests for utility functions."""

    def test_colorize(self):
        """Test colorize function."""
        # Test with valid color
        colored_text = colorize("test", "red")
        if os.name == "nt" and "WT_SESSION" not in os.environ:
            # On Windows without Windows Terminal, no coloring
            assert colored_text == "test"
        else:
            # Otherwise, should have color codes
            assert "\033[31m" in colored_text
            assert "\033[0m" in colored_text

        # Test with invalid color (should use default)
        colored_text = colorize("test", "invalid_color")
        assert colored_text == "test\033[0m" or colored_text == "test"

    def test_print_separator(self):
        """Test print_separator function."""
        # Test with default parameters
        with patch("builtins.print") as mock_print:
            print_separator()
            mock_print.assert_called_once_with("=" * 80)

        # Test with message
        with patch("builtins.print") as mock_print:
            with patch(
                "actionman.utils.colorize", return_value="COLORED_MESSAGE"
            ) as mock_colorize:
                print_separator("Test Message", "red")
                mock_colorize.assert_called_once_with("Test Message", "red")
                assert mock_print.call_count == 1
                # Check that the printed string contains the colored message
                printed_str = mock_print.call_args[0][0]
                assert "COLORED_MESSAGE" in printed_str
                # Check that the printed string has the correct length
                # The actual length might vary slightly due to padding calculations
                assert len(printed_str) >= 80

    def test_run_command(self):
        """Test run_command function."""
        # Mock subprocess.run
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "test output"
        mock_process.stderr = ""

        with patch("subprocess.run", return_value=mock_process) as mock_run:
            returncode, stdout, stderr = run_command(["test", "command"])

            # Verify subprocess.run was called correctly
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            assert args[0] == ["test", "command"]
            assert kwargs["capture_output"] is True
            assert kwargs["text"] is True

            # Verify return values
            assert returncode == 0
            assert stdout == "test output"
            assert stderr == ""

        # Test with error
        mock_process.returncode = 1
        mock_process.stderr = "error message"

        with patch("subprocess.run", return_value=mock_process) as mock_run:
            returncode, stdout, stderr = run_command(["test", "command"])
            assert returncode == 1
            assert stderr == "error message"

        # Test with custom working directory
        with patch("subprocess.run", return_value=mock_process) as mock_run:
            returncode, stdout, stderr = run_command(
                ["test", "command"], cwd="/custom/dir"
            )

            # Verify subprocess.run was called with correct cwd
            args, kwargs = mock_run.call_args
            assert kwargs["cwd"] == "/custom/dir"

    def test_handle_errors_decorator(self):
        """Test handle_errors decorator."""

        # Create a test function with the decorator
        @handle_errors
        def test_func(arg1, arg2=None):
            if arg1 == "raise_key_error":
                raise KeyError("test_key")
            elif arg1 == "raise_subprocess_error":
                raise subprocess.CalledProcessError(1, "test_cmd")
            return f"Success: {arg1}, {arg2}"

        # Test normal execution
        assert test_func("test", "arg2") == "Success: test, arg2"

        # Test with KeyError
        with patch("builtins.print") as mock_print:
            with patch("sys.exit") as mock_exit:
                test_func("raise_key_error")

                # Verify error was printed
                assert mock_print.call_count >= 2
                # Verify sys.exit was called
                mock_exit.assert_called_once_with(1)

        # Test with CalledProcessError
        with patch("builtins.print") as mock_print:
            with patch("sys.exit") as mock_exit:
                test_func("raise_subprocess_error")

                # Verify error was printed
                assert mock_print.call_count >= 1
                # Verify sys.exit was called
                mock_exit.assert_called_once_with(1)

    def test_get_system_info(self):
        """Test get_system_info function."""
        info = get_system_info()

        # Verify the returned dictionary has the expected keys
        assert "os" in info
        assert "architecture" in info
        assert "python" in info
        assert "cpu_count" in info

        # Verify the values are of the expected type
        assert isinstance(info["os"], str)
        assert isinstance(info["architecture"], str)
        assert isinstance(info["python"], str)
        assert isinstance(info["cpu_count"], str)

        # Verify the values contain expected information
        assert platform.system() in info["os"]
        assert platform.machine() in info["architecture"]
        assert platform.python_version() in info["python"]

    def test_is_executable(self, temp_dir):
        """Test is_executable function."""
        # Create a non-executable file
        non_exec_file = os.path.join(temp_dir, "non_exec.txt")
        with open(non_exec_file, "w") as f:
            f.write("test")

        # Create an executable file
        exec_file = os.path.join(temp_dir, "exec.sh")
        with open(exec_file, "w") as f:
            f.write("#!/bin/sh\necho test")
        os.chmod(exec_file, 0o755)

        # Test non-executable file
        assert not is_executable(non_exec_file)

        # Test executable file
        assert is_executable(exec_file)

        # Test non-existent file
        assert not is_executable(os.path.join(temp_dir, "non_existent.txt"))

    def test_find_executable(self):
        """Test find_executable function."""
        # Mock is_executable to control behavior
        with patch("actionman.utils.is_executable") as mock_is_executable:
            # Test with absolute path that exists
            mock_is_executable.return_value = True
            result = find_executable("/usr/bin/python")
            assert result == "/usr/bin/python"

            # Test with absolute path that doesn't exist
            mock_is_executable.return_value = False
            result = find_executable("/usr/bin/nonexistent")
            assert result is None

        # Test with name that should be in PATH
        with patch("os.path.join", return_value="/usr/bin/python") as mock_join:
            with patch(
                "actionman.utils.is_executable", return_value=True
            ) as mock_is_executable:
                result = find_executable("python")
                assert result == "/usr/bin/python"

        # Test with name that is not in PATH
        with patch(
            "os.environ.get", return_value="/usr/bin:/usr/local/bin"
        ) as mock_environ_get:
            with patch(
                "actionman.utils.is_executable", return_value=False
            ) as mock_is_executable:
                result = find_executable("nonexistent")
                assert result is None

    def test_cmake_build_map(self):
        """Test CMAKE_BUILD_MAP constant."""
        # Verify the map contains the expected keys and values
        assert "debug" in CMAKE_BUILD_MAP
        assert "profile" in CMAKE_BUILD_MAP
        assert "release" in CMAKE_BUILD_MAP

        assert CMAKE_BUILD_MAP["debug"] == "Debug"
        assert CMAKE_BUILD_MAP["profile"] == "RelWithDebInfo"
        assert CMAKE_BUILD_MAP["release"] == "Release"
