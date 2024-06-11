import json
import os
from aqt import mw
from aqt.utils import showInfo
from aqt.qt import QDialog, QLabel, QVBoxLayout, QPushButton
from aqt.utils import qconnect

class CheckPokemonData(QDialog):
    def __init__(self, mainpokemon_path, mypokemon_path, config):
        super().__init__()
        self.mainpokemon_path = mainpokemon_path
        self.mypokemon_path = mypokemon_path
        self.config = config
        self.sync_pokemons()
        message = "Ankimon Pokemon Sync:"
        message += "There is a difference between the Ankiweb Synced Pokémon data and the local Pokémon data. \n"
        message += "Please choose to either load the local data and sync to Ankiweb or sync Ankiweb data to your local storage \n"
        # Set the window title for the dialog
        self.setWindowTitle("Ankimon Pokemon Sync:")

        # Create a QLabel instance
        self.label = QLabel(f"{message}", self)

        # Create two QPushButtons for syncing options
        self.sync_local_button = QPushButton("Load Local Data and Sync to Ankiweb", self)
        self.sync_ankiweb_button = QPushButton("Sync Ankiweb Data to Local Storage", self)
        qconnect(self.sync_local_button.clicked, self.sync_data_to_local)
        qconnect(self.sync_ankiweb_button.clicked, self.sync_data_to_ankiweb)
        # Create a QVBoxLayout instance
        self.layout = QVBoxLayout()
        # Add the QLabel and QPushButtons to the layout
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.sync_local_button)
        self.layout.addWidget(self.sync_ankiweb_button)
        # Set the dialog's layout
        self.setLayout(self.layout)

    def sync_pokemons(self):
        self.mainpokemon_web_data = self.config.get('mainpokemon', '')
        self.pokemon_collection_web_data = self.config.get('pokemon_collection', '')
        #showInfo("Pokémon data synced.")
        #showInfo(f"Mainpokemon {mainpokemon}")
        #showInfo(f"Pokémon Collection {pokemon_collection}")    #function to sync pokemon data to ankiweb and local files
            
        with open(str(self.mypokemon_path), 'r', encoding='utf-8') as file:
            self.pokemon_collection_sync_data = json.load(file)
        with open(str(self.mainpokemon_path), 'r', encoding='utf-8') as file:
            self.mainpokemon_sync_data = json.load(file)
            
        if self.mainpokemon_web_data != self.mainpokemon_sync_data or self.pokemon_collection_web_data != self.pokemon_collection_sync_data:
            # Show dialog window with two buttons
            self.show()
    
    def sync_data_to_local(self):
        with open(str(self.mypokemon_path), 'w', encoding='utf-8') as file:
            json.dump(self.mainpokemon_web_data, file, ensure_ascii=False, indent=4)
        with open(str(self.mainpokemon_path), 'w', encoding='utf-8') as file:
            json.dump(self.pokemon_collection_web_data, file, ensure_ascii=False, indent=4)
        showInfo("Ankiweb Data synced to local.")
        self.close()
    
    def sync_data_to_ankiweb(self):
        self.config["pokemon_collection"] = self.pokemon_collection_sync_data
        self.config["mainpokemon"] = self.mainpokemon_sync_data
        mw.addonManager.writeConfig(__name__, self.config)
        showInfo("Local Data synced to local.")
        self.close()
