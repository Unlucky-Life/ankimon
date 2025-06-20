import json
from typing import Any

from aqt import mw
from aqt.qt import (
    Qt,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
    QPixmap,
)
from PyQt6.QtWidgets import QLineEdit, QComboBox, QCheckBox, QMenu
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QFont, QAction, QMovie

from ..pyobj.pokemon_obj import PokemonObject
from ..pyobj.reviewer_obj import Reviewer_Manager
from ..pyobj.test_window import TestWindow
from ..pyobj.translator import Translator
from ..pyobj.collection_dialog import MainPokemon
from ..gui_classes.pokemon_details import PokemonCollectionDetails
from ..pyobj.InfoLogger import ShowInfoLogger
from ..pyobj.settings import Settings
from ..functions.sprite_functions import get_sprite_path
from ..utils import load_custom_font, get_tier_by_id
from ..resources import mypokemon_path

def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout():
            clear_layout(item.layout())

class ScaledMovieLabel(QLabel):
    def __init__(self, gif_path, width, height):
        super().__init__()
        self.target_width = width
        self.target_height = height
        self.movie = QMovie(gif_path)
        self.movie.frameChanged.connect(self.on_frame_changed)
        self.movie.start()
        self.setFixedSize(width, height)

    def on_frame_changed(self, frame_number):
        # Get current frame pixmap
        pixmap = self.movie.currentPixmap()

        # Scale pixmap to target size (keep aspect ratio if you want)
        scaled_pixmap = pixmap.scaled(self.target_width, self.target_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.setPixmap(scaled_pixmap)

class PokemonPC(QDialog):
    def __init__(
            self,
            logger: ShowInfoLogger,
            translator: Translator,
            reviewer_obj: Reviewer_Manager,
            test_window: TestWindow,
            settings: Settings,
            main_pokemon: PokemonObject,
            parent=mw,
            ):
        super().__init__(parent)

        self.logger = logger
        self.translator = translator
        self.reviewer_obj = reviewer_obj
        self.test_window = test_window
        self.settings = settings
        self.main_pokemon_function_callback = lambda _pokemon_data: MainPokemon(_pokemon_data, main_pokemon, logger, translator, reviewer_obj, test_window)

        self.n_cols = 5
        self.n_rows = 6
        self.current_box_idx = 0  # Index of current displayed box
        self.gif_in_collection = settings.get("gui.gif_in_collection", 11)

        self.size = (500, 650)
        self.slot_size = 75 # Side length in pixels of a PC slot
        self.main_layout = QVBoxLayout()

        # These are widgets that will need to hold data through refreshes. Typically, those are the widgets used for filtering and sorting
        self.search_edit = None
        self.type_combo = None
        self.generation_combo = None
        self.tier_combo = None
        self.filter_favorites = None
        self.sort_by_id = None
        self.sort_by_name = None
        self.sort_by_level = None
        self.desc_sort = None  # Sort by descending order

        self.ensure_all_pokemon_have_tier_info()  # Necessary for legacy reasons

        self.create_gui()

    def create_gui(self):
        self.setWindowTitle("Axil's PC")

        pokemon_list = self.load_pokemon_data()
        pokemon_list = self.filter_pokemon_list(pokemon_list)  # Apply all the selected filters
        pokemon_list = self.sort_pokemon_list(pokemon_list)  # Sort the list with the chosen sorting keys
        max_box_idx = (len(pokemon_list) - 1) // (self.n_rows * self.n_cols)

        # Top part of the box that allows you to navigate between boses
        box_selector_layout = QHBoxLayout()
        prev_box_button = QPushButton(f"◀")
        next_box_button = QPushButton(f"▶")
        prev_box_button.setFixedSize(70, 50)
        next_box_button.setFixedSize(70, 50)
        prev_box_button.setFont(QFont('System', 25))
        next_box_button.setFont(QFont('System', 25))
        prev_box_button.clicked.connect(lambda: self.looparound_go_to_box(self.current_box_idx - 1, max_box_idx))
        next_box_button.clicked.connect(lambda: self.looparound_go_to_box(self.current_box_idx + 1, max_box_idx))
        curr_box_label = QLabel(f"Box {self.current_box_idx + 1}")
        curr_box_label.setFixedSize(150, 50)
        curr_box_label.setFont(load_custom_font(20, int(self.settings.get("misc.language", 11))))
        curr_box_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        curr_box_label.setStyleSheet("border: 1px solid gray;")
        box_selector_layout.addWidget(prev_box_button, alignment=Qt.AlignmentFlag.AlignCenter)
        box_selector_layout.addWidget(curr_box_label, alignment=Qt.AlignmentFlag.AlignCenter)
        box_selector_layout.addWidget(next_box_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(box_selector_layout)
        
        # Central part of the box that displays the Pokémon
        start_index = self.current_box_idx * self.n_cols * self.n_rows
        end_index = (self.current_box_idx + 1) * self.n_cols * self.n_rows
        pokemon_list_slice = pokemon_list[start_index:end_index]
        pokemon_grid = QGridLayout()
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                pokemon_idx = col * self.n_rows + row
                if pokemon_idx >= len(pokemon_list_slice):  # This happens on the last box, where there isn't enough pokemon to fill the box
                    empty_label = QLabel()
                    empty_label.setFixedSize(self.slot_size, self.slot_size)
                    pokemon_grid.addWidget(empty_label, col, row, alignment=Qt.AlignmentFlag.AlignCenter)
                    continue

                pokemon = pokemon_list_slice[pokemon_idx]
                pkmn_image_path = get_sprite_path(
                    "front",
                    "gif" if self.gif_in_collection else "png",
                    pokemon['id'],
                    pokemon.get("shiny", False),
                    pokemon["gender"]
                )

                pokemon_button = QPushButton("")
                pokemon_button.setFixedSize(self.slot_size, self.slot_size)
                style_sheet_str = "QPushButton:hover {background-color: lightblue;}"
                if pokemon.get("is_favorite", False):
                    style_sheet_str += " QPushButton {background-color: #FFEB7A;}"
                pokemon_button.setStyleSheet(style_sheet_str)
                pokemon_button.clicked.connect(
                    lambda checked, pb=pokemon_button, pkmn=pokemon: self.show_actions_submenu(pb, pkmn)
                    )
                if self.gif_in_collection:
                    scaled_movie_label = ScaledMovieLabel(pkmn_image_path, self.slot_size - 10, self.slot_size - 10)
                    scaled_movie_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
                    pokemon_grid.addWidget(pokemon_button, col, row, alignment=Qt.AlignmentFlag.AlignCenter)
                    pokemon_grid.addWidget(scaled_movie_label, col, row, alignment=Qt.AlignmentFlag.AlignCenter)
                else:
                    pixmap = QPixmap(pkmn_image_path)
                    pixmap = self.adjust_pixmap_size(pixmap, max_width=300, max_height=230)
                    pokemon_button.setIcon(QIcon(pkmn_image_path))
                    pokemon_button.setIconSize(QSize(self.slot_size - 10, self.slot_size - 10))
                    pokemon_grid.addWidget(pokemon_button, col, row, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(pokemon_grid)

        # We add a bottom part to the box. This part allows the user to filter the Pokémon displayed
        filters_layout = QGridLayout()
        # Name filtering filtering
        prev_text = self.search_edit.text() if self.search_edit is not None else ""
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search Pokémon (by nickname, name)")
        self.search_edit.setText(prev_text)
        search_button = QPushButton("Search")
        search_button.clicked.connect(lambda: self.go_to_box(0))
        # Type filtering
        prev_idx = self.type_combo.currentIndex() if self.type_combo is not None else 0
        self.type_combo = QComboBox()
        self.type_combo.addItem("All types")
        self.type_combo.addItems(["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"])
        self.type_combo.setCurrentIndex(prev_idx)
        self.type_combo.currentIndexChanged.connect(lambda: self.go_to_box(0))
        # Generation filtering
        prev_idx = self.generation_combo.currentIndex() if self.generation_combo is not None else 0
        self.generation_combo = QComboBox()
        self.generation_combo.addItem("All gens")
        self.generation_combo.addItems([f"Gen {i}" for i in range(1, 9, 1)])
        self.generation_combo.setCurrentIndex(prev_idx)
        self.generation_combo.currentIndexChanged.connect(lambda: self.go_to_box(0))
        # Tier filtering
        prev_idx = self.tier_combo.currentIndex() if self.tier_combo is not None else 0
        self.tier_combo = QComboBox()
        self.tier_combo.addItem("All tiers")
        self.tier_combo.addItems(["Normal", "Legendary", "Mythical", "Baby", "Ultra"])
        self.tier_combo.setCurrentIndex(prev_idx)
        self.tier_combo.currentIndexChanged.connect(lambda: self.go_to_box(0))
        # Sorting by ID
        is_checked = self.filter_favorites.isChecked() if self.filter_favorites is not None else False
        self.filter_favorites = QCheckBox("Only favorites")
        self.filter_favorites.setChecked(is_checked)
        self.filter_favorites.stateChanged.connect(lambda: self.go_to_box(0))
        # Sorting by ID
        is_checked = self.sort_by_id.isChecked() if self.sort_by_id is not None else False
        self.sort_by_id = QCheckBox("Sort by ID")
        self.sort_by_id.setChecked(is_checked)
        self.sort_by_id.stateChanged.connect(lambda: self.go_to_box(0))
        # Sorting by name
        is_checked = self.sort_by_name.isChecked() if self.sort_by_name is not None else False
        self.sort_by_name = QCheckBox("Sort by name")
        self.sort_by_name.setChecked(is_checked)
        self.sort_by_name.stateChanged.connect(lambda: self.go_to_box(0))
        # Sorting by level
        is_checked = self.sort_by_level.isChecked() if self.sort_by_level is not None else False
        self.sort_by_level = QCheckBox("Sort by level")
        self.sort_by_level.setChecked(is_checked)
        self.sort_by_level.stateChanged.connect(lambda: self.go_to_box(0))
        # Whether to sort by ascending order or descending order
        is_checked = self.desc_sort.isChecked() if self.desc_sort is not None else False
        self.desc_sort = QCheckBox("Sort by descending order")
        self.desc_sort.setChecked(is_checked)
        self.desc_sort.stateChanged.connect(lambda: self.go_to_box(0))
        # Adding the widgets to the layout
        filters_layout.addWidget(self.search_edit, 0, 0, 1, 3)
        filters_layout.addWidget(search_button, 0, 3, 1, 1)
        filters_layout.addWidget(self.type_combo, 1, 0)
        filters_layout.addWidget(self.generation_combo, 1, 1)
        filters_layout.addWidget(self.tier_combo, 1, 2)
        filters_layout.addWidget(self.filter_favorites, 1, 3)
        filters_layout.addWidget(self.sort_by_id, 2, 0)
        filters_layout.addWidget(self.sort_by_name, 2, 1)
        filters_layout.addWidget(self.sort_by_level, 2, 2)
        filters_layout.addWidget(self.desc_sort, 2, 3)
        self.main_layout.addLayout(filters_layout)

        self.setLayout(self.main_layout)
        self.setFixedSize(*self.size)

    def refresh_gui(self):
        clear_layout(self.main_layout)
        self.create_gui()
        self.layout().invalidate()
        self.layout().activate()

    def go_to_box(self, idx: int):
        self.current_box_idx = idx
        self.refresh_gui()

    def looparound_go_to_box(self, idx: int, max_idx: int):
        if idx < 0:
            idx = max_idx
        elif idx > max_idx:
            idx = 0
        self.go_to_box(idx)

    def adjust_pixmap_size(self, pixmap, max_width, max_height):
        original_width = pixmap.width()
        original_height = pixmap.height()

        if original_width > max_width:
            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pixmap = pixmap.scaled(new_width, new_height)

        return pixmap

    def load_pokemon_data(self) -> list:
        """Reads the mypokemon.json file and loads Pokémon data into self.pokemon_list."""
        try:
            with open(mypokemon_path, "r", encoding="utf-8") as file:
                pokemon_list = json.load(file)
                return pokemon_list
        except FileNotFoundError:
            self.logger.log("error","mypokemon.json file not found.")
        except json.JSONDecodeError:
            self.logger.log("error","mypokemon.json file not found.")

        return []
    
    def filter_pokemon_list(self, pokemon_list: list) -> list:
        def filtering_func(pokemon: dict) -> bool:
            if self.search_edit is not None:
                if self.search_edit.text().lower() not in pokemon.get("name").lower():
                    return False
                
            if self.type_combo is not None:
                if self.type_combo.currentIndex() != 0 and self.type_combo.currentText() not in pokemon.get("type", ""):
                    return False
                
            if self.tier_combo is not None:
                if (
                    self.tier_combo.currentIndex() != 0 
                    and pokemon.get("tier") is not None
                    and self.tier_combo.currentText() != pokemon.get("tier") 
                ):
                    return False
                
            if self.filter_favorites is not None:
                if self.filter_favorites.isChecked() and not pokemon.get("is_favorite", False):
                    return False
                
            if self.generation_combo is not None:
                gen_idx = self.generation_combo.currentIndex()
                if gen_idx != 0 and (
                    (1 <= pokemon["id"] <= 151 and gen_idx != 1) or
                    (152 <= pokemon["id"] <= 251 and gen_idx != 2) or
                    (252 <= pokemon["id"] <= 386 and gen_idx != 3) or
                    (387 <= pokemon["id"] <= 493 and gen_idx != 4) or
                    (494 <= pokemon["id"] <= 649 and gen_idx != 5) or
                    (650 <= pokemon["id"] <= 721 and gen_idx != 6) or
                    (722 <= pokemon["id"] <= 809 and gen_idx != 7) or
                    (810 <= pokemon["id"] <= 898 and gen_idx != 8)
                ):
                    return False
            
            return True

        return list(filter(filtering_func, pokemon_list.copy()))
    
    def sort_pokemon_list(self, pokemon_list: list) -> list:
        reverse = self.desc_sort is not None and self.desc_sort.isChecked()
        filters = []
        if self.sort_by_id is not None and self.sort_by_id.isChecked():
            filters.append("id")
        if self.sort_by_name is not None and self.sort_by_name.isChecked():
            filters.append("name")
            filters.append("nickname")
        if self.sort_by_level is not None and self.sort_by_level.isChecked():
            filters.append("level")

        if not filters:
            return pokemon_list

        return sorted(
            pokemon_list,
            reverse=reverse,
            key=lambda x: tuple(x[key] for key in filters)
            )
    
    def show_actions_submenu(self, button: QPushButton, pokemon: dict[str, Any]):
        menu = QMenu(self)

        # QMenu doesn't have a "window name" property or the like. So let's emulate one.
        if pokemon.get("gender") == "M":
            gender_symbol = "♂"
        elif pokemon.get("gender") == "F":
            gender_symbol = "♀"
        else:
            gender_symbol = ""
        if pokemon.get("nickname"):
            title = f'{pokemon["nickname"]} ({pokemon["name"]}) {gender_symbol} - lvl {pokemon["level"]}'
        else:
            title = f'{pokemon["name"]} {gender_symbol} - lvl {pokemon["level"]}'
        title_action = QAction(title, menu)
        title_action.setEnabled(False)  # Disabled, so it can't be clicked
        menu.addAction(title_action)
        menu.addSeparator()

        pokemon_details_action = QAction("Pokémon details", self)
        main_pokemon_action = QAction("Pick as main Pokémon", self)
        make_favorite_action = QAction(
            "Unmake favorite" if pokemon.get("is_favorite", False) else "Make favorite"
            )

        # Connect actions to methods or lambda functions
        pokemon_details_action.triggered.connect(lambda: self.show_pokemon_details(pokemon))
        main_pokemon_action.triggered.connect(lambda: self.main_pokemon_function_callback(pokemon))
        make_favorite_action.triggered.connect(lambda: self.toggle_favorite(pokemon))
        
        menu.addAction(pokemon_details_action)
        menu.addAction(main_pokemon_action)
        menu.addAction(make_favorite_action)

        # Show the menu at the button's position, aligned below the button
        menu.exec(button.mapToGlobal(button.rect().topRight()))

    def show_pokemon_details(self, pokemon):
        if pokemon.get('base_stats'):
            detail_stats = {**pokemon['base_stats'], "xp": pokemon.get("xp", 0)}
        elif pokemon.get('stats'):
            detail_stats = {**pokemon['stats'], "xp": pokemon.get("xp", 0)}
        else:
            raise ValueError("Could not get the stats information of the Pokémon")
        PokemonCollectionDetails(
            name=pokemon['name'],
            level=pokemon['level'],
            id=pokemon['id'],
            shiny=pokemon.get("shiny", False),
            ability=pokemon['ability'],
            type=pokemon['type'],
            detail_stats=detail_stats,
            attacks=pokemon['attacks'],
            base_experience=pokemon['base_experience'],
            growth_rate=pokemon['growth_rate'],
            ev=pokemon['ev'],
            iv=pokemon['iv'],
            gender=pokemon['gender'],
            nickname=pokemon.get('nickname'),
            individual_id=pokemon.get('individual_id'),
            pokemon_defeated=pokemon.get('pokemon_defeated', 0),
            everstone=pokemon.get('everstone', False),
            captured_date=pokemon.get('captured_date', 'Missing'),
            language=int(self.settings.get("misc.language", 11)),
            gif_in_collection=self.gif_in_collection,
            remove_levelcap=self.settings.get("remove_levelcap", False),
            logger=self.logger,
            refresh_callback=lambda: None,
        )

    def toggle_favorite(self, pokemon: dict[list, Any]):
        pokemon_list = self.load_pokemon_data()
        for i in range(len(pokemon_list)):
            if pokemon_list[i].get("individual_id") == pokemon["individual_id"]:
                is_currently_favorite = pokemon_list[i].get("is_favorite", False)
                pokemon_list[i]["is_favorite"] = not is_currently_favorite

                with open(str(mypokemon_path), "w", encoding="utf-8") as json_file:
                    json.dump(pokemon_list, json_file, indent=2)

                self.refresh_gui()
                return
        
        if self.logger is not None:
            self.logger.log("info", f"Could not make/unmake {pokemon['name']} favorite")

    def ensure_all_pokemon_have_tier_info(self):
        """
        At the time this PokémonPC class was implemented, tier data for caught Pokemon wasn't saved.
        This means that filtering by tier is impossible.
        To address this issue, I made this method that "fixes" the file where caught pokemon are saved.
        """
        pokemon_list = self.load_pokemon_data()
        pokemon_tiers = [p.get("tier") for p in pokemon_list]
        if None in pokemon_tiers:  # If at least 1 pokémon does not have tier information
            for i, pokemon in enumerate(pokemon_list):
                if pokemon.get("tier") is not None:
                    continue
                tier = get_tier_by_id(pokemon["id"])
                if tier is None:
                    self.logger.log("warning", f"Could not find the tier information of {pokemon['name']}")
                pokemon_list[i]["tier"] = tier

            with open(str(mypokemon_path), "w", encoding="utf-8") as json_file:
                json.dump(pokemon_list, json_file, indent=2)


