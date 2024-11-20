import json
import os
from aqt import mw
from aqt.utils import showInfo
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtWidgets import QRadioButton, QHBoxLayout, QMainWindow, QScrollArea

class Settings:
    def __init__(self):
        self.config = self.load_config()

    def get_description(self, key):
        return self.descriptions.get(key, "No description available.")

    def load_config(self):
        config = mw.addonManager.getConfig(__name__) or {}
        if not config:
            config = {
                "battle.dmg_in_reviewer": True,
                "battle.automatic_battle": 0,
                "battle.cards_per_round": 2,
                "controls.pokemon_buttons": True,
                "controls.defeat_key": "5",
                "controls.catch_key": "6",
                "controls.key_for_opening_closing_ankimon": "N",
                "gui.animate_time": True,
                "gui.gif_in_collection": True,
                "gui.styling_in_reviewer": True,
                "gui.hp_bar_config": True,
                "gui.pop_up_dialog_message_on_defeat": False,
                "gui.review_hp_bar_thickness": 2,
                "gui.reviewer_image_gif": False,
                "gui.reviewer_text_message_box": True,
                "gui.reviewer_text_message_box_time": 3,
                "gui.show_mainpkmn_in_reviewer": 1,
                "gui.view_main_front": True,
                "gui.xp_bar_config": True,
                "gui.xp_bar_location": 2,
                "audio.sound_effects": False,
                "audio.sounds": True,
                "audio.battle_sounds": False,
                "misc.gen1": True,
                "misc.gen2": True,
                "misc.gen3": True,
                "misc.gen4": True,
                "misc.gen5": True,
                "misc.gen6": True,
                "misc.gen7": False,
                "misc.gen8": False,
                "misc.gen9": False,
                "misc.remove_level_cap": False,
                "misc.language": 9,
                "misc.ssh": True,
                "misc.YouShallNotPass_Ankimon_News": False,
                "trainer.name": "Ash",
                "trainer.cash": 0,
            }
            self.save_config(config)
        return config
    
    def save_config(self, config):
        mw.addonManager.writeConfig(__name__, config)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config(self.config)
        self.load_config()