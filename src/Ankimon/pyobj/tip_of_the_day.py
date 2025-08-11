import json
import random
from pathlib import Path

from aqt import mw
from aqt.qt import *

from ..pyobj.settings import Settings
from ..resources import rate_path

class TipOfTheDayDialog(QDialog):
    def __init__(self, tip_text, tip_number, total_tips, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Ankimon Tip #{tip_number + 1}/{total_tips}")
        self.setMinimumWidth(400)

        self.settings = Settings()

        self.layout = QVBoxLayout(self)

        self.tip_label = QLabel(tip_text)
        self.tip_label.setWordWrap(True)
        self.layout.addWidget(self.tip_label)

        self.dont_show_again_checkbox = QCheckBox("Don't show tips again")
        self.layout.addWidget(self.dont_show_again_checkbox)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        self.next_tip_button = self.button_box.addButton("Next Tip", QDialogButtonBox.ButtonRole.ActionRole)
        
        self.next_tip_button.clicked.connect(self.show_new_tip)
        self.button_box.accepted.connect(self.accept)
        
        self.layout.addWidget(self.button_box)
        
        self.tips = self._load_tips()
        self.current_tip_index = tip_number

    def _load_tips(self) -> list:
        tips_path = Path(__file__).parent.parent / "addon_files" / "tips.json"
        if not tips_path.exists():
            return []
        try:
            with open(tips_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("tips", [])
        except (json.JSONDecodeError, Exception):
            return []

    def show_new_tip(self):
        self.current_tip_index = (self.current_tip_index + 1) % len(self.tips)
        self.tip_label.setText(self.tips[self.current_tip_index])
        self.setWindowTitle(f"Ankimon Tip #{self.current_tip_index + 1}/{len(self.tips)}")


    def accept(self):
        if self.dont_show_again_checkbox.isChecked():
            self.settings.set("misc.show_tip_on_startup", False)
        self.settings.set("misc.last_tip_index", self.current_tip_index)
        super().accept()

def show_tip_of_the_day():
    """Checks settings and shows the tip of the day dialog if enabled."""
    settings = Settings()
    if not settings.get("misc.show_tip_on_startup", True):
        return

    # Check if the addon has been rated
    try:
        with open(rate_path, "r", encoding="utf-8") as f:
            rate_data = json.load(f)
            if not rate_data.get("rate_this", False):
                return
    except (FileNotFoundError, json.JSONDecodeError):
        return

    tips_path = Path(__file__).parent.parent / "addon_files" / "tips.json"
    if not tips_path.exists():
        return
    try:
        with open(tips_path, "r", encoding="utf-8") as f:
            tips = json.load(f).get("tips", [])
    except (json.JSONDecodeError, Exception):
        return
        
    if not tips:
        return

    last_tip_index = settings.get("misc.last_tip_index", -1)
    next_tip_index = (last_tip_index + 1) % len(tips)
    
    dialog = TipOfTheDayDialog(tips[next_tip_index], next_tip_index, len(tips), mw)
    dialog.exec()