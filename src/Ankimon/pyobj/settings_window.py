import json
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtWidgets import QRadioButton, QHBoxLayout, QMainWindow, QScrollArea, QButtonGroup
from PyQt6.QtWidgets import QMessageBox
from aqt.utils import showWarning, showInfo
from aqt import mw

class SettingsWindow(QMainWindow):
    def __init__(self, config, set_config_callback, save_config_callback, load_config_callback):
        super().__init__()
        self.config = config
        self.original_config = config.copy()  # Store the original config to detect changes
        self.set_config_callback = set_config_callback
        self.save_config_callback = save_config_callback
        self.load_config = load_config_callback
        self.setWindowTitle("Settings")
        self.setMaximumWidth(600)
        self.setMaximumHeight(900)
        self.parent = mw

        # Load settings descriptions and friendly names
        self.descriptions = self.load_descriptions()
        self.friendly_names = self.load_friendly_names()

        self.setup_ui()

    def show_window(self):
        self.config = self.load_config()
        self.show()
        self.raise_()  # Bring the window to the front

    def update_config(self, key, value):
        self.config[key] = value  # Directly update self.config
        self.set_config_callback(key, value)

    def load_descriptions(self):
        descriptions_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'lang',
            'setting_description.json'
        )
        if os.path.exists(descriptions_file):
            try:
                with open(descriptions_file, 'r', encoding='utf-8') as f:  # Ensure UTF-8 encoding
                    return json.load(f)
            except json.JSONDecodeError as e:
                showWarning(f"Error decoding JSON file: {e}")
                return {}
            except UnicodeDecodeError as e:
                showWarning(f"Encoding error in descriptions file: {e}")
                return {}
        showWarning("Descriptions file not found. Using empty descriptions.")
        return {}
        
    def load_friendly_names(self):
        # Load the friendly names from a JSON file one level above the root of the add-on directory
        names_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lang', 'setting_name.json')
        if os.path.exists(names_file):
            with open(names_file, "r", encoding="utf-8") as f:
                return json.load(f)
        showWarning("Friendly names file not found. Using default names.")
        return {}

    def setup_ui(self):
        self.setMinimumSize(400, 300)

        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Scroll area to hold settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_content = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_content)
        scroll_area.setWidget(scroll_area_content)

        # Track label-based settings
        self.label_settings = {}

        keys_to_skip = {"debug_mode", "deprecated_setting", "trainer.cash", "trainer.xp", "trainer.id", "trainer.sprite", "misc.last_tip_index"}

        # Handle different setting types
        for key, value in self.config.items():
            if key in keys_to_skip:
                continue

            friendly_name = self.friendly_names.get(key, key)  # Friendly name if available

            if isinstance(value, bool):
                label = QLabel(friendly_name)
                description_label = QLabel(self.descriptions.get(key, "No description available."))
                
                # Enable word wrap and set maximum width for the description label
                description_label.setWordWrap(True)
                description_label.setMaximumWidth(self.width() - 50)  # Subtracting a bit for padding
                description_label.setContentsMargins(5, 5, 5, 0)  # 5 padding around

                # Create radio buttons and unique button group for each setting
                true_radio = QRadioButton("True")
                false_radio = QRadioButton("False")
                true_radio.setChecked(value)
                false_radio.setChecked(not value)

                # Unique button group for each setting
                button_group = QButtonGroup(self)
                button_group.addButton(true_radio)
                button_group.addButton(false_radio)

                true_radio.toggled.connect(lambda checked, k=key: self.handle_radio_selection(checked, k, True))
                false_radio.toggled.connect(lambda checked, k=key: self.handle_radio_selection(checked, k, False))

                scroll_area_layout.addWidget(label)
                scroll_area_layout.addWidget(description_label)
                h_layout = QHBoxLayout()
                h_layout.addWidget(true_radio)
                h_layout.addWidget(false_radio)
                scroll_area_layout.addLayout(h_layout)

                # Store label-based setting
                self.label_settings[friendly_name] = value

            elif isinstance(value, int) or isinstance(value, str):
                label = QLabel(friendly_name)
                description_label = QLabel(self.descriptions.get(key, "No description available."))

                # Enable word wrap and set maximum width for the description label
                description_label.setWordWrap(True)
                description_label.setMaximumWidth(self.width() - 50)  # Subtracting a bit for padding
                description_label.setContentsMargins(5, 5, 5, 0)  # 5 padding around

                line_edit = QLineEdit(str(value))
                scroll_area_layout.addWidget(label)
                scroll_area_layout.addWidget(description_label)
                scroll_area_layout.addWidget(line_edit)

                line_edit.editingFinished.connect(lambda k=key, le=line_edit: self.update_config(k, le.text()))

                # Store label-based setting
                self.label_settings[friendly_name] = value

        layout.addWidget(scroll_area)

        # Save button
        save_button = QPushButton("Save")
        save_button.setToolTip("Click to save your settings.")
        save_button.clicked.connect(self.on_save)
        layout.addWidget(save_button)

    def handle_radio_selection(self, checked, key, value):
        if checked:
            self.config[key] = value  # Directly update self.config
            self.set_config_callback(key, value)

    def on_save(self):
        excluded_patterns = {
        'mypokemon', 'mainpokemon', 'pokemon_collection', 'trainer.cash', 'misc.last_tip_index'
        }

        # Check for changes, excluding 'mypokemon' and 'mainpokemon'
        changed_settings = {
            key: self.config[key]
            for key in self.config
            if not any(pattern in key for pattern in excluded_patterns)
            and self.config[key] != self.original_config.get(key)
        }


        #showInfo(f"{changed_settings}")

        # Call the save configuration callback
        self.save_config_callback(self.config)

        # Display only the changed settings
        if changed_settings:
            changed_message = "\n".join([f"{key}: {value}" for key, value in changed_settings.items()])
            QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
            QMessageBox.information(self, "Config changes", f"Changed settings:\n{changed_message}")
        else:
            QMessageBox.information(self, "No Changes", "No settings were changed.")
