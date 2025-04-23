import os
import json
from aqt import QDialog, QVBoxLayout, QWebEngineView, mw
from aqt.qt import QPushButton, QCheckBox, QFrame
from PyQt6.QtCore import QUrl, QUrlQuery

class AchievementsDialog(QDialog):
    def __init__(self, addon_dir, data_handler):
        super().__init__()
        self.addon_dir = addon_dir
        self.data_handler = data_handler
        self.setWindowTitle("Achievements & Badges")

        self.layout = QVBoxLayout()
        self.frame = QFrame()
        self.layout.addWidget(self.frame)
        self.setLayout(self.layout)

        self.webview = QWebEngineView()
        self.frame.setLayout(QVBoxLayout())
        self.frame.layout().addWidget(self.webview)

        # Add toggle button for showing locked/unlocked
        self.show_all_checkbox = QCheckBox("Show Locked Achievements")
        self.show_all_checkbox.setChecked(False)  # Default: only unlocked
        self.show_all_checkbox.stateChanged.connect(self.load_html)
        self.layout.addWidget(self.show_all_checkbox)
        # this is the reason for the "Qt debug: Compositor returned null texture" message

        self.load_html()

    def load_html(self):
        # Load badge definitions
        with open(self.addon_dir / "addon_files" / "badges.json", "r") as f:  # Fixed line
            badge_definitions = json.load(f)
        
        # Load user's unlocked badges
        unlocked_badges = getattr(self.data_handler, "badges", [])

        file_path = os.path.join(self.addon_dir, "achievements", "achievements.html")
        url = QUrl.fromLocalFile(file_path)
        
        query = QUrlQuery()
        query.addQueryItem("addon_name", mw.addonManager.addonFromModule(__name__))
        query.addQueryItem("badge_definitions", json.dumps(badge_definitions))
        query.addQueryItem("unlocked_badges", json.dumps(unlocked_badges))
        show_all = "1" if self.show_all_checkbox.isChecked() else "0"
        query.addQueryItem("show_all", show_all)
        
        url.setQuery(query.toString())
        
        self.webview.setUrl(url)


