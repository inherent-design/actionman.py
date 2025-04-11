#!/usr/bin/env python3

"""
Integration tests for ActionMan.

This module contains integration tests that verify the complete workflow
of the ActionMan tool, from building to running and testing.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from actionman.core import BuildManager
from actionman.utils import CMAKE_BUILD_MAP


class TestIntegration:
    """Integration tests for ActionMan."""

    def test_build_and_run_workflow(self, temp_dir, mock_command_runner):
        """Test the complete build and run workflow."""
        # Create a BuildManager with the temp directory
        manager = BuildManager(cwd=temp_dir)

        # Execute the complete workflow: configure -> build -> run
        manager.configure("debug")
        manager.build("debug")
        manager.run("debug", ["--test-arg"])

        # Verify that the correct commands were executed in sequence
        assert len(mock_command_runner["history"]) >= 3

        # Check configure command
        configure_cmd = mock_command_runner["history"][0]
        assert "cmake" in configure_cmd["cmd"]
        assert "-DCMAKE_BUILD_TYPE=Debug" in configure_cmd["cmd"]

        # Check build command
        build_cmd = None
        for cmd in mock_command_runner["history"]:
            if "cmake" in cmd["cmd"] and "--build" in cmd["cmd"]:
                build_cmd = cmd
                break
        assert build_cmd is not None, "No build command found in command history"
        assert "--build" in build_cmd["cmd"]

        # Check run command (should contain the executable path and arguments)
        run_cmd = mock_command_runner["history"][-1]
        assert "--test-arg" in run_cmd["cmd"]

    def test_build_and_test_workflow(self, temp_dir, mock_command_runner):
        """Test the complete build and test workflow."""
        # Create a BuildManager with the temp directory
        manager = BuildManager(cwd=temp_dir)

        # Execute the complete workflow: configure -> build -> test
        manager.configure("debug")
        manager.build("debug")
        manager.test("debug", "TestCase")

        # Verify that the correct commands were executed in sequence
        assert len(mock_command_runner["history"]) >= 3

        # Check configure command
        configure_cmd = mock_command_runner["history"][0]
        assert "cmake" in configure_cmd["cmd"]
        assert "-DCMAKE_BUILD_TYPE=Debug" in configure_cmd["cmd"]

        # Check build command
        build_cmd = None
        for cmd in mock_command_runner["history"]:
            if "cmake" in cmd["cmd"] and "--build" in cmd["cmd"]:
                build_cmd = cmd
                break
        assert build_cmd is not None, "No build command found in command history"
        assert "--build" in build_cmd["cmd"]

        # Check test command
        test_cmd = mock_command_runner["history"][-1]
        assert "ctest" in test_cmd["cmd"]
        assert "-R" in test_cmd["cmd"]
        assert "TestCase" in test_cmd["cmd"]

    def test_clean_build_install_workflow(self, temp_dir, mock_command_runner):
        """Test the complete clean, build, and install workflow."""
        # Create a BuildManager with the temp directory
        manager = BuildManager(cwd=temp_dir)

        # Create a mock build directory
        build_dir = os.path.join(temp_dir, "build")
        os.makedirs(build_dir, exist_ok=True)

        # Execute the complete workflow: clean -> configure -> build -> install
        manager.clean()
        manager.configure("release")
        manager.build("release")
        manager.install("release", "/custom/prefix")

        # Verify that the correct commands were executed in sequence
        assert len(mock_command_runner["history"]) >= 3

        # Check configure command
        configure_cmd = None
        for cmd in mock_command_runner["history"]:
            if "cmake" in cmd["cmd"] and "-DCMAKE_BUILD_TYPE=Release" in cmd["cmd"]:
                configure_cmd = cmd
                break
        assert configure_cmd is not None

        # Check build command
        build_cmd = None
        for cmd in mock_command_runner["history"]:
            if "cmake" in cmd["cmd"] and "--build" in cmd["cmd"]:
                build_cmd = cmd
                break
        assert build_cmd is not None

        # Check install command
        install_cmd = None
        for cmd in mock_command_runner["history"]:
            if "cmake" in cmd["cmd"] and "--install" in cmd["cmd"]:
                install_cmd = cmd
                break
        assert install_cmd is not None
        assert "--prefix" in install_cmd["cmd"]
        assert "/custom/prefix" in install_cmd["cmd"]

    def test_build_all_and_test_all_workflow(self, temp_dir, mock_command_runner):
        """Test the complete build_all and test_all workflow."""
        # Create a BuildManager with the temp directory
        manager = BuildManager(cwd=temp_dir)

        # Execute the complete workflow: build_all -> test_all
        with patch.object(manager.build_ops, "build") as mock_build:
            with patch.object(manager.test_ops, "test") as mock_test:
                manager.build_all()
                manager.test_all()

                # Verify that build was called for each build type
                assert mock_build.call_count == len(CMAKE_BUILD_MAP)

                # Verify that test was called for each build type
                assert mock_test.call_count == len(CMAKE_BUILD_MAP)

                # Verify that each build type was built and tested
                built_types = [call[0][0] for call in mock_build.call_args_list]
                tested_types = [call[0][0] for call in mock_test.call_args_list]

                for build_type in CMAKE_BUILD_MAP.keys():
                    assert build_type in built_types
                    assert build_type in tested_types
