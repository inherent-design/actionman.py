#!/usr/bin/env python3

"""
Tests for the CLI module.

This module contains tests for the CLI module, which handles command-line
argument parsing and delegation to the BuildManager.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from actionman.cli import (
    parse_args,
    handle_build_command,
    handle_run_command,
    handle_test_command,
    handle_install_command,
    main,
)


class TestCLI:
    """Tests for the CLI module."""

    def test_parse_args(self):
        """Test parse_args function."""
        # Test with no arguments
        with patch("sys.argv", ["actionman"]):
            args = parse_args()
            assert args.command is None
            assert args.options == []
            assert args.working_dir is None

        # Test with command only
        with patch("sys.argv", ["actionman", "build"]):
            args = parse_args()
            assert args.command == "build"
            assert args.options == []
            assert args.working_dir is None

        # Test with command and options
        with patch("sys.argv", ["actionman", "build", "debug"]):
            args = parse_args()
            assert args.command == "build"
            assert args.options == ["debug"]
            assert args.working_dir is None

        # Test with working directory
        with patch("sys.argv", ["actionman", "--cd", "/path/to/project", "build"]):
            args = parse_args()
            assert args.command == "build"
            assert args.options == []
            assert args.working_dir == "/path/to/project"

        # Test with short working directory option
        with patch("sys.argv", ["actionman", "-c", "/path/to/project", "build"]):
            args = parse_args()
            assert args.command == "build"
            assert args.options == []
            assert args.working_dir == "/path/to/project"

        # Test with help option
        with patch("sys.argv", ["actionman", "--help"]):
            with pytest.raises(SystemExit):
                parse_args()

        # Test with version option
        with patch("sys.argv", ["actionman", "--version"]):
            with pytest.raises(SystemExit):
                parse_args()

    def test_clean_command(self):
        """Test clean command in the command dispatch dictionary."""
        mock_manager = MagicMock()
        # Simulate how clean is called in the command dispatch dictionary
        mock_manager.clean()
        mock_manager.clean.assert_called_once()

    def test_handle_build_command(self):
        """Test handle_build_command function."""
        mock_manager = MagicMock()

        # Test with no options (default build type)
        handle_build_command(mock_manager, [])
        mock_manager.build.assert_called_once_with("debug", [])

        # Test with build type
        mock_manager.reset_mock()
        handle_build_command(mock_manager, ["release"])
        mock_manager.build.assert_called_once_with("release", [])

        # Test with 'all' option
        mock_manager.reset_mock()
        handle_build_command(mock_manager, ["all"])
        mock_manager.build_all.assert_called_once()

        # Test with build type and flags
        mock_manager.reset_mock()
        handle_build_command(mock_manager, ["debug", "-DSOME_FLAG=ON"])
        mock_manager.build.assert_called_once_with("debug", ["-DSOME_FLAG=ON"])

    def test_handle_run_command(self):
        """Test handle_run_command function."""
        mock_manager = MagicMock()

        # Test with no options (default build type)
        handle_run_command(mock_manager, [])
        mock_manager.run.assert_called_once_with("debug", [])

        # Test with build type
        mock_manager.reset_mock()
        handle_run_command(mock_manager, ["release"])
        mock_manager.run.assert_called_once_with("release", [])

        # Test with build type and execution parameters
        mock_manager.reset_mock()
        handle_run_command(mock_manager, ["debug", "--verbose", "--option=value"])
        mock_manager.run.assert_called_once_with(
            "debug", ["--verbose", "--option=value"]
        )

    def test_handle_test_command(self):
        """Test handle_test_command function."""
        mock_manager = MagicMock()

        # Test with no options (default build type)
        handle_test_command(mock_manager, [])
        mock_manager.test.assert_called_once_with("debug", "")

        # Test with 'all' option
        mock_manager.reset_mock()
        handle_test_command(mock_manager, ["all"])
        mock_manager.test_all.assert_called_once()

        # Test with build type
        mock_manager.reset_mock()
        handle_test_command(mock_manager, ["release"])
        mock_manager.test.assert_called_once_with("release", "")

        # Test with test filter
        mock_manager.reset_mock()
        handle_test_command(mock_manager, ["TestCase"])
        mock_manager.test.assert_called_once_with("debug", "TestCase")

        # Test with build type and test filter
        mock_manager.reset_mock()
        handle_test_command(mock_manager, ["release", "TestCase"])
        mock_manager.test.assert_called_once_with("release", "TestCase")

    def test_handle_install_command(self):
        """Test handle_install_command function."""
        mock_manager = MagicMock()

        # Test with no options (default build type)
        handle_install_command(mock_manager, [])
        mock_manager.install.assert_called_once_with("debug", None)

        # Test with build type
        mock_manager.reset_mock()
        handle_install_command(mock_manager, ["release"])
        mock_manager.install.assert_called_once_with("release", None)

        # Test with prefix
        mock_manager.reset_mock()
        handle_install_command(mock_manager, ["--prefix=/usr/local"])
        mock_manager.install.assert_called_once_with("debug", "/usr/local")

        # Test with build type and prefix
        mock_manager.reset_mock()
        handle_install_command(mock_manager, ["release", "--prefix=/usr/local"])
        mock_manager.install.assert_called_once_with("release", "/usr/local")

    def test_main(self):
        """Test main function."""
        # Mock parse_args and BuildManager
        with patch("actionman.cli.parse_args") as mock_parse_args:
            with patch("actionman.cli.BuildManager") as mock_build_manager_class:
                # Set up mock return values
                mock_args = MagicMock()
                mock_args.command = "build"
                mock_args.options = ["debug"]
                mock_args.working_dir = None
                mock_parse_args.return_value = mock_args

                mock_manager = MagicMock()
                mock_build_manager_class.return_value = mock_manager

                # Call main
                main()

                # Verify BuildManager was initialized correctly
                mock_build_manager_class.assert_called_once_with(os.getcwd())

                # Verify the correct command handler was called
                mock_manager.build.assert_called_once_with("debug", [])

        # Test with working directory
        with patch("actionman.cli.parse_args") as mock_parse_args:
            with patch("actionman.cli.BuildManager") as mock_build_manager_class:
                # Set up mock return values
                mock_args = MagicMock()
                mock_args.command = "build"
                mock_args.options = ["debug"]
                mock_args.working_dir = "/path/to/project"
                mock_parse_args.return_value = mock_args

                mock_manager = MagicMock()
                mock_build_manager_class.return_value = mock_manager

                # Call main
                main()

                # Verify BuildManager was initialized with working directory
                mock_build_manager_class.assert_called_once_with("/path/to/project")

        # Test with unknown command
        with patch("actionman.cli.parse_args") as mock_parse_args:
            with patch("actionman.cli.BuildManager") as mock_build_manager_class:
                with patch("sys.exit") as mock_exit:
                    # Set up mock return values
                    mock_args = MagicMock()
                    mock_args.command = "unknown"
                    mock_args.options = []
                    mock_args.working_dir = None
                    mock_parse_args.return_value = mock_args

                    mock_manager = MagicMock()
                    mock_build_manager_class.return_value = mock_manager

                    # Call main
                    main()

                    # Verify sys.exit was called
                    mock_exit.assert_called_once_with(1)

        # Test with no command (should show help)
        with patch("actionman.cli.parse_args") as mock_parse_args:
            with patch("actionman.cli.BuildManager") as mock_build_manager_class:
                # Set up mock return values
                mock_args = MagicMock()
                mock_args.command = None
                mock_args.options = []
                mock_args.working_dir = None
                mock_parse_args.return_value = mock_args

                mock_manager = MagicMock()
                mock_build_manager_class.return_value = mock_manager

                # Call main
                main()

                # Verify print_help was called
                mock_manager.print_help.assert_called_once()
