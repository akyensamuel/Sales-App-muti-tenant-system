#!/usr/bin/env python
"""
Test Runner for Sales Management Project

This script provides an easy way to run various types of tests and utilities.
Usage:
    python run_tests.py [test_type]
    
Test types:
    - all: Run all Django unit tests
    - integration: Run integration tests
    - debug: Run debug scripts
    - utils: Show available utilities
"""

import os
import sys
import subprocess
from pathlib import Path

def run_django_tests():
    """Run all Django unit tests"""
    print("Running Django unit tests...")
    subprocess.run([sys.executable, "manage.py", "test"], cwd=Path(__file__).parent)

def run_integration_tests():
    """Run integration tests"""
    print("Running integration tests...")
    integration_dir = Path(__file__).parent / "tests" / "integration"
    
    for test_file in integration_dir.glob("*.py"):
        if test_file.name != "__init__.py":
            print(f"Running {test_file.name}...")
            subprocess.run([sys.executable, str(test_file)])

def show_debug_scripts():
    """Show available debug scripts"""
    print("Available debug scripts:")
    debug_dir = Path(__file__).parent / "tests" / "debug"
    
    for script in debug_dir.glob("*.py"):
        if script.name != "__init__.py":
            print(f"  - {script.name}")
    
    print("\nTo run a debug script:")
    print("python tests/debug/[script_name]")

def show_utilities():
    """Show available utility scripts"""
    print("Available utility scripts:")
    utils_dir = Path(__file__).parent / "tests" / "utils"
    
    for script in utils_dir.glob("*.py"):
        if script.name != "__init__.py":
            print(f"  - {script.name}")
    
    print("\nTo run a utility script:")
    print("python tests/utils/[script_name]")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    test_type = sys.argv[1].lower()
    
    if test_type == "all":
        run_django_tests()
    elif test_type == "integration":
        run_integration_tests()
    elif test_type == "debug":
        show_debug_scripts()
    elif test_type == "utils":
        show_utilities()
    else:
        print(f"Unknown test type: {test_type}")
        print(__doc__)

if __name__ == "__main__":
    main()
