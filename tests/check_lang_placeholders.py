import json
import re
from pathlib import Path

def find_placeholders(text):
    """Extracts all placeholders in the format {placeholder} from a string."""
    return set(re.findall(r"\{(.+?)\}", text))

def check_language_files():
    """
    Checks for placeholder consistency across language files, using en_text.json as the reference.
    """
    lang_dir = Path("src/Ankimon/lang")
    en_file = lang_dir / "en_text.json"
    
    if not en_file.exists():
        print(f"Error: Reference file not found at {en_file}")
        return

    with open(en_file, "r", encoding="utf-8") as f:
        en_data = json.load(f)

    en_placeholders = {key: find_placeholders(value) for key, value in en_data.items()}

    errors_found = False
    for lang_file in lang_dir.glob("*_text.json"):
        if lang_file == en_file:
            continue

        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                lang_data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {lang_file}")
            errors_found = True
            continue

        print(f"--- Checking {lang_file.name} ---")

        for key, expected_placeholders in en_placeholders.items():
            if key not in lang_data:
                print(f"  [ERROR] Missing key: '{key}'")
                errors_found = True
                continue

            actual_placeholders = find_placeholders(lang_data[key])

            if expected_placeholders != actual_placeholders:
                print(f"  [ERROR] Mismatch in key '{key}':")
                print(f"    Expected: {sorted(list(expected_placeholders))}")
                print(f"    Found:    {sorted(list(actual_placeholders))}")
                errors_found = True

    if not errors_found:
        print("All placeholders are consistent across all language files.")

if __name__ == "__main__":
    check_language_files()
