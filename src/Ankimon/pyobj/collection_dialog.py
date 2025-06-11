from ..resources import mypokemon_path, frontdefault, user_path_sprites
from ..gui_entities import MovieSplashLabel
from ..functions.pokedex_functions import search_pokeapi_db_by_id, get_pokemon_diff_lang_name
import json
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from ..gui_classes.pokemon_details import PokemonCollectionDetails
from aqt import mw
from aqt.utils import showInfo, showWarning
from ..functions.sprite_functions import get_sprite_path

class ClickableWidget(QWidget):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()

class PokemonCollectionDialog(QDialog):
    def __init__(self, logger, settings_obj, mainpokemon_function, main_pokemon, parent=mw):
        super().__init__(parent)

        # Logger and settings object
        self.logger = logger
        self.settings = settings_obj
        self.language = int(self.settings.get("misc.language", 11))
        self.remove_levelcap = settings_obj.get("remove_levelcap", False)
        self.main_pokemon_function_callback = mainpokemon_function
        self.main_pokemon = main_pokemon
        self.mypokemon_path = mypokemon_path
        self.gif_in_collection = self.settings.get("gui.gif_in_collection", 11)

        # Paginator variables
        self.current_page = 0
        self.items_per_page = 9
        self.pokemon_list = []

        self.setWindowTitle("Captured Pokemon")
        self.setMinimumWidth(750)
        self.setMinimumHeight(400)
        self.layout = QVBoxLayout(self)

        # Add Widget to sort by ID
        self.sort_checkbox = QCheckBox("Sort by ID")
        self.sort_checkbox.stateChanged.connect(lambda: self.sort_pokemon() if self.sort_checkbox.isChecked() else self.filter_pokemon())

        # Search Filter
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search Pokémon (by nickname, name)")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(lambda: self.sort_pokemon() if self.sort_checkbox.isChecked() else self.filter_pokemon())

        # Add dropdown menu for generation filtering
        self.generation_combo = QComboBox()
        self.generation_combo.addItem("All")
        self.generation_combo.addItems(["Generation 1", "Generation 2", "Generation 3", "Generation 4", "Generation 5", "Generation 6", "Generation 7", "Generation 8"])
        self.generation_combo.currentIndexChanged.connect(lambda: self.sort_pokemon() if self.sort_checkbox.isChecked() else self.filter_pokemon())

        # Add dropdown menu for type filtering
        self.type_combo = QComboBox()
        self.type_combo.addItem("All")
        self.type_combo.addItems(["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"])
        self.type_combo.currentIndexChanged.connect(lambda: self.sort_pokemon() if self.sort_checkbox.isChecked() else self.filter_pokemon())

        # Add widgets to filter layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.search_edit)
        filter_layout.addWidget(self.search_button)
        filter_layout.addWidget(self.generation_combo)
        filter_layout.addWidget(self.type_combo)
        filter_layout.addWidget(self.sort_checkbox)
        self.layout.addLayout(filter_layout)

        # Content layout for grid and details
        self.content_layout = QHBoxLayout()

        # Scroll area for Pokémon grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.container = QWidget()
        self.scroll_layout = QGridLayout(self.container)
        self.scroll_area.setWidget(self.container)
        self.content_layout.addWidget(self.scroll_area, stretch=3)

        # Details scroll area
        self.details_scroll = QScrollArea()
        self.details_scroll.setWidgetResizable(True)
        self.details_scroll.setMinimumWidth(500)
        self.default_widget = QWidget()
        self.default_layout = QVBoxLayout(self.default_widget)
        self.default_label = QLabel("Select a Pokémon to view details")
        self.default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.default_layout.addWidget(self.default_label)
        self.details_scroll.setWidget(self.default_widget)
        self.content_layout.addWidget(self.details_scroll, stretch=1)

        # Add content layout to main layout
        self.layout.addLayout(self.content_layout)

        # Paginator
        self.paginator = QWidget()
        self.pagination_layout = QHBoxLayout(self.paginator)
        self.layout.addWidget(self.paginator)

        # Track selected container
        self.selected_container = None

    def showEvent(self, event):
        self.current_page = 0
        pokemon_list = self.load_pokemon_data()
        self.refresh_collection(pokemon_list)

    def load_pokemon_data(self):
        """Reads the mypokemon.json file and loads Pokémon data into self.pokemon_list."""
        try:
            with open(self.mypokemon_path, "r", encoding="utf-8") as file:
                self.pokemon_list = json.load(file)
                return self.pokemon_list
        except FileNotFoundError:
            self.logger.log("error", "mypokemon.json file not found.")
        except json.JSONDecodeError:
            self.logger.log("error", "mypokemon.json file not found.")

    def refresh_pokemon_collection(self):
        """Clear all items from the scroll layout that display Pokémon."""
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

    def refresh_paginator_layout(self):
        """Clear all items from the pagination layout."""
        while self.pagination_layout.count():
            item = self.pagination_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()
                
    def _make_default_widget(self) -> QWidget:
        """Return a new ‘nothing-selected’ placeholder widget."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lbl = QLabel("Select a Pokémon to view details")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(lbl)
        return w
    
    def refresh_collection(self, pokemon_list=None):
        """
        Clear the grid + paginator and rebuild them.
        A *new* placeholder widget is created every time to avoid using
        a QWidget that Qt has already deleted.
        """
        if pokemon_list is None:
            pokemon_list = self.pokemon_list

        # wipe the old grid and paginator
        self.refresh_pokemon_collection()
        self.refresh_paginator_layout()

        # reset selection border
        if self.selected_container:
            self.selected_container.setStyleSheet("")
            self.selected_container = None

        # --- create a brand-new placeholder and show it ----------------
        self.default_widget = self._make_default_widget()
        self.details_scroll.setWidget(self.default_widget)

        # rebuild the grid and paginator
        self.setup_ui(pokemon_list)
        
    def setup_ui(self, pokemon_list=[]):
        try:
            start_index = self.current_page * self.items_per_page
            end_index = start_index + self.items_per_page
            paginated_pokemon = pokemon_list[start_index:end_index]

            row, column = 0, 0
            for pokemon in paginated_pokemon:
                pokemon_id = pokemon['id']
                pokemon_name = pokemon['name']
                pokemon_shiny = pokemon.get("shiny", False)
                pokemon_nickname = pokemon.get('nickname') or ''
                if pokemon_shiny:
                    pokemon_nickname += " ⭐ "
                pokemon_gender = pokemon.get("gender", "M")
                pokemon_level = pokemon['level']
                pokemon_ability = pokemon['ability']
                pokemon_type = pokemon['type']
                pokemon_stats = pokemon['stats']
                if pokemon_shiny:
                    pokemon_name += " ⭐ "
                pkmn_image_path = get_sprite_path(
                    "front",
                    "gif" if self.gif_in_collection else "png",
                    pokemon_id,
                    pokemon_shiny,
                    pokemon_gender
                )

                if self.gif_in_collection:
                    splash_label = MovieSplashLabel(pkmn_image_path)
                    splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    pixmap = QPixmap(pkmn_image_path)
                    pixmap = self.adjust_pixmap_size(pixmap, max_width=300, max_height=230)
                    image_label = QLabel()
                    image_label.setPixmap(pixmap)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                name_label = self.create_label(
                    pokemon_nickname or f"{pokemon_name.capitalize()} {self.get_gender_symbol(pokemon_gender)}", 12
                )
                level_label = self.create_label(f"Level: {pokemon_level}", 8)
                type_label = self.create_label("Type: " + " ".join([t.capitalize() for t in pokemon_type]), 8)
                ability_label = self.create_label(f"Ability: {pokemon_ability.capitalize()}", 8)

                choose_pokemon_button = self.create_button("Pick as main Pokemon", pokemon, "Pick As Main")

                container_layout = QVBoxLayout()
                if self.gif_in_collection:
                    container_layout.addWidget(splash_label)
                else:
                    container_layout.addWidget(image_label)

                container_layout.addWidget(name_label)
                container_layout.addWidget(level_label)
                container_layout.addWidget(type_label)
                container_layout.addWidget(ability_label)
                container_layout.addWidget(choose_pokemon_button)

                pokemon_container = ClickableWidget()
                pokemon_container.setLayout(container_layout)
                pokemon_container.clicked.connect(lambda p=pokemon, c=pokemon_container: self.show_pokemon_details_on_panel(p, c))

                self.scroll_layout.addWidget(pokemon_container, row, column)
                column += 1
                if column >= 3:
                    column = 0
                    row += 1

            self.add_pagination_controls(pokemon_list)

        except FileNotFoundError:
            self.layout.addWidget(QLabel(f"Can't open the Saving File. {mypokemon_path}"))

    def show_pokemon_details_on_panel(self, pokemon, container):
        if self.selected_container:
            self.selected_container.setStyleSheet("")
        self.selected_container = container
        self.selected_container.setStyleSheet("border: 3px solid #00BFFF; background-color: rgba(0, 191, 255, 0.1);")

        details_widget = PokemonCollectionDetails(
            name=pokemon['name'],
            level=pokemon['level'],
            id=pokemon['id'],
            shiny=pokemon.get("shiny", False),
            ability=pokemon['ability'],
            type=pokemon['type'],
            detail_stats=pokemon['stats'],
            attacks=pokemon['attacks'],
            base_experience=pokemon.get('base_experience', 'Unknown'),
            growth_rate=pokemon.get('growth_rate', 'Unknown'),
            ev=pokemon.get('ev', {}),
            iv=pokemon.get('iv', {}),
            gender=pokemon['gender'],
            nickname=pokemon.get('nickname', 'None'),
            individual_id=pokemon.get('individual_id', 'Unknown'),
            pokemon_defeated=pokemon.get('pokemon_defeated', 0),
            everstone=pokemon.get('everstone', False),
            captured_date=pokemon.get('captured_date', 'Missing'),
            language=self.language,
            gif_in_collection=self.gif_in_collection,
            remove_levelcap=self.remove_levelcap,
            logger=self.logger,
            refresh_callback=self.refresh_collection,
        )
        self.details_scroll.setWidget(details_widget)

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
        font.setPointSize(int(font_size))
        label.setFont(font)
        return label

    def create_button(self, text, pokemon_data, button_type):
        pkmn_image_path = frontdefault / f"{pokemon_data['id']}.png"
        if not pkmn_image_path.exists():
            pkmn_image_path = frontdefault / "placeholder.png"
        button = QPushButton(text)
        if button_type == "Pick As Main":
            pixmap = QPixmap(str(pkmn_image_path))
            if not pixmap.isNull():
                button.setIcon(QIcon(pixmap))
                small_icon_size = QSize(32, 32)
                button.setIconSize(small_icon_size)
            button.clicked.connect(lambda state: self.main_pokemon_function_callback(pokemon_data))
        return button

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
                        if pokemon.get("shiny", False):
                            pokemon_name += " (shiny) "
                        pokemon_nickname = pokemon.get('nickname') or ''
                        if pokemon.get("shiny", False):
                            pokemon_nickname += " (shiny) "
                        pokemon_type = pokemon.get("type", " ")
                        if (
                            (search_text.lower() in pokemon_name.lower() or 
                            (pokemon_nickname is not None and search_text.lower() in pokemon_nickname.lower()))
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
                    self.refresh_collection(filtered_pokemon)
                    if not filtered_pokemon:
                        showInfo("No Pokemon for the desired filter options!")
                    self.current_page = 0
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
        sorted_pokemon_list = sorted(pokemon_list, key=lambda x: x['id'])
        try:
            if sorted_pokemon_list:
                for position, pokemon in enumerate(sorted_pokemon_list):
                    pokemon_id = pokemon['id']
                    pokemon_name = pokemon['name'].lower()
                    if pokemon.get("shiny", False):
                        pokemon_name += " (shiny) "
                    pokemon_nickname = pokemon.get('nickname') or ''
                    if pokemon.get("shiny", False):
                        pokemon_nickname += " (shiny) "
                    pokemon_type = pokemon.get("type", " ")
                    if (
                        (search_text.lower() in pokemon_name.lower() or 
                        (pokemon_nickname is not None and search_text.lower() in pokemon_nickname.lower()))
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
                self.refresh_collection(filtered_pokemon)
                if not filtered_pokemon:
                    showInfo("No Pokemon for the desired filter options!")
                self.current_page = 0
        except FileNotFoundError:
            self.layout.addWidget(QLabel(f"Can't open the Saving File. {mypokemon_path}"))

    def add_pagination_controls(self, pokemon_list=[]):
        self.pagination_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_pages = (len(pokemon_list) + self.items_per_page - 1) // self.items_per_page
        if self.current_page > 0:
            prev_button = QPushButton("Previous")
            prev_button.clicked.connect(lambda: self.previous_page(pokemon_list))
            self.pagination_layout.addWidget(prev_button)
        if self.current_page < total_pages - 1:
            next_button = QPushButton("Next")
            next_button.clicked.connect(lambda: self.next_page(pokemon_list))
            self.pagination_layout.addWidget(next_button)

    def next_page(self, pokemon_list):
        self.current_page += 1
        self.refresh_collection(pokemon_list)

    def previous_page(self, pokemon_list):
        self.current_page -= 1
        self.refresh_collection(pokemon_list)

from aqt.utils import showWarning
from ..resources import mainpokemon_path

def PokemonTrade(name, id, level, ability, iv, ev, gender, attacks, position):
     # Load the data from the file
    with open(mainpokemon_path, "r", encoding="utf-8") as file:
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
        with open(mypokemon_path, "r", encoding="utf-8") as file:
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
