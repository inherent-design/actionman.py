#!/usr/bin/env python3

"""
Tests for the TestOperations class.

This module contains tests for the TestOperations class, which handles
testing C++ projects built with CMake.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from actionman.modules.test_operations import TestingOperations
from actionman.utils import CMAKE_BUILD_MAP


class TestTestingOperations:
    """Tests for the TestingOperations class."""

    def test_init(self, build_operations):
        """Test TestingOperations initialization."""
        test_ops = TestingOperations(build_operations)
        assert test_ops.build_ops == build_operations
        assert test_ops.build_dir == build_operations.build_dir

    def test_test(self, test_operations, mock_command_runner):
        """Test test method."""
        # Test with default build type
        test_operations.test()

        # Verify that the correct command was called
        assert len(mock_command_runner["history"]) > 0
        last_command = mock_command_runner["history"][-1]
        assert "ctest" in last_command["cmd"]
        assert "--output-on-failure" in last_command["cmd"]

        # Test with specific build type
        mock_command_runner["history"].clear()
        test_operations.test("release")

        # Verify that the correct command was called
        assert len(mock_command_runner["history"]) > 0
        last_command = mock_command_runner["history"][-1]
        assert "ctest" in last_command["cmd"]

        # Test with test filter
        mock_command_runner["history"].clear()
        test_filter = "SomeTestCase"
        test_operations.test("debug", test_filter)

        # Verify that the correct command was called with filter
        assert len(mock_command_runner["history"]) > 0
        last_command = mock_command_runner["history"][-1]
        assert "ctest" in last_command["cmd"]
        assert "-R" in last_command["cmd"]
        filter_index = last_command["cmd"].index("-R")
        assert last_command["cmd"][filter_index + 1] == test_filter

    def test_test_build_if_not_found(self, test_operations, mock_command_runner):
        """Test test method builds the project if build directory not found."""
        # Mock os.path.exists to return False for build_dir
        with patch("os.path.exists", return_value=False):
            # Mock the build method to track calls
            with patch.object(test_operations.build_ops, "build") as mock_build:
                test_operations.test("debug")

                # Verify that build was called
                mock_build.assert_called_once_with("debug")

                # Verify that ctest was called after building
                assert len(mock_command_runner["history"]) > 0
                last_command = mock_command_runner["history"][-1]
                assert "ctest" in last_command["cmd"]

    def test_test_all(self, test_operations, mock_command_runner):
        """Test test_all method."""
        # Mock the test method to track calls
        with patch.object(test_operations, "test") as mock_test:
            test_operations.test_all()

            # Verify that test was called for each build type
            assert mock_test.call_count == len(CMAKE_BUILD_MAP)

            # Verify that each build type was tested
            called_build_types = [call[0][0] for call in mock_test.call_args_list]
            for build_type in CMAKE_BUILD_MAP.keys():
                assert build_type in called_build_types

    def test_test_all_with_failures(self, test_operations):
        """Test test_all method when some tests fail."""

        # Mock the test method to raise SystemExit for some build types
        def mock_test(build_type, test_filter=""):
            if build_type == "release":
                raise SystemExit(1)

        with patch.object(test_operations, "test", side_effect=mock_test):
            # Mock sys.exit to prevent actual exit
            with patch("sys.exit") as mock_exit:
                test_operations.test_all()

                # Verify that sys.exit was called with error code
                mock_exit.assert_called_once_with(1)
