import json
import os
import sys
import ast
from pathlib import Path

# Define the base directory for the Ankimon source code
ANKIMON_SRC_DIR = Path(__file__).parent.parent / "src" / "Ankimon"

def test_settings_consistency():
    """
    Checks for consistency between setting_name.json, setting_description.json,
    and hierarchial_groups in settings_window.py.
    """
    setting_names_path = ANKIMON_SRC_DIR / "lang" / "setting_name.json"
    setting_descriptions_path = ANKIMON_SRC_DIR / "lang" / "setting_description.json"
    settings_window_path = ANKIMON_SRC_DIR / "pyobj" / "settings_window.py"

    assert setting_names_path.exists(), f"File not found: {setting_names_path}"
    assert setting_descriptions_path.exists(), f"File not found: {setting_descriptions_path}"
    assert settings_window_path.exists(), f"File not found: {settings_window_path}"

    with open(setting_names_path, "r", encoding="utf-8") as f:
        setting_names = json.load(f)

    with open(setting_descriptions_path, "r", encoding="utf-8") as f:
        setting_descriptions = json.load(f)

    # Extract hierarchial_groups from settings_window.py
    hierarchial_groups = {}
    with open(settings_window_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=settings_window_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "setup_ui":
                for sub_node in ast.walk(node):
                    if isinstance(sub_node, ast.Assign):
                        for target in sub_node.targets:
                            if isinstance(target, ast.Name) and target.id == "hierarchical_groups":
                                if isinstance(sub_node.value, ast.Dict):
                                    # Recursively parse the dictionary structure
                                    def parse_dict(dict_node):
                                        parsed = {}
                                        for k, v in zip(dict_node.keys, dict_node.values):
                                            if isinstance(k, ast.Constant):
                                                key_val = k.value
                                                if isinstance(v, ast.Dict):
                                                    parsed[key_val] = parse_dict(v)
                                                elif isinstance(v, ast.List):
                                                    parsed[key_val] = [item.value for item in v.elts if isinstance(item, ast.Constant)]
                                        return parsed
                                    hierarchial_groups = parse_dict(sub_node.value)
                                    break
                if hierarchial_groups:
                    break

    assert hierarchial_groups, "Could not find 'hierarchial_groups' in settings_window.py"

    # Check 1: Every key in setting_names must exist in setting_descriptions
    for key in setting_names.keys():
        assert key in setting_descriptions, f"Setting '{key}' in setting_name.json is missing from setting_description.json"

    # Check 2: Every friendly name in setting_names must exist in hierarchial_groups
    all_hierarchial_friendly_names = set()

    def extract_friendly_names(group_data):
        if isinstance(group_data, dict):
            if "settings" in group_data:
                for setting in group_data["settings"]:
                    all_hierarchial_friendly_names.add(setting)
            if "subgroups" in group_data:
                for subgroup_data in group_data["subgroups"].values():
                    extract_friendly_names(subgroup_data)

    for group_data in hierarchial_groups.values():
        extract_friendly_names(group_data)

    for key, friendly_name in setting_names.items():
        assert friendly_name in all_hierarchial_friendly_names, f"Friendly name '{friendly_name}' (key: '{key}') from setting_name.json is missing from hierarchial_groups in settings_window.py"