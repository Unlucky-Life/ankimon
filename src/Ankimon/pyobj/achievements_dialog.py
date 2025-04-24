import os
import json
from aqt import QDialog, QVBoxLayout, QWebEngineView, mw
from aqt.qt import QPushButton, QCheckBox, QFrame
from PyQt6.QtCore import QUrl, QUrlQuery
from pathlib import Path

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
        from pathlib import Path
        import json
        from PyQt6.QtCore import QUrl, QUrlQuery

        # Load badge definitions
        badges_path = self.addon_dir / "addon_files" / "badges.json"
        with open(badges_path, "r") as f:
            badge_definitions = json.load(f)
        
        # Load user's unlocked badges
        unlocked_badges = getattr(self.data_handler, "badges", [])

        # Construct absolute path to HTML file
        html_path = self.addon_dir / "achievements" / "achievements.html"
        
        # Convert to POSIX path for QUrl compatibility
        html_path_str = html_path.as_posix()
        
        # Create URL with proper encoding for macOS
        url = QUrl.fromLocalFile(html_path_str)
        
        # Create and encode query parameters
        query = QUrlQuery()
        query.addQueryItem("addon_name", mw.addonManager.addonFromModule(__name__))
        query.addQueryItem(
            "badge_definitions", 
            json.dumps(badge_definitions, separators=(",", ":"))  # Minimize JSON size
        )
        query.addQueryItem(
            "unlocked_badges", 
            json.dumps(unlocked_badges, separators=(",", ":"))
        )
        query.addQueryItem(
            "show_all", 
            "1" if self.show_all_checkbox.isChecked() else "0"
        )
        
        # Set query and ensure proper encoding
        url.setQuery(query.query(QUrl.ComponentFormattingOption.FullyEncoded))
        
        # Load the URL
        self.webview.setUrl(url)



