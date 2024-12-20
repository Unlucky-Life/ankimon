from ..resources import mypokemon_path, frontdefault, user_path_sprites, frontdefault
from ..gui_entities import MovieSplashLabel
from ..functions.pokedex_functions import search_pokeapi_db_by_id, get_pokemon_diff_lang_name
import json
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from ..gui_classes.pokemon_details import PokemonCollectionDetails
from aqt import mw

class PokemonCollectionDialog(QDialog):
    def __init__(self, logger, settings_obj, mainpokemon_function, main_pokemon, parent=mw):
        super().__init__(parent)

        #logger and settings object
        self.logger = logger
        self.settings = settings_obj
        self.language = int(self.settings.get("misc.language", 11))
        self.remove_levelcap = settings_obj.get("remove_levelcap", False)
        self.main_pokemon_function_callback = mainpokemon_function
        self.main_pokemon = main_pokemon
        #mypokemon file path
        self.mypokemon_path = mypokemon_path

        self.gif_in_collection = self.settings.get("gui.gif_in_collection", 11)

        # Initialize the Pokémon list as an empty list
        self.pokemon_list = []

        self.setWindowTitle("Captured Pokemon")
        self.setMinimumWidth(750)
        self.setMinimumHeight(400)
        self.layout = QVBoxLayout(self)

        #add Widget to sort by ID
        self.sort_checkbox = QCheckBox("Sort by ID")
        self.sort_checkbox.stateChanged.connect(lambda: self.sort_pokemon() if self.sort_checkbox.isChecked() else self.filter_pokemon())

        # Search Filter
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search Pokémon (by nickname, name)")
        #self.search_edit.textChanged.connect(self.filter_pokemon)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(lambda: self.sort_pokemon() if self.sort_checkbox.isChecked() else self.filter_pokemon())

        # Add dropdown menu for generation filtering
        self.generation_combo = QComboBox()
        self.generation_combo.addItem("All")
        self.generation_combo.addItems(["Generation 1", "Generation 2", "Generation 3", "Generation 4", "Generation 5", "Generation 6", "Generation 7", "Generation 8"])
        self.generation_combo.currentIndexChanged.connect(lambda: self.sort_pokemon() if self.sort_checkbox.isChecked() else self.filter_pokemon())

        # Add dropdown menu for generation filtering
        self.type_combo = QComboBox()
        self.type_combo.addItem("All")
        self.type_combo.addItems(["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"])
        self.type_combo.currentIndexChanged.connect(lambda: self.sort_pokemon() if self.sort_checkbox.isChecked() else self.filter_pokemon())

        # Add widgets to layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.search_edit)
        filter_layout.addWidget(self.search_button)
        filter_layout.addWidget(self.generation_combo)
        filter_layout.addWidget(self.type_combo)
        filter_layout.addWidget(self.sort_checkbox)
        self.layout.addLayout(filter_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget()
        self.scroll_layout = QGridLayout(self.container)

    def showEvent(self, event):
        # Call refresh_pokemon_collection when the dialog is shown
        self.refresh_pokemon_collection()
        pokemon_list = self.load_pokemon_data()
        self.setup_ui(pokemon_list)

    def load_pokemon_data(self):
        """Reads the mypokemon.json file and loads Pokémon data into self.pokemon_list."""
        try:
            with open(self.mypokemon_path, 'r') as file:
                self.pokemon_list = json.load(file)
                return self.pokemon_list
        except FileNotFoundError:
            self.logger.log("error","mypokemon.json file not found.")
        except json.JSONDecodeError:
            self.logger.log("error","mypokemon.json file not found.")

    def refresh_pokemon_collection(self):
        # Clear previous contents
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
    
    def refresh_collection(self):
        self.refresh_pokemon_collection()
        self.load_pokemon_data()
        self.setup_ui(self.pokemon_list)

    def setup_ui(self, pokemon_list=[]):
        try:
            row, column = 0, 0
            for position, pokemon in enumerate(pokemon_list):
                # Extract Pokemon data
                pokemon_id = pokemon['id']
                pokemon_name = pokemon['name']
                pokemon_nickname = pokemon.get('nickname','')
                pokemon_gender = pokemon['gender']
                pokemon_level = pokemon['level']
                pokemon_ability = pokemon['ability']
                pokemon_type = pokemon['type']
                pokemon_stats = pokemon['stats']
                pokemon_hp = pokemon_stats["hp"]
                pokemon_attacks = pokemon['attacks']
                pokemon_base_experience = pokemon['base_experience']
                pokemon_growth_rate = pokemon['growth_rate']
                pokemon_ev = pokemon['ev']
                pokemon_iv = pokemon['iv']
                pokemon_description = search_pokeapi_db_by_id(pokemon_id, "description")
                pkmn_image_path = str(frontdefault / f"{pokemon_id}.png")
                if self.gif_in_collection:
                    pkmn_image_path = str(user_path_sprites / "front_default_gif" / f"{pokemon_id}.gif")
                    splash_label = MovieSplashLabel(pkmn_image_path)

                # Load image and adjust size
                pixmap = QPixmap(pkmn_image_path)
                pixmap = self.adjust_pixmap_size(pixmap, max_width=300, max_height=230)

                # Create UI elements
                name_label = self.create_label(pokemon_nickname or f"{get_pokemon_diff_lang_name(int(pokemon_id), self.language).capitalize()} {self.get_gender_symbol(pokemon_gender)}", 12)
                level_label = self.create_label(f"Level: {pokemon_level}", 8)
                type_label = self.create_label("Type: " + " ".join([t.capitalize() for t in pokemon_type]), 8)
                ability_label = self.create_label(f"Ability: {pokemon_ability.capitalize()}", 8)

                image_label = QLabel()
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # Create buttons
                pokemon_button = self.create_button("Show me Details", pokemon, "Show Details")
                choose_pokemon_button = self.create_button("Pick as main Pokemon", pokemon, "Pick As Main")


                # Setup layout
                container_layout = QVBoxLayout()
                container_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
                if self.gif_in_collection:
                    container_layout.addWidget(splash_label)
                    splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    container_layout.addWidget(image_label)
                container_layout.addWidget(name_label)
                container_layout.addWidget(level_label)
                container_layout.addWidget(type_label)
                container_layout.addWidget(ability_label)
                container_layout.addWidget(pokemon_button)
                container_layout.addWidget(choose_pokemon_button)

                pokemon_container = QWidget()
                pokemon_container.setLayout(container_layout)

                # Add to layout
                self.scroll_layout.addWidget(pokemon_container, row, column)
                column += 1
                if column >= 3:
                    column = 0
                    row += 1

            self.container.setLayout(self.scroll_layout)
            self.scroll_area.setWidget(self.container)
            self.layout.addWidget(self.scroll_area)
            self.setLayout(self.layout)
        except FileNotFoundError:
            self.layout.addWidget(QLabel(f"Can't open the Saving File. {mypokemon_path}"))

    def adjust_pixmap_size(self, pixmap, max_width, max_height):
        original_width = pixmap.width()
        original_height = pixmap.height()

        if original_width > max_width:
            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pixmap = pixmap.scaled(new_width, new_height)

        return pixmap

    def create_label(self, text, font_size):
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        font = QFont()
        font.setPointSize(font_size)
        label.setFont(font)
        return label

    def create_button(self, text, pokemon_data, button_type):
        pkmn_image_path = frontdefault / f"{pokemon_data['id']}.png"
        
        # Ensure the image path exists, else fallback
        if not pkmn_image_path.exists():
            pkmn_image_path = frontdefault / "placeholder.png"

        button = QPushButton(text)

        # Set button action
        if button_type == "Show Details":
            button.clicked.connect(lambda state: self.show_pokemon_details(pokemon_data))
        elif button_type == "Pick As Main":
            pixmap = QPixmap(str(pkmn_image_path))
            if not pixmap.isNull():
                button.setIcon(QIcon(pixmap))
                # Set a smaller custom size for the icon (e.g., 32x32 pixels)
                small_icon_size = QSize(32, 32)  # Change 32 to your preferred size
                button.setIconSize(small_icon_size)
            button.clicked.connect(lambda state: self.main_pokemon_function_callback(pokemon_data))
        
        return button

    def show_pokemon_details(self, pokemon, **kwargs):
        PokemonCollectionDetails(
            name=pokemon['name'],
            level=pokemon['level'],
            id=pokemon['id'],
            ability=pokemon['ability'],
            type=pokemon['type'],
            detail_stats=pokemon['stats'],
            attacks=pokemon['attacks'],
            base_experience=pokemon['base_experience'],
            growth_rate=pokemon['growth_rate'],
            ev=pokemon['ev'],
            iv=pokemon['iv'],
            gender=pokemon['gender'],
            nickname=pokemon.get('nickname'),
            individual_id=pokemon.get('individual_id'),
            language=self.language,
            gif_in_collection=self.gif_in_collection,
            remove_levelcap=self.remove_levelcap,
            logger=self.logger,
            refresh_callback=self.refresh_collection,
        )

    def get_gender_symbol(self, gender):
        if gender == "M":
            return "♂"
        elif gender == "F":
            return "♀"
        else:
            return ""
        
    def filter_pokemon(self):
        filtered_pokemon = []
        pokemon_list = self.pokemon_list
        if not self.sort_checkbox.isChecked():
            type_index = self.type_combo.currentIndex()
            type_text = self.type_combo.currentText()
            search_text = self.search_edit.text().lower()
            generation_index = self.generation_combo.currentIndex()
            
            try:                  
                if pokemon_list:
                    for position, pokemon in enumerate(pokemon_list):
                        pokemon_id = pokemon['id']
                        pokemon_name = pokemon['name'].lower()
                        pokemon_nickname = pokemon.get("nickname", None)
                        pokemon_type = pokemon.get("type", " ")
                        
                        # Check if the Pokémon matches the search text and generation filter
                        if (
                            search_text.lower() in pokemon_name.lower() or 
                            (pokemon_nickname is not None and search_text.lower() in pokemon_nickname.lower())
                        ) and \
                        0 <= generation_index <= 8 and \
                        (
                            generation_index == 0 or
                            (1 <= pokemon_id <= 151 and generation_index == 1) or
                            (152 <= pokemon_id <= 251 and generation_index == 2) or
                            (252 <= pokemon_id <= 386 and generation_index == 3) or
                            (387 <= pokemon_id <= 493 and generation_index == 4) or
                            (494 <= pokemon_id <= 649 and generation_index == 5) or
                            (650 <= pokemon_id <= 721 and generation_index == 6) or
                            (722 <= pokemon_id <= 809 and generation_index == 7) or
                            (810 <= pokemon_id <= 898 and generation_index == 8)
                        ) and \
                        (
                            type_index == 0 or type_text in pokemon_type
                        ):
                            filtered_pokemon.append(pokemon)
                    self.refresh_pokemon_collection()
                    self.setup_ui(filtered_pokemon)
            except FileNotFoundError:
                self.layout.addWidget(QLabel(f"Can't open the Saving File. {mypokemon_path}"))
        else:
            self.sort_pokemon()
    
    def sort_pokemon(self):
        filtered_pokemon = []
        pokemon_list = self.pokemon_list
        search_text = self.search_edit.text().lower()
        generation_index = self.generation_combo.currentIndex()
        type_index = self.type_combo.currentIndex()
        type_text = self.type_combo.currentText()
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        try:
            if pokemon_list:
                for position, pokemon in enumerate(pokemon_list):
                    pokemon_id = pokemon['id']
                    pokemon_name = pokemon['name'].lower()
                    pokemon_nickname = pokemon.get("nickname", None)
                    pokemon_type = pokemon.get("type", " ")
                    # Check if the Pokémon matches the search text and generation filter
                    if (
                        search_text.lower() in pokemon_name.lower() or 
                        (pokemon_nickname is not None and search_text.lower() in pokemon_nickname.lower())
                    ) and \
                    0 <= generation_index <= 8 and \
                    (
                        generation_index == 0 or
                        (1 <= pokemon_id <= 151 and generation_index == 1) or
                        (152 <= pokemon_id <= 251 and generation_index == 2) or
                        (252 <= pokemon_id <= 386 and generation_index == 3) or
                        (387 <= pokemon_id <= 493 and generation_index == 4) or
                        (494 <= pokemon_id <= 649 and generation_index == 5) or
                        (650 <= pokemon_id <= 721 and generation_index == 6) or
                        (722 <= pokemon_id <= 809 and generation_index == 7) or
                        (810 <= pokemon_id <= 898 and generation_index == 8)
                    ) and \
                    (
                        type_index == 0 or type_text in pokemon_type
                    ):

                        filtered_pokemon.append(pokemon)
                self.refresh_pokemon_collection()
                self.setup_ui(filtered_pokemon)
        except FileNotFoundError:
            self.layout.addWidget(QLabel(f"Can't open the Saving File. {mypokemon_path}"))

from aqt.utils import showWarning
from ..resources import mainpokemon_path

def PokemonTrade(name, id, level, ability, iv, ev, gender, attacks, position):
     # Load the data from the file
    with open(mainpokemon_path, 'r') as file:
        pokemon_data = json.load(file)
    #check if player tries to trade mainpokemon
    found = False
    for pokemons in pokemon_data:
        if pokemons["name"] == name and pokemons["id"] == id and pokemons["level"] == level and pokemons["ability"] == ability and pokemons["iv"] == iv and pokemons["ev"] == ev and pokemons["gender"] == gender and pokemons["attacks"] == attacks:
            found = True
            break

    if not found:
        # Create a main window
        window = QDialog()
        window.setWindowTitle(f"Trade Pokemon {name}")
        # Create an input field for error code
        trade_code_input = QLineEdit()
        trade_code_input.setPlaceholderText("Enter Pokemon Code you want to Trade for")

        # Create a button to save the input
        trade_button = QPushButton("Trade Pokemon")
        qconnect(trade_button.clicked, lambda: PokemonTradeIn(trade_code_input.text(), name, position))
        # Information label
        info = "Pokemon Infos have been Copied to your Clipboard! \nNow simply paste this text into Teambuilder in PokemonShowdown. \nNote: Fight in the [Gen 9] Anything Goes - Battle Mode"

        pokemon_ev = ','.join([f"{value}" for stat, value in ev.items()])
        pokemon_iv = ','.join([f"{value}" for stat, value in iv.items()])
        if gender == "M":
            gender = 0
        elif gender == "F":
            gender = 1
        elif gender == "N":
            gender = 2
        else:
            gender = 3 #None

        attacks_ids = []
        for attack in attacks:
            attack = attack.replace(" ", "").lower()
            move_details = find_details_move(attack)
            if move_details:
                attacks_ids.append(str(move_details["num"]))

        attacks_id_string = ','.join(attacks_ids)  # Concatenated with a delimiter

        # Concatenating details to form a single string
        info = f"{id},{level},{gender},{pokemon_ev},{pokemon_iv},{attacks_id_string}"

        Trade_Info = QLabel(f"{name} Code: {info}")

        # Create a layout and add the labels
        layout = QVBoxLayout()
        layout.addWidget(Trade_Info)
        layout.addWidget(trade_code_input)
        layout.addWidget(trade_button)
        layout.addWidget(trade_code_input)
        # Set the layout for the main window
        window.setLayout(layout)

        # Copy text to clipboard in Anki
        mw.app.clipboard().setText(f"{info}")

        window.exec()
    else:
        showWarning("You cant trade your Main Pokemon ! \n Please pick a different Main Pokemon and then you can trade this one.")


def PokemonTradeIn(number_code, old_pokemon_name, position):
    if len(number_code) > 15:
        # Split the string into a list of integers
        numbers = [int(num) for num in number_code.split(',')]

        # Extracting specific parts of the list
        pokemon_id = numbers[0]
        level = numbers[1]
        gender_id = numbers[2]
        ev_stats = {'hp': numbers[3], 'atk': numbers[4], 'def': numbers[5], 'spa': numbers[6], 'spd': numbers[7],
                    'spe': numbers[8]}
        iv_stats = {'hp': numbers[9], 'atk': numbers[10], 'def': numbers[11], 'spa': numbers[12], 'spd': numbers[13],
                    'spe': numbers[14]}
        attack_ids = numbers[15:]
        attacks = []
        for attack_id in attack_ids:
            move = find_move_by_num(int(attack_id))
            attacks.append(move['name'])
        details = find_pokemon_by_id(pokemon_id)
        name = details["name"]
        type = details["types"]
        if gender_id == 0:
            gender = "M"
        elif gender_id == 1:
            gender = "F"
        elif gender_id == 2:
            gender = "N"
        else:
            gender = None #None
        stats = details["baseStats"]
        evos = details.get("evos", "None")
        #type = search_pokedex(name, "types")
        #stats = search_pokedex(name, "baseStats")
        with open(str(pokeapi_db_path), "r") as json_file:
            pokemon_data = json.load(json_file)
            for pokemon in pokemon_data:
                if pokemon["id"] == pokemon_id:
                    growth_rate = pokemon["growth_rate"]
        # Creating a dictionary to organize the extracted information
        stats["xp"] = 0
        pokemon_trade = {
                "name": name,
                "gender": gender,
                "ability": ability,
                "level": level,
                "id": pokemon_id,
                "type": type,
                "stats": stats,
                "ev": ev_stats,
                "iv": iv_stats,
                "attacks": attacks,
                "base_experience": base_experience,
                "current_hp": calculate_hp(stats["hp"], level, ev, iv),
                "growth_rate": growth_rate,
                "evos": evos
        }
        trade_pokemon(f"{old_pokemon_name}", pokemon_trade, position)
        logger.log_and_showinfo("info",f"You have sucessfully traded your {old_pokemon_name} for {name} ")
    else:
        showWarning("Please enter a valid Code !")

from aqt.utils import showWarning

def trade_pokemon(old_pokemon_name, pokemon_trade, position):
    try:
        # Load the current list of Pokemon
        with open(mypokemon_path, 'r') as file:
            pokemon_list = json.load(file)
    except FileNotFoundError:
        print("The Pokemon file was not found. Please check the file path.")
        return
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    # Find and replace the specific Pokemon's information
    for i, pokemon in enumerate(pokemon_list):
        pokemon_list[position] = pokemon_trade  # Replace with new Pokemon data
        break
    else:
        showWarning("info",f"Pokemon named '{old_pokemon_name}' not found.")
        return

    # Write the updated data back to the file
    try:
        with open(mypokemon_path, 'w') as file:
            json.dump(pokemon_list, file, indent=2)
        showWarning(f"{old_pokemon_name} has been traded successfully!")
    except Exception as e:
        showWarning(f"An error occurred while writing to the file: {e}")