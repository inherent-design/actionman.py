#!/usr/bin/env python3

"""Command-line interface for ActionMan.

This module provides the command-line interface for the ActionMan build tool,
including argument parsing and command execution.
"""

import sys
import argparse
import os
from typing import List, Dict, Optional, Callable, Tuple

from actionman.core import BuildManager
from actionman.utils import CMAKE_BUILD_MAP


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

    if options[0] in CMAKE_BUILD_MAP:
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
        if options[0] in CMAKE_BUILD_MAP:
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
    build_type = options[0] if options and options[0] in CMAKE_BUILD_MAP else "debug"
    manager.install(build_type, prefix)


def main(args: List[str] = None) -> None:
    """Execute the command based on parsed arguments.

    Args:
        args (List[str], optional): Command line arguments. Defaults to None.
    """
    if args is None:
        args = sys.argv[1:]

    # Create a temporary manager for help and version functions
    temp_manager = BuildManager(os.getcwd())

    # Custom help formatter to use our detailed help message
    class CustomHelpFormatter(argparse.HelpFormatter):
        def __init__(self, prog):
            super().__init__(prog, max_help_position=40, width=80)

        def format_help(self):
            # Capture the detailed help message
            import io
            from contextlib import redirect_stdout

            f = io.StringIO()
            with redirect_stdout(f):
                temp_manager.print_help()
            return f.getvalue()

    # Create parser with custom formatter
    parser = argparse.ArgumentParser(
        description="ActionMan - Build and run management tool",
        formatter_class=CustomHelpFormatter,
        add_help=False,
    )

    # Add help argument with both long and short forms
    parser.add_argument(
        "--help", "-h", action="help", help="Show this help message and exit"
    )

    # Add version argument with both long and short forms
    from actionman import __version__

    # Custom version action that prints only the version
    class VersionAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            print(f"ActionMan v{__version__}")
            sys.exit(0)

    parser.add_argument(
        "--version",
        "-v",
        action=VersionAction,
        nargs=0,
        help="Show version information",
    )

    parser.add_argument(
        "command",
        nargs="?",
        help="Command to execute (clean, build, run, test, install, info)",
    )
    parser.add_argument(
        "--cd",
        "-c",
        "-C",
        dest="cwd",
        help="Specify working directory for build operations",
        default=os.getcwd(),
    )
    parser.add_argument("options", nargs="*", help="Options for the command")

    # If no arguments provided, show help and exit
    if len(args) == 0:
        parser.print_help()
        return

    parsed_args = parser.parse_args(args)

    # If no command provided, show help and exit
    if parsed_args.command is None:
        parser.print_help()
        return

    command = parsed_args.command.lower()
    options = parsed_args.options

    manager = BuildManager(parsed_args.cwd)

    # Command dispatch dictionary
    commands: Dict[str, Callable] = {
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
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(130)
