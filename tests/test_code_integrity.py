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

# --- Helper Functions for Import Checks ---

def get_python_files(directory):
    """Recursively get all Python files in a directory."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def check_imports(file_path):
    """Checks for unresolved imports and incorrect import depths in a given Python file."""
    unresolved_imports = []
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)

    # Determine the fully qualified module name for the current file
    relative_to_src_parent_dir = os.path.relpath(file_path, ANKIMON_SRC_PARENT_DIR)
    module_name_for_current_file = os.path.splitext(relative_to_src_parent_dir)[0].replace(os.sep, '.')
    if module_name_for_current_file.endswith(".__init__"):
        module_name_for_current_file = module_name_for_current_file[:-len(".__init__")]

    package_name_for_resolve_name = ".".join(module_name_for_current_file.split('.')[:-1])
    if not package_name_for_resolve_name and module_name_for_current_file == "Ankimon":
        package_name_for_resolve_name = "Ankimon"
    elif not package_name_for_resolve_name:
        package_name_for_resolve_name = module_name_for_current_file

    # Patch importlib.util.find_spec to control how external modules are resolved
    with patch('importlib.util.find_spec') as mock_find_spec:
        def custom_find_spec(name, package=None):
            # Handle platform-specific imports in playsound.py
            if "playsound.py" in file_path:
                if platform.system() == 'Darwin' and (name == 'AppKit' or name == 'Foundation'):
                    return MagicMock(spec=importlib.machinery.ModuleSpec, origin='mock')
                if platform.system() == 'Windows' and (name == 'ctypes' or name == 'windll' or name == 'wintypes'):
                    return MagicMock(spec=importlib.machinery.ModuleSpec, origin='mock')
                if platform.system() == 'Linux' and (name == 'gi' or name.startswith('gi.repository.')):
                    # For gi modules, return a mock ModuleSpec with a mock loader
                    mock_loader = MagicMock()
                    mock_spec = MagicMock(spec=importlib.machinery.ModuleSpec, origin='mock', loader=mock_loader)
                    return mock_spec
            
            # Ignore known external dependencies
            if name.startswith("aqt") or name.startswith("PyQt6") or name.startswith("gi") or name.startswith("showdown") or name == "constants" or name.startswith("anki"):
                return MagicMock(spec=importlib.machinery.ModuleSpec, origin='mock')
            
            # For other modules, use the original find_spec
            return _original_find_spec(name, package)

        mock_find_spec.side_effect = custom_find_spec

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name
                        if not importlib.util.find_spec(module_name):
                            unresolved_imports.append(f"Unresolved import: {module_name} in {file_path}")
                elif isinstance(node, ast.ImportFrom):
                    if node.level > 0: # Relative import
                        try:
                            resolved_module_name = importlib.util.resolve_name(f"{'.' * node.level}{node.module if node.module else ''}", package=package_name_for_resolve_name)
                            if not importlib.util.find_spec(resolved_module_name):
                                unresolved_imports.append(f"Unresolved relative import: {'.' * node.level}{node.module if node.module else ''} in {file_path} (resolved as {resolved_module_name})")
                        except ValueError as e:
                            unresolved_imports.append(f"Invalid relative import: {'.' * node.level}{node.module if node.module else ''} in {file_path}: {e}")
                        except ModuleNotFoundError as e:
                            unresolved_imports.append(f"Unresolved relative import: {'.' * node.level}{node.module if node.module else ''} in {file_path}: {e}")
                    else: # Absolute import
                        module_name = node.module
                        if not importlib.util.find_spec(module_name):
                            unresolved_imports.append(f"Unresolved import: {module_name} in {file_path}")
    return unresolved_imports

# --- Test Functions ---

def test_all_imports_are_resolvable():
    """
    Tests that all imports in the Ankimon codebase are resolvable.
    This helps catch unresolved imports and potentially incorrect import depths.
    """
    python_files = get_python_files(ANKIMON_SRC_DIR)
    all_unresolved = []
    for file_path in python_files:
        all_unresolved.extend(check_imports(file_path))
    
    assert not all_unresolved, "\n".join(all_unresolved)

def test_settings_consistency():
    """
    Checks for consistency between setting_name.json, setting_description.json,
    and the hierarchical_groups in settings_window.py.
    """
    settings_name_path = os.path.join(ANKIMON_SRC_DIR, "lang", "setting_name.json")
    settings_description_path = os.path.join(ANKIMON_SRC_DIR, "lang", "setting_description.json")
    settings_window_path = os.path.join(ANKIMON_SRC_DIR, "pyobj", "settings_window.py")

    # Load setting_name.json
    with open(settings_name_path, "r", encoding="utf-8") as f:
        setting_names = json.load(f)

    # Load setting_description.json
    with open(settings_description_path, "r", encoding="utf-8") as f:
        setting_descriptions = json.load(f)

    # Extract hierarchical_groups from settings_window.py using AST
    hierarchical_groups = {}
    with open(settings_window_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=settings_window_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "hierarchical_groups":
                    try:
                        hierarchical_groups = ast.literal_eval(node.value)
                    except (ValueError, SyntaxError) as e:
                        pytest.fail(f"Could not parse hierarchical_groups in {settings_window_path}: {e}")
                    break
        if not hierarchical_groups:
            pytest.fail(f"Could not find 'hierarchical_groups' assignment in {settings_window_path}")

    # Check 1: All keys in setting_names must exist in setting_descriptions
    missing_descriptions = [key for key in setting_names if key not in setting_descriptions]
    assert not missing_descriptions, f"Keys in setting_name.json missing from setting_description.json: {missing_descriptions}"

    # Check 2: All keys in setting_descriptions must exist in setting_names
    missing_names = [key for key in setting_descriptions if key not in setting_names]
    assert not missing_names, f"Keys in setting_description.json missing from setting_name.json: {missing_names}"

    # Check 3 & 4: Consistency between friendly names in hierarchical_groups and values in setting_name.json
    all_friendly_names_in_groups = set()

    def extract_friendly_names(group_data):
        if "settings" in group_data:
            for setting_name in group_data["settings"]:
                all_friendly_names_in_groups.add(setting_name)
        if "subgroups" in group_data:
            for subgroup_data in group_data["subgroups"].values():
                extract_friendly_names(subgroup_data)

    for l1_data in hierarchical_groups.values():
        extract_friendly_names(l1_data)
    
    all_setting_names_values = set(setting_names.values())

    # Check if all friendly names in hierarchical_groups are present as values in setting_name.json
    missing_in_setting_names_values = [name for name in all_friendly_names_in_groups if name not in all_setting_names_values]
    assert not missing_in_setting_names_values, f"Friendly names in hierarchical_groups (settings_window.py) not found as values in setting_name.json: {missing_in_setting_names_values}"

    # Check if all values in setting_name.json are present as friendly names in hierarchical_groups
    missing_from_groups = [name for name in all_setting_names_values if name not in all_friendly_names_in_groups]
    assert not missing_from_groups, f"Setting names (values from setting_name.json) not found in hierarchical_groups (settings_window.py): {missing_from_groups}"