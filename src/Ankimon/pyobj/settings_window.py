import json
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QRadioButton, QHBoxLayout, QMainWindow, QScrollArea, QButtonGroup, QMessageBox
)
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QRectF
from aqt.utils import showWarning
from aqt import mw
from aqt.theme import theme_manager

# create_rounded_pixmap function remains the same
def create_rounded_pixmap(source_pixmap, radius):
    if source_pixmap.isNull():
        return QPixmap()
    rounded = QPixmap(source_pixmap.size())
    rounded.fill(Qt.GlobalColor.transparent)
    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    path = QPainterPath()
    rect = QRectF(source_pixmap.rect())
    path.addRoundedRect(rect, radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, source_pixmap)
    painter.end()
    return rounded


class SettingsWindow(QMainWindow):
    def __init__(self, config, set_config_callback, save_config_callback, load_config_callback):
        super().__init__()
        self.config = config
        self.original_config = config.copy()
        self.save_config_callback = save_config_callback
        self.load_config = load_config_callback
        self.setWindowTitle("Settings")
        self.setMaximumWidth(600)
        self.setMaximumHeight(900)
        self.parent = mw

        self.descriptions = self.load_descriptions()
        self.friendly_names = self.load_friendly_names()
        self.key_map = {v: k for k, v in self.friendly_names.items()}

        self.group_widgets = {}
        self.group_states = {}
        self.searchable_settings = []
        self.title_buttons = {}  # To store references to title buttons
        self.input_widgets = {}  # To store references to input widgets

        self.setup_ui()

    @property
    def is_dark_mode(self):
        """Checks if Anki is in dark mode."""
        return theme_manager.night_mode

    def _apply_stylesheet(self):
        """Applies the appropriate stylesheet based on the current theme."""
        if self.is_dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #2e2e2e;
                    color: #f0f0f0;
                }
                QLabel[class="setting-label"] {
                    font-weight: bold;
                    margin-top: 5px;
                    color: #f0f0f0;
                }
                QLabel[class="description-label"] {
                    color: #aaaaaa;
                    padding-left: 5px;
                }
                QRadioButton {
                    color: #f0f0f0;
                }
                QLineEdit {
                    background-color: #3c3c3c;
                    color: #f0f0f0;
                    border: 1px solid #555555;
                    padding: 4px;
                }
                QPushButton {
                    background-color: #4a4a4a;
                    border: 1px solid #555555;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
                QPushButton[class="title-button"] {
                    font-weight: bold;
                    text-align: left;
                    border: none;
                    background-color: transparent;
                }
                QPushButton[class="title-button"][level="1"] {
                    font-size: 18px;
                    margin-top: 15px;
                    margin-bottom: 5px;
                    color: #87CEEB;
                }
                QPushButton[class="title-button"][level="2"] {
                    font-size: 14px;
                    margin-top: 10px;
                    padding-left: 15px;
                    color: #ADD8E6;
                }
            """)
        else: # Light Mode
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #f5f5f5;
                    color: #212121;
                }
                QLabel[class="setting-label"] {
                    font-weight: bold;
                    margin-top: 5px;
                    color: #212121;
                }
                QLabel[class="description-label"] {
                    color: #666666;
                    padding-left: 5px;
                }
                QRadioButton {
                    color: #212121;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #212121;
                    border: 1px solid #adadad;
                    padding: 4px;
                }
                QPushButton {
                    background-color: #e1e1e1;
                    border: 1px solid #adadad;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #cacaca;
                }
                QPushButton[class="title-button"] {
                    font-weight: bold;
                    text-align: left;
                    border: none;
                    background-color: transparent;
                }
                QPushButton[class="title-button"][level="1"] {
                    font-size: 18px;
                    margin-top: 15px;
                    margin-bottom: 5px;
                    color: #253D5B;
                }
                QPushButton[class="title-button"][level="2"] {
                    font-size: 14px;
                    margin-top: 10px;
                    padding-left: 15px;
                    color: #355882;
                }
            """)

    def load_descriptions(self):
        descriptions_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lang', 'setting_description.json')
        if os.path.exists(descriptions_file):
            try:
                with open(descriptions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                showWarning(f"Error reading descriptions file: {e}")
        return {}

    def load_friendly_names(self):
        names_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lang', 'setting_name.json')
        if os.path.exists(names_file):
            try:
                with open(names_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                showWarning(f"Error reading friendly names file: {e}")
        return {}

    def _create_setting(self, key, layout):
        if not key or key not in self.config:
            return [], "", ""

        value = self.config[key]
        friendly_name = self.friendly_names.get(key, key)
        description = self.descriptions.get(key, "No description available.")
        
        created_widgets = []
        label = QLabel(friendly_name)
        label.setProperty("class", "setting-label")
        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setProperty("class", "description-label")
        description_label.setMaximumWidth(self.width() - 50)
        layout.addWidget(label)
        layout.addWidget(description_label)
        created_widgets.extend([label, description_label])

        if isinstance(value, bool):
            radio_container = QWidget()
            h_layout = QHBoxLayout(radio_container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            true_radio = QRadioButton("True")
            false_radio = QRadioButton("False")
            true_radio.setChecked(value)
            false_radio.setChecked(not value)
            button_group = QButtonGroup(self)
            button_group.addButton(true_radio)
            button_group.addButton(false_radio)
            h_layout.addWidget(true_radio)
            h_layout.addWidget(false_radio)
            layout.addWidget(radio_container)
            created_widgets.append(radio_container)
            self.input_widgets[key] = button_group
        elif isinstance(value, (int, str)):
            line_edit = QLineEdit(str(value))
            layout.addWidget(line_edit)
            created_widgets.append(line_edit)
            self.input_widgets[key] = line_edit

        return created_widgets, friendly_name, description

    def _create_title(self, text, level=1):
        button = QPushButton(f" {text}")
        button.setCheckable(True)
        button.setChecked(True)
        button.setProperty("class", "title-button")
        button.setProperty("level", str(level))
        return button
        
    def setup_ui(self):
        self.setMinimumSize(450, 600)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self._apply_stylesheet()
        
        layout = QVBoxLayout(central_widget)
        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_files', 'web', 'images', 'ankimon_logo.png')
        image_label = QLabel()
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaledToWidth(250, Qt.TransformationMode.SmoothTransformation)
            rounded_pixmap = create_rounded_pixmap(scaled_pixmap, 15)
            image_label.setPixmap(rounded_pixmap)
        else:
            image_label.setText("Ankimon Logo Not Found")
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(image_label)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search settings...")
        self.search_bar.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_bar)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area_content = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_content)
        scroll_area.setWidget(scroll_area_content)
        hierarchical_groups = {
            "General": { "settings": ["Trainer Name", "Language", "Show Tip of the Day On Startup"], "subgroups": { "Technical Settings": {"settings": ["SSH Access", "Receive Ankimon News", "AnkiWeb Sync", "Ankimon Leaderboard", "Developer Mode"]}, "Discord Integration": {"settings": ["Discord Rich Presence - Ankimon", "Discord Rich Presence - Quote Type"]} } },
            "Battle": { "settings": ["Automatic Battle", "Cards per Round", "Show Main Pokémon in Reviewer", "Show Pokémon Buttons", "Pop-Up on Defeat", "Show Text Message Box in Reviewer", "Message Box Display Time"], "subgroups": { "Fight Hotkeys": {"settings": ["Key for Defeat", "Key for Catching", "Key for Opening/Closing Ankimon", "Allow Choosing Moves"]}, "HP, XP and Level Settings": {"settings": ["HP Bar Configuration", "XP Bar Configuration", "XP Bar Location", "Remove Level Cap"]} } },
            "Styling": {"settings": ["Styling in Reviewer", "Animate Time", "HP Bar Thickness", "Reviewer Image as GIF", "View Main Pokémon Front", "Show GIFs in Collection"]},
            "Sound": {"settings": ["Enable Sound Effects", "Enable Sounds", "Enable Battle Sounds"]},
            "Study": {"settings": ["Goal of Daily Average Cards", "Card Max Time"]},
            "Generations": {"settings": ["Generation 1", "Generation 2", "Generation 3", "Generation 4", "Generation 5", "Generation 6", "Generation 7", "Generation 8", "Generation 9"]}
        }
        for l1_title, l1_data in hierarchical_groups.items():
            self.group_states[l1_title] = True
            l1_widgets = []
            l1_button = self._create_title(l1_title, level=1)
            scroll_area_layout.addWidget(l1_button)
            self.title_buttons[l1_title] = l1_button
            for friendly_name in l1_data.get("settings", []):
                key = self.key_map.get(friendly_name)
                widgets, name, desc = self._create_setting(key, scroll_area_layout)
                if widgets:
                    l1_widgets.extend(widgets)
                    self.searchable_settings.append({ "widgets": widgets, "friendly_name": name, "description": desc, "l1_title": l1_title, "l2_title": None })
            if "subgroups" in l1_data:
                for l2_title, l2_data in l1_data["subgroups"].items():
                    self.group_states[l2_title] = True
                    l2_widgets = []
                    l2_button = self._create_title(l2_title, level=2)
                    scroll_area_layout.addWidget(l2_button)
                    self.title_buttons[l2_title] = l2_button
                    l1_widgets.append(l2_button)
                    for friendly_name in l2_data.get("settings", []):
                        key = self.key_map.get(friendly_name)
                        widgets, name, desc = self._create_setting(key, scroll_area_layout)
                        if widgets:
                            l1_widgets.extend(widgets)
                            l2_widgets.extend(widgets)
                            self.searchable_settings.append({ "widgets": widgets, "friendly_name": name, "description": desc, "l1_title": l1_title, "l2_title": l2_title })
                    self.group_widgets[l2_title] = l2_widgets
                    l2_button.clicked.connect(lambda _, t=l2_title, b=l2_button: self._toggle_group_visibility(t, b))
            self.group_widgets[l1_title] = l1_widgets
            l1_button.clicked.connect(lambda _, t=l1_title, b=l1_button: self._toggle_group_visibility(t, b))
        scroll_area_layout.addStretch()
        layout.addWidget(scroll_area)
        save_button = QPushButton("Save")
        save_button.setToolTip("Click to save your settings.")
        save_button.clicked.connect(self.on_save)
        layout.addWidget(save_button)
    
    def show_window(self):
        self._apply_stylesheet()
        self.config = self.load_config()
        self.show()
        self.raise_()

    def _on_search_changed(self, text):
        search_term = text.lower().strip()
        if not search_term:
            for setting in self.searchable_settings:
                for widget in setting["widgets"]: widget.setVisible(True)
            for title, button in self.title_buttons.items():
                button.setVisible(True)
                is_expanded = self.group_states.get(title, True)
                for w in self.group_widgets.get(title, []): w.setVisible(is_expanded)
            return
        
        for setting in self.searchable_settings:
            for widget in setting["widgets"]:
                widget.setVisible(False)
        for button in self.title_buttons.values():
            button.setVisible(False)

        titles_to_show = set()
        for setting in self.searchable_settings:
            name = setting["friendly_name"].lower()
            desc = setting["description"].lower()
            if search_term in name or search_term in desc:
                for widget in setting["widgets"]:
                    widget.setVisible(True)
                titles_to_show.add(setting["l1_title"])
                if setting["l2_title"]:
                    titles_to_show.add(setting["l2_title"])

        for title in titles_to_show:
            if title in self.title_buttons:
                self.title_buttons[title].setVisible(True)

    def _toggle_group_visibility(self, title, button):
        is_expanded = not self.group_states.get(title, True)
        self.group_states[title] = is_expanded
        if title in self.group_widgets:
            for widget in self.group_widgets[title]:
                widget.setVisible(is_expanded)

    def on_save(self):
        # Update self.config from the current state of all UI widgets
        for key, widget in self.input_widgets.items():
            original_value = self.original_config.get(key)
            
            if isinstance(widget, QLineEdit):
                new_text = widget.text()
                # Attempt to cast back to original type (int or str)
                if isinstance(original_value, int):
                    try:
                        self.config[key] = int(new_text)
                    except ValueError:
                        self.config[key] = original_value
                else:
                    self.config[key] = new_text
            elif isinstance(widget, QButtonGroup):
                self.config[key] = (widget.checkedButton().text() == "True")

        # Now that self.config is up-to-date, call the save callback
        self.save_config_callback(self.config)

        # The rest is for showing the confirmation message
        excluded_patterns = { 'mypokemon', 'mainpokemon', 'pokemon_collection', 'trainer.cash', 'misc.last_tip_index', 'trainer.xp_share'}
        changed_settings = { key: self.config[key] for key in self.config if not any(pattern in key for pattern in excluded_patterns) and self.config[key] != self.original_config.get(key) }
        
        if changed_settings:
            friendly_changed = {self.friendly_names.get(k, k): v for k, v in changed_settings.items()}
            changed_message = "\n".join([f"{key}: {value}" for key, value in friendly_changed.items()])
            QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully.")
            QMessageBox.information(self, "Config changes", f"Changed settings:\n{changed_message}")
            self.original_config = self.config.copy()
        else:
            QMessageBox.information(self, "No Changes", "No settings were changed.")
