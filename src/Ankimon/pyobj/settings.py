import json
import os
from aqt import mw
from aqt.utils import showInfo
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtWidgets import QRadioButton, QHBoxLayout, QMainWindow, QScrollArea

class Settings:
    def __init__(self):
        self.config = self.load_config()
        self.compute_gui_config()

    def get_description(self, key):
        return self.descriptions.get(key, "No description available.")

    def load_config(self):
        config = mw.addonManager.getConfig(__name__) or {}
        if not config:
            #Card max time in Seconds
            config = {
                "battle.dmg_in_reviewer": True,
                "battle.automatic_battle": 0,
                "battle.cards_per_round": 2,
                "battle.card_max_time": 60,
                "battle.daily_average": 100,
                
                "controls.pokemon_buttons": True,
                "controls.defeat_key": "5",
                "controls.catch_key": "6",
                "controls.key_for_opening_closing_ankimon": "N",
                "controls.allow_to_choose_moves": False,
                
                "gui.animate_time": True,
                "gui.gif_in_collection": True,
                "gui.styling_in_reviewer": True,
                "gui.hp_bar_config": True,
                "gui.pop_up_dialog_message_on_defeat": False,
                "gui.review_hp_bar_thickness": 2 * 4,
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

    def compute_gui_config(self):
        # Manage conditional GUI settings
        config = self.config
        sound_effects = config.get("audio.sound_effects", False)
        if sound_effects:
            from . import playsound

        view_main_front = config.get("gui.view_main_front", True)
        reviewer_image_gif = config.get("gui.reviewer_image_gif", False)
        self.view_main_front = -1 if view_main_front and reviewer_image_gif else 1

        animate_time = config.get("gui.animate_time", False)
        self.animate_time = 0.8 if animate_time else 0

        xp_bar_location = config.get("gui.xp_bar_location", 0)
        xp_bar_config = config.get("gui.xp_bar_config", False)
        if xp_bar_config:
            if xp_bar_location == 1:
                self.xp_bar_location = "top"
                self.xp_bar_spacer = 0
            elif xp_bar_location == 2:
                self.xp_bar_location = "bottom"
                self.xp_bar_spacer = 20
        else:
            self.xp_bar_spacer = 0

        hp_bar_config = config.get("gui.hp_bar_config", True)
        if not hp_bar_config:
            self.hp_only_spacer = 15
            self.wild_hp_spacer = 65
        else:
            self.hp_only_spacer = 0
            self.wild_hp_spacer = 0