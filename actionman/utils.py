#!/usr/bin/env python3

"""
Utility functions for ActionMan.

This module provides utility functions used across the ActionMan package.
"""

import os
import platform
from typing import Dict, List, Optional, Tuple, Callable
from functools import wraps
import sys
import subprocess


# CMake build type mapping
CMAKE_BUILD_MAP = {
    "debug": "Debug",
    "profile": "RelWithDebInfo",
    "release": "Release",
}


# ANSI color codes
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
}


def handle_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            print(colorize(f"Invalid build type: {e}", "red"))
            print(f"Available build types: {', '.join(CMAKE_BUILD_MAP.keys())}")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(colorize(f"Command failed: {e}", "red"))
            sys.exit(1)

    return wrapper


def colorize(text: str, color: str) -> str:
    """Add color to terminal text if supported.

    Args:
        text (str): Text to colorize
        color (str): Color name from COLORS dict

    Returns:
        str: Colorized text or original text if colors not supported
    """
    # Skip coloring on Windows unless in Windows Terminal
    if os.name == "nt" and "WT_SESSION" not in os.environ:
        return text
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def print_separator(message: str = "", color: str = "bold", width: int = 80) -> None:
    """Print a separator line with an optional message.

    Args:
        message (str, optional): Message to display in the separator. Defaults to "".
        color (str, optional): Color for the message. Defaults to "bold".
        width (int, optional): Width of the separator line. Defaults to 80.
    """
    if message:
        padding = (width - len(message) - 2) // 2
        print(
            "=" * padding
            + " "
            + colorize(message, color)
            + " "
            + "=" * (width - padding - len(message) - 2)
        )
    else:
        print("=" * width)


def get_system_info() -> Dict[str, str]:
    """Get system information.

    Returns:
        Dict[str, str]: Dictionary containing system information
    """
    info = {
        "os": f"{platform.system()} {platform.release()}",
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "cpu_count": str(os.cpu_count() or 0),
    }
    return info


def is_executable(path: str) -> bool:
    """Check if a file is executable.

    Args:
        path (str): Path to the file

    Returns:
        bool: True if the file is executable, False otherwise
    """
    return os.path.isfile(path) and os.access(path, os.X_OK)


def find_executable(name: str) -> Optional[str]:
    """Find an executable in the system PATH.

    Args:
        name (str): Name of the executable

    Returns:
        Optional[str]: Path to the executable if found, None otherwise
    """
    # On Windows, executables can have different extensions
    if platform.system() == "Windows":
        extensions = os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD").split(";")
    else:
        extensions = [""]  # No extensions on Unix-like systems

    # Check if the name already has a path
    if os.path.dirname(name):
        if is_executable(name):
            return name
        return None

    # Search in PATH
    for path in os.environ.get("PATH", "").split(os.pathsep):
        path = path.strip('"')
        for ext in extensions:
            executable = os.path.join(path, name + ext)
            if is_executable(executable):
                return executable

    return None


def ensure_dir_exists(directory: str) -> None:
    """Ensure a directory exists, creating it if necessary.

    Args:
        directory (str): Directory path to ensure exists
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def print_error(message: str) -> None:
    """Print an error message in red.

    Args:
        message (str): Error message to print
    """
    print(colorize(f"ERROR: {message}", "red"))


def print_success(message: str) -> None:
    """Print a success message in green.

    Args:
        message (str): Success message to print
    """
    print(colorize(f"SUCCESS: {message}", "green"))


def print_warning(message: str) -> None:
    """Print a warning message in yellow.

    Args:
        message (str): Warning message to print
    """
    print(colorize(f"WARNING: {message}", "yellow"))


def print_info(message: str) -> None:
    """Print an info message in blue.

    Args:
        message (str): Info message to print
    """
    print(colorize(f"INFO: {message}", "blue"))


def run_command(cmd: List[str], cwd: str = None) -> Tuple[int, str, str]:
    """Run a command and capture output.

    Args:
        cmd (List[str]): Command and arguments to run
        cwd (str, optional): Directory to run command in. Defaults to None.

    Returns:
        Tuple[int, str, str]: Return code, stdout, stderr
    """
    import subprocess

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=cwd
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr
