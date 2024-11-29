import os
from aqt import QDialog, QVBoxLayout, QWebEngineView, mw
from PyQt6.QtCore import QUrlQuery
from aqt.qt import Qt, QFile, QUrl, QFrame, QPushButton
from aqt.utils import showInfo
import json

class Pokedex(QDialog):
    def __init__(self, addon_dir, ankimon_tracker):
        super().__init__()
        self.addon_dir = addon_dir
        self.ankimon_tracker = ankimon_tracker
        self.owned_pokemon_ids = ankimon_tracker.owned_pokemon_ids
        self.setWindowTitle("Pokedex - from https://pokedex.hybridshivam.com/")
        self.layout = QVBoxLayout()
        
        # Frame for WebEngineView
        self.frame = QFrame()
        self.layout.addWidget(self.frame)
        self.setLayout(self.layout)
        
        self.webview = QWebEngineView()
        self.frame.setLayout(QVBoxLayout())  # Add this line to create a layout for the frame
        self.frame.layout().addWidget(self.webview)

        # Add a button to go to a local file
        self.offline_pokedex_button = QPushButton("Go to own Pokedex")
        self.offline_pokedex_button.clicked.connect(self.go_to_offline_pokedex)
        self.layout.addWidget(self.offline_pokedex_button)
        
        # Add a button to go to a local file
        self.online_pokedex_button = QPushButton("Go to online Pokedex by: hybridshivam")
        self.online_pokedex_button.clicked.connect(self.go_to_online_pokedex)
        self.layout.addWidget(self.online_pokedex_button)

        self.load_html()

    def load_html(self):
        self.ankimon_tracker.get_ids_in_collection()
        self.owned_pokemon_ids = self.ankimon_tracker.owned_pokemon_ids
        str_owned_pokemon_ids = str(self.owned_pokemon_ids)
        str_owned_pokemon_ids = str_owned_pokemon_ids.replace("[", "").replace("]", "").replace(" ", "")
        file_path = os.path.join(self.addon_dir, "pokedex", "pokedex.html").replace("\\","/")
        url = QUrl.fromLocalFile(file_path)
        
        query = QUrlQuery()
        query.addQueryItem("numbers", str_owned_pokemon_ids)
        url.setQuery(query.toString())
        
        self.webview.setUrl(url)
    
    def go_to_online_pokedex(self):
        # Path to the local file you want to open
        url = QUrl("https://pokedex.hybridshivam.com/")
        
        # Load the local file into the QWebEngineView
        self.webview.setUrl(url)
    
    def go_to_offline_pokedex(self):
        self.load_html()

    def showEven(self, event):
        self.load_html()
        self.webview.reload()
        self.show()
