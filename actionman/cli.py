#!/usr/bin/env python3

"""Command-line interface for ActionMan.

This module provides the command-line interface for the ActionMan build tool,
including argument parsing and command execution.
"""

import sys
import argparse
from typing import List, Dict, Optional, Callable, Tuple

from actionman.core import BuildManager


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args (List[str]): Command line arguments

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="ActionMan - Build and run management tool", add_help=False
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="help",
        help="Command to execute (clean, build, run, test, install, info, help)",
    )
    parser.add_argument("options", nargs="*", help="Options for the command")
    return parser.parse_args(args)


def extract_prefix(options: List[str]) -> Tuple[List[str], Optional[str]]:
    """Extract installation prefix from options.

    Args:
        options (List[str]): Command options

    Returns:
        Tuple[List[str], Optional[str]]: Updated options and prefix if found
    """
    prefix = None
    new_options = []

    for opt in options:
        if opt.startswith("--prefix="):
            prefix = opt.split("=", 1)[1]
        else:
            new_options.append(opt)

    return new_options, prefix


def handle_build_command(manager: BuildManager, options: List[str]) -> None:
    """Handle the build command with its options.

    Args:
        manager (BuildManager): The build manager instance
        options (List[str]): Command options
    """
    if options and options[0] == "all":
        manager.build_all()
    else:
        build_type = options[0] if options else "debug"
        manager.build(build_type)


def handle_run_command(manager: BuildManager, options: List[str]) -> None:
    """Handle the run command with its options.

    Args:
        manager (BuildManager): The build manager instance
        options (List[str]): Command options
    """
    if not options:
        manager.run("debug", [])
        return

    if options[0] in manager.CMAKE_BUILD_MAP:
        build_type = options[0]
        execution_params = options[1:]
    else:
        build_type = "debug"
        execution_params = options

    manager.run(build_type, execution_params)


def handle_test_command(manager: BuildManager, options: List[str]) -> None:
    """Handle the test command with its options.

    Args:
        manager (BuildManager): The build manager instance
        options (List[str]): Command options
    """
    if options and options[0] == "all":
        manager.test_all()
        return

    build_type = "debug"
    test_filter = ""

    if options:
        if options[0] in manager.CMAKE_BUILD_MAP:
            build_type = options[0]
            if len(options) > 1:
                test_filter = options[1]
        else:
            test_filter = options[0]

    manager.test(build_type, test_filter)


def handle_install_command(manager: BuildManager, options: List[str]) -> None:
    """Handle the install command with its options.

    Args:
        manager (BuildManager): The build manager instance
        options (List[str]): Command options
    """
    options, prefix = extract_prefix(options)
    build_type = (
        options[0] if options and options[0] in manager.CMAKE_BUILD_MAP else "debug"
    )
    manager.install(build_type, prefix)


def main(args: List[str] = None) -> None:
    """Execute the command based on parsed arguments.

    Args:
        args (List[str], optional): Command line arguments. Defaults to None.
    """
    if args is None:
        args = sys.argv[1:]

    parsed_args = parse_args(args)
    command = parsed_args.command.lower()
    options = parsed_args.options

    manager = BuildManager()

    # Command dispatch dictionary
    commands: Dict[str, Callable] = {
        "help": lambda: manager.print_help(),
        "clean": lambda: manager.clean(),
        "build": lambda: handle_build_command(manager, options),
        "run": lambda: handle_run_command(manager, options),
        "test": lambda: handle_test_command(manager, options),
        "install": lambda: handle_install_command(manager, options),
        "info": lambda: manager.system_info(),
    }

    # Execute the command if it exists, otherwise show help
    if command in commands:
        commands[command]()
    else:
        print(manager.colorize(f"Unknown command: {command}", "red"))
        manager.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(130)
