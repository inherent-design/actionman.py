# Virtual Environment Usage

## Overview

ActionMan now uses a virtual environment to isolate its Python dependencies from the global Python installation. This helps prevent conflicts between different Python projects and ensures consistent behavior across different systems.

## How It Works

1. When you run `build.py` or `setup.py`, the script will check if it's running inside a virtual environment using the `ensure_virtualenv()` function in `actionman/utils.py`.
2. If not, it will automatically create a virtual environment named `env` in the project's root directory.
3. All pip installations will be performed within this virtual environment.
4. This functionality is centralized in a common utility function to ensure consistent behavior across the project.

## Manual Usage

If you want to manually activate the virtual environment:

### On Unix/macOS

```bash
source env/bin/activate
```

### On Windows

```cmd
env\Scripts\activate
```

After activation, you can run Python commands directly within the virtual environment.

## Deactivation

To exit the virtual environment, simply run:

```bash
deactivate
```

## Troubleshooting

If you encounter issues with the virtual environment:

1. Delete the `env` directory
2. Run `build.py` or `setup.py` again to recreate it

This will create a fresh virtual environment with all the necessary dependencies.
