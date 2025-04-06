# ActionMan

ActionMan is a build and run management tool for C++ projects built with CMake. It provides a command-line interface for configuring, building, testing, and running C++ projects.

[![Version](https://img.shields.io/badge/version-0.2.2-blue.svg)](https://github.com/zer0cell/actionman)

## Features

- Configure, build, test, and run C++ projects built with CMake
- Support for multiple build types (debug, profile, release)
- Parallel builds using available CPU cores
- Colorized output for better readability
- System information display
- Cross-platform support (Windows, macOS, Linux)
- Specify working directory for build operations with `--cd` flag

## Installation

### From PyPI

```bash
pip install actionman
```

### From Source

1. Clone this repository
2. Install for development (with editable mode):
   ```bash
   pip install -e .
   ```

### As a Local Package

```bash
pip install .
```

## Usage

After installation, you can use the `actionman` command:

```bash
actionman <command> [options]
```

Or run directly from the repository:

```bash
python -m actionman.cli <command> [options]
```

### Global Options

- `--cd`, `-c`, `-C` - Specify working directory for build operations (default: current directory)
- `--help`, `-h` - Show help message
- `--version`, `-v` - Show program version

### Available Commands

- `clean` - Clean the build directory
- `build` - Build the project
  - `debug` - Build with debug symbols and no optimization (default)
  - `profile` - Build with debug symbols and full optimization
  - `release` - Build with no debug symbols and full optimization
  - `all` - Build all configurations
- `run` - Run the executable
  - `debug` - Run the debug build (default)
  - `profile` - Run the profile build
  - `release` - Run the release build
  - Additional arguments after the build type are passed to the executable
- `test` - Run tests
  - `debug` - Run tests for debug build (default)
  - `profile` - Run tests for profile build
  - `release` - Run tests for release build
  - `all` - Run tests for all configurations
  - Additional arguments can be used as test filters
- `install` - Install the built application
  - `debug` - Install debug build (default)
  - `profile` - Install profile build
  - `release` - Install release build
  - `--prefix=<path>` - Installation prefix
- `info` - Display system information


### Examples

```bash
# Build the release configuration
actionman build release

# Run the debug build with command-line arguments
actionman run debug --help

# Run tests for the profile build
actionman test profile

# Build in a specific directory
actionman build release --cd /path/to/project

# Clean the build directory in a specific location
actionman clean -c /path/to/project

# Install to a custom location
actionman install release --prefix=/usr/local

# Display system information
actionman info
```

## Building a Standalone Executable

To create a single-file executable, use the included build script:

```bash
python build.py
```

Or with options:

```bash
python build.py --clean --debug
```

The executable will be created in the `dist` directory.

## Development

For development, install the package in editable mode with development dependencies:

```bash
pip install -e .[dev]
```

## License

MIT License
