import json
import os
from aqt import mw
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtWidgets import QRadioButton, QHBoxLayout

class Settings:
    def __init__(self):
        self.config = self.load_config()

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
                "misc.YouShallNotPass_Ankimon_News": False
            }
            self.save_config(config)
        return config
    
    def save_config(self, config):
        mw.addonManager.writeConfig(__name__, config)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()
        self.save_config(self.config)

    def create_settings_window(self):
        app = QApplication([])
        window = QWidget()
        layout = QVBoxLayout()

        for key, value in self.config.items():
            if isinstance(value, bool):
                label = QLabel(key)
                true_radio = QRadioButton("True")
                false_radio = QRadioButton("False")
                if value:
                    true_radio.setChecked(True)
                else:
                    false_radio.setChecked(True)
                
                true_radio.toggled.connect(lambda checked, k=key: self.set(k, checked))
                false_radio.toggled.connect(lambda checked, k=key: self.set(k, not checked))
                
                layout.addWidget(label)
                h_layout = QHBoxLayout()
                h_layout.addWidget(true_radio)
                h_layout.addWidget(false_radio)
                layout.addLayout(h_layout)
            elif isinstance(value, int):
                label = QLabel(key)
                line_edit = QLineEdit(str(value))
                layout.addWidget(label)
                layout.addWidget(line_edit)
                line_edit.editingFinished.connect(lambda k=key, le=line_edit: self.set(k, int(le.text())))
            elif isinstance(value, str):
                label = QLabel(key)
                line_edit = QLineEdit(value)
                layout.addWidget(label)
                layout.addWidget(line_edit)
                line_edit.editingFinished.connect(lambda k=key, le=line_edit: self.set(k, le.text()))

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config(self.config))
        layout.addWidget(save_button)

        window.setLayout(layout)
        window.setWindowTitle("Settings")
        window.show()
        app.exec()