import json
from ..resources import lang_path_de, lang_path_ch, lang_path_en, lang_path_fr, lang_path_jp, lang_path_sp, lang_path_kr, lang_path_it, lang_path_cz, lang_path_po

LANG_PATHS = {
    "de": lang_path_de,
    "ch": lang_path_ch,
    "en": lang_path_en,
    "fr": lang_path_fr,
    "jp": lang_path_jp,
    "sp": lang_path_sp,
    "kr": lang_path_kr,
    "it": lang_path_it,
    "cz": lang_path_cz,
    "po": lang_path_po
}

LANG_NUMBERS = {
    1: 'jp',
    2: 'jp',
    3: 'kr',
    4: 'ch',
    5: 'fr',
    6: 'de',
    7: 'sp',
    8: 'it',
    9: 'en',
    10: 'cz',
    11: 'jp',
    12: 'ch',
    13: 'po',
}

class Translator:
    def __init__(self, language):
        short_language = LANG_NUMBERS.get(int(language), 'en')
        self.filepath = LANG_PATHS.get(short_language, lang_path_en)
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            raise Exception(f"Translation file not found: {self.filepath}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON format in translation file: {self.filepath}")

    def translate(self, key, **kwargs):
        template = self.translations.get(key, None)
        if template is None:
            with open(lang_path_en, 'r', encoding='utf-8') as f:
                fallback_translations = json.load(f)
            template = fallback_translations.get(key, key)

        try:
            return template.format(**kwargs)
        except KeyError as e:
            missing_key = str(e).strip("'")
            raise Exception(f"Missing placeholder: {missing_key} in translation for key '{key}'")

