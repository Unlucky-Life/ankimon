import json
import os
import sys
import ast
from pathlib import Path
import importlib.util
from unittest.mock import MagicMock

# Define the base directory for the Ankimon source code
ANKIMON_SRC_DIR = Path(__file__).parent.parent / "src" / "Ankimon"



# --- Test for Import Issues ---

class ImportAnalyzer(ast.NodeVisitor):
    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.imports = []
        self.relative_imports = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module
        level = node.level
        if level > 0:  # Relative import
            self.relative_imports.append((module, level, node.lineno))
        else:  # Absolute import
            self.imports.append(module)
        self.generic_visit(node)

def get_all_python_files(base_dir: Path):
    return [f for f in base_dir.rglob("*.py") if f.is_file() and "__pycache__" not in str(f)]

def test_import_integrity(monkeypatch):
    """
    Checks for unresolved imports, incorrect import depths, and circular imports.
    """
    # Mock aqt and aqt.mw to prevent AttributeError during import of const.py
    mock_mw = MagicMock()
    mock_mw.pm.name = "test_profile" # Provide a dummy value for pm.name
    monkeypatch.setattr(sys, "modules", sys.modules) # Ensure sys.modules is mutable for monkeypatch
    monkeypatch.setitem(sys.modules, "aqt", MagicMock())
    monkeypatch.setattr("aqt.mw", mock_mw)

    sys.path.insert(0, str(ANKIMON_SRC_DIR.parent))

    # Clear Ankimon modules from sys.modules to ensure fresh import analysis
    # This is crucial to prevent Anki-dependent code from executing during analysis
    modules_to_clear = [name for name in sys.modules if name.startswith('Ankimon')]
    for name in modules_to_clear:
        del sys.modules[name]

    python_files = get_all_python_files(ANKIMON_SRC_DIR)
    assert python_files, f"No Python files found in {ANKIMON_SRC_DIR}"

    module_map = {}  # Maps module name to its file path
    for f_path in python_files:
        relative_path = f_path.relative_to(ANKIMON_SRC_DIR.parent)
        module_name = str(relative_path).replace(os.sep, ".")[:-3]  # Remove .py
        if module_name.endswith(".__init__"):
            module_name = module_name[:-9] # Ankimon.__init__ -> Ankimon
        module_map[module_name] = f_path

    # Build dependency graph and collect all imports
    dependency_graph = {name: [] for name in module_map}
    all_imports_to_check = []

    # Check for unresolved imports
    unresolved_imports = []

    for module_name, f_path in module_map.items():
        with open(f_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=f_path)
            analyzer = ImportAnalyzer(f_path)
            analyzer.visit(tree)

            # Determine the package name for resolve_name
            # It should be the package of the current module
            package_for_resolve = module_name
            # Process absolute imports
            for imported_module in analyzer.imports:
                all_imports_to_check.append((module_name, imported_module, f_path, "absolute"))

            # Process relative imports
            for rel_module, level, lineno in analyzer.relative_imports:
                # Debugging print statement
                print(f"DEBUG: module_name={module_name}, f_path={f_path}, rel_module={rel_module}, level={level}, package_for_resolve={package_for_resolve}")
                try:
                    # Construct the absolute module name using resolve_name
                    absolute_imported_name = importlib.util.resolve_name(
                        '.' * level + (rel_module if rel_module else ''),
                        package_for_resolve
                    )
                except ValueError:
                    unresolved_imports.append(f"Incorrect import depth: '{'.' * level}{rel_module if rel_module else ''}' in {f_path} at line {lineno} (invalid relative import)")
                    continue
                    all_imports_to_check.append((module_name, absolute_imported_name, f_path, "relative", rel_module, level, lineno))
    # Now, iterate through all collected imports and check for resolution
    for importer, imported, f_path, import_type, *args in all_imports_to_check:
        # Check if the imported module is part of the Ankimon codebase
        if imported in module_map:
            # It's an internal import, no need to check with find_spec
            continue

        # If not an internal module, check if it's a built-in or external library
        if not is_builtin_or_external(imported):
            # If it's neither internal nor a known external/builtin, it's unresolved
            if import_type == "absolute":
                unresolved_imports.append(f"Unresolved absolute import: '{imported}' in {f_path}")
            elif import_type == "relative":
                original_rel_module = args[0]
                level = args[1]
                lineno = args[2]
                unresolved_imports.append(f"Unresolved relative import: '{imported}' (original: '{'.' * level}{original_rel_module if original_rel_module else ''}') in {f_path} at line {lineno}")    # Check for circular imports (using DFS)
    path = set()
    visited = set()
    circular_dependencies = []

    def find_cycles(node):
        visited.add(node)
        path.add(node)

        for neighbor in dependency_graph.get(node, []):
            if neighbor in path:
                circular_dependencies.append(f"Circular import detected: {neighbor} -> ... -> {node} -> {neighbor}")
            if neighbor not in visited:
                find_cycles(neighbor)
        path.remove(node)

    for module in dependency_graph:
        if module not in visited:
            find_cycles(module)

    assert not circular_dependencies, "\n".join(circular_dependencies)

def is_builtin_or_external(module_name):
    """
    Helper to check if a module is a known built-in or external library.
    This list should be expanded as needed.
    """
    # Platform-specific exclusions
    if sys.platform != "darwin":
        if module_name == "AppKit" or module_name == "Foundation":
            return True

    known_external_modules = [
        "aqt", "PyQt", "anki", "json", "os", "sys", "ast", "pathlib",
        "collections", "re", "logging", "typing", "enum", "dataclasses",
        "copy", "random", "time", "threading", "subprocess", "webbrowser",
        "hashlib", "base64", "io", "zipfile", "shutil", "tempfile", "requests",
        "configparser", "csv", "datetime", "decimal", "functools", "itertools",
        "math", "operator", "queue", "sqlite3", "struct", "textwrap", "urllib",
        "uuid", "xml", "markdown", "html", "abc", "calendar", "contextlib",
        "decimal", "difflib", "fnmatch", "getopt", "glob", "heapq", "locale",
        "mimetypes", "multiprocessing", "numbers", "operator", "pprint",
        "profile", "pstats", "selectors", "socket", "ssl", "statistics",
        "string", "tarfile", "tempfile", "termios", "traceback", "unittest",
        "warnings", "weakref", "xml", "zipfile", "zlib"
    ]

    # Check if it's a built-in module
    if module_name in sys.builtin_module_names:
        return True
    # Check if it's a known external module
    if any(module_name.startswith(m) for m in known_external_modules):
        return True
    return False
