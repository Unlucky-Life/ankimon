import json

from aqt import mw
from aqt.qt import (
    Qt,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
    QFrame,
    QPixmap,
    QMessageBox,
)
from PyQt6.QtWidgets import QLineEdit, QComboBox
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QFont

from ..pyobj.InfoLogger import ShowInfoLogger
from ..pyobj.settings import Settings
from ..functions.sprite_functions import get_sprite_path
from ..resources import mypokemon_path

def transpose_grid_layout(grid_layout):
    items = []
    # Step 1: Extract all items with their positions
    for i in reversed(range(grid_layout.count())):
        item = grid_layout.itemAt(i)
        row, col, rowspan, colspan = grid_layout.getItemPosition(i)
        widget = item.widget()
        if widget:
            items.append((widget, row, col, rowspan, colspan))
            grid_layout.removeWidget(widget)

    # Step 2: Add them back transposed
    for widget, row, col, rowspan, colspan in items:
        grid_layout.addWidget(widget, col, row, colspan, rowspan)

    return grid_layout

def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout():
            clear_layout(item.layout())

class PokemonPC(QDialog):
    def __init__(self, settings: Settings, parent=mw):
        super().__init__(parent)

        self.n_cols = 6
        self.n_rows = 5
        self.current_box_idx = 0  # Index of current displayed box
        self.gif_in_collection = settings.get("gui.gif_in_collection", 11)

        self.size = (400, 570)
        self.slot_size = 75 # Side length in pixels of a PC slot
        self.main_layout = QVBoxLayout()

        # These are widgets that will need to hold data through refreshes
        self.search_edit = None
        self.type_combo = None
        self.generation_combo = None

        self.create_gui()

    def create_gui(self):
        self.setWindowTitle("Axil's PC")

        pokemon_list = self.load_pokemon_data()
        pokemon_list = self.filter_pokemon_list(pokemon_list)  # Apply all the selected filters
        max_box_idx = len(pokemon_list) // (self.n_rows * self.n_cols)

        # Top part of the box that allows you to navigate between boses
        box_selector_layout = QHBoxLayout()
        prev_box_button = QPushButton(f"◀")
        next_box_button = QPushButton(f"▶")
        prev_box_button.setFixedSize(70, 50)
        next_box_button.setFixedSize(70, 50)
        prev_box_button.setFont(QFont('Times', 25))
        next_box_button.setFont(QFont('Times', 25))
        prev_box_button.clicked.connect(lambda: self.looparound_go_to_box(self.current_box_idx - 1, max_box_idx))
        next_box_button.clicked.connect(lambda: self.looparound_go_to_box(self.current_box_idx + 1, max_box_idx))
        curr_box_label = QLabel(f"Box {self.current_box_idx + 1}")
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
                    pokemon_grid.addWidget(empty_label, row, col, alignment=Qt.AlignmentFlag.AlignCenter)
                else:
                    pokemon = pokemon_list_slice[pokemon_idx]
                    pkmn_image_path = get_sprite_path(
                        "front",
                        "gif" if self.gif_in_collection else "png",
                        pokemon['id'],
                        pokemon.get("shiny", False),
                        pokemon["gender"]
                    )

                    pixmap = QPixmap(pkmn_image_path)
                    pixmap = self.adjust_pixmap_size(pixmap, max_width=300, max_height=230)
                    pokemon_button = QPushButton("")
                    pokemon_button.setFixedSize(self.slot_size, self.slot_size)
                    pokemon_button.setIcon(QIcon(pkmn_image_path))
                    pokemon_button.setIconSize(QSize(self.slot_size - 10, self.slot_size - 10))
                    pokemon_grid.addWidget(pokemon_button, row, col, alignment=Qt.AlignmentFlag.AlignCenter)
        pokemon_grid = transpose_grid_layout(pokemon_grid)
        self.main_layout.addLayout(pokemon_grid)

        # We add a bottom part to the box. This part allows the user to filter the Pokémon displayed
        filters_layout = QHBoxLayout()
        # Name filtering filtering
        prev_text = self.search_edit.text() if self.search_edit is not None else ""
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search Pokémon (by nickname, name)")
        self.search_edit.setText(prev_text)
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.refresh_gui)
        # Type filtering
        prev_idx = self.type_combo.currentIndex() if self.type_combo is not None else 0
        self.type_combo = QComboBox()
        self.type_combo.addItem("All")
        self.type_combo.addItems(["Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy"])
        self.type_combo.setCurrentIndex(prev_idx)
        self.type_combo.currentIndexChanged.connect(self.refresh_gui)
        # Generation filtering
        prev_idx = self.generation_combo.currentIndex() if self.generation_combo is not None else 0
        self.generation_combo = QComboBox()
        self.generation_combo.addItem("All")
        self.generation_combo.addItems([f"Gen {i}" for i in range(1, 9, 1)])
        self.generation_combo.setCurrentIndex(prev_idx)
        self.generation_combo.currentIndexChanged.connect(self.refresh_gui)
        # Adding the widgets to the layout
        filters_layout.addWidget(self.search_edit)
        filters_layout.addWidget(search_button)
        filters_layout.addWidget(self.type_combo)
        filters_layout.addWidget(self.generation_combo)
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
        idx_to_remove = []
        for i, pokemon in enumerate(pokemon_list):
            if self.search_edit is not None:
                if self.search_edit.text().lower() not in pokemon.get("name").lower():
                    idx_to_remove.append(i)

            if self.type_combo is not None:
                if self.type_combo.currentIndex() != 0 and self.type_combo.currentText() not in pokemon.get("type", ""):
                    idx_to_remove.append(i)
            
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
                    idx_to_remove.append(i)
        
        # Now we create a list of Pokemon that have not been filtered out
        result = []
        for i, pokemon in enumerate(pokemon_list):
            if i not in idx_to_remove:
                result.append(pokemon)

        return result
