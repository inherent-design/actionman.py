#!/usr/bin/env python3

"""Core functionality for the ActionMan build tool.

This module contains the main functionality for configuring, building,
testing, and running C++ projects built with CMake.
"""

import os
import subprocess
import sys
import shutil
import time
import platform
from typing import List, Optional, Tuple

from .utils import colorize, print_separator as utils_print_separator


class BuildManager:
    """Manages the build process for C++ projects using CMake.

    This class provides methods for configuring, building, testing,
    and running C++ projects built with CMake.
    """

    # CMake build type mapping
    CMAKE_BUILD_MAP = {
        "debug": "Debug",
        "profile": "RelWithDebInfo",
        "release": "Release",
    }

    def __init__(self, cwd: Optional[str] = None):
        """Initialize the BuildManager.

        Args:
            cwd (Optional[str]): Current working directory. Defaults to os.getcwd().
        """
        self.cwd = cwd or os.getcwd()
        self.build_dir = os.path.join(self.cwd, "build")

    def colorize(self, text: str, color: str) -> str:
        """Add color to terminal text if supported.

        Args:
            text (str): Text to colorize
            color (str): Color name from COLORS dict

        Returns:
            str: Colorized text or original text if colors not supported
        """
        return colorize(text, color)

    def print_separator(self, message: str = "", color: str = "bold") -> None:
        """Print a separator line with an optional message.

        Args:
            message (str, optional): Message to display in the separator. Defaults to "".
            color (str, optional): Color for the message. Defaults to "bold".
        """
        utils_print_separator(message, color)

    def run_command(
        self, cmd: List[str], cwd: Optional[str] = None
    ) -> Tuple[int, str, str]:
        """Run a command and capture output.

        Args:
            cmd (List[str]): Command and arguments to run
            cwd (Optional[str]): Directory to run command in. Defaults to None.

        Returns:
            Tuple[int, str, str]: Return code, stdout, stderr
        """
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr

    def configure(self, build_type: str = "debug", flags: List[str] = []) -> None:
        """Configure the build environment using CMake.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            flags (List[str], optional): Additional CMake flags. Defaults to empty list.

        Raises:
            SystemExit: If configuration fails or build type is invalid
        """
        try:
            # Create build directory if it doesn't exist
            os.makedirs(self.build_dir, exist_ok=True)

            self.print_separator(f"BEGIN CONFIGURE ({build_type.upper()})", "cyan")

            # Determine generator based on platform
            generator = "Ninja"
            if shutil.which("ninja") is None:
                if os.name == "nt":
                    generator = "Visual Studio 17 2022"
                else:
                    generator = "Unix Makefiles"

            start_time = time.time()

            cmd = [
                "cmake",
                "-G",
                generator,
                "-S",
                ".",
                "-B",
                self.build_dir,
                f"-DCMAKE_BUILD_TYPE={self.CMAKE_BUILD_MAP[build_type]}",
            ] + flags

            print(f"Running: {' '.join(cmd)}")
            returncode, stdout, stderr = self.run_command(cmd)

            if stdout:
                print(stdout)
            if stderr:
                print(self.colorize(stderr, "red"))

            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)

            elapsed = time.time() - start_time
            self.print_separator(
                f"END CONFIGURE ({build_type.upper()}) - {elapsed:.2f}s", "green"
            )
        except subprocess.CalledProcessError as e:
            print(self.colorize(f"Configuration failed: {e}", "red"))
            sys.exit(1)
        except KeyError:
            print(self.colorize(f"Invalid build type: {build_type}", "red"))
            print(f"Available build types: {', '.join(self.CMAKE_BUILD_MAP.keys())}")
            sys.exit(1)

    def build(self, build_type: str = "debug", flags: List[str] = []) -> None:
        """Build the specified configuration.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            flags (List[str], optional): Additional CMake flags. Defaults to empty list.

        Raises:
            SystemExit: If build fails or build type is invalid
        """
        try:
            self.configure(build_type, flags)

            self.print_separator(f"BEGIN BUILD OUTPUT ({build_type.upper()})", "cyan")
            start_time = time.time()

            # Determine number of CPU cores for parallel builds
            cpu_count = os.cpu_count() or 4

            cmd = ["cmake", "--build", ".", f"-j{cpu_count}"]
            print(f"Running: {' '.join(cmd)}")

            returncode, stdout, stderr = self.run_command(cmd, self.build_dir)

            if stdout:
                print(stdout)
            if stderr and returncode != 0:
                print(self.colorize(stderr, "red"))

            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)

            elapsed = time.time() - start_time
            self.print_separator(
                f"END BUILD OUTPUT ({build_type.upper()}) - {elapsed:.2f}s", "green"
            )
        except subprocess.CalledProcessError as e:
            print(self.colorize(f"{build_type.capitalize()} build failed: {e}", "red"))
            sys.exit(1)
        except KeyError:
            print(self.colorize(f"Invalid build type: {build_type}", "red"))
            print(f"Available build types: {', '.join(self.CMAKE_BUILD_MAP.keys())}")
            sys.exit(1)

    def run(self, build_type: str = "debug", execution_params: List[str] = []) -> None:
        """Run the executable for the specified build type.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            execution_params (List[str], optional): Parameters to pass to the executable. Defaults to empty list.

        Raises:
            SystemExit: If execution fails or build type is invalid
        """
        try:
            executable = os.path.join(self.build_dir, "bin", "Fabric")
            if os.name == "nt":
                executable += ".exe"

            if not os.path.exists(executable):
                print(f"Executable not found. Building {build_type}...")
                self.build(build_type)

            print(
                self.colorize(f"Running with arguments: {execution_params}", "cyan")
                if execution_params
                else self.colorize("Running without arguments", "cyan")
            )

            self.print_separator(f"BEGIN FABRIC OUTPUT ({build_type.upper()})", "cyan")
            start_time = time.time()

            cmd = [executable] + execution_params
            returncode, stdout, stderr = self.run_command(cmd)

            if stdout:
                print(stdout)
            if stderr:
                print(self.colorize(stderr, "red" if returncode != 0 else "yellow"))

            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)

            elapsed = time.time() - start_time
            self.print_separator(
                f"END FABRIC OUTPUT ({build_type.upper()}) - {elapsed:.2f}s", "green"
            )
        except subprocess.CalledProcessError as e:
            print(self.colorize(f"Execution failed: {e}", "red"))
            sys.exit(1)
        except KeyError:
            print(self.colorize(f"Invalid build type: {build_type}", "red"))
            print(f"Available build types: {', '.join(self.CMAKE_BUILD_MAP.keys())}")
            sys.exit(1)

    def clean_directory(self, directory: str) -> None:
        """Remove all files and subdirectories in the specified directory.

        Args:
            directory (str): Directory to clean
        """
        if not os.path.exists(directory):
            print(f"Directory {directory} does not exist. Nothing to clean.")
            return

        try:
            print(f"Cleaning {os.path.basename(directory)} directory...")
            shutil.rmtree(directory, ignore_errors=True)
            print(
                self.colorize(
                    f"Cleaned {os.path.basename(directory)} directory.", "green"
                )
            )
        except Exception as e:
            print(
                self.colorize(
                    f"An error occurred during cleaning {os.path.basename(directory)}: {e}",
                    "red",
                )
            )

    def clean(self) -> None:
        """Clean the build directory."""
        self.clean_directory(self.build_dir)

    def build_all(self) -> None:
        """Build all configurations (debug, profile, release)."""
        success = True
        results = []

        for build_type in self.CMAKE_BUILD_MAP.keys():
            print(f"\nBuilding {build_type} configuration...")
            start_time = time.time()
            try:
                self.build(build_type)
                elapsed = time.time() - start_time
                results.append((build_type, True, elapsed))
            except SystemExit:
                elapsed = time.time() - start_time
                results.append((build_type, False, elapsed))
                success = False

        # Print summary
        self.print_separator("BUILD SUMMARY", "bold")
        for build_type, result, elapsed in results:
            status = (
                self.colorize("SUCCESS", "green")
                if result
                else self.colorize("FAILED", "red")
            )
            print(f"{build_type.ljust(10)}: {status} ({elapsed:.2f}s)")

        if not success:
            sys.exit(1)

    def test(self, build_type: str = "debug", test_filter: str = "") -> None:
        """Run tests for the specified build type.

        Args:
            build_type (str, optional): Build type (debug, profile, release). Defaults to "debug".
            test_filter (str, optional): Filter to run specific tests. Defaults to "".

        Raises:
            SystemExit: If tests fail or build type is invalid
        """
        try:
            # Ensure the build exists
            if not os.path.exists(self.build_dir):
                print(f"Build directory not found. Building {build_type}...")
                self.build(build_type)

            self.print_separator(f"BEGIN TEST OUTPUT ({build_type.upper()})", "cyan")
            start_time = time.time()

            cmd = ["ctest", "--output-on-failure"]
            if test_filter:
                cmd.extend(["-R", test_filter])

            print(f"Running: {' '.join(cmd)}")
            returncode, stdout, stderr = self.run_command(cmd, self.build_dir)

            if stdout:
                print(stdout)
            if stderr:
                print(self.colorize(stderr, "red" if returncode != 0 else "yellow"))

            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)

            elapsed = time.time() - start_time
            self.print_separator(
                f"END TEST OUTPUT ({build_type.upper()}) - {elapsed:.2f}s", "green"
            )
        except subprocess.CalledProcessError as e:
            print(self.colorize(f"Tests failed: {e}", "red"))
            sys.exit(1)
        except KeyError:
            print(self.colorize(f"Invalid build type: {build_type}", "red"))
            print(f"Available build types: {', '.join(self.CMAKE_BUILD_MAP.keys())}")
            sys.exit(1)

    def test_all(self) -> None:
        """Run tests for all configurations."""
        success = True
        results = []

        for build_type in self.CMAKE_BUILD_MAP.keys():
            print(f"\nTesting {build_type} configuration...")
            start_time = time.time()
            try:
                self.test(build_type)
                elapsed = time.time() - start_time
                results.append((build_type, True, elapsed))
            except SystemExit:
                elapsed = time.time() - start_time
                results.append((build_type, False, elapsed))
                success = False

        # Print summary
        self.print_separator("TEST SUMMARY", "bold")
        for build_type, result, elapsed in results:
            status = (
                self.colorize("SUCCESS", "green")
                if result
                else self.colorize("FAILED", "red")
            )
            print(f"{build_type.ljust(10)}: {status} ({elapsed:.2f}s)")

        if not success:
            sys.exit(1)

    def install(self, build_type: str = "debug", prefix: Optional[str] = None) -> None:
        """Install the built application.

        Args:
            build_type (str, optional): Build type to install. Defaults to "debug".
            prefix (Optional[str], optional): Installation prefix. Defaults to None.

        Raises:
            SystemExit: If installation fails
        """
        try:
            # Ensure the build exists
            if not os.path.exists(self.build_dir):
                print(f"Build directory not found. Building {build_type}...")
                self.build(build_type)

            self.print_separator(f"BEGIN INSTALL ({build_type.upper()})", "cyan")
            start_time = time.time()

            cmd = ["cmake", "--install", "."]
            if prefix:
                cmd.extend(["--prefix", prefix])

            print(f"Running: {' '.join(cmd)}")
            returncode, stdout, stderr = self.run_command(cmd, self.build_dir)

            if stdout:
                print(stdout)
            if stderr:
                print(self.colorize(stderr, "red" if returncode != 0 else "yellow"))

            if returncode != 0:
                raise subprocess.CalledProcessError(returncode, cmd)

            elapsed = time.time() - start_time
            self.print_separator(
                f"END INSTALL ({build_type.upper()}) - {elapsed:.2f}s", "green"
            )
        except subprocess.CalledProcessError as e:
            print(self.colorize(f"Installation failed: {e}", "red"))
            sys.exit(1)
        except KeyError:
            print(self.colorize(f"Invalid build type: {build_type}", "red"))
            print(f"Available build types: {', '.join(self.CMAKE_BUILD_MAP.keys())}")
            sys.exit(1)

    def system_info(self) -> None:
        """Display system information relevant to the build."""
        self.print_separator("SYSTEM INFORMATION", "cyan")

        # Platform info
        print(f"OS: {platform.system()} {platform.release()}")
        print(f"Architecture: {platform.machine()}")
        print(f"Python: {platform.python_version()}")

        # Check for required tools
        tools = {
            "CMake": "cmake --version",
            "Ninja": "ninja --version",
            "C++ Compiler": "c++ --version",
        }

        print("\nBuild Tools:")
        for tool, cmd in tools.items():
            try:
                returncode, stdout, stderr = self.run_command(cmd.split())
                version = stdout.split("\n")[0] if stdout else "Unknown version"
                if returncode == 0:
                    print(f"  {tool}: {version}")
                else:
                    print(f"  {tool}: {self.colorize('Not found', 'yellow')}")
            except Exception:
                print(f"  {tool}: {self.colorize('Not found', 'yellow')}")

        # CPU info
        cpu_count = os.cpu_count() or 0
        print(f"\nCPU Cores: {cpu_count}")

        self.print_separator()

    def print_help(self) -> None:
        """Print the help message with available commands."""
        print(self.colorize("Fabric Engine - ActionMan Build Tool", "bold"))
        print("\nUsage: actionman <command> [options]")
        print("")
        print(self.colorize("Available commands:", "bold"))

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
            ("help", "Show this help message"),
        ]

        # Find the longest command to align descriptions
        max_cmd_len = max(len(cmd) for cmd, _ in commands)

        # Print commands with aligned descriptions
        for cmd, desc in commands:
            print(f"  {cmd.ljust(max_cmd_len + 4)}{desc}")

        print("")
        print(self.colorize("Examples:", "bold"))
        print("  actionman build release    # Build release configuration")
        print("  actionman run debug --help # Run debug build with --help flag")
        print("  actionman test profile     # Run tests for profile build")
