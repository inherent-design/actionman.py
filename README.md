# ActionMan

ActionMan is a build and run management tool for C++ projects built with CMake. It provides a command-line interface for configuring, building, testing, and running C++ projects.

## Features

- Configure, build, test, and run C++ projects built with CMake
- Support for multiple build types (debug, profile, release)
- Parallel builds using available CPU cores
- Colorized output for better readability
- System information display
- Cross-platform support (Windows, macOS, Linux)

## Installation

### From Source

1. Clone this repository
2. Install for development (with editable mode):
   ```
   pip install -e .
   ```

### As a Package

```
pip install .
```

## Usage

After installation, you can use the `actionman` command:

```
actionman <command> [options]
```

Or run directly from the repository:

```
python main.py <command> [options]
```

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
- `test` - Run tests
  - `debug` - Run tests for debug build (default)
  - `profile` - Run tests for profile build
  - `release` - Run tests for release build
  - `all` - Run tests for all configurations
- `install` - Install the built application
  - `debug` - Install debug build (default)
  - `profile` - Install profile build
  - `release` - Install release build
  - `--prefix=<path>` - Installation prefix
- `info` - Display system information
- `help` - Show help message

### Examples

```
actionman build release    # Build release configuration
actionman run debug --help # Run debug build with --help flag
actionman test profile     # Run tests for profile build
```

## Building a Standalone Executable

To create a single-file executable, use the included build script:

```
python build.py
```

Or with options:

```
python build.py --clean --debug
```

The executable will be created in the `dist` directory.

## Development

For development, install the package in editable mode with development dependencies:

```
pip install -e .[dev]
```
