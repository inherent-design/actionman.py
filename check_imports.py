#!/usr/bin/env python3

import sys
print("Python path:")
for path in sys.path:
    print(f"  - {path}")

try:
    import actionman
    print("\nactionman imported successfully")
    print(f"Version: {actionman.__version__}")
    
    # Check if parse_args is properly exposed
    try:
        from actionman.cli import parse_args
        print("parse_args imported successfully from actionman.cli")
    except ImportError as e:
        print(f"Error importing parse_args: {e}")
        
except ImportError as e:
    print(f"\nError importing actionman: {e}")