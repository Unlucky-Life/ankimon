import json
from ..resources import lang_path_de, lang_path_ch, lang_path_en, lang_path_fr, lang_path_jp, lang_path_sp

LANG_PATHS = {
    "de": lang_path_de,
    "ch": lang_path_ch,
    "en": lang_path_en,
    "fr": lang_path_fr,
    "jp": lang_path_jp,
    "sp": lang_path_sp,
}

class Translator:
    def __init__(self, language="en"):
        filepath = LANG_PATHS.get(language, lang_path_en)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            raise Exception(f"Translation file not found: {filepath}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON format in translation file: {filepath}")

    def translate(self, key, **kwargs):
        template = self.translations.get(key, None)
        if template is None:
            # Fallback to English
            with open(lang_path_en, 'r', encoding='utf-8') as f:
                fallback_translations = json.load(f)
            template = fallback_translations.get(key, key)
        return template.format(**kwargs)
