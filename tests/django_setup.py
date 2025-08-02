#!/usr/bin/env python
"""
Common Django setup for test scripts

This module provides common Django setup functionality for test scripts
located in subdirectories of the tests folder.
"""

import os
import sys
from pathlib import Path

def setup_django():
    """
    Setup Django environment for test scripts.
    This works regardless of the script's location within the tests directory.
    """
    # Get the project root directory (where manage.py is located)
    current_file = Path(__file__)
    project_root = current_file.parent.parent  # Go up from tests/ to project root
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_management_project.settings')
    
    # Setup Django
    import django
    django.setup()
    
    return project_root
