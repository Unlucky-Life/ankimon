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

# --- Dynamic Import and Circular Dependency Tests ---

# List of modules to mock before importing Ankimon modules
# These are dependencies provided by the Anki environment
MOCK_MODULES = [
    'aqt',
    'aqt.main',
    'aqt.mw',
    'aqt.utils',
    'aqt.qt',
    'aqt.gui_hooks',
    'anki',
    'anki.hooks',
    'anki.consts',
    'anki.utils',
    'anki.collection',
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
]

# Mock the modules
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = MagicMock()

def get_all_ankimon_modules():
    """Discovers all Python modules within the Ankimon addon directory."""
    import Ankimon
    package = Ankimon
    prefix = package.__name__ + '.'
    
    module_names = []
    # pkgutil.walk_packages can handle packages and subpackages automatically
    for _, module_name, is_pkg in pkgutil.walk_packages(package.__path__, prefix):
        module_names.append(module_name)
        if is_pkg:
            # Also add the package itself, not just its contents
            # This ensures __init__.py files are processed
            module_names.append(module_name)
            
    # Deduplicate and return
    return sorted(list(set(module_names)))

ALL_MODULES = get_all_ankimon_modules()

@pytest.mark.parametrize("module_name", ALL_MODULES)
def test_module_imports_and_circular_dependencies(module_name):
    """
    Attempts to import each module to check for:
    1. Unresolved Imports: Raises ImportError if a module can't be found.
    2. Incorrect Import Depths: Relative imports that go too high will fail.
    3. Circular Imports: Python raises ImportError or AttributeError on circular dependencies.
    4. Syntax Errors: Invalid Python syntax will raise SyntaxError.
    """
    try:
        importlib.import_module(module_name)
    except Exception as e:
        pytest.fail(f"Failed to import module '{module_name}'. Error: {e.__class__.__name__}: {e}")


# --- Settings Consistency Test ---

def get_settings_keys_from_json(file_path):
    """Loads a JSON file and returns the set of its top-level keys."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(data.keys())

def get_setting_keys_from_hierarchical_groups(file_path):
    """
    Parses settings_window.py using AST to safely extract all setting keys
    from the 'hierarchical_groups' dictionary.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=file_path)

    keys = set()
    
    class HierarchicalGroupVisitor(ast.NodeVisitor):
        def visit_Assign(self, node):
            # Find the assignment to 'hierarchical_groups'
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'hierarchical_groups':
                if isinstance(node.value, ast.Dict):
                    self.parse_dict(node.value)
            self.generic_visit(node)

        def parse_dict(self, node):
            for key_node, value_node in zip(node.keys, node.values):
                if isinstance(value_node, ast.Dict):
                    # Check for a 'settings' list in the dictionary value
                    for sub_key_node, sub_value_node in zip(value_node.keys, value_node.values):
                        if isinstance(sub_key_node, ast.Constant) and sub_key_node.value == 'settings':
                            if isinstance(sub_value_node, (ast.List, ast.Tuple)):
                                for element in sub_value_node.elts:
                                    if isinstance(element, ast.Constant) and isinstance(element.value, str):
                                        keys.add(element.value)
                        # Recursively parse subgroups
                        elif isinstance(sub_key_node, ast.Constant) and sub_key_node.value == 'subgroups':
                             if isinstance(sub_value_node, ast.Dict):
                                self.parse_dict(sub_value_node)


    visitor = HierarchicalGroupVisitor()
    visitor.visit(tree)
    return keys

def test_settings_consistency():
    """
    Ensures that setting keys are consistent across setting_name.json,
    setting_description.json, and hierarchical_groups in settings_window.py.
    """
    base_path = os.path.join(ANKIMON_SRC_PARENT_DIR, 'Ankimon')
    setting_name_path = os.path.join(base_path, 'lang', 'setting_name.json')
    setting_description_path = os.path.join(base_path, 'lang', 'setting_description.json')
    settings_window_path = os.path.join(base_path, 'pyobj', 'settings_window.py')

    # 1. Load keys from JSON files
    name_keys = get_settings_keys_from_json(setting_name_path)
    description_keys = get_settings_keys_from_json(setting_description_path)

    # 2. Extract keys from settings_window.py
    hierarchical_keys = get_setting_keys_from_hierarchical_groups(settings_window_path)

    # 3. Perform assertions

    # Check for consistency between the two JSON files
    missing_in_description = name_keys - description_keys
    assert not missing_in_description, \
        f"Keys in setting_name.json are missing from setting_description.json: {missing_in_description}"

    missing_in_name = description_keys - name_keys
    assert not missing_in_name, \
        f"Keys in setting_description.json are missing from setting_name.json: {missing_in_name}"

    # Check for consistency with hierarchical_groups
    # Note: We check against name_keys, assuming it's the source of truth.
    # The previous check ensures it's consistent with description_keys.
    missing_in_hierarchical = name_keys - hierarchical_keys
    assert not missing_in_hierarchical, \
        f"Keys from setting JSON files are missing in settings_window.py: {missing_in_hierarchical}"

    missing_from_json = hierarchical_keys - name_keys
    assert not missing_from_json, \
        f"Keys from settings_window.py are missing from setting JSON files: {missing_from_json}"

