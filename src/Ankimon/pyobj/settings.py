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

        # Load existing config or initialize as empty
        config = mw.addonManager.getConfig(__name__) or {}

        # Check if "misc.leaderboard" exists; if not, add it
        if "misc.leaderboard" not in config:
            config["misc.leaderboard"] = False  # Add the new setting with its default value
            self.save_config(config)
        if "misc.ankiweb_sync" not in config:
            config["misc.ankiweb_sync"] = False  # Default to disabled
            self.save_config(config)

        if not config:
            #Card max time in Seconds
            config = {
                "battle.dmg_in_reviewer": True,
                "battle.automatic_battle": int(0),
                "battle.cards_per_round": int(2),
                "battle.daily_average": int(100),
                "battle.card_max_time": int(60),

                "controls.pokemon_buttons": True,
                "controls.defeat_key": "5",
                "controls.catch_key": "6",
                "controls.key_for_opening_closing_ankimon": "Ctrl+Shift+P",
                "controls.allow_to_choose_moves": False,

                "gui.animate_time": True,
                "gui.gif_in_collection": True,
                "gui.styling_in_reviewer": True,
                "gui.hp_bar_config": True,
                "gui.pop_up_dialog_message_on_defeat": False,
                "gui.review_hp_bar_thickness": int(2),
                "gui.reviewer_image_gif": False,
                "gui.reviewer_text_message_box": True,
                "gui.reviewer_text_message_box_time": int(3),
                "gui.show_mainpkmn_in_reviewer": int(1),
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
                "misc.gen7": True,
                "misc.gen8": True,
                "misc.gen9": False,
                "misc.remove_level_cap": False,
                "misc.language": 9,
                "misc.ssh": True,
                "misc.leaderboard": False,
                "misc.ankiweb_sync": False,
                "misc.YouShallNotPass_Ankimon_News": False,
                "misc.discord_rich_presence": False,
                "misc.discord_rich_presence_text": 1,

                "trainer.name": "Ash",
                "trainer.sprite": "ash",
                "trainer.id": 0,
                "trainer.cash": 0,
                "trainer.level": 0,
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
            from .. import playsound

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

    def compute_special_variable(self, key):
        # Dynamically compute and return the requested GUI variable
        if key == "view_main_front":
            view_main_front = self.config.get("gui.view_main_front", True)
            reviewer_image_gif = self.config.get("gui.reviewer_image_gif", False)
            return -1 if view_main_front and reviewer_image_gif else 1

        elif key == "animate_time":
            animate_time = self.config.get("gui.animate_time", False)
            return 0.8 if animate_time else 0

        elif key == "xp_bar_location":
            xp_bar_config = self.config.get("gui.xp_bar_config", True)
            xp_bar_location = int(self.config.get("gui.xp_bar_location", 2))

            if xp_bar_config:
                if xp_bar_location == 1:
                    return "top"
                elif xp_bar_location == 2:
                    return "bottom"
            return None  # Default when XP bar is disabled

        elif key == "xp_bar_spacer":
            xp_bar_config = self.config.get("gui.xp_bar_config", False)
            xp_bar_location = self.config.get("gui.xp_bar_location", 0)

            if xp_bar_config:
                if xp_bar_location == '2': # Bottom
                    return 20
                elif xp_bar_location == '1': # Top
                    return 0
            return 0  # Default spacer

        elif key == "hp_only_spacer":
            hp_bar_config = self.config.get("gui.hp_bar_config", True)
            return 15 if not hp_bar_config else 0

        elif key == "wild_hp_spacer":
            hp_bar_config = self.config.get("gui.hp_bar_config", True)
            return 65 if not hp_bar_config else 0

        else:
            raise ValueError(f"Unknown key: {key}")
