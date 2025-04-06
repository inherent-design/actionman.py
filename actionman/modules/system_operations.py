#!/usr/bin/env python3

"""
System operations for the ActionMan build tool.

This module contains functionality for displaying system information and help.
"""

import platform
import os

from .. import __version__
from ..utils import colorize, print_separator, run_command


class SystemOperations:
    """Handles system operations for the ActionMan build tool.

    This class provides methods for displaying system information and help.
    """

    def system_info(self) -> None:
        """Display system information relevant to the build."""
        print_separator("SYSTEM INFORMATION", "cyan")

        # Platform info
        print(f"OS: {platform.system()} {platform.release()}")
        print(f"Architecture: {platform.machine()}")
        print(f"Python: {platform.python_version()}")

        # Check for required tools
        tools = {
            "CMake": "cmake --version",
            "Ninja": "ninja --version",
        }

        print("\nBuild Tools:")
        for tool, cmd in tools.items():
            try:
                returncode, stdout, stderr = run_command(cmd.split())
                version = stdout.split("\n")[0] if stdout else "Unknown version"
                if returncode == 0:
                    print(f"  {tool}: {version}")
                else:
                    print(f"  {tool}: {colorize('Not found', 'yellow')}")
            except Exception:
                print(f"  {tool}: {colorize('Not found', 'yellow')}")

        # CPU info
        cpu_count = os.cpu_count() or 0
        print(f"\nCPU Cores: {cpu_count}")

        print_separator()

    def print_help(self) -> None:
        """Print the help message with available commands."""
        print(colorize(f"ActionMan Build Tool v{__version__}", "bold"))
        print("\nUsage: actionman <command> [options]")
        print("")
        print(colorize("Global options:", "bold"))
        print("  --help                  Show this help message")
        print("  --version               Show version information")
        print(
            "  --cd, -c, -C <path>     Specify working directory for build operations"
        )
        print("")
        print(colorize("Available commands:", "bold"))

        # Command definitions with aligned descriptions
        commands = [
            ("clean", "Clean the build directory"),
            ("build", "Build the project"),
            ("  debug", "Build with debug symbols and no optimization (default)"),
            ("  profile", "Build with debug symbols and full optimization"),
            ("  release", "Build with no debug symbols and full optimization"),
            ("  all", "Build all configurations"),
            ("run", "Run the executable"),
            ("  debug", "Run the debug build (default)"),
            ("  profile", "Run the profile build"),
            ("  release", "Run the release build"),
            ("test", "Run tests"),
            ("  debug", "Run tests for debug build (default)"),
            ("  profile", "Run tests for profile build"),
            ("  release", "Run tests for release build"),
            ("  all", "Run tests for all configurations"),
            ("install", "Install the built application"),
            ("  debug", "Install debug build (default)"),
            ("  profile", "Install profile build"),
            ("  release", "Install release build"),
            ("  --prefix=<path>", "Installation prefix"),
            ("info", "Display system information"),
        ]

        # Find the longest command to align descriptions
        max_cmd_len = max(len(cmd) for cmd, _ in commands)

        # Print commands with aligned descriptions
        for cmd, desc in commands:
            print(f"  {cmd.ljust(max_cmd_len + 4)}{desc}")

        print("")
        print(colorize("Examples:", "bold"))
        print("  actionman build release    # Build release configuration")
        print("  actionman run debug --help # Run debug build with --help flag")
        print("  actionman test profile     # Run tests for profile build")
