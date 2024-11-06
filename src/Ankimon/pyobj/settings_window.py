import json
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtWidgets import QRadioButton, QHBoxLayout, QMainWindow, QScrollArea, QButtonGroup
from PyQt6.QtWidgets import QMessageBox
from aqt.utils import showWarning, showInfo

class SettingsWindow(QMainWindow):
    def __init__(self, config, set_config_callback, save_config_callback):
        super().__init__()
        self.config = config
        self.original_config = config.copy()  # Store the original config to detect changes
        self.set_config_callback = set_config_callback
        self.save_config_callback = save_config_callback
        self.setWindowTitle("Settings")

        # Load settings descriptions and friendly names
        self.descriptions = self.load_descriptions()
        self.friendly_names = self.load_friendly_names()

        self.setup_ui()

    def show_window(self):
        self.show()

    def load_descriptions(self):
        # Load descriptions from a JSON file one level above the root of the add-on directory
        descriptions_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lang', 'setting_description.json')
        if os.path.exists(descriptions_file):
            with open(descriptions_file, 'r') as f:
                return json.load(f)
        showWarning("Descriptions file not found. Using empty descriptions.")
        return {}
        
    def load_friendly_names(self):
        # Load the friendly names from a JSON file one level above the root of the add-on directory
        names_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lang', 'setting_name.json')
        if os.path.exists(names_file):
            with open(names_file, 'r') as f:
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

        # Handle different setting types
        for key, value in self.config.items():
            friendly_name = self.friendly_names.get(key, key)  # Friendly name if available

            if isinstance(value, bool):
                label = QLabel(friendly_name)
                description_label = QLabel(self.descriptions.get(key, "No description available."))

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
                line_edit = QLineEdit(str(value))
                scroll_area_layout.addWidget(label)
                scroll_area_layout.addWidget(description_label)
                scroll_area_layout.addWidget(line_edit)

                line_edit.editingFinished.connect(lambda k=key, le=line_edit: self.set_config_callback(k, le.text()))

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
            self.set_config_callback(key, value)

    def on_save(self):
        # Call the save configuration callback
        self.save_config_callback(self.config)

        # Check for changes, excluding 'mypokemon' and 'mainpokemon'
        changed_settings = {
            key: self.config[key]
            for key in self.config
            if key not in ['mypokemon', 'mainpokemon'] and self.config[key] != self.original_config.get(key)
        }

        # Display only the changed settings
        if changed_settings:
            changed_message = "\n".join([f"{key}: {value}" for key, value in changed_settings.items()])
            QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
            QMessageBox.information(self, "Config changes", f"Changed settings:\n{changed_message}")
        else:
            QMessageBox.information(self, "No Changes", "No settings were changed.")