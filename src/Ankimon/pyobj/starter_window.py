import random
import json
import uuid
from datetime import datetime

from aqt.utils import showWarning
from aqt.qt import (
    QFont,
    QLabel,
    QPainter,
    QPixmap,
    Qt,
    QVBoxLayout,
    QWidget,
    qconnect
    )
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    )

from ..business import resize_pixmap_img
from ..pyobj.pokemon_obj import PokemonObject
from ..pyobj.settings import Settings
from ..pyobj.InfoLogger import ShowInfoLogger
from ..functions.badges_functions import check_for_badge, receive_badge
from ..functions.battle_functions import calculate_hp
from ..functions.pokedex_functions import search_pokedex, search_pokeapi_db_by_id
from ..functions.pokemon_functions import get_random_moves_for_pokemon, pick_random_gender
from ..utils import load_custom_font
from ..resources import starters_path, addon_dir, frontdefault, mainpokemon_path, mypokemon_path


class StarterWindow(QWidget):
    def __init__(
            self,
            logger: ShowInfoLogger,
            settings_obj: Settings,
            ):
        super().__init__()
        self.init_ui()
        #self.update()

        # To avoid circular imports, instead of importing those things, we
        # save a reference to them as an attribute
        self.logger = logger
        self.settings_obj = settings_obj

    def init_ui(self):
        basic_layout = QVBoxLayout()
        # Set window
        self.setWindowTitle('Choose a Starter')
        self.setLayout(basic_layout)
        self.starter = False

    def open_dynamic_window(self):
        if self.isVisible() is False:
            self.show()
        else:
            self.close()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def keyPressEvent(self, event):
        # Close the main window when the spacebar is pressed
        if event.key() == Qt.Key.Key_G:  # Updated to Key_G for PyQt 6
            # First encounter image
            if not self.starter:
                self.display_starter_pokemon()
            # If self.starter is True, simply pass (do nothing)
            else:
                pass
    
    def choose_pokemon(self, starter_name): 
        # Create a dictionary to store the Pokémon's data
        # add all new values like hp as max_hp, evolution_data, description and growth rate
        name = search_pokedex(starter_name, "name")
        id = search_pokedex(starter_name, "num")
        stats = search_pokedex(starter_name, "baseStats")
        abilities = search_pokedex(starter_name, "abilities")
        evos = search_pokedex(starter_name, "evos")
        gender = pick_random_gender(name.lower())
        numeric_abilities = {k: v for k, v in abilities.items() if k.isdigit()}
        # Check if there are numeric abilities
        if numeric_abilities:
            # Convert the filtered abilities dictionary values to a list
            abilities_list = list(numeric_abilities.values())
            # Select a random ability from the list
            ability = random.choice(abilities_list)
        else:
            # Set to "No Ability" if there are no numeric abilities
            ability = "No Ability"
        type = search_pokedex(starter_name, "types")
        name = search_pokedex(starter_name, "name")
        generation_file = "pokeapi_db.json"
        growth_rate = search_pokeapi_db_by_id(id, "growth_rate")
        base_experience = search_pokeapi_db_by_id(id, "base_experience")
        description= search_pokeapi_db_by_id(id, "description")
        level = 5
        attacks = get_random_moves_for_pokemon(starter_name, level)
        stats["xp"] = 0
        ev = {
            "hp": 0,
            "atk": 0,
            "def": 0,
            "spa": 0,
            "spd": 0,
            "spe": 0
        }
        iv = {
            "hp": random.randint(1, 32),
            "atk": random.randint(1, 32),
            "def": random.randint(1, 32),
            "spa": random.randint(1, 32),
            "spd": random.randint(1, 32),
            "spe": random.randint(1, 32)
        }
        caught_pokemon = {
            "name": name,
            "nickname": name,
            "gender": gender,
            "level": level,
            "id": id,
            "ability": ability,
            "type": type,
            "stats": stats,
            "ev": ev,
            "iv": iv,
            "attacks": attacks,
            "base_experience": base_experience,
            "current_hp": calculate_hp(int(stats["hp"]), level, ev, iv),
            "growth_rate": growth_rate,
            "evos": evos,
            "individual_id":  str(uuid.uuid4()),
            "friendship": 0,
            "pokemon_defeated": 0,
            "captured_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "everstone": False,
            "shiny": False,
            "mega": False,
            "special-form": None,
        }

        # Load existing Pokémon data if it exists
        if mypokemon_path.is_file():
            with open(mypokemon_path, "r", encoding="utf-8") as json_file:
                caught_pokemon_data = json.load(json_file)
        else:
            caught_pokemon_data = []

        # Append the caught Pokémon's data to the list
        caught_pokemon_data.append(caught_pokemon)
        # Save the caught Pokémon's data to a JSON file
        with open(str(mainpokemon_path), "w") as json_file:
            json.dump(caught_pokemon_data, json_file, indent=2)

        main_pokemon = PokemonObject(**caught_pokemon_data[0])

        # Save the caught Pokémon's data to a JSON file
        with open(str(mypokemon_path), "w") as json_file:
            json.dump(caught_pokemon_data, json_file, indent=2)

        self.logger.log_and_showinfo("info",f"{name.capitalize()} has been chosen as Starter Pokemon !")

        self.display_chosen_starter_pokemon(starter_name)

    def get_random_starter(self):
        category = "Starter"
        try:
            # Reload the JSON data from the file
            with open(str(starters_path), "r", encoding="utf-8") as file:
                pokemon_in_tier = json.load(file)
                # Filter the Pokémon data to only include those in the given tier
                water_starter = []
                fire_starter = []
                grass_starter = []
                for pokemon in pokemon_in_tier:
                    pokemon = (pokemon).lower()
                    types = search_pokedex(pokemon, "types")
                    for type in types:
                        if type == "Grass":
                            grass_starter.append(pokemon)
                        if type == "Fire":
                            fire_starter.append(pokemon)
                        if type == "Water":
                            water_starter.append(pokemon)
                random_gen = random.randint(0, 6)
                water_start = f"{water_starter[random_gen]}"
                fire_start = f"{fire_starter[random_gen]}"
                grass_start = f"{grass_starter[random_gen]}"
                return water_start, fire_start, grass_start
        except Exception as e:
            showWarning(f"Error in get_random_starter: {e}")
            return None, None, None

    def display_starter_pokemon(self):
        self.setMaximumWidth(512)
        self.setMaximumHeight(320)
        self.clear_layout(self.layout())
        layout = self.layout()
        water_start, fire_start, grass_start = self.get_random_starter()
        starter_label = self.pokemon_display_starter(water_start, fire_start, grass_start)
        self.water_starter_button, self.fire_starter_button, self.grass_start_button = self.pokemon_display_starter_buttons(water_start, fire_start, grass_start)
        layout.addWidget(starter_label)
        button_widget = QWidget()
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.water_starter_button)
        layout_buttons.addWidget(self.fire_starter_button)
        layout_buttons.addWidget(self.grass_start_button)
        button_widget.setLayout(layout_buttons)
        layout.addWidget(button_widget)
        self.setStyleSheet("background-color: rgb(14,14,14);")
        self.setLayout(layout)
        self.show()
        
    def display_chosen_starter_pokemon(self, starter_name):
        self.clear_layout(self.layout())
        layout = self.layout()
        starter_label = self.pokemon_display_chosen_starter(starter_name)
        layout.addWidget(starter_label)
        self.setStyleSheet("background-color: rgb(14,14,14);")
        self.setLayout(layout)
        self.setMaximumWidth(512)
        self.setMaximumHeight(340)
        self.show()
        self.starter = True
        self.logger.log_and_showinfo("info","You have chosen your Starter Pokemon ! \n You can now close this window ! \n Please restart your Anki to restart your Pokemon Journey!")
        #global achievments
        #check = check_for_badge(achievements, 7)
        #if check is False:
        #    receive_badge(7, achievements)
    
    def display_fossil_pokemon(self, fossil_id, fossil_name):
        self.clear_layout(self.layout())
        layout = self.layout()
        fossil_label = self.pokemon_display_fossil_pokemon(fossil_id, fossil_name)
        layout.addWidget(fossil_label)
        self.setStyleSheet("background-color: rgb(14,14,14);")
        self.setLayout(layout)
        self.setMaximumWidth(512)
        self.setMaximumHeight(340)
        self.show()
        self.starter = True
        self.logger.log_and_showinfo("info","You have received your Fossil Pokemon ! \n You can now close this window !")
        global achievments
        #check = check_for_badge(achievements, 19)
        #if check is False:
        #    receive_badge(19, achievements)

    def pokemon_display_starter_buttons(self, water_start, fire_start, grass_start):
        # Create buttons for catching and killing the Pokémon
        water_starter_button = QPushButton(f"{(water_start).capitalize()}")
        water_starter_button.setFont(QFont("Arial",12))  # Adjust the font size and style as needed
        water_starter_button.setStyleSheet("background-color: rgb(44,44,44);")
        #qconnect(water_starter_button.clicked, choose_pokemon)
        qconnect(water_starter_button.clicked, lambda: self.choose_pokemon(water_start))

        fire_starter_button = QPushButton(f"{(fire_start).capitalize()}")
        fire_starter_button.setFont(QFont("Arial", 12))  # Adjust the font size and style as needed
        fire_starter_button.setStyleSheet("background-color: rgb(44,44,44);")
        #qconnect(fire_starter_button.clicked, choose_pokemon)
        qconnect(fire_starter_button.clicked, lambda: self.choose_pokemon(fire_start))
        # Set the merged image as the pixmap for the QLabel

        grass_start_button = QPushButton(f"{(grass_start).capitalize()}")
        grass_start_button.setFont(QFont("Arial", 12))  # Adjust the font size and style as needed
        grass_start_button.setStyleSheet("background-color: rgb(44,44,44);")
        #qconnect(grass_start_button.clicked, choose_pokemon)
        qconnect(grass_start_button.clicked, lambda: self.choose_pokemon(grass_start))
        # Set the merged image as the pixmap for the QLabel

        return water_starter_button, fire_starter_button, grass_start_button

    def pokemon_display_starter(self, water_start, fire_start, grass_start):
        bckgimage_path = addon_dir / "addon_sprites" / "starter_screen" / "bckg.png"
        water_id = int(search_pokedex(water_start, "num"))
        grass_id = int(search_pokedex(grass_start, "num"))
        fire_id = int(search_pokedex(fire_start, "num"))

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        # Display the Pokémon image
        water_path = frontdefault / f"{water_id}.png"
        water_label = QLabel()
        water_pixmap = QPixmap()
        water_pixmap.load(str(water_path))

        # Display the Pokémon image
        fire_path = frontdefault / f"{fire_id}.png"
        fire_label = QLabel()
        fire_pixmap = QPixmap()
        fire_pixmap.load(str(fire_path))

        # Display the Pokémon image
        grass_path = frontdefault / f"{grass_id}.png"
        grass_label = QLabel()
        grass_pixmap = QPixmap()
        grass_pixmap.load(str(grass_path))

        def resize_pixmap_img(pixmap):
            max_width = 150
            original_width = pixmap.width()
            original_height = pixmap.height()
            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pixmap2 = pixmap.scaled(new_width, new_height)
            return pixmap2

        water_pixmap = resize_pixmap_img(water_pixmap)
        fire_pixmap = resize_pixmap_img(fire_pixmap)
        grass_pixmap = resize_pixmap_img(grass_pixmap)

        # Merge the background image and the Pokémon image
        merged_pixmap = QPixmap(pixmap_bckg.size())
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        #merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)

        painter.drawPixmap(57,-5,water_pixmap)
        painter.drawPixmap(182,-5,fire_pixmap)
        painter.drawPixmap(311,-3,grass_pixmap)

        # custom font
        custom_font = load_custom_font(int(28), int(self.settings_obj.get("misc.language",11)))
        message_box_text = "Choose your Starter Pokemon"
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(110, 310, message_box_text)
        custom_font = load_custom_font(int(20), int(self.settings_obj.get("misc.language",11)))
        painter.setFont(custom_font)
        painter.drawText(10, 330, "Press G to change Generation")
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        starter_label = QLabel()
        starter_label.setPixmap(merged_pixmap)

        return starter_label

    def pokemon_display_chosen_starter(self, starter_name):
        bckgimage_path = addon_dir / "addon_sprites" / "starter_screen" / "bg.png"
        id = int(search_pokedex(starter_name, "num"))

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        # Display the Pokémon image
        image_path = frontdefault / f"{id}.png"
        image_label = QLabel()
        image_pixmap = QPixmap()
        image_pixmap.load(str(image_path))
        image_pixmap = resize_pixmap_img(image_pixmap, 250)

        # Merge the background image and the Pokémon image
        merged_pixmap = QPixmap(pixmap_bckg.size())
        #merged_pixmap.fill(Qt.transparent)
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)
        painter.drawPixmap(125,10,image_pixmap)

        # custom font
        custom_font = load_custom_font(int(32), int(self.settings_obj.get("misc.language",11)))
        message_box_text = f"{(starter_name).capitalize()} was chosen as Starter !"
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(40, 290, message_box_text)
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        starter_label = QLabel()
        starter_label.setPixmap(merged_pixmap)

        return starter_label
    
    def pokemon_display_fossil_pokemon(self, fossil_id, fossil_name):
        bckgimage_path = addon_dir / "addon_sprites" / "starter_screen" / "bg.png"
        id = fossil_id

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        # Display the Pokémon image
        image_path = frontdefault / f"{id}.png"
        image_label = QLabel()
        image_pixmap = QPixmap()
        image_pixmap.load(str(image_path))
        image_pixmap = resize_pixmap_img(image_pixmap, 250)

        # Merge the background image and the Pokémon image
        merged_pixmap = QPixmap(pixmap_bckg.size())
        #merged_pixmap.fill(Qt.transparent)
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)
        painter.drawPixmap(125,10,image_pixmap)

        # custom font
        custom_font = load_custom_font(int(32), int(self.settings_obj.get("misc.language",11)))
        message_box_text = f"{(fossil_name).capitalize()} was brought to life !"
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(40, 290, message_box_text)
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        fossil_label = QLabel()
        fossil_label.setPixmap(merged_pixmap)

        return fossil_label