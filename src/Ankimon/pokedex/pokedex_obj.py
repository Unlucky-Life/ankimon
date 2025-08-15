import os
import json
from aqt import QDialog, QVBoxLayout, QWebEngineView, mw
from PyQt6.QtCore import QUrlQuery
from aqt.qt import Qt, QFile, QUrl, QFrame, QPushButton
from aqt.utils import showInfo
from ..resources import mypokemon_path

class Pokedex(QDialog):
    def __init__(self, addon_dir, ankimon_tracker):
        super().__init__()
        self.addon_dir = addon_dir
        self.ankimon_tracker = ankimon_tracker
        self.owned_pokemon_ids = ankimon_tracker.owned_pokemon_ids
        self.setWindowTitle("Pokedex - Ankimon")

        # Remove default background to make it transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Set a default size for the dialog
        self.resize(900, 800)  # Width: 900px, Height: 800px

        # Create the layout with no margins
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.layout.setSpacing(0)  # Remove spacing between widgets

        # Frame for WebEngineView
        self.frame = QFrame()
        self.frame.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.frame.setFrameStyle(QFrame.Shape.NoFrame)  # Remove frame border

        self.layout.addWidget(self.frame)
        self.setLayout(self.layout)

        # WebEngineView setup
        self.webview = QWebEngineView()
        self.webview.setContentsMargins(0, 0, 0, 0)  # Remove margins
        self.frame.setLayout(QVBoxLayout())
        self.frame.layout().setContentsMargins(0, 0, 0, 0)  # Remove margins in frame layout
        self.frame.layout().setSpacing(0)  # Remove spacing
        self.frame.layout().addWidget(self.webview)

        # Remove the online/offline buttons since we’re focusing on the local Pokédex
        self.load_html()

    def load_html(self):
        self.ankimon_tracker.get_ids_in_collection()
        self.owned_pokemon_ids = self.ankimon_tracker.owned_pokemon_ids
        #print("POKEDEX_DEBUG: Caught Pokémon IDs:", self.owned_pokemon_ids)

        # Convert caught IDs to string
        str_owned_pokemon_ids = ",".join(map(str, self.owned_pokemon_ids)) if self.owned_pokemon_ids else ""
        #print("POKEDEX_DEBUG: Caught IDs string:", str_owned_pokemon_ids)

        # Calculate defeated Pokémon count
        defeated_count = 0
        # Try multiple possible paths for mypokemon.json

        pokemon_list = None

        if os.path.exists(mypokemon_path):
            try:
                with open(mypokemon_path, "r", encoding="utf-8") as file:
                    pokemon_list = json.load(file)
                    print("POKEDEX_DEBUG: Loaded pokemon_list!")

            except json.JSONDecodeError:
                print("POKEDEX_DEBUG: Invalid JSON in mypokemon.json at", mypokemon_path)
            except Exception as e:
                print("POKEDEX_DEBUG: Error reading mypokemon.json at", mypokemon_path, ":", str(e))

        if pokemon_list:
            for pokemon in pokemon_list:
                defeated = pokemon.get("pokemon_defeated", 0)
                try:
                    defeated_num = int(float(str(defeated)))  # Handle int, float, string
                    defeated_count += defeated_num
                    #print(f"POKEDEX_DEBUG: Pokemon ID {pokemon.get('id', 'unknown')}: pokemon_defeated = {defeated_num}")
                except (TypeError, ValueError):
                    print(f"POKEDEX_DEBUG: Invalid pokemon_defeated for ID {pokemon.get('id', 'unknown')}: {defeated}")
        else:
            print("POKEDEX_DEBUG: No valid mypokemon.json found")

        #print("POKEDEX_DEBUG: Total defeated_count =", defeated_count)

        file_path = os.path.join(self.addon_dir, "pokedex", "pokedex.html").replace("\\", "/")
        #print("POKEDEX_DEBUG: Loading HTML from:", file_path)
        url = QUrl.fromLocalFile(file_path)

        query = QUrlQuery()
        query.addQueryItem("numbers", str_owned_pokemon_ids)
        query.addQueryItem("defeated", str(defeated_count))
        url.setQuery(query)
        #print("POKEDEX_DEBUG: Final URL:", url.toString())

        self.webview.setUrl(url)

    def showEvent(self, event):
        self.load_html()
        self.webview.reload()
