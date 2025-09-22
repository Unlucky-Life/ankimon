# Ankimon Integrity Tests

This directory contains a suite of tests designed to check the integrity of the Ankimon codebase, focusing on common issues that can arise during development and deployment, especially in a complex environment like Anki.

## Prerequisites

To run these tests, you need:

1.  **Python 3.x**
2.  **`pip`** (Python package installer)
3.  **`pytest`**: A Python testing framework.
4.  **An Anki environment with `aqt` available**: These tests assume that `aqt` and other Anki-specific modules are resolvable by the Python interpreter. This is typically achieved by running the tests within a virtual environment that has access to Anki's Python site-packages, or by configuring `PYTHONPATH` appropriately.

## Setup

It is highly recommended to run these tests within a virtual environment to manage dependencies.

1.  **Navigate to the project root:**
    ```bash
    cd ~/Documents/ankimon
    ```

2.  **Create a virtual environment (if you don't have one configured for Anki):**
    ```bash
    python3 -m venv venv_ankimon_tests
    ```

3.  **Activate the virtual environment:**
    *   On Linux/macOS:
        ```bash
        source venv_ankimon_tests/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv_ankimon_tests\Scripts\activate
        ```

4.  **Install `pytest`:**
    ```bash
    pip install pytest
    ```

5.  **Ensure Anki's Python environment is accessible:**
    This is the most critical step for import resolution. The exact method depends on your Anki installation and how you've set up your development environment. Common approaches include:
    *   **Symlinking/Copying Anki's site-packages:** If you have a portable Anki installation or know the location of its `site-packages`, you might symlink or copy them into your `venv_ankimon_tests`.
    *   **Setting `PYTHONPATH`:** You can set the `PYTHONPATH` environment variable to include the directory where Anki's Python modules (like `aqt`) are located. For example:
        ```bash
        export PYTHONPATH="/path/to/anki/site-packages:$PYTHONPATH"
        ```
        (Replace `/path/to/anki/site-packages` with the actual path).
    *   **Using Anki's Python interpreter directly:** If you can identify the Python interpreter used by Anki, you might configure your virtual environment to use that interpreter, or simply run `pytest` using that interpreter directly.

    **Note:** The `test_import_integrity` test relies on the Python interpreter being able to resolve `aqt` and other Anki-specific imports. If these are not resolvable, the test will report them as "unresolved imports."

## Running the Tests

Once your virtual environment is set up and activated, and Anki's Python environment is accessible, you can run the tests:

1.  **Navigate to the project root (if not already there):**
    ```bash
    cd /var/home/uwu/Documents/ankimon
    ```

2.  **Run `pytest`:**
    ```bash
    pytest tests/test_ankimon_integrity.py
    ```

    To run all tests in the `tests/` directory:
    ```bash
    pytest tests/
    ```

## Test Descriptions

*   **`check_lang_placeholders.py`**:
    *   Verifies consistency of placeholders (e.g., `{placeholder}`) across all language JSON files in `src/Ankimon/lang/`, using `en_text.json` as the reference. It checks for missing keys and mismatched placeholders between language files.

*   **`test_settings_consistency.py`**: (Moved from `test_ankimon_integrity.py`)
    *   Checks if every key in `src/Ankimon/lang/setting_name.json` also exists in `src/Ankimon/lang/setting_description.json`.
    *   Checks if every key in `src/Ankimon/lang/setting_name.json` is present within the `hierarchical_groups` structure defined in `src/Ankimon/pyobj/settings_window.py`. This check is case-sensitive and accounts for the nested structure of `hierarchical_groups`.

*   **`test_import_integrity`**:
    *   **Unresolved Imports**: Scans all Python files in `src/Ankimon/` and identifies any imports (both absolute and relative) that cannot be resolved by the current Python environment. This includes both internal Ankimon modules and external libraries.
    *   **Incorrect Import Depths**: Analyzes relative imports (e.g., `from . import ...`) to ensure they correctly point to an existing module within the Ankimon project structure.
    *   **Circular Imports**: Detects any circular dependencies between modules within the `src/Ankimon/` directory.

*   **`test_addon_integrity.py`**: Contains additional tests related to addon integrity, including module import checks and settings consistency. Note that the primary and most robust import and settings consistency checks are now located in `test_ankimon_integrity.py` and `test_settings_consistency.py` respectively.
*   **`test_code_integrity.py`**: Contains further code integrity checks. Similar to `test_addon_integrity.py`, some of its functionalities might overlap with the more refined tests in `test_ankimon_integrity.py` and `test_settings_consistency.py`.
