#!/usr/bin/env python3

"""
Tests for the SystemOperations class.

This module contains tests for the SystemOperations class, which handles
displaying system information and help.
"""

import pytest
from unittest.mock import patch, MagicMock

from actionman.modules.system_operations import SystemOperations


class TestSystemOperations:
    """Tests for the SystemOperations class."""

    def test_init(self):
        """Test SystemOperations initialization."""
        system_ops = SystemOperations()
        assert isinstance(system_ops, SystemOperations)

    def test_system_info(self, system_operations, mock_command_runner):
        """Test system_info method."""
        # Capture stdout to verify output
        with patch("builtins.print") as mock_print:
            system_operations.system_info()

            # Verify that system information was printed
            assert mock_print.call_count > 0

            # Check for key system information sections
            system_info_call = False
            build_tools_call = False
            cpu_cores_call = False

            for call in mock_print.call_args_list:
                args = call[0][0] if call[0] else ""
                if isinstance(args, str):
                    if "OS:" in args:
                        system_info_call = True
                    elif "Build Tools:" in args:
                        build_tools_call = True
                    elif "CPU Cores:" in args:
                        cpu_cores_call = True

            assert system_info_call, "System OS information not displayed"
            assert build_tools_call, "Build tools information not displayed"
            assert cpu_cores_call, "CPU cores information not displayed"

            # Verify that run_command was called to check for build tools
            assert len(mock_command_runner["history"]) > 0

            # Check that we tried to get versions of required tools
            tool_checks = [
                cmd
                for cmd in mock_command_runner["history"]
                if "--version" in " ".join(cmd["cmd"])
            ]
            assert len(tool_checks) > 0, "No version checks performed for build tools"

    def test_print_help(self, system_operations):
        """Test print_help method."""
        with patch("builtins.print") as mock_print:
            system_operations.print_help()

            # Verify that help information was printed
            assert mock_print.call_count > 0

            # Check for key help sections
            usage_call = False
            global_options_call = False
            available_commands_call = False

            for call in mock_print.call_args_list:
                args = call[0][0] if call[0] else ""
                if isinstance(args, str):
                    if "Usage:" in args:
                        usage_call = True
                    elif "Global options:" in args:
                        global_options_call = True
                    elif "Available commands:" in args:
                        available_commands_call = True

            assert usage_call, "Usage information not displayed"
            assert global_options_call, "Global options not displayed"
            assert available_commands_call, "Available commands not displayed"

            # Check that key commands are included in the help output
            commands_to_check = ["clean", "build", "run", "test", "install"]
            command_calls = []

            for call in mock_print.call_args_list:
                args = call[0][0] if call[0] else ""
                if isinstance(args, str):
                    for cmd in commands_to_check:
                        if cmd in args:
                            command_calls.append(cmd)

            for cmd in commands_to_check:
                assert cmd in command_calls, f"Command '{cmd}' not found in help output"
