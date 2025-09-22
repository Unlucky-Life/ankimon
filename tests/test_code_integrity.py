import pytest
import os
import sys
import json
import ast
import importlib.util
import platform
from unittest.mock import MagicMock, patch

# Define ANKIMON_ROOT_DIR and ANKIMON_SRC_PARENT_DIR first
ANKIMON_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) # /var/home/uwu/Documents/ankimon
ANKIMON_SRC_PARENT_DIR = os.path.join(ANKIMON_ROOT_DIR, "src") # /var/home/uwu/Documents/ankimon/src

# ANKIMON_SRC_DIR is still needed for globbing python files and for Ankimon mock
ANKIMON_SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src", "Ankimon"))

# Add the parent directory of ANKIMON_SRC_DIR (which is 'src') to sys.path
# This makes 'Ankimon' a top-level package
sys.path.insert(0, ANKIMON_SRC_PARENT_DIR)

# Store the original find_spec before patching
_original_find_spec = importlib.util.find_spec
