import os
import sys
import importlib
import pkgutil
import json
import ast
from unittest.mock import patch, MagicMock
import pytest

# Add the 'src' directory to the Python path to allow for absolute imports of Ankimon
ANKIMON_SRC_PARENT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if ANKIMON_SRC_PARENT_DIR not in sys.path:
    sys.path.insert(0, ANKIMON_SRC_PARENT_DIR)






