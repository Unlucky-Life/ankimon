from pathlib import Path
import random
import json
from typing import Any

from aqt import mw
from aqt.qt import (
    QGridLayout,
    QPixmap,
    Qt,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QComboBox,
    QLineEdit,
    QScrollArea,
)

from Ankimon.pyobj.InfoLogger import ShowInfoLogger
from Ankimon.pyobj.evolution_window import EvoWindow
from Ankimon.pyobj.pokemon_obj import PokemonObject
from Ankimon.pyobj.starter_window import StarterWindow

from ..business import (
    get_id_and_description_by_item_name
)
from ..functions.pokedex_functions import (
    search_pokedex_by_id,
    return_id_for_item_name,
    check_evolution_by_item,
)
from ..resources import mypokemon_path, icon_path, items_path, itembag_path
from ..functions.badges_functions import check_for_badge, receive_badge
from ..functions.pokemon_functions import save_fossil_pokemon
from ..utils import play_effect_sound
from .error_handler import show_warning_with_traceback

# At the moment when I write this line, "UserRole" is defined as UserRole 1000 in the Ankimon __init__.py file. IDK what it's about.
UserRole = 1000

class ItemWindow(QWidget):
    def __init__(
            self,
            logger: ShowInfoLogger,
            main_pokemon: PokemonObject,
            enemy_pokemon: PokemonObject,
            itembagpath: Path,
            achievements: dict[str, bool],
            starter_window: StarterWindow,
            evo_window: EvoWindow
            ):
        super().__init__()
        self.itembag_path: Path = itembagpath
        self.logger: ShowInfoLogger = logger
        self.main_pokemon: PokemonObject = main_pokemon
        self.enemy_pokemon: PokemonObject = enemy_pokemon
        self.achievements: dict[str, bool] = achievements
        self.starter_window: StarterWindow = starter_window
        self.evo_window: EvoWindow = evo_window
        self.initUI()

    def initUI(self):
        self.hp_heal_items = {
            'potion': 20,
            'sweet-heart': 20,
            'berry-juice': 20,
            'fresh-water': 30,
            'soda-pop': 50,
            'super-potion': 60,
            'energy-powder': 60,
            'lemonade': 70,
            'moomoo-milk': 100,
            'hyper-potion': 120,
            'energy-root': 120,
            'full-restore': 1000,
            'max-potion': 1000
        }

        self.fossil_pokemon = {
            "helix-fossil": 138,
            "dome-fossil": 140,
            "old-amber": 142,
            "root-fossil": 345,
            "claw-fossil": 347,
            "skull-fossil": 408,
            "armor-fossil": 410,
            "cover-fossil": 564,
            "plume-fossil": 566
        }

        self.pokeball_chances = {
            'dive-ball': 11,      # Increased chance when fishing or underwater
            'dusk-ball': 11,      # Increased chance at night or in caves
            'great-ball': 12,     # Increased catch rate (original was 9, now 12)
            'heal-ball': 12,      # Same as a Poké Ball but heals the Pokémon
            'iron-ball': 12,      # Used for Steel-type Pokémon, 1.5x chance
            'light-ball': 1,      # Not actually used for catching Pokémon; it's an item
            'luxury-ball': 12,    # Same as a Poké Ball but increases happiness
            'master-ball': 100,   # Guarantees a successful catch (100% chance)
            'nest-ball': 12,      # Works better on lower-level Pokémon
            'net-ball': 12,       # Higher chance for Water- and Bug-type Pokémon
            'poke-ball': 8,       # Increased chance from 5 to 8
            'premier-ball': 8,    # Same as Poké Ball, but it's a special ball
            'quick-ball': 13,     # High chance if used at the start of battle
            'repeat-ball': 12,    # Higher chance on Pokémon that have been caught before
            'safari-ball': 8,     # Used in Safari Zone, with a fixed catch rate
            'smoke-ball': 1,      # Used to flee from wild battles, no catch chance
            'timer-ball': 13,     # Higher chance the longer the battle goes
            'ultra-ball': 13      # Increased catch rate (original was 10, now 13)
        }

        self.evolution_items = {}

        self.setWindowIcon(QIcon(str(icon_path)))  # Add a Pokeball icon
        self.setWindowTitle("Itembag")
        self.layout = QVBoxLayout()  # Main layout is now a QVBoxLayout

        # Search Filter
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search Items...")
        self.search_edit.returnPressed.connect(self.filter_items)
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.filter_items)

        # Add dropdown menu for generation filtering
        self.category = QComboBox()
        self.category.addItem("All")
        self.category.addItems(["Fossils", "TMs and HMs", "Heal", "Evolution Items"])
        self.category.currentIndexChanged.connect(self.filter_items)

        # Add widgets to layout
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(self.search_edit)
        filter_layout.addWidget(self.search_button)
        filter_layout.addWidget(self.category)
        self.layout.addLayout(filter_layout)

        # Create the scroll area and its properties
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        # Create a widget and layout for content inside the scroll area
        self.contentWidget = QWidget()
        self.contentLayout = QGridLayout()  # The layout for items

        # FIX 1: Set equal column stretches for consistent column widths
        self.contentLayout.setColumnStretch(0, 1)  # Column 0 gets stretch factor 1
        self.contentLayout.setColumnStretch(1, 1)  # Column 1 gets stretch factor 1
        self.contentLayout.setColumnStretch(2, 1)  # Column 2 gets stretch factor 1

        # FIX 2: Set minimum column widths to ensure consistent sizing
        min_column_width = 200  # Adjust this value as needed
        self.contentLayout.setColumnMinimumWidth(0, min_column_width)
        self.contentLayout.setColumnMinimumWidth(1, min_column_width)
        self.contentLayout.setColumnMinimumWidth(2, min_column_width)

        # Set uniform spacing
        self.contentLayout.setHorizontalSpacing(10)
        self.contentLayout.setVerticalSpacing(10)

        self.contentWidget.setLayout(self.contentLayout)

        # Add the content widget to the scroll area
        self.scrollArea.setWidget(self.contentWidget)

        # Add the scroll area to the main layout
        self.layout.addWidget(self.scrollArea)
        self.setLayout(self.layout)

        # FIX 3: Increase initial window size to better accommodate 3 columns
        # Calculate appropriate width: 3 columns * min_width + spacing + margins
        initial_width = 3 * min_column_width + 2 * 10 + 40  # 3 cols + 2 spacings + margins
        initial_height = 600  # Increased from 500
        self.resize(initial_width, initial_height)

    def renewWidgets(self):
        # Clear the existing widgets from the content layout
        for i in reversed(range(self.contentLayout.count())):
            widget = self.contentLayout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        row, col = 0, 0
        max_items_per_row = 3

        itembag_list = self.read_items_file()
        if not itembag_list:  # Simplified check
            empty_label = QLabel("You don't own any items yet.")
            self.contentLayout.addWidget(empty_label, 1, 1)
        else:
            for item in itembag_list:
                item_widget = self.ItemLabel(item["item"], item["quantity"], item.get("type"))
                # FIX 4: Set consistent size policy for all item widgets
                item_widget.setMinimumWidth(180)  # Ensure minimum width for each item
                self.contentLayout.addWidget(item_widget, row, col)
                col += 1
                if col >= max_items_per_row:
                    row += 1
                    col = 0

    def filter_items(self):
        search_text = self.search_edit.text().lower()
        category_index = self.category.currentIndex()
        # Clear the existing widgets from the content layout
        for i in reversed(range(self.contentLayout.count())):
            widget = self.contentLayout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        row, col = 0, 0
        max_items_per_row = 3

        filtered_items = list(self.read_items_file())
        if not filtered_items:
            empty_label = QLabel("You don't own any items yet.")
            self.contentLayout.addWidget(empty_label, 1, 1)
            return

        try:
            # Filter items based on category index
            if category_index == 1:  # Fossils
                filtered_items = [
                    item for item in filtered_items
                    if isinstance(item, dict) and "item" in item and item["item"] in self.fossil_pokemon
                ]
            elif category_index == 2:  # TMs and HMs
                filtered_items = list(filter(lambda item: item.get("type") == "TM", filtered_items))
            elif category_index == 3:  # Heal items
                filtered_items = [
                    item for item in filtered_items
                    if isinstance(item, dict) and "item" in item and item["item"] in self.hp_heal_items
                ]
            elif category_index == 4:  # Evolution items
                filtered_items = [
                    item for item in filtered_items
                    if isinstance(item, dict) and "item" in item and item["item"] in self.evolution_items
                ]
            elif category_index == 5: # Pokeballs
                filtered_items = [
                    item for item in filtered_items
                    if isinstance(item, dict) and "item" in item and item["item"] in self.pokeball_chances
                ]

            # Now filter by search
            filtered_items = list(filter(lambda item: search_text in item["item"].lower(), filtered_items))
        except Exception as e:
            filtered_items = []
            self.logger.log_and_showinfo("error", f"Error filtering items: {e}")

        if not filtered_items:
            empty_label = QLabel("Empty Search")
            self.contentLayout.addWidget(empty_label, 1, 1)
            return

        for item in filtered_items:
            item_widget = self.ItemLabel(item["item"], item["quantity"], item.get("type"))
            # FIX 5: Ensure consistent sizing for filtered items too
            item_widget.setMinimumWidth(180)
            self.contentLayout.addWidget(item_widget, row, col)
            col += 1
            if col >= max_items_per_row:
                row += 1
                col = 0

    def ItemLabel(self, item_name: str, quantity: int, item_type: str | None):
        item_file_path = items_path / f"{item_name}.png"
        if item_type == "TM":
            item_file_path = items_path / "Bag_TM_Normal_SV_Sprite.png"
        item_frame = QVBoxLayout()  # itemframe
        info_item_button = QPushButton("More Info")
        info_item_button.clicked.connect(lambda: self.more_info_button_act(item_name))
        item_name_for_label = item_name.replace("-", " ")  # Remove hyphens from item_name
        item_name_for_label = f"{item_name_for_label.capitalize()} x{quantity}"  # Display quantity
        if item_type == "TM":
            item_name_for_label = f"TM : {item_name_for_label}"
        item_name_label = QLabel(item_name_for_label)
        item_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_picture_pixmap = QPixmap(str(item_file_path))
        item_picture_label = QLabel()
        item_picture_label.setPixmap(item_picture_pixmap)
        item_picture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_frame.addWidget(item_picture_label)
        item_frame.addWidget(item_name_label)

        item_name = item_name.lower()
        if item_name in self.hp_heal_items:
            use_item_button = QPushButton("Heal Mainpokemon")
            hp_heal = self.hp_heal_items[item_name]
            use_item_button.clicked.connect(lambda: self.Check_Heal_Item(self.main_pokemon.name, hp_heal, item_name, self.achievements))
        elif item_name in self.fossil_pokemon:
            fossil_id = self.fossil_pokemon[item_name]
            fossil_pokemon_name = search_pokedex_by_id(fossil_id)
            use_item_button = QPushButton(f"Evolve Fossil to {fossil_pokemon_name.capitalize()}")
            use_item_button.clicked.connect(lambda: self.Evolve_Fossil(item_name, fossil_id, fossil_pokemon_name))
        elif item_name in self.pokeball_chances:
            use_item_button = QPushButton("Try catching wild Pokemon")
            use_item_button.clicked.connect(lambda: self.Handle_Pokeball(item_name))
        elif item_type == "TM":
            use_item_button = QLabel()

            # FIX: Remove indentation by using textwrap.dedent() or reformatting the string
            import textwrap

            description_text = f"""Allows the user to teach {item_name.replace('-', ' ').title()} to Pokémon that can learn this move.\n\nTeaching the move doesn't consume the TM."""

            info_item_button = QLabel(textwrap.dedent(description_text).strip())

            # Enable word wrapping for TM description
            info_item_button.setWordWrap(True)
            # Optional: Set alignment for better appearance
            info_item_button.setAlignment(Qt.AlignmentFlag.AlignTop)

        else:
            use_item_button = QPushButton("Evolve Pokemon")
            use_item_button.clicked.connect(
                lambda: self.Check_Evo_Item(
                    comboBox.itemData(comboBox.currentIndex(), role=UserRole),
                    comboBox.itemData(comboBox.currentIndex(), role=UserRole + 1),
                    item_name
                    )
            )
            comboBox = QComboBox()
            self.PokemonList(comboBox)
            item_frame.addWidget(comboBox)
        item_frame.addWidget(use_item_button)
        item_frame.addWidget(info_item_button)
        item_frame_widget = QWidget()
        item_frame_widget.setLayout(item_frame)

        return item_frame_widget

    def PokemonList(self, comboBox):
        try:
            with open(mypokemon_path, "r", encoding="utf-8") as json_file:
                captured_pokemon_data = json.load(json_file)
                if captured_pokemon_data:
                    for pokemon in captured_pokemon_data:
                        pokemon_name = pokemon['name']
                        individual_id = pokemon.get('individual_id', None)
                        id_ = pokemon.get('id', None)
                        if individual_id and id_:  # Ensure the ID exists
                            # Add Pokémon name to comboBox
                            comboBox.addItem(pokemon_name)
                            # Store both individual_id and id as separate data using roles
                            comboBox.setItemData(comboBox.count() - 1, individual_id, role=UserRole)
                            comboBox.setItemData(comboBox.count() - 1, id_, role=UserRole + 1)
        except Exception as e:
            self.logger.log_and_showinfo("error", f"Error loading Pokémon list: {e}")

    def Evolve_Fossil(self, item_name: str, fossil_id: int, fossil_poke_name: str):
        self.starter_window.display_fossil_pokemon(fossil_id, fossil_poke_name)
        save_fossil_pokemon(fossil_id)
        self.delete_item(item_name)

    def modified_pokeball_chances(self, item_name: str, catch_chance: int):
        # Adjust catch chance based on Pokémon type and Poké Ball
        if item_name == 'net-ball' and ('water' in self.enemy_pokemon.type or 'bug' in self.enemy_pokemon.type):
            catch_chance += 10  # Additional 10% for Water or Bug-type Pokémon
            self.logger.log("game", f"{item_name} gets a bonus for Water/Bug-type Pokémon!")

        elif item_name == 'iron-ball' and 'steel' in self.enemy_pokemon.type:
            catch_chance += 10  # Additional 10% for Steel-type Pokémon
            self.logger.log("game", f"{item_name} gets a bonus for Steel-type Pokémon!")

        elif item_name == 'dive-ball' and 'water' in self.enemy_pokemon.type:
            catch_chance += 10  # Additional 10% for Water-type Pokémon
            self.logger.log("game", f"{item_name} gets a bonus for Water-type Pokémon!")

        return catch_chance

    def Handle_Pokeball(self, item_name: str):
        # Check if the item exists in the pokeball chances
        if item_name in self.pokeball_chances:
            catch_chance = self.pokeball_chances[item_name]
            catch_chance = self.modified_pokeball_chances(item_name, catch_chance)

            # Simulate catching the Pokémon based on the catch chance
            if random.randint(1, 100) <= catch_chance:
                # Pokémon caught successfully
                self.logger.log_and_showinfo("info", f"{item_name} successfully caught the Pokémon!")
                self.delete_item(item_name)  # Delete the Poké Ball after use
            else:
                # Pokémon was not caught
                self.logger.log_and_showinfo("info", f"{item_name} failed to catch the Pokémon.")
                self.delete_item(item_name)  # Still delete the Poké Ball after use
        else:
            self.logger.log_and_showinfo("error", f"{item_name} is not a valid Poké Ball!")

    def delete_item(self, item_name: str):
        itembag_list = self.read_items_file()
        for item in itembag_list:
            # Check if the item exists and if the name matches
            if item['item'] == item_name:
                # Decrease the quantity by 1
                item['quantity'] -= 1

                # If quantity reaches 0, remove the item from the list
                if item['quantity'] == 0:
                    itembag_list.remove(item)

        self.write_items_file(itembag_list)
        self.renewWidgets()

    def Check_Heal_Item(self, prevo_name: str, heal_points: int, item_name: str, achievements):
        check = check_for_badge(achievements, 20)
        if check is False:
            receive_badge(20, achievements)
        if item_name == "fullrestore" or item_name == "maxpotion":
            heal_points = self.main_pokemon.max_hp
        self.main_pokemon.hp += heal_points
        if self.main_pokemon.hp > (self.main_pokemon.max_hp):
            self.main_pokemon.hp = self.main_pokemon.max_hp
        self.delete_item(item_name)
        play_effect_sound("HpHeal")
        self.logger.log_and_showinfo("info", f"{prevo_name} was healed for {heal_points}")

    def Check_Evo_Item(self, individual_id: str, prevo_id: str, item_name: str):
        try:
            item_id = return_id_for_item_name(item_name)
            evo_id = check_evolution_by_item(prevo_id, item_id)
            if evo_id is not None:
                # Perform your action when the item matches the Pokémon's evolution item
                self.logger.log_and_showinfo("info", "Pokemon Evolution is fitting !")
                self.evo_window.display_pokemon_evo(individual_id, prevo_id, evo_id)
            else:
                self.logger.log_and_showinfo("info", "This Pokemon does not need this item.")
        except Exception as e:
            show_warning_with_traceback(parent=self, exception=e, message=f"{e}")

    def write_items_file(self, itembag_list: list[Any]):
        with open(itembag_path, 'w') as json_file:
            json.dump(itembag_list, json_file)

    def read_items_file(self):
        """
        Reads the list from the JSON file. If the file contains malformed items,
        it tries to fix them by converting strings to the correct structure.
        """
        try:
            with open(self.itembag_path, "r", encoding="utf-8") as json_file:
                return json.load(json_file)
        except json.JSONDecodeError:
            self.logger.log("error", "Malformed JSON detected. Attempting to fix.")
            itembag_list = self._fix_and_load_items()
            self.write_items_file(itembag_list)
            return itembag_list

    def _fix_and_load_items(self):
        """
        Attempts to fix and load malformed JSON items.
        Reads the JSON file as a string and corrects malformed items.
        """
        try:
            with open(self.itembag_path, "r", encoding="utf-8") as json_file:
                raw_data = json_file.read()

            # Parse raw data as JSON (handling malformed structures)
            corrected_items = []
            json_data = raw_data.strip().lstrip("[").rstrip("]").split("},")
            for entry in json_data:
                entry = entry.strip()
                if not entry.endswith("}"):
                    entry += "}"

                try:
                    item = json.loads(entry)
                    corrected_items.append(item)
                except json.JSONDecodeError:
                    # Fix malformed item (assume it's missing proper structure)
                    if entry.startswith('{"') and entry.endswith('"}'):
                        item_name = entry[2:-2]  # Extract item name
                        corrected_items.append({"item": item_name, "quantity": 1})
                        self.logger.log("info", f"Fixed malformed item: {item_name}")
                    else:
                        self.logger.log("warning", f"Skipping unknown item format: {entry}")

            return corrected_items

        except Exception as e:
            self.logger.log("error", f"Error fixing and loading items: {e}")

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def showEvent(self, event):
        # This method is called when the window is shown or displayed
        self.renewWidgets()

    def show_window(self):
        # Get the geometry of the main screen
        main_screen_geometry = mw.geometry()

        # Calculate the position to center the ItemWindow on the main screen
        x = int(main_screen_geometry.center().x() - self.width() // 2)
        y = int(main_screen_geometry.center().y() - self.height() // 2)

        # Move the ItemWindow to the calculated position
        self.move(x, y)

        self.show()

    def more_info_button_act(self, item_name: str):
        description = get_id_and_description_by_item_name(item_name)
        self.logger.log_and_showinfo("info", f"{description}")
