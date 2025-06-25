import json
from PyQt6.QtGui import QTextOption
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QTextEdit, QPushButton, QDialog
from aqt import mw
from aqt.utils import showWarning, showInfo, tooltip
from ..resources import mypokemon_path, mainpokemon_path

class CheckPokemonData(QDialog):
    def __init__(self, settings_obj, logger):
        super().__init__()
        self.config = settings_obj
        self.logger = logger
        self.mypokemon_path = mypokemon_path
        self.mainpokemon_path = mainpokemon_path
        self.get_pokemon_data()
        self.setup_ui()
        self.sync_pokemons()
        self.display_data_comparison()

    def setup_ui(self):
        # Set the window title for the dialog
        self.setWindowTitle("Ankimon Pokemon Sync")

        # Create a QLabel instance
        message = (
            "Ankimon Pokemon Sync:\n"
            "There is a difference between the Ankiweb Synced Pokémon data and the local Pokémon data.\n"
            "Please choose to either load the local data and sync to Ankiweb or sync Ankiweb data to your local storage."
        )
        self.label = QLabel(message, self)

        # Create two QPushButtons for syncing options
        self.sync_local_button = QPushButton("Export data to ankiweb", self)
        self.sync_ankiweb_button = QPushButton("Import data from ankiweb", self)
        self.sync_local_button.clicked.connect(self.sync_data_to_ankiweb)
        self.sync_ankiweb_button.clicked.connect(self.sync_data_to_local)

        # Create a QVBoxLayout instance
        self.layout = QVBoxLayout()

        # Create two QTextEdit widgets for displaying data side by side
        self.local_text_area = QTextEdit(self)
        self.local_text_area.setReadOnly(True)  # Make it read-only
        #self.local_text_area.setWordWrapMode(QTextOption.NoWrap)  # Use QTextOption::NoWrap
        self.local_text_area.setWordWrapMode(QTextOption.WrapMode.NoWrap) # Correct usage in PyQt6
        self.web_text_area = QTextEdit(self)
        self.web_text_area.setReadOnly(True)  # Make it read-only
        #self.web_text_area.setWordWrapMode(QTextOption.NoWrap)  # Use QTextOption::NoWrap
        self.web_text_area.setWordWrapMode(QTextOption.WrapMode.NoWrap) # Correct usage in PyQt6
        # Add the QLabel and QPushButtons to the layout
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.sync_local_button)
        self.layout.addWidget(self.sync_ankiweb_button)
        self.layout.addWidget(self.local_text_area)
        self.layout.addWidget(self.web_text_area)

        # Set the dialog's layout
        self.setLayout(self.layout)

    def get_pokemon_data(self):
        try:
            with open(self.mypokemon_path, 'r', encoding='utf-8') as file:
                self.pokemon_collection_sync_data = json.load(file)
            with open(self.mainpokemon_path, 'r', encoding='utf-8') as file:
                self.mainpokemon_sync_data = json.load(file)
        except Exception as e:
            self.logger.log("error", "Failed to load Pokémon data: " + str(e))
            self.pokemon_collection_sync_data = []
            self.mainpokemon_sync_data = []

    def sync_pokemons(self):
        try:
            for pokelist in [
                self.pokemon_collection_sync_data,
                self.mainpokemon_sync_data,
            ]:
                for p in pokelist:
                    if not isinstance(p.get("evos"), list):
                        p["evos"] = []
            self.mainpokemon_web_data = self.config.get('mainpokemon', [])
            self.pokemon_collection_web_data = self.config.get('pokemon_collection', [])
        except Exception as e:
            self.logger.log("error", "Failed to retrieve Pokémon data from AnkiWeb.")
            self.mainpokemon_web_data = []
            self.pokemon_collection_web_data = []
        self.get_pokemon_data()
        
        differences_exist = self.display_data_comparison()
        if differences_exist:
            self.show()

        
    def sync_data_to_local(self):
        try:
            with open(self.mypokemon_path, 'w', encoding='utf-8') as file:
                json.dump(self.pokemon_collection_web_data, file, ensure_ascii=False, indent=4)
            with open(self.mainpokemon_path, 'w', encoding='utf-8') as file:
                json.dump(self.mainpokemon_web_data, file, ensure_ascii=False, indent=4)
            showInfo("Ankiweb Data synced to local.")
        except Exception as e:
            showWarning("Failed to sync data to local: " + str(e))
        self.close()

    def sync_data_to_ankiweb(self):
        try:
            self.config.set("pokemon_collection", self.pokemon_collection_sync_data)
            self.config.set("mainpokemon", self.mainpokemon_sync_data)
            showInfo("Local Data synced to AnkiWeb.")
        except Exception as e:
            showWarning("Failed to sync data to AnkiWeb: " + str(e))
        self.close()

    def sync_on_anki_close(self):
        tooltip("Syncing PokemonData to AnkiWeb")
        self.get_pokemon_data()
        self.config.set("pokemon_collection", self.pokemon_collection_sync_data)
        self.config.set("mainpokemon", self.mainpokemon_sync_data)

    def modify_json_configuration_on_save(self, text: str) -> str:
        try:
            config = json.loads(text)
            self.get_pokemon_data()
            self.config.set("pokemon_collection", self.pokemon_collection_sync_data)
            self.config.set("mainpokemon", self.mainpokemon_sync_data)
            tooltip("Saved Ankimon Configuration, Please Restart Anki")
            modified_text = json.dumps(config, indent=4)
            return modified_text
        except json.JSONDecodeError:
            showWarning("Invalid JSON format")
            return text

    def display_pokemon_info(self, pokemon_data):
        # Display Pokémon information
        pokemon_info = (
            f"Name: {pokemon_data['name']}\n"
            f"Gender: {pokemon_data['gender']}\n"
            f"Level: {pokemon_data['level']}\n"
            f"ID: {pokemon_data['id']}\n"
            f"Ability: {pokemon_data['ability']}\n"
            f"Type: {', '.join(pokemon_data['type'])}\n"
            f"Stats:\n"
            f"  HP: {pokemon_data['stats']['hp']}\n"
            f"  Attack: {pokemon_data['stats']['atk']}\n"
            f"  Defense: {pokemon_data['stats']['def']}\n"
            f"  Special Attack: {pokemon_data['stats']['spa']}\n"
            f"  Special Defense: {pokemon_data['stats']['spd']}\n"
            f"  Speed: {pokemon_data['stats']['spe']}\n"
            f"XP: {pokemon_data['stats']['xp']}\n"
            f"EVs:\n"
            f"  HP: {pokemon_data['ev']['hp']}\n"
            f"  Attack: {pokemon_data['ev']['atk']}\n"
            f"  Defense: {pokemon_data['ev']['def']}\n"
            f"  Special Attack: {pokemon_data['ev']['spa']}\n"
            f"  Special Defense: {pokemon_data['ev']['spd']}\n"
            f"  Speed: {pokemon_data['ev']['spe']}\n"
            f"IVs:\n"
            f"  HP: {pokemon_data['iv']['hp']}\n"
            f"  Attack: {pokemon_data['iv']['atk']}\n"
            f"  Defense: {pokemon_data['iv']['def']}\n"
            f"  Special Attack: {pokemon_data['iv']['spa']}\n"
            f"  Special Defense: {pokemon_data['iv']['spd']}\n"
            f"  Speed: {pokemon_data['iv']['spe']}\n"
            f"Attacks: {', '.join(pokemon_data['attacks'])}\n"
            f"Base Experience: {pokemon_data['base_experience']}\n"
            f"Current HP: {pokemon_data['current_hp']}\n"
            f"Growth Rate: {pokemon_data['growth_rate']}\n"
            f"Evolves to: {', '.join(pokemon_data['evos'])}\n"
            f"Individual ID: {pokemon_data['individual_id']}\n"
            f"Everstone: {pokemon_data['everstone']}\n"
            f"Shiny: {pokemon_data['shiny']}\n"
            f"Friendship: {pokemon_data['friendship']}\n"
            f"Pokémon Defeated: {pokemon_data['pokemon_defeated']}\n"
            f"Captured Date: {pokemon_data['captured_date']}"
        )

        return pokemon_info

    def display_data_comparison(self):
        # Main Pokémon Data Comparison
        local_main_differences = []
        web_main_differences = []

        for local, ankiweb in zip(self.mainpokemon_sync_data, self.mainpokemon_web_data):
            pokemon_name = local.get('name', "Unknown")
            individual_id = local.get('individual_id', "Unknown")
            for key in set(local.keys()).union(ankiweb.keys()):
                local_value = local.get(key, [])
                web_value = ankiweb.get(key, [])
                if local_value != web_value:
                    local_main_differences.append(f"{pokemon_name} - {individual_id} - {key}: {local_value}")
                    web_main_differences.append(f"{pokemon_name} - {individual_id} - {key}: {web_value}")        

        # Pokémon Collection Data Comparison
        local_pokemon_differences = []
        web_pokemon_differences = []

        for local, ankiweb in zip(self.pokemon_collection_sync_data, self.pokemon_collection_web_data):
            pokemon_name = local.get('name', "Unknown")
            individual_id = local.get('individual_id', "Unknown")
            for key in set(local.keys()).union(ankiweb.keys()):
                local_value = local.get(key, [])
                web_value = ankiweb.get(key, [])
                if local_value != web_value:
                    local_pokemon_differences.append(f"{pokemon_name} - {individual_id} - {key}: {local_value}")
                    web_pokemon_differences.append(f"{pokemon_name} - {individual_id} - {key}: {web_value}")

        # Prepare the local text content
        local_text_content = ""

        # Main Pokémon Data Differences
        if local_main_differences:
            local_text_content += f"**Main Pokémon Local Data Differences:**\n\n" + "\n".join(local_main_differences) + "\n\n"

        # Pokémon Collection Data Differences
        if local_pokemon_differences:
            local_text_content += f"**Pokémon Collection Local Data Differences:**\n\n" + "\n".join(local_pokemon_differences)

        # Set the local text area with the prepared content
        self.local_text_area.setPlainText(local_text_content)

        # Prepare the web text content
        web_text_content = ""

        # Main Pokémon Web Data Differences
        if web_main_differences:
            web_text_content += f"**Main Pokémon Web Data Differences:**\n\n" + "\n".join(web_main_differences) + "\n\n"

        # Pokémon Collection Web Data Differences
        if web_pokemon_differences:
            web_text_content += f"**Pokémon Collection Web Data Differences:**\n\n" + "\n".join(web_pokemon_differences)
        
        # Set the web text area with the prepared content
        self.web_text_area.setPlainText(web_text_content)
        
        any_differences = bool(local_main_differences or web_main_differences or local_pokemon_differences or web_pokemon_differences)
        return any_differences
