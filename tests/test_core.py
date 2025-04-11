#!/usr/bin/env python3

"""
Tests for the BuildManager class.

This module contains tests for the BuildManager class, which serves as a facade
for all build-related operations in the ActionMan tool.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from actionman.core import BuildManager
from actionman.modules.build_operations import BuildOperations
from actionman.modules.run_operations import RunOperations
from actionman.modules.test_operations import TestingOperations
from actionman.modules.system_operations import SystemOperations


class TestBuildManager:
    """Tests for the BuildManager class."""

    def test_init(self, temp_dir):
        """Test BuildManager initialization."""
        # Test with default working directory
        with patch("os.getcwd", return_value=temp_dir):
            manager = BuildManager()
            assert manager.cwd == temp_dir
            assert manager.build_dir == os.path.join(temp_dir, "build")

            # Verify that operation modules are initialized
            assert isinstance(manager.build_ops, BuildOperations)
            assert isinstance(manager.run_ops, RunOperations)
            assert isinstance(manager.test_ops, TestingOperations)
            assert isinstance(manager.system_ops, SystemOperations)

        # Test with custom working directory
        manager = BuildManager(cwd=temp_dir)
        assert manager.cwd == temp_dir
        assert manager.build_dir == os.path.join(temp_dir, "build")

    def test_init_invalid_directory(self):
        """Test BuildManager initialization with invalid directory."""
        # Test with non-existent directory
        with pytest.raises(ValueError, match="does not exist"):
            BuildManager(cwd="/non/existent/directory")

        # Test with file instead of directory
        with patch("os.path.exists", return_value=True):
            with patch("os.path.isdir", return_value=False):
                with pytest.raises(ValueError, match="not a directory"):
                    BuildManager(cwd="/path/to/file")

    def test_configure(self, build_manager):
        """Test configure method."""
        # Mock the build_ops.configure method
        with patch.object(build_manager.build_ops, "configure") as mock_configure:
            # Test with default parameters
            build_manager.configure()
            mock_configure.assert_called_once_with("debug", [])

            # Test with custom parameters
            mock_configure.reset_mock()
            build_manager.configure("release", ["-DSOME_FLAG=ON"])
            mock_configure.assert_called_once_with("release", ["-DSOME_FLAG=ON"])

    def test_build(self, build_manager):
        """Test build method."""
        # Mock the build_ops.build method
        with patch.object(build_manager.build_ops, "build") as mock_build:
            # Test with default parameters
            build_manager.build()
            mock_build.assert_called_once_with("debug", [])

            # Test with custom parameters
            mock_build.reset_mock()
            build_manager.build("release", ["-DSOME_FLAG=ON"])
            mock_build.assert_called_once_with("release", ["-DSOME_FLAG=ON"])

    def test_run(self, build_manager):
        """Test run method."""
        # Mock the run_ops.run method
        with patch.object(build_manager.run_ops, "run") as mock_run:
            # Test with default parameters
            build_manager.run()
            mock_run.assert_called_once_with("debug", [])

            # Test with custom parameters
            mock_run.reset_mock()
            build_manager.run("release", ["--verbose"])
            mock_run.assert_called_once_with("release", ["--verbose"])

    def test_clean_directory(self, build_manager):
        """Test clean_directory method."""
        # Mock the build_ops.clean_directory method
        with patch.object(build_manager.build_ops, "clean_directory") as mock_clean:
            directory = "/path/to/clean"
            build_manager.clean_directory(directory)
            mock_clean.assert_called_once_with(directory)

    def test_clean(self, build_manager):
        """Test clean method."""
        # Mock the build_ops.clean method
        with patch.object(build_manager.build_ops, "clean") as mock_clean:
            build_manager.clean()
            mock_clean.assert_called_once()

    def test_build_all(self, build_manager):
        """Test build_all method."""
        # Mock the build_ops.build_all method
        with patch.object(build_manager.build_ops, "build_all") as mock_build_all:
            build_manager.build_all()
            mock_build_all.assert_called_once()

    def test_test(self, build_manager):
        """Test test method."""
        # Mock the test_ops.test method
        with patch.object(build_manager.test_ops, "test") as mock_test:
            # Test with default parameters
            build_manager.test()
            mock_test.assert_called_once_with("debug", "")

            # Test with custom parameters
            mock_test.reset_mock()
            build_manager.test("release", "TestCase")
            mock_test.assert_called_once_with("release", "TestCase")

    def test_test_all(self, build_manager):
        """Test test_all method."""
        # Mock the test_ops.test_all method
        with patch.object(build_manager.test_ops, "test_all") as mock_test_all:
            build_manager.test_all()
            mock_test_all.assert_called_once()

    def test_install(self, build_manager):
        """Test install method."""
        # Mock the build_ops.install method
        with patch.object(build_manager.build_ops, "install") as mock_install:
            # Test with default parameters
            build_manager.install()
            mock_install.assert_called_once_with("debug", None)

            # Test with custom parameters
            mock_install.reset_mock()
            build_manager.install("release", "/custom/prefix")
            mock_install.assert_called_once_with("release", "/custom/prefix")

    def test_system_info(self, build_manager):
        """Test system_info method."""
        # Mock the system_ops.system_info method
        with patch.object(build_manager.system_ops, "system_info") as mock_info:
            build_manager.system_info()
            mock_info.assert_called_once()

    def test_print_help(self, build_manager):
        """Test print_help method."""
        # Mock the system_ops.print_help method
        with patch.object(build_manager.system_ops, "print_help") as mock_help:
            build_manager.print_help()
            mock_help.assert_called_once()
