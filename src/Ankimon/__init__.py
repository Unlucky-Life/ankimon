import os, sys
from aqt.utils import *
from typing import Optional
#showInfo, qconnect, showWarning
from aqt.qt import *
import anki
import threading
from anki.hooks import addHook, wrap
from aqt.reviewer import Reviewer
from aqt import mw, editor, gui_hooks
from aqt.qt import QDialog, QGridLayout, QLabel, QPixmap, QPainter, QFont, Qt, QVBoxLayout, QWidget
import random
import csv
from aqt.qt import *
import requests
import json
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWidgets import QAction
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl
import base64
from aqt import utils
from PyQt6.QtGui import QSurfaceFormat
import aqt
import pathlib
from pathlib import Path
from typing import List, Union
import shutil
import distutils.dir_util
from anki.collection import Collection
import csv
import time, wave
from .download_pokeapi_db import create_pokeapidb

config = mw.addonManager.getConfig(__name__)
#show config .json file

# Find current directory
addon_dir = Path(__file__).parents[0]
currdirname = addon_dir

def check_folders_exist(parent_directory, folder):
    folder_path = os.path.join(parent_directory, folder)
    if not os.path.isdir(folder_path):
       #showInfo(f"Folder '{folder}' does not exist in '{parent_directory}'")
       return False
    else:
       return True

def check_file_exists(folder, filename):
    file_path = os.path.join(folder, filename)
    if os.path.isfile(file_path):
        #showInfo(f"File '{filename}' exists in '{folder}'.")
        return True
    else:
        #showInfo(f"File '{filename}' does not exist in '{folder}'.")
        return False

# Assign Pokemon Image folder directory name
pkmnimgfolder = addon_dir / "pokemon_sprites"
backdefault = addon_dir / "pokemon_sprites" / "back_default"
frontdefault = addon_dir / "pokemon_sprites" / "front_default"
#Assign saved Pokemon Directory
mypokemon_path = currdirname / "mypokemon.json"
mainpokemon_path = addon_dir / "mainpokemon.json"
battlescene_path = addon_dir / "battle_scenes"
battlescene_path_without_dialog = addon_dir / "battle_scenes_without_dialog"
battle_ui_path = addon_dir / "pkmnbattlescene - UI_transp"
battle_ui_path_without_dialog = addon_dir / "pkmnbattlescene - UI_transp.png - without dialog.png"
type_style_file = addon_dir / "types.json"
allxp_file_path = addon_dir / "TotalExpPokemonAddon.csv"
next_lvl_file_path = addon_dir / "ExpPokemonAddon.csv"
berries_path = addon_dir / "berries"
background_dialog_image_path  = addon_dir / "background_dialog_image.png"
attack_animation_path = addon_dir / "grass_bind_animation.gif"
min_level_file_path = addon_dir / "evolution_info_sorted.json"
pokedex_image_path = addon_dir / "pokedex_template.jpg"
evolve_image_path = addon_dir / "evo_temp.jpg"
learnset_path = addon_dir / "learnsets.json"
pokedex_path = addon_dir / "pokedex.json"
all_species_path = addon_dir / "all_species.json"
species_path = addon_dir / "species.json"
items_path = addon_dir / "pokemon_sprites" / "items"
itembag_path = addon_dir / "items.json"
# Get the profile folder
profilename = mw.pm.name
#profilefolder = Path(mw.pm.profileFolder())
#mediafolder = Path(mw.col.media.dir())
font_name = "Axolotl"
font_file = "Axolotl.ttf"
mainpkmn = 0
mainpokemon_hp = 100
#test mainpokemon
#battlescene_file = "pkmnbattlescene.png"
pokemon_encounter = 0
moves_file_path = addon_dir / "moves.json"
effectiveness_chart_file_path = addon_dir / "eff_chart.json"

# check for sprites, data
back_sprites = check_folders_exist(pkmnimgfolder, "back_default")
front_sprites = check_folders_exist(pkmnimgfolder, "front_default")
berries_sprites = check_folders_exist(addon_dir, "berries")
item_sprites = check_folders_exist(pkmnimgfolder, "items")
poke_api_data = check_file_exists(addon_dir, "pokeapi_db.json")
pokedex_data = check_file_exists(addon_dir, "pokedex.json")
learnsets_data = check_file_exists(addon_dir, "learnsets.json")
all_species = check_file_exists(addon_dir, "all_species.json")

if back_sprites and front_sprites == True:
    sprites_complete = True
else:
    sprites_complete = False
if pokedex_data and learnsets_data and all_species and poke_api_data == True:
    database_complete = True
else:
    database_complete = False

class CheckFiles(QDialog):
    def __init__(self):
        super().__init__()

        check_files_message = "Ankimon Files:"
        if sprites_complete != True:
            check_files_message += " \n Sprite Files incomplete. \n  Please go to Ankimon => 'Download Sprite Files' to download the needed files"
        if database_complete != True:
            check_files_message += " \n Data Files incomplete. \n  Please go to Ankimon => 'Download Database Files' to download the needed files"
        check_files_message += "\n Once all files have been download.\n Please restart Anki"
        # Set the window title for the dialog
        self.setWindowTitle("Ankimon Files Checker")

        # Create a QLabel instance
        self.label = QLabel(f"{check_files_message}", self)

        # Create a QVBoxLayout instance
        self.layout = QVBoxLayout()

        # Add the QLabel to the layout
        self.layout.addWidget(self.label)

        # Set the dialog's layout
        self.setLayout(self.layout)

dialog = CheckFiles()
if database_complete != True:
    dialog.show()
elif sprites_complete != True:
    dialog.show()

window = None
gender = None
card_counter = 0
only_online_sprites = config["only_use_online_sprites"]
cards_per_round = config["cards_per_round"]
reviewer_image_gif = config["reviewer_image_gif"]
sounds = config["sounds"]
sounds = False

def test_online_connectivity(url='http://www.google.com', timeout=5):
    try:
        # Attempt to get the URL
        response = requests.get(url, timeout=timeout)

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            return True
    except requests.ConnectionError:
        # Connection error means no internet connectivity
        return False

online_connectivity = test_online_connectivity()

try:
    from aqt.sound import av_player
    from anki.sound import SoundOrVideoTag
    legacy_play = None
except (ImportError, ModuleNotFoundError):
    from anki.sound import play as legacy_play
    av_player = None

gen_ids = {
    "gen_1": 151,
    "gen_2": 251,
    "gen_3": 386,
    "gen_4": 493,
    "gen_5": 649,
    "gen_6": 721,
    "gen_7": 809,
    "gen_8": 905,
    "gen_9": 1025
}

gen_config = []
for i in range(1,10):
    gen_config.append(config[f"gen{i}"])

def check_id_ok(id_num):
    # Determine the generation of the given ID
    generation = 0
    for gen, max_id in gen_ids.items():
        if id_num <= max_id:
            generation = int(gen.split('_')[1])
            break

    if generation == 0:
        return False  # ID does not belong to any generation

    return gen_config[generation - 1]

#count index - count 10 cards - easy = 20, good = 10, hard = 5, again = 0
# if index = 40 - 100 => normal ; multiply with damage
# if index < 40 => attack misses


def special_pokemon_names_for_min_level(name):
    if name == "flabébé":
        return "flabebe"
    elif name == "sirfetch'd":
        return "sirfetchd"
    elif name == "farfetch'd":
        return "farfetchd"
    elif name == "porygon-z":
        return "porygonz"
    elif name == "kommo-o":
        return "kommoo"
    elif name == "hakamo-o":
        return "hakamoo"
    elif name == "jangmo-o":
        return "jangmoo"
    elif name == "mr. rime":
        return "mrrime"
    elif name == "mr. mime":
        return "mrmime"
    elif name == "nidoran♂":
        return "nidoranm"
    elif name == "nidoran":
        return "nidoranf"
    else:
        #showWarning("Error in Handling Pokémon name")
        return name

def answerCard_before(filter, reviewer, card):
	utils.answBtnAmt = reviewer.mw.col.sched.answerButtons(card)
	return filter

aqt.gui_hooks.reviewer_will_answer_card.append(answerCard_before)
# Globale Variable für die Zählung der Bewertungen
card_ratings_count = {"Again": 0, "Hard": 0, "Good": 0, "Easy": 0}

def answerCard_after(rev, card, ease):
    maxEase = utils.answBtnAmt
    aw = aqt.mw.app.activeWindow() or aqt.mw
    # Aktualisieren Sie die Zählung basierend auf der Bewertung
    global card_ratings_count
    if ease == 1:
        msg = "Again"
        color = "#FF9999"
        card_ratings_count["Again"] += 1
    elif ease == maxEase - 2:
        msg = "Hard"
        color = "#A3A3A3"
        card_ratings_count["Hard"] += 1
    elif ease == maxEase - 1:
        msg = "Good"
        color = "#99FFA4"
        card_ratings_count["Good"] += 1
    elif ease == maxEase:
        msg = "Easy"
        color = "#BBEEFF"
        card_ratings_count["Easy"] += 1
    else:
        # default behavior for unforeseen cases
        tooltip("Error in ColorConfirmation add-on: Couldn't interpret ease")
    #showInfo(f"{msg} + {card_ratings_count['Again']}, {card_ratings_count['Hard']}, {card_ratings_count['Good']}, {card_ratings_count['Easy']}")

aqt.gui_hooks.reviewer_did_answer_card.append(answerCard_after)

def get_image_as_base64(path):
    with open(path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

if learnsets_data != False:
    def get_random_moves_for_pokemon(pokemon_name, level):
        """
        Get up to 4 random moves learned by a Pokémon at a specific level and lower, along with the highest level,
        excluding moves that can be learned at a higher level.

        Args:
            json_file_name (str): The name of the JSON file containing Pokémon learnset data.
            pokemon_name (str): The name of the Pokémon.
            level (int): The level at which to check for moves.

        Returns:
            list: A list of up to 4 random moves and their highest levels.
        """
        global learnset_path
        # Load the JSON file
        with open(learnset_path, 'r') as file:
            learnsets = json.load(file)

        # Normalize the Pokémon name to lowercase for consistency
        pokemon_name = pokemon_name.lower()

        # Retrieve the learnset for the specified Pokémon
        pokemon_learnset = learnsets.get(pokemon_name, {})

        # Create a dictionary to store moves and their corresponding highest levels
        moves_at_level_and_lower = {}

        # Loop through the learnset dictionary
        for move, levels in pokemon_learnset.get('learnset', {}).items():
            highest_level = float('-inf')  # Initialize with negative infinity
            eligible_moves = []  # Store moves eligible for inclusion

            for move_level in levels:
                # Check if the move_level string contains 'L'
                if 'L' in move_level:
                    # Extract the level from the move_level string
                    move_level_int = int(move_level.split('L')[1])

                    # Check if the move can be learned at the specified level or lower
                    if move_level_int <= level:
                        # Update the highest_level if a higher level is found
                        highest_level = max(highest_level, move_level_int)
                        eligible_moves.append(move)

            # Check if the eligible moves can be learned at a higher level
            if highest_level != float('-inf'):
                can_learn_at_higher_level = any(
                    int(move_level.split('L')[1]) > highest_level
                    for move_level in levels
                    if 'L' in move_level
                )
                if not can_learn_at_higher_level:
                    moves_at_level_and_lower[move] = highest_level

        attacks = []
        if moves_at_level_and_lower:
            # Convert the dictionary into a list of tuples for random selection
            moves_and_levels_list = list(moves_at_level_and_lower.items())
            random.shuffle(moves_and_levels_list)

            # Pick up to 4 random moves and append them to the attacks list
            for move, highest_level in moves_and_levels_list[:4]:
                #attacks.append(f"{move} at level: {highest_level}")
                attacks.append(f"{move}")

        return attacks

def pick_random_gender(pokemon_name):
    """
    Randomly pick a gender for a given Pokémon based on its gender ratios.

    Args:
        pokemon_name (str): The name of the Pokémon.
        pokedex_data (dict): Pokémon data loaded from the pokedex JSON file.

    Returns:
        str: "M" for male, "F" for female, or "Genderless" for genderless Pokémon.
    """
    global pokedex_path
    with open(pokedex_path, 'r', encoding="utf-8") as file:
        pokedex_data = json.load(file)
    pokemon_name = pokemon_name.lower()  # Normalize Pokémon name to lowercase
    pokemon = pokedex_data.get(pokemon_name)

    if pokemon:
        gender_ratio = pokemon.get("genderRatio")
        if gender_ratio:
            random_number = random.random()  # Generate a random number between 0 and 1
            if random_number < gender_ratio["M"]:
                #return "M"  # Male
                gender = "M"
                return gender
            elif random_number > gender_ratio["M"]:
                #return "F"  # Female
                gender = "F"
                return gender
        else:
            genders = pokemon.get("gender")
            if genders:
                #showInfo(f"gender ist {gender}")
                if genders == "F":
                    #return "M"
                    gender = "F"
                elif genders == "M":
                    #return "F"
                    gender = "M"
                elif genders == "N":
                    gender = "N"
                return gender
            else:
                genders = ["M", "F"]
                #genders = ["M", "♀"]
                gender = random.choice(genders)
                return gender
                # Randomly choose between "M" and "F"
    else:
        genders = ["M", "F"]
        gender = random.choice(genders)
        return gender

if learnsets_data != False:
    def get_levelup_move_for_pokemon(pokemon_name, level):
        """
        Get a random move learned by a Pokémon at a specific level and lower, excluding moves that can be learned at a higher level.

        Args:
            pokemon_name (str): The name of the Pokémon.
            level (int): The level at which to check for moves.

        Returns:
            str: A random move and its highest level.
        """
        global learnset_path
        # Load the JSON file
        with open(learnset_path, 'r') as file:
            learnsets = json.load(file)

        # Normalize the Pokémon name to lowercase for consistency
        pokemon_name = pokemon_name.lower()

        # Retrieve the learnset for the specified Pokémon
        pokemon_learnset = learnsets.get(pokemon_name, {})

        # Create a dictionary to store moves and their corresponding highest levels
        moves_at_level_and_lower = {}

        # Loop through the learnset dictionary
        for move, levels in pokemon_learnset.get('learnset', {}).items():
            highest_level = float('-inf')  # Initialize with negative infinity
            eligible_moves = []  # Store moves eligible for inclusion

            for move_level in levels:
                # Check if the move_level string contains 'L'
                if 'L' in move_level:
                    # Extract the level from the move_level string
                    move_level_int = int(move_level.split('L')[1])

                    # Check if the move can be learned at the specified level or lower
                    if move_level_int <= level:
                        # Update the highest_level if a higher level is found
                        highest_level = max(highest_level, move_level_int)
                        eligible_moves.append(move)

            # Check if the move can be learned at a higher level
            can_learn_at_higher_level = any(
                'L' in move_level and int(move_level.split('L')[1]) > level
                for move_level in levels
            )

            # Add the move and its highest level to the dictionary if not learnable at a higher level
            if highest_level != float('-inf') and not can_learn_at_higher_level:
                moves_at_level_and_lower[move] = highest_level

        if moves_at_level_and_lower:
            # Filter moves with the same highest level as the input level
            eligible_moves = [
                move for move, highest_level in moves_at_level_and_lower.items()
                if highest_level == level
            ]
            #if eligible_moves:
                # Randomly select and return a move
               #random_attack = random.choice(eligible_moves)
               # return f"{random_attack} at level: {level}"
           # else:
                #return "No moves to be found."
       # else:
            #return f"{pokemon_name} does not learn any new moves at level {level} or lower."
            return eligible_moves

def split_string_by_length(input_string, max_length):
    current_length = 0
    current_line = []

    for word in input_string.split():
        word_length = len(word)  # Change this to calculate length in pixels

        if current_length + len(current_line) + word_length <= max_length:
            current_line.append(word)
            current_length += word_length
        else:
            yield ' '.join(current_line)
            current_line = [word]
            current_length = word_length

    yield ' '.join(current_line)


def resize_pixmap_img(pixmap, max_width):
    original_width = pixmap.width()
    original_height = pixmap.height()
    new_width = max_width
    new_height = (original_height * max_width) // original_width
    pixmap2 = pixmap.scaled(new_width, new_height)
    return pixmap2

def random_battle_scene():
    global battlescene_path
    battle_scenes = {}
    for index, filename in enumerate(os.listdir(battlescene_path)):
        if filename.endswith(".png"):
            battle_scenes[index + 1] = filename
    # Get the corresponding file name
    battlescene_file = battle_scenes.get(random.randint(1, len(battle_scenes)))

    return battlescene_file

if berries_sprites != False:
    def random_berries():
        global berries_path
        berries = {}
        for index, filename in enumerate(os.listdir(berries_path)):
            if filename.endswith(".png"):
                berries[index + 1] = filename
        # Get the corresponding file name
        berries_file = berries.get(random.randint(1, len(berries)))
        return berries_file

if item_sprites != False:
    def random_item():
        global items_path
        # Initialize an empty list to store the file names
        item_names = []
        # Iterate over each file in the directory
        for file in os.listdir(items_path):
            # Check if the file is a .png file
            if file.endswith(".png"):
                # Append the file name without the .png extension to the list
                item_names.append(file[:-4])
        item_names = [name for name in item_names if not name.endswith("-ball")]
        item_names = [name for name in item_names if not name.endswith("-repel")]
        item_names = [name for name in item_names if not name.endswith("-incense")]
        item_names = [name for name in item_names if not name.endswith("-fang")]
        item_names = [name for name in item_names if not name.endswith("dust")]
        item_names = [name for name in item_names if not name.endswith("-piece")]
        item_names = [name for name in item_names if not name.endswith("-nugget")]
        item_name = random.choice(item_names)
        return item_name

    def random_fossil():
        global items_path
        fossil_names = []
        # Iterate over each file in the directory
        for file in os.listdir(items_path):
            # Check if the file is a .png file
            if file.endswith("-fossil.png"):
                # Append the file name without the .png extension to the list
                fossil_names.append(file[:-4])
        fossil_name = random.choice(fossil_names)
        return fossil_name

def random_egg():
    # Fetch random Pokémon data from Generation
    # Load the JSON file with Pokémon data
    global addon_dir
    global pokemon_hp
    global pokemon_encounter
    egg_counter = random.randint(200, 1500)
    generation_file = "merged_file.json"
    try:
        with open(str(addon_dir / generation_file), "r") as json_file:
            wild_pokemon_data = json.load(json_file)
            # Select 1 Pokémon from the list
            random_pokemon_list = random.sample(wild_pokemon_data, 1)
            # Extract information about the selected Pokémon
            for random_pokemon_data in random_pokemon_list:
                true_name = random_pokemon_data["name"]
                name = "Egg"
                id = random_pokemon_data["id"]
                ability = random.sample(random_pokemon_data["abilities"], 1)
                type = random.sample(random_pokemon_data["types"], 1)
                stats = random_pokemon_data["stats"]
                level = 0  # Random level between 1 and 100
                enemy_attacks = get_random_moves_for_pokemon(name, level)
                base_experience = random_pokemon_data["base_experience"]
                return name, id, level, ability, type, stats, attacks, base_experience, egg_counter
    except FileNotFoundError:
        mw.showInfo("Error", "Can't create egg.")
        # Set the layout for the dialog

#def copy_directory(dir_addon: str, dir_anki: str = None)
#       if not dir_anki:
        #dir_anki = dir_addon
    #fromdir = addon_dir / dir_addon
    #todir = mediafolder / dir_anki
    #if not fromdir.is_dir():
        #return
    #if not todir.is_dir():
        #shutil.copytree(str(fromdir), str(todir))
    #else:
        #distutils.dir_util.copy_tree(str(fromdir), str(todir))

#hp = 100
caught_pokemon = {} #pokemon not caught

def get_pokemon_names_by_category_from_file(category_name):
    global all_species_path
    # Load the JSON data from the file
    with open(all_species_path, 'r') as file:
        pokemon_data = json.load(file)
    # Convert the input to lowercase to match the keys in our JSON data
    category_name = category_name.lower()
    # Filter the Pokémon data to only include those in the given category
    pokemon_in_category = [
        name for name, details in pokemon_data.items()
        if details['Species'].lower() == category_name
    ]
    return pokemon_in_category

def check_min_generate_level(pkmn_name):
    name = f"{pkmn_name}"
    # Update mainpokemon_evolution and handle evolution logic
    #mainpokemon_evolution = search_pokedex(name.lower(), "evos")
    #if mainpokemon_evolution is not None:
    #    try:
    #        for pokemon in mainpokemon_evolution:
    #            mainpokemon_evolution_type = search_pokedex(pokemon.lower(), "evoType")
    #            min_level = search_pokedex(pokemon.lower(), "evoLevel")
    #            if mainpokemon_evolution_type is not None:
    #                min_level = 100
    #            return min_level
    #    except Exception as e:
    #        showInfo(f"An error occurred: {e}")
    #        return None
    evoType = search_pokedex(name.lower(), "evoType")
    evoLevel = search_pokedex(name.lower(), "evoLevel")
    #showInfo(f"{evoLevel}, {evoType}")
    if evoLevel is not None:
        return int(evoLevel)
    elif evoType is not None:
        min_level = 100
        return int(min_level)
    elif evoType and evoLevel is None:
        min_level = 1
        return int(min_level)
    else:
        min_level = 1
        return min_level

def check_evo_level(pkmn_name):
    global min_level_file_path
    try:
        with open(min_level_file_path, 'r') as file:
            data = json.load(file)

        pokemon_info = data.get(pkmn_name.lower())

        if pokemon_info:
            evolution_level = pokemon_info.get('evolution_level')
            evolution_type = pokemon_info.get('evolution_type')
            evolution_condition = pokemon_info.get('evolution_condition')
            # Check if the evolution level is a number or "None"
            if evolution_level == "None":
                evolution_level = 0
        else:
            evolution_level = 0
        return evolution_level
            #showInfo(f"Pokemon '{pkmn_name}' not found in the file.")
            #return None
    except Exception as e:
        showInfo(f"An error occurred: {e}")
        return None

def customCloseTooltip(tooltipLabel):
	if tooltipLabel:
		try:
			tooltipLabel.deleteLater()
		except:
			# already deleted as parent window closed
			pass
		tooltipLabel = None

def tooltipWithColour(msg, color, x=0, y=20, xref=1, period=3000, parent=None, width=0, height=0, centered=False):
    global _tooltipLabel
    tooltipTimer = 4000
    class CustomLabel(QLabel):
        silentlyClose = True

        def mousePressEvent(self, evt):
            evt.accept()
            self.hide()

    closeTooltip()
    aw = parent or aqt.mw.app.activeWindow() or aqt.mw
    x = aw.mapToGlobal(QPoint(x + int(round(aw.width() / 2, 0)), 0)).x()
    y = aw.mapToGlobal(QPoint(0,aw.height()-180)).y()

    # apply width and height
    styleString1 = "height:100%; height: 100%; background: red;"
    styleString2 = "padding: 8px 13px; text-align: center;"

    lab = CustomLabel("""\
<table cellpadding=0 padding=0px style="height:100%; height: 100%;">
<tr>
<td style="padding: 8px 13px; text-align: center; z-index: 10000;">""" + msg + """</td>
</tr>
</table>""", aw)
    lab.setFrameStyle(QFrame.Panel)
    lab.setLineWidth(2)
    lab.setWindowFlags(Qt.ToolTip)
    lab.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)

    # adjust height if user configured custom height

    if (width > 0):
        lab.setFixedWidth(width)
    if (height > 0):
        lab.setFixedHeight(height)

    p = QPalette()
    p.setColor(QPalette.Window, QColor(color))
    p.setColor(QPalette.WindowText, QColor("#000000"))
    lab.setPalette(p)
    lab.show()
    lab.move(QPoint(x - int(round(lab.width() * 0.5 * xref, 0)), y))

    def handler():
        customCloseTooltip(lab)

    t = QTimer(aqt.mw)
    t.setSingleShot = True
    t.timeout.connect(handler)
    t.start(period)

    _tooltipLabel = lab
# Your random Pokémon generation function using the PokeAPI
if all_species != False:
    def generate_random_pokemon():
        # Fetch random Pokémon data from Generation
        # Load the JSON file with Pokémon data
        global addon_dir
        global pokemon_encounter
        global hp, gender, name
        global mainpokemon_level
        pokemon_encounter = 0
        generation_file = ("pokeapi_db.json")
        try:
            if card_counter < 100:
                name = get_pokemon_by_category("Normal")
            elif card_counter < 200:
                name = get_pokemon_by_category("Ultra")
            elif card_counter < 300:
                name = get_pokemon_by_category("Legendary")
            elif card_counter < 400:
                name = get_pokemon_by_category("Mythical")
            var_level = 3
            try:
                level = random.randint((mainpokemon_level - (random.randint(0, var_level))), (
                        mainpokemon_level + (random.randint(0, var_level))))  # Random level between 1 and 100
            except:
                mainpokemon_level = 5
                level = 5
            if level < 0:
                level = 1
            try:
                min_level = check_min_generate_level(name.lower())
            except:
                # showInfo(f"{name}")
                generate_random_pokemon()
            if min_level is not None:
                min_level = int(min_level)
            elif min_level is None:
                # showInfo(f"{min_level}, {name}")
                level = 5
                min_level = 0
            if mainpokemon_level is None:
                level = 5
                min_level = 0
            if min_level < level:
                id = search_pokedex(name, "num")
                id_check = check_id_ok(id)
                if id_check:
                    pass
                else:
                    return generate_random_pokemon()
                abilities = search_pokedex(name, "abilities")
                # Filter abilities to include only those with numeric keys
                # numeric_abilities = {k: v for k, v in abilities.items() if k.isdigit()}
                numeric_abilities = None
                try:
                    numeric_abilities = {k: v for k, v in abilities.items() if k.isdigit()}
                except:
                    ability = "No Ability"
                # Check if there are numeric abilities
                if numeric_abilities:
                    # Convert the filtered abilities dictionary values to a list
                    abilities_list = list(numeric_abilities.values())
                    # Select a random ability from the list
                    ability = random.choice(abilities_list)
                else:
                    # Set to "No Ability" if there are no numeric abilities
                    ability = "No Ability"
                # ability = abilities.get("0", "No ability")
                # if ability == "No ability":
                #    ability = abilities.get("H", None)
                type = search_pokedex(name, "types")
                stats = search_pokedex(name, "baseStats")
                enemy_attacks = get_random_moves_for_pokemon(name, level)
                # base_experience = search_pokeapi_db(name, "base_experience")
                base_experience = 100
                growth_rate = search_pokeapi_db(f"{name.lower()}", "growth_rate")
                if gender is None:
                    gender = pick_random_gender(name)
                iv = {
                    "hp": random.randint(1, 32),
                    "atk": random.randint(1, 32),
                    "def": random.randint(1, 32),
                    "spa": random.randint(1, 32),
                    "spd": random.randint(1, 32),
                    "spe": random.randint(1, 32)
                }
                ev = {
                    "hp": 0,
                    "atk": 0,
                    "def": 0,
                    "spa": 0,
                    "spd": 0,
                    "spe": 0
                }
                # battle_stats = {}
                # for d in [stats, iv, ev]:
                #    for key, value in d.items():
                #        battle_stats[key] = value
                battle_stats = stats
                battle_status = "fighting"
                try:
                    hp_stat = int(stats['hp'])
                except Exception as e:
                    showInfo(f"Error occured: {e}")
                hp = calculate_hp(hp_stat, level, ev, iv)
                max_hp = hp
                global ev_yield
                ev_yield = search_pokeapi_db(f"{name.lower()}", "effort_values")
                return name, id, level, ability, type, stats, enemy_attacks, base_experience, growth_rate, hp, max_hp, ev, iv, gender, battle_status, battle_stats
            else:
                return generate_random_pokemon()  # Return the result of the recursive call
        except FileNotFoundError:
            showInfo("Error", "Can't open the JSON File.")
            # Set the layout for the dialog

def kill_pokemon():
    global level, hp, name, image_url, mainpokemon_xp, mainpokemon_base_experience, mainpokemon_name, mainpokemon_level, mainpokemon_path, mainpokemon_growth_rate, mainpokemon_hp, ev_yield
    global pkmn_window
    name = name.capitalize()
    exp = int(calc_experience(mainpokemon_base_experience, level))
    mainpokemon_level = save_main_pokemon_progress(mainpokemon_path, mainpokemon_level, mainpokemon_name, mainpokemon_base_experience, mainpokemon_growth_rate, exp)
    if pkmn_window is True:
        new_pokemon()  # Show a new random Pokémon

caught = 0

def display_dead_pokemon():
    global pokemon_hp, name, id, level, caught_pokemon, pkmnimgfolder, frontdefault, addon_dir, caught
    # Create the dialog
    w_dead_pokemon = QDialog(mw)
    w_dead_pokemon.setWindowTitle(f"Would you want to kill or catch the wild {name} ?")
    # Create a layout for the dialog
    layout2 = QVBoxLayout()
    # Display the Pokémon image
    pkmnimage_file = f"{id}.png"
    pkmnimage_path = addon_dir / frontdefault / pkmnimage_file
    pkmnimage_label = QLabel()
    pkmnpixmap = QPixmap()
    pkmnpixmap.load(str(pkmnimage_path))
    # Calculate the new dimensions to maintain the aspect ratio
    max_width = 200
    original_width = pkmnpixmap.width()
    original_height = pkmnpixmap.height()

    if original_width > max_width:
        new_width = max_width
        new_height = (original_height * max_width) // original_width
        pkmnpixmap = pkmnpixmap.scaled(new_width, new_height)

    # Create a painter to add text on top of the image
    painter2 = QPainter(pkmnpixmap)

    # Capitalize the first letter of the Pokémon's name
    capitalized_name = name.capitalize()
    # Create level text
    lvl = (f" Level: {level}")

    # Draw the text on top of the image
    font = QFont()
    font.setPointSize(16)  # Adjust the font size as needed
    painter2.setFont(font)
    fontlvl = QFont()
    fontlvl.setPointSize(12)
    painter2.end()

    # Create a QLabel for the capitalized name
    name_label = QLabel(capitalized_name)
    name_label.setFont(font)

    # Create a QLabel for the level
    level_label = QLabel(lvl)
    # Align to the center
    level_label.setFont(fontlvl)

    # Create buttons for catching and killing the Pokémon
    catch_button = QPushButton("Catch Pokémon")
    kill_button = QPushButton("Kill Pokémon")
    qconnect(catch_button.clicked, catch_pokemon)
    qconnect(kill_button.clicked, kill_pokemon)

    # Set the merged image as the pixmap for the QLabel
    pkmnimage_label.setPixmap(pkmnpixmap)
    layout2.addWidget(pkmnimage_label)

    # add all widgets to the dialog window
    layout2.addWidget(name_label)
    layout2.addWidget(level_label)
    layout2.addWidget(catch_button)
    layout2.addWidget(kill_button)

    # align things needed to middle
    pkmnimage_label.setAlignment(Qt.AlignCenter)
    level_label.setAlignment(Qt.AlignCenter)
    name_label.setAlignment(Qt.AlignCenter)  # Align to the center

    # Set the layout for the dialog
    w_dead_pokemon.setLayout(layout2)

    if w_dead_pokemon is not None:
        # Close the existing dialog if it's open
        w_dead_pokemon.accept()
    # Show the dialog
    result = w_dead_pokemon.exec_()
    # Check the result to determine if the user closed the dialog
    if result == QDialog.Rejected:
        w_dead_pokemon = None  # Reset the global window reference

def get_pokemon_by_category(category_name):
    # Reload the JSON data from the file
    global all_species_path
    with open(all_species_path, 'r') as file:
        pokemon_data = json.load(file)
    # Convert the input to lowercase to match the values in our JSON data
    category_name = category_name.lower()

    # Filter the Pokémon data to only include those in the given tier
    pokemon_in_tier = [pokemon['name'] for pokemon in pokemon_data if pokemon['Tier'].lower() == category_name]
    random_pokemon_name_from_tier = f"{(random.choice(pokemon_in_tier)).lower()}"
    random_pokemon_name_from_tier = special_pokemon_names_for_min_level(random_pokemon_name_from_tier)
    return random_pokemon_name_from_tier #return random pokemon name from that category

def save_caught_pokemon(nickname):
    # Create a dictionary to store the Pokémon's data
    # add all new values like hp as max_hp, evolution_data, description and growth rate
    stats = search_pokedex(name.lower(),"baseStats")
    stats["xp"] = 0
    ev = {
      "hp": 0,
      "atk": 0,
      "def": 0,
      "spa": 0,
      "spd": 0,
      "spe": 0
    }
    evos = search_pokedex(name, "evos")
    if evos is None:
        evos = ""
    caught_pokemon = {
        "name": name.capitalize(),
        "nickname": nickname,
        "level": level,
        "gender": gender,
        "id": search_pokedex(name.lower(),'num'),
        "ability": ability,
        "type": type,
        "stats": stats,
        "ev": ev,
        "iv": iv,
        "attacks": enemy_attacks,
        "base_experience": base_experience,
        "current_hp": calculate_hp(int(stats["hp"]),level, ev, iv),
        "growth_rate": growth_rate,
        "evos": evos
    }
    # Load existing Pokémon data if it exists
    if mypokemon_path.is_file():
        with open(mypokemon_path, "r") as json_file:
            caught_pokemon_data = json.load(json_file)
    else:
        caught_pokemon_data = []

    # Append the caught Pokémon's data to the list
    caught_pokemon_data.append(caught_pokemon)

    # Save the caught Pokémon's data to a JSON file
    with open(str(mypokemon_path), "w") as json_file:
        json.dump(caught_pokemon_data, json_file, indent=2)

def find_details_move(move_name):
    global moves_file_path
    try:
        with open(moves_file_path, "r", encoding="utf-8") as json_file:
            moves_data = json.load(json_file)
            move = moves_data.get(move_name.lower())  # Use get() to access the move by name
            if move:
                return move
            else:
                showInfo(f"Move '{move_name}' not found.")
                return None
    except FileNotFoundError:
        showInfo("Moves Data File Missing!\nPlease Download Moves Data")
        return None
    except json.JSONDecodeError as e:
        showInfo(f"Error decoding JSON: {e}")
        return None

def save_main_pokemon_progress(mainpokemon_path, mainpokemon_level, mainpokemon_name, mainpokemon_base_experience, mainpokemon_growth_rate, exp):
    global mainpokemon_current_hp, mainpokemon_ev, ev_yield, mainpokemon_evolution, mainpokemon_xp
    experience = find_experience_for_level(mainpokemon_growth_rate, mainpokemon_level)
    mainpokemon_xp += exp
    if mainpokemon_path.is_file():
        with open(mainpokemon_path, "r") as json_file:
            main_pokemon_data = json.load(json_file)
    else:
        showWarning("Missing Mainpokemon Data !")
    if int(experience) < int(mainpokemon_xp):
        mainpokemon_level += 1
        showInfo(f"Your {mainpokemon_name} is now level {mainpokemon_level} !")
        mainpokemon_xp = 0
        name = f"{mainpokemon_name}"
        # Update mainpokemon_evolution and handle evolution logic
        mainpokemon_evolution = search_pokedex(name.lower(), "evos")
        if mainpokemon_evolution:
            for pokemon in mainpokemon_evolution:
                min_level = search_pokedex(pokemon.lower(), "evoLevel")
                if min_level == mainpokemon_level:
                    showInfo(f"{mainpokemon_name} is about to evolve to {pokemon} at level {min_level}")
                    evo_window.display_pokemon_evo(mainpokemon_name.lower())
                else:
                    for mainpkmndata in main_pokemon_data:
                        if mainpkmndata["name"] == mainpokemon_name.capitalize():
                            attacks = mainpkmndata["attacks"]
                            # showInfo(f"{attacks}")
                            new_attacks = get_levelup_move_for_pokemon(mainpokemon_name.lower(),int(mainpokemon_level))
                            if new_attacks:
                                showInfo(f"Your {mainpokemon_name.capitalize()} can now learn a new attack !")
                            for new_attack in new_attacks:
                                if len(attacks) < 4:
                                    attacks.append(new_attack)
                                else:
                                    dialog = AttackDialog(attacks, new_attack)
                                    if dialog.exec() == QDialog.DialogCode.Accepted:
                                        selected_attack = dialog.selected_attack
                                        index_to_replace = None
                                        for index, attack in enumerate(attacks):
                                            if attack == selected_attack:
                                                index_to_replace = index
                                                pass
                                            else:
                                                pass
                                        # If the attack is found, replace it with 'new_attack'
                                        if index_to_replace is not None:
                                            attacks[index_to_replace] = new_attack
                                            showInfo(
                                                f"Replaced '{selected_attack}' with '{new_attack}'")
                                        else:
                                            showInfo(f"'{selected_attack}' not found in the list")
                                    else:
                                        # Handle the case where the user cancels the dialog
                                        showInfo("No attack selected")
                            mainpkmndata["attacks"] = attacks
                            break
        else:
            for mainpkmndata in main_pokemon_data:
                if mainpkmndata["name"] == mainpokemon_name.capitalize():
                    attacks = mainpkmndata["attacks"]
                    # showInfo(f"{attacks}")
                    new_attacks = get_levelup_move_for_pokemon(mainpokemon_name.lower(), int(mainpokemon_level))
                    if new_attacks:
                        showInfo(f"Your {mainpokemon_name.capitalize()} can now learn a new attack !")
                    for new_attack in new_attacks:
                        if len(attacks) < 4:
                            attacks.append(new_attack)
                        else:
                            dialog = AttackDialog(attacks, new_attack)
                            if dialog.exec() == QDialog.DialogCode.Accepted:
                                selected_attack = dialog.selected_attack
                                index_to_replace = None
                                for index, attack in enumerate(attacks):
                                    if attack == selected_attack:
                                        index_to_replace = index
                                        pass
                                    else:
                                        pass
                                # If the attack is found, replace it with 'new_attack'
                                if index_to_replace is not None:
                                    attacks[index_to_replace] = new_attack
                                    showInfo(
                                        f"Replaced '{selected_attack}' with '{new_attack}'")
                                else:
                                    showInfo(f"'{selected_attack}' not found in the list")
                            else:
                                # Handle the case where the user cancels the dialog
                                showInfo("No attack selected")
                    mainpkmndata["attacks"] = attacks
                    break
    else:
        showInfo(f"Your {mainpokemon_name} has gained {exp} XP.\n {experience} exp is needed for next level \n Your pokemon currently has {mainpokemon_xp}")
    # Load existing Pokémon data if it exists

    for mainpkmndata in main_pokemon_data:
        mainpkmndata["stats"]["xp"] = int(mainpokemon_xp)
        mainpkmndata["level"] = int(mainpokemon_level)
        mainpkmndata["current_hp"] = int(mainpokemon_current_hp)
        #for stat, values in ev_yield.items():
        #for attribute, value in values.items():
        #mainpkmndata["ev"][stat][attribute] += int(value)
        mainpkmndata["ev"]["hp"] += ev_yield["hp"]
        mainpkmndata["ev"]["atk"] += ev_yield["attack"]
        mainpkmndata["ev"]["def"] += ev_yield["defense"]
        mainpkmndata["ev"]["spa"] += ev_yield["special-attack"]
        mainpkmndata["ev"]["spd"] += ev_yield["special-defense"]
        mainpkmndata["ev"]["spe"] += ev_yield["speed"]
    mypkmndata = mainpkmndata
    mainpkmndata = [mainpkmndata]
    # Save the caught Pokémon's data to a JSON file
    with open(str(mainpokemon_path), "w") as json_file:
        json.dump(mainpkmndata, json_file, indent=2)

    # Find the specified Pokémon's data in mainpokemondata
    #selected_pokemon_data = None
    #for pokemon_data in mainpkmndata:
        #if pokemon_data["name"] == mainpokemon_name:
            #selected_pokemon_data = pokemon_data

    #if selected_pokemon_data is not None:
        # Modify the selected Pokémon's data
        #selected_pokemon_data["stats"]["xp"] = mainpokemon_xp
        #selected_pokemon_data["level"] = mainpokemon_level  # Replace with the actual level
        #selected_pokemon_data["current_hp"] = mainpokemon_current_hp  # save current hp

        # Load data from the output JSON file
    with open(str(mypokemon_path), "r") as output_file:
        mypokemondata = json.load(output_file)

        # Find and replace the specified Pokémon's data in mypokemondata
        for index, pokemon_data in enumerate(mypokemondata):
            if pokemon_data["name"] == mainpokemon_name:
                mypokemondata[index] = mypkmndata
                break
        # Save the modified data to the output JSON file
        with open(str(mypokemon_path), "w") as output_file:
            json.dump(mypokemondata, output_file, indent=2)

    return mainpokemon_level

def evolve_pokemon(pkmn_name):
    global mainpokemon_path
    global addon_dir
    try:
        evoName = search_pokedex(pkmn_name.lower(), "evos")
        evoName = f"{evoName[0]}"
        #showInfo(f"{evoName}")
        with open(mypokemon_path, "r") as json_file:
            captured_pokemon_data = json.load(json_file)
            pokemon = None
            if captured_pokemon_data:
                for pokemon_data in captured_pokemon_data:
                    if pokemon_data['name'] == pkmn_name.capitalize():
                        pokemon = pokemon_data
                        if pokemon is not None:
                            pokemon["name"] = evoName.capitalize()
                            pokemon["id"] = int(search_pokedex(evoName.lower(), "num"))
                            # pokemon["ev"] = ev
                            # pokemon["iv"] = iv
                            pokemon["type"] = search_pokedex(evoName.lower(), "types")
                            pokemon["evos"] = []
                            attacks = pokemon["attacks"]
                            #showInfo(f"{attacks}")
                            new_attacks = get_random_moves_for_pokemon(evoName, int(pokemon["level"]))
                            for new_attack in new_attacks:
                                if len(attacks) < 4:
                                    attacks.append(new_attack)
                                else:
                                    dialog = AttackDialog(attacks, new_attack)
                                    if dialog.exec() == QDialog.DialogCode.Accepted:
                                        selected_attack = dialog.selected_attack
                                        index_to_replace = None
                                        for index, attack in enumerate(attacks):
                                            if attack == selected_attack:
                                                index_to_replace = index
                                                pass
                                            else:
                                                pass
                                        # If the attack is found, replace it with 'new_attack'
                                        if index_to_replace is not None:
                                            attacks[index_to_replace] = new_attack
                                            showInfo(
                                                f"Replaced '{selected_attack}' with '{new_attack}'")
                                        else:
                                            showInfo(f"'{selected_attack}' not found in the list")
                                    else:
                                        # Handle the case where the user cancels the dialog
                                        showInfo("No attack selected")
                            pokemon["attacks"] = attacks
                            if search_pokedex(evoName, "evos"):
                                pokemon["evos"].append(search_pokedex(evoName.lower(), "evos"))
                            stats = search_pokedex(evoName.lower(), "baseStats")
                            pokemon["stats"] = stats
                            pokemon["stats"]["xp"] = 0
                            hp_stat = int(stats['hp'])
                            hp = calculate_hp(hp_stat, level, ev, iv)
                            pokemon["current_hp"] = int(hp)
                            pokemon["gender"] = pick_random_gender(evoName.lower())
                            pokemon["growth_rate"] = search_pokeapi_db(evoName.lower(), "growth_rate")
                            abilities = search_pokedex(evoName.lower(), "abilities")
                            # Filter abilities to include only those with numeric keys
                            # numeric_abilities = {k: v for k, v in abilities.items() if k.isdigit()}
                            numeric_abilities = None
                            try:
                                numeric_abilities = {k: v for k, v in abilities.items() if k.isdigit()}
                            except:
                                ability = "No Ability"
                            # Check if there are numeric abilities
                            if numeric_abilities:
                                # Convert the filtered abilities dictionary values to a list
                                abilities_list = list(numeric_abilities.values())
                                # Select a random ability from the list
                                pokemon["ability"] = random.choice(abilities_list)
                            else:
                                # Set to "No Ability" if there are no numeric abilities
                                pokemon["ability"] = "No Ability"
                            # Load data from the output JSON file
                            with open(str(mypokemon_path), "r") as output_file:
                                mypokemondata = json.load(output_file)
                                # Find and replace the specified Pokémon's data in mypokemondata
                                for index, pokemon_data in enumerate(mypokemondata):
                                    if pokemon_data["name"] == pkmn_name.capitalize():
                                        mypokemondata[index] = pokemon
                                        break
                                        # Save the modified data to the output JSON file
                                with open(str(mypokemon_path), "w") as output_file:
                                    json.dump(mypokemondata, output_file, indent=2)
                            with open(str(mainpokemon_path), "r") as output_file:
                                mainpokemon_data = json.load(output_file)
                                # Find and replace the specified Pokémon's data in mypokemondata
                                for index, pokemon_data in enumerate(mainpokemon_data):
                                    if pokemon_data["name"] == pkmn_name.capitalize():
                                        mypokemondata[index] = pokemon
                                        break
                                    else:
                                        pass
                                            # Save the modified data to the output JSON file
                                with open(str(mainpokemon_path), "w") as output_file:
                                        pokemon = [pokemon]
                                        json.dump(pokemon, output_file, indent=2)
                            showInfo(f"Your {pkmn_name.capitalize()} has evolved to {evoName.capitalize()}! \n You can now close this Window.")
    except Exception as e:
        showWarning(f"{e}")
    prevo_name = pkmn_name
    evo_window.display_evo_pokemon(evoName.capitalize(), prevo_name)

def cancel_evolution(pkmn_name):
    global mainpokemon_current_hp, mainpokemon_ev, ev_yield, mainpokemon_evolutions
    # Load existing Pokémon data if it exists
    if mainpokemon_path.is_file():
        with open(mainpokemon_path, "r") as json_file:
            main_pokemon_data = json.load(json_file)
            for pokemon in main_pokemon_data:
                if pokemon["name"] == pkmn_name.capitalize():
                    attacks = pokemon["attacks"]
                    # showInfo(f"{attacks}")
                    new_attacks = get_random_moves_for_pokemon(pkmn_name.lower(), int(main_pokemon_data["level"]))
                    for new_attack in new_attacks:
                        if len(attacks) < 4:
                            attacks.append(new_attack)
                        else:
                            dialog = AttackDialog(attacks, new_attack)
                            if dialog.exec() == QDialog.DialogCode.Accepted:
                                selected_attack = dialog.selected_attack
                                index_to_replace = None
                                for index, attack in enumerate(attacks):
                                    if attack == selected_attack:
                                        index_to_replace = index
                                        pass
                                    else:
                                        pass
                                # If the attack is found, replace it with 'new_attack'
                                if index_to_replace is not None:
                                    attacks[index_to_replace] = new_attack
                                    showInfo(
                                        f"Replaced '{selected_attack}' with '{new_attack}'")
                                else:
                                    showInfo(f"'{selected_attack}' not found in the list")
                            else:
                                # Handle the case where the user cancels the dialog
                                showInfo("No attack selected")
                    break
            for mainpkmndata in main_pokemon_data:
                mainpkmndata["stats"]["xp"] = int(mainpokemon_xp)
                mainpkmndata["level"] = int(mainpokemon_level)
                mainpkmndata["current_hp"] = int(mainpokemon_current_hp)
                mainpkmndata["ev"]["hp"] += ev_yield["hp"]
                mainpkmndata["ev"]["atk"] += ev_yield["attack"]
                mainpkmndata["ev"]["def"] += ev_yield["defense"]
                mainpkmndata["ev"]["spa"] += ev_yield["special-attack"]
                mainpkmndata["ev"]["spd"] += ev_yield["special-defense"]
                mainpkmndata["ev"]["spe"] += ev_yield["speed"]
                mainpkmndata["attacks"] = attacks
    mypkmndata = mainpkmndata
    mainpkmndata = [mainpkmndata]
    # Save the caught Pokémon's data to a JSON file
    with open(str(mainpokemon_path), "w") as json_file:
        json.dump(mainpkmndata, json_file, indent=2)

    # Find the specified Pokémon's data in mainpokemondata
    #selected_pokemon_data = None
    #for pokemon_data in mainpkmndata:
        #if pokemon_data["name"] == mainpokemon_name:
            #selected_pokemon_data = pokemon_data

    #if selected_pokemon_data is not None:
        # Modify the selected Pokémon's data
        #selected_pokemon_data["stats"]["xp"] = mainpokemon_xp
        #selected_pokemon_data["level"] = mainpokemon_level  # Replace with the actual level
        #selected_pokemon_data["current_hp"] = mainpokemon_current_hp  # save current hp
        #selected_pokemon_data["attacks"] = attacks
        #selected_pokemon_data["ev"]["hp"] += ev_yield["hp"]
        #selected_pokemon_data["ev"]["atk"] += ev_yield["attack"]
        #selected_pokemon_data["ev"]["def"] += ev_yield["defense"]
        #selected_pokemon_data["ev"]["spa"] += ev_yield["special-attack"]
        #selected_pokemon_data["ev"]["spd"] += ev_yield["special-defense"]
        #selected_pokemon_data["ev"]["spe"] += ev_yield["speed"]

        # Load data from the output JSON file
    with open(str(mypokemon_path), "r") as output_file:
        mypokemondata = json.load(output_file)

        # Find and replace the specified Pokémon's data in mypokemondata
        for index, pokemon_data in enumerate(mypokemondata):
            if pokemon_data["name"] == pkmn_name:
                mypokemondata[index] = mypkmndata
                break
        # Save the modified data to the output JSON file
        with open(str(mypokemon_path), "w") as output_file:
            json.dump(mypokemondata, output_file, indent=2)

def calc_experience(base_experience, enemy_level):
    exp = base_experience * enemy_level / 7
    return exp

def catch_pokemon(nickname):
    global pokemon_hp, name, ability, enemy_attacks, type, stats, base_experience, level, growth_rate, gender, id, iv
    global mypokemon_path, caught
    caught += 1
    if caught == 1:
        save_caught_pokemon(nickname)
        name = name.capitalize()
        showInfo(f"You caught {name}!") # Display a message when the Pokémon is caught
        new_pokemon()  # Show a new random Pokémon
    else:
        showInfo("You have already caught the pokemon. Please close this window!") # Display a message when the Pokémon is caught

def get_random_starter():
    global addon_dir
    starters_path = addon_dir / "starters.json"
    # event if pokemon
    category = "Starter"
    try:
        # Reload the JSON data from the file
        with open(str(starters_path), 'r') as file:
            pokemon_in_tier = json.load(file)
            # Convert the input to lowercase to match the values in our JSON data
            category_name = category.lower()
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
            #showInfo(f"{water_starter}, {fire_starter}, {grass_starter}")
            random_gen = random.randint(0, 6)
            water_start = f"{water_starter[random_gen]}"
            fire_start = f"{fire_starter[random_gen]}"
            grass_start = f"{grass_starter[random_gen]}"
            #showInfo(f"{water_start}, {fire_start}, {grass_start}")
            return water_start, fire_start, grass_start
    except Exception as e:
        showWarning(f"Error in get_random_starter: {e}")
        return None, None, None


def calculate_max_hp_wildpokemon():
    global stats, level, ev, iv
    wild_pk_max_hp = calculate_hp(stats["hp"], level, ev, iv)
    return wild_pk_max_hp

def new_pokemon():
    global name, id, level, hp, max_hp, ability, type, attacks, base_experience, stats, battlescene_file, ev, iv, gender, battle_status
    global font_file
    global font_name
    # new pokemon
    gender = None
    name, id, level, ability, type, stats, enemy_attacks, base_experience, growth_rate, hp, max_hp, ev, iv, gender, battle_status, battle_stats = generate_random_pokemon()
    battlescene_file = random_battle_scene()
    max_hp = calculate_hp(stats["hp"], level, ev, iv)
    if test_window is not None:
        test_window.display_first_encounter()

def calc_atk_dmg(level, critical, power, stat_atk, wild_stat_def, main_type, move_type, wild_type, critRatio):
        if power is None:
            # You can choose a default power or handle it according to your requirements
            power = 0
        if critRatio == 1:
            crit_chance = 0.0417
        elif critRatio == 2:
            crit_chance = 0.125
        elif critRatio == 3:
            crit_chance = 0.5
        elif critRatio > 3:
            crit_chance = 1
        random_number = random.random()  # Generate a random number between 0 and 1
        if random_number > crit_chance:
            critical = critical * 1
        else:
            critical += 2
        # damage = (((2 * level * critical)+2)/ 5) * power * stat_atk / wild_stat_def)+2)/ 50 * stab * random
        # if move_typ is the same as the main pkmn type => damage * 1.5; else damage * 1.0
        # STAB calculation
        stab = 1.5 if move_type == main_type else 1.0
        eff = get_effectiveness(move_type)
        # random luck
        random_number = random.randint(217, 255)
        random_factor = random_number / 255
        damage = (((((2 * level * critical) + 2) / 5) * power * stat_atk / wild_stat_def) + 2) / 50 * stab * eff * random_factor
        # if main pkmn type = move type => damage * 1,5
        # if wild pokemon type x main pokemon type => 0.5 not very eff.; 1.0 eff.; 2 very eff.
        return damage

def calculate_hp(base_stat_hp, level, ev, iv):
    ev_value = ev["hp"] / 4
    iv_value = iv["hp"]
    #hp = int(((iv + 2 * (base_stat_hp + ev) + 100) * level) / 100 + 10)
    hp = int((((((base_stat_hp + iv_value) * 2 ) + ev_value) * level) / 100) + level + 10)
    return hp

def get_mainpokemon_evo(pokemon_name):
    global pokedex_path
    with open(str(pokedex_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            if pokemon_name in pokedex_data:
                pokemon_info = pokedex_data[pokemon_name]
                evolutions = pokemon_info.get("evos", [])
                return evolutions
            else:
                return []

def search_pokedex(pokemon_name,variable):
    global pokedex_path
    with open(str(pokedex_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            if pokemon_name in pokedex_data:
                pokemon_info = pokedex_data[pokemon_name]
                var = pokemon_info.get(variable, None)
                return var
            else:
                return []

def search_pokeapi_db(pokemon_name,variable):
    global addon_dir
    pokeapi_db_path = addon_dir / "pokeapi_db.json"
    with open(str(pokeapi_db_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            for pokemon_data in pokedex_data:
                name = pokemon_data["name"]
                if pokemon_data["name"] == pokemon_name:
                    var = pokemon_data.get(variable, None)
                    return var
            else:
                return []
def mainpokemon_data():
    global mainpkmn
    global mainpokemon_name, mainpokemon_id, mainpokemon_ability, mainpokemon_type, mainpokemon_stats, mainpokemon_attacks, mainpokemon_level, mainpokemon_base_experience, mainpokemon_xp, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate, mainpokemon_ev, mainpokemon_iv, mainpokemon_evolutions, mainpokemon_battle_stats, mainpokemon_gender
    mainpkmn = 1
    try:
        with (open(str(mainpokemon_path), "r", encoding="utf-8") as json_file):
                main_pokemon_datalist = json.load(json_file)
                main_pokemon_data = []
                for main_pokemon_data in main_pokemon_datalist:
                    mainpokemon_name = main_pokemon_data["name"]
                    mainpokemon_id = main_pokemon_data["id"]
                    mainpokemon_ability = main_pokemon_data["ability"]
                    mainpokemon_type = main_pokemon_data["type"]
                    mainpokemon_stats = main_pokemon_data["stats"]
                    mainpokemon_attacks = main_pokemon_data["attacks"]
                    mainpokemon_level = main_pokemon_data["level"]
                    mainpokemon_hp_base_stat = mainpokemon_stats["hp"]
                    mainpokemon_evolutions = search_pokedex(mainpokemon_name, "evos")
                    mainpokemon_xp = mainpokemon_stats["xp"]
                    mainpokemon_ev = main_pokemon_data["ev"]
                    mainpokemon_iv = main_pokemon_data["iv"]
                    #mainpokemon_battle_stats = mainpokemon_stats
                    mainpokemon_battle_stats = {}
                    for d in [mainpokemon_stats, mainpokemon_iv, mainpokemon_ev]:
                        for key, value in d.items():
                            mainpokemon_battle_stats[key] = value
                    #mainpokemon_battle_stats += mainpokemon_iv
                    #mainpokemon_battle_stats += mainpokemon_ev
                    mainpokemon_hp = calculate_hp(mainpokemon_hp_base_stat,mainpokemon_level, mainpokemon_ev, mainpokemon_iv)
                    mainpokemon_current_hp = calculate_hp(mainpokemon_hp_base_stat,mainpokemon_level, mainpokemon_ev, mainpokemon_iv)
                    mainpokemon_base_experience = main_pokemon_data["base_experience"]
                    mainpokemon_growth_rate = main_pokemon_data["growth_rate"]
                    mainpokemon_gender = main_pokemon_data["gender"]
                    return mainpokemon_name, mainpokemon_id, mainpokemon_ability, mainpokemon_type, mainpokemon_stats, mainpokemon_attacks, mainpokemon_level, mainpokemon_base_experience, mainpokemon_xp, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate, mainpokemon_ev, mainpokemon_iv, mainpokemon_evolutions, mainpokemon_battle_stats, mainpokemon_gender
    except:
            pass
#get main pokemon details:
if database_complete and sprites_complete != False:
    try:
        mainpokemon_name, mainpokemon_id, mainpokemon_ability, mainpokemon_type, mainpokemon_stats, mainpokemon_attacks, mainpokemon_level, mainpokemon_base_experience, mainpokemon_xp, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate, mainpokemon_ev, mainpokemon_iv, mainpokemon_evolutions, mainpokemon_battle_stats, mainpokemon_gender = mainpokemon_data()
        starter = True
    except:
        starter = False
    name, id, level, ability, type, stats, enemy_attacks, base_experience, growth_rate, hp, max_hp, ev, iv, gender, battle_status, battle_stats = generate_random_pokemon()
    battlescene_file = random_battle_scene()

def show_random_pokemon():
    global hp, name, id, stats, level, max_hp, base_experience, ev, iv
    global caught_pokemon
    global pkmnimgfolder, backdefault, addon_dir
    global caught
    global mainpkmn, mainpokemon_path
    global mainpokemon_id, mainpokemon_name, mainpokemon_level, mainpokemon_ability, mainpokemon_type, mainpokemon_xp, mainpokemon_stats, mainpokemon_attacks, mainpokemon_base_experience, mainpokemon_ev, mainpokemon_iv, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate
    global battlescene_path, battlescene_path_without_dialog, battlescene_file, battle_ui_path, battle_ui_path_without_dialog
    global pokemon_encounter, attack_counter, merged_pixmap, window
    attack_counter = 0
    pokemon_encounter += 1
    if pokemon_encounter == 1:
        bckgimage_path = battlescene_path / battlescene_file
    elif pokemon_encounter > 1:
        bckgimage_path = battlescene_path_without_dialog / battlescene_file
    # get main pokemon details:
    mainpokemon_name, mainpokemon_id, mainpokemon_ability, mainpokemon_type, mainpokemon_stats, mainpokemon_attacks, mainpokemon_level, mainpokemon_base_experience, mainpokemon_xp, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate, mainpokemon_ev, mainpokemon_iv, mainpokemon_evolutions, mainpokemon_battle_stats, mainpokemon_gender = mainpokemon_data()
    caught = 0
    # Capitalize the first letter of the Pokémon's name
    name = name.capitalize()
    #calculate wild pokemon max hp
    max_hp = calculate_hp(stats["hp"], level, ev, iv)

    # Create the dialog
    window = QDialog(mw)
    window.setWindowTitle(f"{name} appeared in the wild grass !")
    # Create a layout for the dialog
    layout = QVBoxLayout()
    message_box_text = (f"{name} appeared in the wild grass !")
    def window_show():
        ui_path = battle_ui_path

        pixmap_ui = QPixmap()
        pixmap_ui.load(str(ui_path))

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        # Display the Pokémon image
        pkmnimage_file = f"{id}.png"
        pkmnimage_path = frontdefault / pkmnimage_file
        image_label = QLabel()
        pixmap = QPixmap()
        pixmap.load(str(pkmnimage_path))

        # Display the Main Pokémon image
        pkmnimage_file2 = f"{mainpokemon_id}.png"
        pkmnimage_path2 = backdefault / pkmnimage_file2
        pixmap2 = QPixmap()
        pixmap2.load(str(pkmnimage_path2))

        # Calculate the new dimensions to maintain the aspect ratio
        max_width = 150
        original_width = pixmap.width()
        original_height = pixmap.height()
        new_width = max_width
        new_height = (original_height * max_width) // original_width
        pixmap = pixmap.scaled(new_width, new_height)

        # Calculate the new dimensions to maintain the aspect ratio
        max_width = 150
        original_width2 = pixmap2.width()
        original_height2 = pixmap2.height()

        new_width2 = max_width
        new_height2 = (original_height2 * max_width) // original_width2
        pixmap2 = pixmap2.scaled(new_width2, new_height2)

        # Merge the background image and the Pokémon image
        merged_pixmap = QPixmap(pixmap_bckg.size())
        merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)
        def draw_hp_bar(x, y, h, w, hp, max_hp):
            pokemon_hp_percent = (hp / max_hp) * 100
            hp_bar_value = (w * (hp / max_hp))
            # Draw the HP bar
            if pokemon_hp_percent < 25:
                hp_color = QColor(255, 0, 0)  # Red
            elif pokemon_hp_percent < 50:
                hp_color = QColor(255, 140, 0)  # Orange
            elif pokemon_hp_percent < 75:
                hp_color = QColor(255, 255, 0)  # Yellow
            else:
                hp_color = QColor(110, 218, 163)  # Green
            painter.setBrush(hp_color)
            painter.drawRect(x, y, hp_bar_value, h)
        draw_hp_bar(118,76,8, 116, hp, max_hp) #enemy pokemon hp_bar
        draw_hp_bar(401,208,8,116,mainpokemon_current_hp,mainpokemon_hp) #main pokemon hp_bar

        painter.drawPixmap(0, 0, pixmap_ui)
        #Find the Pokemon Images Height and Width
        wpkmn_width = (new_width / 2)
        wpkmn_height = new_height
        mpkmn_width = (new_width2 / 2)
        mpkmn_height = new_height2
        # draw pokemon image to a specific pixel
        painter.drawPixmap((410 - wpkmn_width), (170 - wpkmn_height), pixmap)
        painter.drawPixmap((144 - mpkmn_width), (290 - mpkmn_height), pixmap2)

        experience = find_experience_for_level(mainpokemon_growth_rate, mainpokemon_level)
        experience = int(experience)
        mainxp_bar_width = 5
        mainpokemon_xp_value = int((mainpokemon_xp / experience) * 148)
        #Paint XP Bar
        painter.setBrush(QColor(58,155,220))
        painter.drawRect(366, 246, mainpokemon_xp_value, mainxp_bar_width)

        #create level text
        lvl = (f"{level}")
        mainlvl = (f"{mainpokemon_level}")

        #custom font
        custom_font = load_custom_font(font_file, 28)
        msg_font = load_custom_font(font_file, 32)

        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(31,31,39))  # Text color
        painter.drawText(48, 67, name)
        painter.drawText(326, 200, mainpokemon_name)
        painter.drawText(208, 67, lvl)
        painter.drawText(490, 199, mainlvl)
        painter.drawText(487, 238, f"{mainpokemon_hp}")
        painter.drawText(442, 238, f"{mainpokemon_current_hp}")
        painter.setFont(msg_font)
        painter.setPen(QColor(240,240,208))  # Text color
        painter.drawText(40, 320, message_box_text)
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        image_label.setPixmap(merged_pixmap)
        return image_label, msg_font
    image_label, msg_font = window_show()
    layout.addWidget(image_label)
    if pokemon_encounter > 1:
        attack_label = QLabel("Choose a Move: ")
        attack_label.setFont(msg_font)
        def choose_move(mainpokemon_attacks, image_label, layout, attack_label):
            widget = QWidget()
            grid_layout = QGridLayout()
            button_width = 250  # Set your desired width
            button_height = 40  # Set your desired height
            row, col = 0, 0
            for attack in mainpokemon_attacks:
                attack = attack.capitalize()
                button = QPushButton(attack)
                button.clicked.connect(lambda checked, attack=attack, image_label=image_label, layout=layout, attack_label=attack_label : on_attack_button_clicked(attack, image_label, layout, attack_label))
                # Set fixed size for the button
                button.setFixedSize(button_width, button_height)
                grid_layout.addWidget(button, row, col)
                col += 1
                if col > 1:
                    col = 0
                    row += 1

            # Add the grid layout to the parent widget
            widget.setLayout(grid_layout)
            return widget
        pokemon_attacks_widget = choose_move(mainpokemon_attacks, image_label, layout, attack_label)
        pokemon_attacks_widget.setFont(msg_font)
        layout.addWidget(attack_label)
        layout.addWidget(pokemon_attacks_widget)

    def update_hp_bar(image_label, layout, attack_label):
        image_label2, msg_font = window_show()
        layout.replaceWidget(image_label, image_label2)
        def create_gif_widget():
            global attack_animation_path
            widget = QWidget()
            vbox = QVBoxLayout(widget)

            label = QLabel(widget)
            movie = QMovie(str(attack_animation_path))

            label.setMovie(movie)
            movie.start()
            vbox.addWidget(label)
            widget.setLayout(vbox)
            widget.setGeometry(100, 100, 400, 300)
            return widget

        gif_widget = create_gif_widget()
        gif_widget.move(-200,-400)
        layout.addWidget(gif_widget)
        # Use QTimer for a delay instead of time.sleep
        #delay_timer = QTimer()
        #delay_timer.singleShot(50, lambda: layout.replaceWidget(image_label3, image_label2))

    def calc_atk_dmg(level, critical, power, stat_atk, wild_stat_def, main_type, move_type, wild_type):
        if power is None:
            # You can choose a default power or handle it according to your requirements
            power = 0
        # damage = (((2 * level * critical)+2)/ 5) * power * stat_atk / wild_stat_def)+2)/ 50 * stab * random
        # if move_typ is the same as the main pkmn type => damage * 1.5; else damage * 1.0
        # STAB calculation
        stab = 1.5 if move_type == main_type else 1.0
        eff = get_effectiveness(move_type)
        # random luck
        random_number = random.randint(217, 255)
        random_factor = random_number / 255
        damage = (((((2 * level * critical) + 2) / 5) * power * stat_atk / wild_stat_def) + 2) / 50 * stab * eff * random_factor
        # if main pkmn type = move type => damage * 1,5
        # if wild pokemon type x main pokemon type => 0.5 not very eff.; 1.0 eff.; 2 very eff.
        return damage

    def find_details_move(move_name):
        global moves_file_path
        try:
            with open(moves_file_path, "r", encoding="utf-8") as json_file:
                moves_data = json.load(json_file)
                # Check if there are any captured Pokémon
                for move in moves_data:
                    if move["name"].lower() == move_name.lower():
                        return {
                            "id": move["id"],
                            "name": move["name"],
                            "accuracy": move["accuracy"],
                            "pp": move["pp"],
                            "power": move["power"],
                            "damage_class": move["damage_class"],
                            "type": move["type"]
                        }
        except FileNotFoundError:
            showInfo("Moves Data File Missing!\nPlease Download Moves Data")
            return None
        except json.JSONDecodeError as e:
            showInfo(f"Error decoding JSON: {e}")
            return None

    def on_attack_button_clicked(attack, image_label, layout, attack_label):
        global attack_counter, hp, max_hp, mainpokemon_current_hp, mainpokemon_hp
        if attack_counter == 0:
            attack_counter += 1
            move_info = find_details_move(attack)
            if move_info["accuracy"] is None:
                # You can choose a default power or handle it according to your requirements
                move_info["accuracy"] = 100
            global mainpokemon_level, mainpokemon_type, mainpokemon_stats, stats, hp, name, type
            critical = 1
            damage = int(calc_atk_dmg(mainpokemon_level, critical, move_info["power"], mainpokemon_stats["attack"],
                                      stats["defense"], mainpokemon_type, move_info["type"], type))
            hp -= damage
            if hp < 0:
                hp = 0
            update_hp_bar(image_label, layout, attack_label)
            showInfo(f"{attack} was clicked ! \n Wild {name.capitalize()} receives {damage} Damage!")
        else:
            showInfo("A move was already chosen !")

    # Set the layout for the dialog
    window.setLayout(layout)

    # Show the dialog
    #window.exec_()

    window.show()

def get_effectiveness(move_type):
    global mainpokemon_type, effectiveness_chart_file_path, type
    move_type = move_type.capitalize()
    #showInfo(f"{move_type}")
    attacking_types = []
    attacking_types.append(move_type)
    defending_types = type
    attacking_types = [attacking_type.capitalize() for attacking_type in attacking_types]
    defending_types = [defending_type.capitalize() for defending_type in defending_types]
    with open(effectiveness_chart_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        # Find the effectiveness values for each attacking type
        effectiveness_values = []
        for attacking_type in attacking_types:
            if attacking_type in data:
                # Find the effectiveness values for each defending type
                eff_values = [data[attacking_type][defending_type] for defending_type in defending_types]
                effectiveness_values.extend(eff_values)  # Use extend to add values to the list
        if effectiveness_values:
            if len(effectiveness_values) > 1:
                # Multiply all values in the list
                eff_value = 1
                for value in effectiveness_values:
                    eff_value *= value
                effective_txt = effectiveness_text(eff_value)
                #showInfo(f"Attack {effective_txt} \n Effectiveness is {int(eff_value)}x")
                return eff_value
            else:
                effective_txt = effectiveness_text(effectiveness_values[0])
                #showInfo(f"Effectiveness is {int(effectiveness_values[0])}x \nAttack {effective_txt}")
                return effectiveness_values[0]
    # If the combination is not found, return None or a default value
    return None

def effectiveness_text(effect_value):
    if effect_value == 0:
        effective_txt = "has missed."
    elif effect_value <= 0.5:
        effective_txt = "was not very effective."
    elif effect_value <= 1:
        effective_txt = "was effective."
    elif effect_value <= 1.5:
        effective_txt = "was very effective !"
    elif effect_value <= 2:
        effective_txt = "was super effective !"
    else:
        showInfo(f"{effect_value}")
        return None
    return effective_txt

def calc_multiply_card_rating():
    global card_ratings_count
    max_points = cards_per_round * 10
    multiply_sum = 0
    multiply_sum += (card_ratings_count['Easy'] * 20)
    multiply_sum += (card_ratings_count['Hard'] * 5)
    multiply_sum += (card_ratings_count['Good'] * 10)
    multiply_sum += (card_ratings_count['Again'] * 0)
    card_ratings_count = {"Again": 0, "Hard": 0, "Good": 0, "Easy": 0}
    multiplier = multiply_sum / max_points
    return multiplier

reviewed_cards_count = 0
# Hook into Anki's card review event
def on_review_card():
    global reviewed_cards_count, card_ratings_count, card_counter
    global hp, stats, type, battle_status, name, battle_stats
    global pokemon_encounter
    global mainpokemon_xp, mainpokemon_current_hp, mainpokemon_attacks, mainpokemon_level, mainpokemon_stats, mainpokemon_type, mainpokemon_name, mainpokemon_battle_stats
    global attack_counter
    global pkmn_window
    # Increment the counter when a card is reviewed
    reviewed_cards_count += 1
    card_counter += 1
    if reviewed_cards_count >= cards_per_round:
        reviewed_cards_count = 0
        attack_counter = 0
        slp_counter = 0
        pokemon_encounter += 1
        multiplier = calc_multiply_card_rating()
        #showInfo(f"{multiplier}x has been calc")
        msg = ""
        msg += f"{multiplier}x Multiplier - "
        # If 10 or more cards have been reviewed, show the random Pokémon
        if pokemon_encounter > 0 and hp > 0:
            random_attack = random.choice(mainpokemon_attacks)
            msg += f"\n {random_attack.capitalize()} has been choosen !"
            move = find_details_move(random_attack)
            category = move.get("category")
            acc = move.get("accuracy")
            if battle_status != "fighting":
                msg, acc, battle_status, stats = status_effect(battle_status, name, move, hp, slp_counter, battle_stats, msg, acc)
            if acc is True:
                acc = 100
            if acc != 0:
                calc_acc = 100 / acc
            else:
                calc_acc = 0
            if battle_status == "slp":
                calc_acc = 0
                msg += f"{name.capitalize()} is deep asleep."
                #slp_counter -= 1
            elif battle_status == "par":
                msg += f"\n {name.capitalize()} is paralyzed."
                missing_chance = 1 / 4
                random_number = random.random()
                if random_number < missing_chance:
                   acc = 0
            if random.random() > calc_acc:
                #showInfo("Move has missed !")
                msg += "\n Move has missed !"
            else:
                if category == "Status":
                    color = "#F7DC6F"
                    msg = effect_status_moves(random_attack, mainpokemon_stats, stats, msg, name, mainpokemon_name)
                elif category == "Physical" or category == "Special":
                    critRatio = move.get("critRatio", 1)
                    if category == "Physical":
                        color = "#F0B27A"
                    elif category == "Special":
                        color = "#D2B4DE"
                    #showInfo(f"{random_attack} has been choosen")
                    if move["basePower"] == 0:
                        dmg = bP_none_moves(move)
                        hp -= dmg
                        if dmg == 0:
                            #showInfo("Move was useless !")
                            msg += "\n Move has missed !"
                            #dmg = 1
                    else:
                        if category == "Special":
                            def_stat = stats["spd"]
                            atk_stat = mainpokemon_stats["spa"]
                        elif category == "Physical":
                            def_stat = stats["def"]
                            atk_stat = mainpokemon_stats["atk"]
                        dmg = int(calc_atk_dmg(mainpokemon_level, multiplier,move["basePower"], atk_stat, def_stat, mainpokemon_type, move["type"],type, critRatio))
                        if dmg == 0:
                            dmg = 1
                        hp -= dmg
                        msg += f" {dmg} dmg is dealt to {name.capitalize()}."
                        move_stat = move.get("status", None)
                        secondary = move.get("secondary", None)
                        if secondary is not None:
                            bat_status = move.get("secondary", None).get("status", None)
                            if bat_status is not None:
                                move_with_status(move, move_stat, secondary)
                        if move_stat is not None:
                            move_with_status(move, move_stat, secondary)
                        if dmg == 0:
                            #showInfo("Move was useless !")
                            msg += " \n Move has missed !"
                    if hp < 0:
                        hp = 0
                        msg += f" {name.capitalize()} has fainted"
                tooltipWithColour(msg, color)
        else:
            if pkmn_window is True:
                test_window.display_pokemon_death()
            elif pkmn_window is False:
                new_pokemon()
        if pkmn_window is True:
            if hp > 0:
                test_window.display_first_encounter()
            elif hp < 1:
                hp = 0
                test_window.display_pokemon_death()
        elif pkmn_window is False:
            if hp < 1:
                hp = 0
                kill_pokemon()
        # Reset the counter
        reviewed_cards_count = 0


def create_status_label(status_name):
    #to create status symbols
    # Define the background and outline colors for each status
    status_colors = {
        "burned": {"background": "#FF4500", "outline": "#C13500"},
        "frozen": {"background": "#ADD8E6", "outline": "#91B0C0"},
        "paralysis": {"background": "#FFFF00", "outline": "#CCCC00"},
        "poisoned": {"background": "#A020F0", "outline": "#8000C0"},
        "asleep": {"background": "#FFC0CB", "outline": "#D895A1"},
        "confusion": {"background": "#FFA500", "outline": "#CC8400"},
        "flinching": {"background": "#808080", "outline": "#666666"},
        "fainted": {"background": "#000000", "outline": "#000000", "text_color": "#FFFFFF"},
    }

    # Get the colors for the given status name
    colors = status_colors.get(status_name.lower())

    # If the status name is valid, create and style the QLabel
    if colors:
        label = QLabel(status_name.capitalize())
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            f"background-color: {colors['background']};"
            f"border: 2px solid {colors['outline']};"
            f"border-radius: 5px;"
            f"padding: 5px 10px;"
            f"font-weight: bold;"
            f"color: {colors.get('text_color', '#000000')};"
        )
    else:
        label = QLabel("Unknown Status")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            "padding: 5px 10px;"
        )

    return label
def create_status_html(status_name):

    status_colors = {
        "brn": {"background": "#FF4500", "outline": "#C13500", "name": "Burned"},
        "frz": {"background": "#ADD8E6", "outline": "#91B0C0", "name": "Frozen"},
        "par": {"background": "#FFFF00", "outline": "#CCCC00", "name": "Paralysis"},
        "psn": {"background": "#A020F0", "outline": "#8000C0", "name": "Poisoned"},
        "tox": {"background": "#A545FF", "outline": "#842BFF", "name": "Badly Poisoned"},
        "slp": {"background": "#FFC0CB", "outline": "#D895A1", "name": "Asleep"},
        "confusion": {"background": "#FFA500", "outline": "#CC8400", "name": "Confusion"},
        "flinching": {"background": "#808080", "outline": "#666666", "name": "Flinching"},
        "fainted": {"background": "#000000", "outline": "#000000", "text_color": "#FFFFFF", "name": "Fainted"},
        "fighting": {"background": "#C03028", "outline": "#7D1F1A", "name": "Fighting"},  # Example colors for Fighting
    }

    # Get the colors for the given status name
    colors = status_colors.get(status_name.lower())

    # If the status name is valid, create the HTML with inline CSS
    if colors:
        html = f"""
        <div id=pokestatus style="
            position: fixed;
            bottom: 57px; /* Adjust as needed */
            left: 17px;
            z-index: 9999;
            background-color: {colors['background']};
            border: 2px solid {colors['outline']};
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 8px;
            font-weight: bold;
            display: inline-block;
            color: {colors.get('text_color', '#000000')};
            text-transform: uppercase;
            text-align: center;
            margin: 4px;
        ">{colors['name']}</div>
        """
    else:
        html = "<div>Unknown Status</div>"

    return html

def get_multiplier_stats(stage):
    # Define the mapping of stage to factor
    stage_to_factor = {
        -6: 3/9, -5: 3/8, -4: 3/7, -3: 3/6, -2: 3/5, -1: 3/4,
        0: 3/3,
        1: 4/3, 2: 5/3, 3: 6/3, 4: 7/3, 5: 8/3, 6: 9/3
    }

    # Return the corresponding factor or a default value if the stage is out of range
    return stage_to_factor.get(stage, "Invalid stage")

def get_multiplier_acc_eva(stage):
    # Define the mapping of stage to factor
    stage_to_factor_new = {
        -6: 2/8, -5: 2/7, -4: 2/6, -3: 2/5, -2: 2/4, -1: 2/3,
        0: 2/2,
        1: 3/2, 2: 4/2, 3: 5/2, 4: 6/2, 5: 7/2, 6: 8/2
    }

    # Return the corresponding factor or a default value if the stage is out of range
    return stage_to_factor_new.get(stage, "Invalid stage")

def bP_none_moves(move):
    target =  move.get("target", None)
    if target == "normal":
        damage = move.get("damage")
        return damage

def effect_status_moves(move_name, mainpokemon_stats, stats, msg, name, mainpokemon_name):
    global battle_status
    move = find_details_move(move_name)
    target = move.get("target")
    boosts = move.get("boosts", {})
    stat_boost_value = {
        "hp": boosts.get("hp", 0),
        "atk": boosts.get("atk", 0),
        "def": boosts.get("def", 0),
        "spa": boosts.get("spa", 0),
        "spd": boosts.get("spd", 0),
        "spe": boosts.get("spe", 0),
        "xp": mainpokemon_stats.get("xp", 0)
    }
    #showInfo(f"{stat_boost_value}")
    move_stat = move.get("status",None)
    status = move.get("secondary",None)
    if move_stat is not None:
        battle_status = move_stat
    if status is not None:
        random_number = random.random()
        chances = status["chance"] / 100
        if random_number < chances:
            battle_status = status["status"]
    if battle_status == "slp":
        slp_counter = random.randint(1, 3)
    #showInfo(f"{battle_status}")
    if target == "self":
        for boost, stage in boosts.items():
            stat = get_multiplier_stats(stage)
            #showInfo(f"{stat}")
            mainpokemon_stats[boost] = mainpokemon_stats.get(boost, 0) * stat
            msg += f" {mainpokemon_name.capitalize()}'s "
            if stage < 0:
                msg += f"{boost.capitalize()} is decreased."
            elif stage > 0:
                msg += f"{boost.capitalize()} is increased."
            #showInfo(f"{mainpokemon_stats[boost]}")
    elif target in ["normal", "allAdjacentFoes"]:
        for boost, stage in boosts.items():
            stat = get_multiplier_stats(stage)
            #showInfo(f"{stat}")
            stats[boost] = stats.get(boost, 0) * stat
            msg += f" {name.capitalize()}'s "
            if stage < 0:
                msg += f"{boost.capitalize()} is decreased."
            elif stage > 0:
                msg += f"{boost.capitalize()} is increased."
            #showInfo(f"{stats[boost]}")
    return msg

def move_with_status(move, move_stat, status):
    global battle_status
    target = move.get("target")
    bat_status = move.get("secondary", None).get("status", None)
    #showInfo(f"{battle_status}")
    if target in ["normal", "allAdjacentFoes"]:
        if move_stat is not None:
            battle_status = move_stat
        if status is not None:
            random_number = random.random()
            chances = status["chance"] / 100
            if random_number < chances:
                battle_status = status["status"]
    if battle_status == "slp":
        slp_counter = random.randint(1, 3)

def status_effect(stat, name, move, hp, slp_counter, stats, msg, acc):
    # Extend the existing dictionary with the "Fighting" status
    if stat == "par":
        stats["spe"] = stats["spe"] * 0.5
        msg += f" {name.capitalize()}'s speed is reduced."
        missing_chance = 1/4
        random_number = random.random()
        if random_number < missing_chance:
            msg += (f"{name} is paralyzed! It can't move!")
            acc = 0
    elif stat == "brn":
        dmg = 1/16 * calculate_max_hp_wildpokemon()
        hp -= dmg
        msg += (f"Wild {name} was hurt by burning!")
    elif stat == "psn":
        max_hp = calculate_max_hp_wildpokemon()
        dmg = 1 / 8 * max_hp
        hp -= dmg
        msg += (f"The wild {name} was hurt by its poisoning!")
    elif stat == "tox":
        max_hp = calculate_max_hp_wildpokemon()
        dmg = ((random.randint(1,3)) / 16 * max_hp)
        hp -= dmg
        msg += (f"The wild {name} is badly poisoned and was hurt by is poisoning!")
        stat = "psn"
    elif stat == "frz":
        free_chance = 20 / 100
        if move["type"] == "fire" and move["target"] != "self":
            free_chance = 1
        random_number = random.random()
        if random_number < free_chance:
            msg += (f"Wild {name} is frozen solid!")
            acc = 0
        else:
            stat = None
            msg += (f"Wild {name} is no longer frozen!")
    elif stat == "slp":
            if slp_counter > 1:
                slp_counter -= 1
                msg += (f"Wild {name} is asleep!")
            else:
                stat = None
                msg += (f"Wild {name} is no longer asleep!")
    return msg, acc, stat, battle_stats

# Connect the hook to Anki's review event
addHook("showQuestion", on_review_card)

def ShowPokemonCollection():
    # Create the dialog
    window = QDialog(mw)
    #window = QMessageBox(mw)
    window.setWindowTitle(f"Captured Pokemon")

    # Create a QScrollArea to enable scrolling
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    # Create a layout for the scroll area using QGridLayout
    scroll_layout = QGridLayout()

    # Create a widget to hold the layout
    container = QWidget()

    # Set the widget for the scroll area
    scroll_area.setWidget(container)

    #Set Window Width
    window.setMinimumWidth(750)
    window.setMinimumHeight(400)

    global mypokemon_path
    global pkmnimgfolder
    global frontdefault
    try:
        with (open(mypokemon_path, "r") as json_file):
            captured_pokemon_data = json.load(json_file)
            # Check if there are any captured Pokémon
            if captured_pokemon_data:
                # Counter for tracking the column position
                column = 0
                row = 0
                for pokemon in captured_pokemon_data:
                    pokemon_container = QWidget()
                    image_label = QLabel()
                    pixmap = QPixmap()
                    pokemon_name = pokemon['name']
                    try:
                        pokemon_nickname = pokemon['nickname']
                    except:
                        pokemon_nickname = None
                    pokemon_gender = pokemon['gender']
                    pokemon_level = pokemon['level']
                    pokemon_id = pokemon['id']
                    pokemon_ability = pokemon['ability']
                    pokemon_type = pokemon['type']
                    pokemon_stats = pokemon['stats']
                    pokemon_hp = pokemon_stats["hp"],
                    pokemon_attacks = pokemon['attacks']
                    pokemon_base_experience = pokemon['base_experience']
                    pokemon_growth_rate = pokemon['growth_rate']
                    pokemon_ev = pokemon['ev']
                    pokemon_iv = pokemon['iv']
                    pokemon_description = search_pokeapi_db(f"{pokemon_name.lower()}", "description")
                    pokemon_imagefile = f"{pokemon_id}.png"
                    pixmap.load(str(frontdefault / pokemon_imagefile))

                    # Calculate the new dimensions to maintain the aspect ratio
                    max_width = 300
                    max_height = 230
                    original_width = pixmap.width()
                    original_height = pixmap.height()

                    if original_width > max_width:
                        new_width = max_width
                        new_height = (original_height * max_width) // original_width
                        pixmap = pixmap.scaled(new_width, new_height)

                    # Create a painter to add text on top of the image
                    painter = QPainter(pixmap)

                    # Capitalize the first letter of the Pokémon's name
                    if pokemon_nickname is None:
                        capitalized_name = f"{pokemon_name.capitalize()} ({pokemon_gender})"
                    else:
                        capitalized_name = f"{pokemon_nickname.capitalize()} ({pokemon_gender})"
                    # Create level text
                    lvl = (f" Level: {pokemon_level}")
                    type_txt = "Type: "
                    for type in pokemon_type:
                        type_txt += f"{type.capitalize()}"
                    #if len(pokemon_type) > 1:
                        #type_txt = (f" Type: {(pokemon_type[0].capitalize())} and {(pokemon_type[1].capitalize())}")
                    #else:
                        #type_txt = (f" Type: {(pokemon_type[0].capitalize())}")
                    ability_txt = (f" Ability: {pokemon_ability.capitalize()}")
                    # Draw the text on top of the image
                    font = QFont()
                    font.setPointSize(12)  # Adjust the font size as needed
                    painter.setFont(font)
                    fontpkmnspec = QFont()
                    fontpkmnspec.setPointSize(8)
                    painter.end()

                    # Create a QLabel for the capitalized name
                    name_label = QLabel(capitalized_name)
                    name_label.setAlignment(Qt.AlignLeft)  # Align to the left
                    name_label.setFont(font)

                    # Create a QLabel for the level
                    level_label = QLabel(lvl)
                    level_label.setAlignment(Qt.AlignLeft)  # Align to the left
                    level_label.setFont(fontpkmnspec)

                    # Create a QLabel for the type
                    type_label = QLabel(type_txt)
                    type_label.setAlignment(Qt.AlignLeft)  # Align to the left
                    type_label.setFont(fontpkmnspec)

                    # Create a QLabel for the ability
                    ability_label = QLabel(ability_txt)
                    ability_label.setAlignment(Qt.AlignLeft)  # Align to the left
                    ability_label.setFont(fontpkmnspec)

                    # Set the merged image as the pixmap for the QLabel
                    image_label.setPixmap(pixmap)

                    # Create a QPushButton for the Pokémon
                    pokemon_button = QPushButton("Show me Details")
                    pokemon_button.setIconSize(pixmap.size())
                    if len(pokemon_type) > 1:
                        pokemon_button.clicked.connect(lambda state, name = pokemon_name, level = pokemon_level, id = pokemon_id, ability=pokemon_ability, type=[pokemon_type[0], pokemon_type[1]], detail_stats=pokemon_stats, attacks = pokemon_attacks, base_experience=pokemon_base_experience, growth_rate = pokemon_growth_rate, description = pokemon_description, gender = pokemon_gender, nickname = pokemon_nickname: PokemonCollectionDetails(name, level, id, ability, type, detail_stats, attacks, base_experience, growth_rate, description, gender, nickname))
                    else:
                        pokemon_button.clicked.connect(lambda state, name = pokemon_name, level = pokemon_level, id = pokemon_id, ability=pokemon_ability, type=[pokemon_type[0]], detail_stats=pokemon_stats, attacks = pokemon_attacks, base_experience=pokemon_base_experience, growth_rate = pokemon_growth_rate, description = pokemon_description, gender = pokemon_gender, nickname = pokemon_nickname: PokemonCollectionDetails(name, level, id, ability, type, detail_stats, attacks, base_experience, growth_rate, description, gender, nickname))

                    # Create a QPushButton for the Pokémon
                    choose_pokemon_button = QPushButton("Pick as main Pokemon")
                    choose_pokemon_button.setIconSize(pixmap.size())
                    choose_pokemon_button.clicked.connect(lambda state, name=pokemon_name, level=pokemon_level, id=pokemon_id, ability=pokemon_ability, type=pokemon_type, detail_stats=pokemon_stats, attacks=pokemon_attacks, hp = pokemon_hp , base_experience = mainpokemon_base_experience, growth_rate = pokemon_growth_rate, ev = pokemon_ev, iv = pokemon_iv, gender = pokemon_gender: MainPokemon(name, level, id, ability, type, detail_stats, attacks, hp, base_experience, growth_rate, ev, iv, gender))

                    # Create a QVBoxLayout for the container
                    container_layout = QVBoxLayout()
                    container_layout.addWidget(image_label)
                    container_layout.addWidget(name_label)
                    container_layout.addWidget(level_label)
                    container_layout.addWidget(type_label)
                    container_layout.addWidget(ability_label)
                    container_layout.addWidget(pokemon_button)
                    container_layout.addWidget(choose_pokemon_button)
                    image_label.setAlignment(Qt.AlignCenter)
                    type_label.setAlignment(Qt.AlignCenter)
                    name_label.setAlignment(Qt.AlignCenter)
                    level_label.setAlignment(Qt.AlignCenter)
                    ability_label.setAlignment(Qt.AlignCenter)

                    # Set the QVBoxLayout as the layout for the container
                    pokemon_container.setLayout(container_layout)

                    # Add the container to the layout at the current column and row position
                    scroll_layout.addWidget(pokemon_container, row, column)

                    # Increment the column counter
                    column += 1
                    MAX_ITEMS_PER_ROW = 3
                    if column >= MAX_ITEMS_PER_ROW:
                        column = 0
                        row += 1

                    # If the column exceeds the screen width, move to the next row
                    #if column * (max_width + 20) > window.width():
                        #column = 0
                        #row += 1

                     # test new code - if +3 pokemon per column =>
                    #if column > 3:
                        #column = 0
                        #row += 1

                # Set the layout for the container
                container.setLayout(scroll_layout)

                # Set the widget for the scroll area
                scroll_area.setWidget(container)

                # Add the scroll area to the dialog
                window_layout = QVBoxLayout()
                window_layout.addWidget(scroll_area)
                window.setLayout(window_layout)
                # Show the dialog
                window.exec_()
                #window.show()
            else:
                showInfo("You haven't captured any Pokémon yet.")
    except FileNotFoundError:
        showInfo(f"Can't open the Saving File. {mypokemon_path}")

def rename_pkmn(nickname, pkmn_name):
    try:
        with open(mypokemon_path, "r") as json_file:
            captured_pokemon_data = json.load(json_file)
            pokemon = None
            if captured_pokemon_data:
                for pokemon_data in captured_pokemon_data:
                    if pokemon_data['name'] == pkmn_name:
                        pokemon = pokemon_data
                        if pokemon is not None:
                            pokemon["nickname"] = nickname
                            # Load data from the output JSON file
                            with open(str(mypokemon_path), "r") as output_file:
                                mypokemondata = json.load(output_file)
                                # Find and replace the specified Pokémon's data in mypokemondata
                                for index, pokemon_data in enumerate(mypokemondata):
                                    if pokemon_data["name"] == pkmn_name:
                                        mypokemondata[index] = pokemon
                                        break
                                        # Save the modified data to the output JSON file
                                with open(str(mypokemon_path), "w") as output_file:
                                    json.dump(mypokemondata, output_file, indent=2)
                                showInfo(f"Your {pkmn_name.capitalize()} has been renamed to {nickname}!")
    except Exception as e:
        showWarning(f"An error occured: {e}")

def PokemonCollectionDetails(name, level, id, ability, type, detail_stats, attacks, base_experience, growth_rate, description, gender, nickname):
    global frontdefault, type_style_file
    # Create the dialog
    wpkmn_details = QDialog(mw)
    if nickname is None:
        wpkmn_details.setWindowTitle(f"Infos to : {name} ")
    else:
        wpkmn_details.setWindowTitle(f"Infos to : {nickname} ({name}) ")

    wpkmn_details.setFixedWidth(500)
    wpkmn_details.setMaximumHeight(400)

    # Create a layout for the dialog
    layout = QVBoxLayout()
    typelayout = QHBoxLayout()
    attackslayout = QVBoxLayout()
    # Display the Pokémon image
    pkmnimage_file = f"{search_pokedex(name.lower(), 'num')}.png"
    pkmnimage_path = frontdefault / pkmnimage_file
    typeimage_file = f"{type[0]}.png"
    typeimage_path = addon_dir / pkmnimgfolder / "Types" / typeimage_file
    pkmnimage_label = QLabel()
    pkmnpixmap = QPixmap()
    pkmnpixmap.load(str(pkmnimage_path))
    pkmntype_label = QLabel()
    pkmntypepixmap = QPixmap()
    pkmntypepixmap.load(str(typeimage_path))
    if len(type) > 1:
        type_image_file2 = f"{type[1]}.png"
        typeimage_path2 = addon_dir / pkmnimgfolder / "Types" / type_image_file2
        pkmntype_label2 = QLabel()
        pkmntypepixmap2 = QPixmap()
        pkmntypepixmap2.load(str(typeimage_path2))
    # Calculate the new dimensions to maintain the aspect ratio
    max_width = 150
    original_width = pkmnpixmap.width()
    original_height = pkmnpixmap.height()
    new_width = max_width
    new_height = (original_height * max_width) // original_width
    pkmnpixmap = pkmnpixmap.scaled(new_width, new_height)

    # Create a painter to add text on top of the image
    painter2 = QPainter(pkmnpixmap)

    #custom font
    custom_font = load_custom_font(font_file, 20)

    # Capitalize the first letter of the Pokémon's name
    if nickname is None:
        capitalized_name = f"{name.capitalize()}"
    else:
        capitalized_name = f"{nickname} ({name.capitalize()})"
    # Create level text
    result = list(split_string_by_length(description, 65))
    description_formated = '\n'.join(result)
    description_txt = f"Description: \n {description_formated}"
    #curr_hp_txt = (f"Current Hp:{current_hp}")
    growth_rate_txt = (f"Growth Rate: {growth_rate.capitalize()}")
    lvl = (f" Level: {level}")
    ability_txt = (f" Ability: {ability.capitalize()}")
    type_txt = (f" Type:")
    stats_list = [
        detail_stats["hp"],
        detail_stats["atk"],
        detail_stats["def"],
        detail_stats["spa"],
        detail_stats["spd"],
        detail_stats["spe"],
        detail_stats["xp"]
    ]
    stats_txt = f"Stats:\n\
        Hp: {stats_list[0]}\n\
        Attack: {stats_list[1]}\n\
        Defense: {stats_list[2]}\n\
        Special-attack: {stats_list[3]}\n\
        Special-defense: {stats_list[4]}\n\
        Speed: {stats_list[5]}\n\
        XP: {stats_list[6]}"
    attacks_txt = "Moves:"
    for attack in attacks:
        attacks_txt += f"\n{attack.capitalize()}"

    CompleteTable_layout = PokemonDetailsStats(detail_stats, growth_rate, level)

    # Properties of the text of the image
    # custom font
    namefont = load_custom_font(font_file, 30)
    namefont.setUnderline(True)
    painter2.setFont(namefont)
    font = load_custom_font(font_file, 20)
    painter2.end()

    # Create a QLabel for the capitalized name
    name_label = QLabel(f"{capitalized_name} ({gender})")
    name_label.setFont(namefont)
    # Create a QLabel for the level
    description_label = QLabel(description_txt)
    level_label = QLabel(lvl)
    growth_rate_label = QLabel(growth_rate_txt)
    base_exp_label = QLabel(f"Base XP: {base_experience}")
    # Align to the center
    level_label.setFont(font)
    base_exp_label.setFont(font)
    type_label= QLabel("Type:")
    type_label.setFont(font)
    # Create a QLabel for the level
    ability_label = QLabel(ability_txt)
    ability_label.setFont(font)
    attacks_label = QLabel(attacks_txt)
    attacks_label.setFont(font)
    growth_rate_label.setFont(font)
    description_font = load_custom_font(font_file, 15)
    description_label.setFont(description_font)
    #stats_label = QLabel(stats_txt)

    # Set the merged image as the pixmap for the QLabel
    pkmnimage_label.setPixmap(pkmnpixmap)
    # Set the merged image as the pixmap for the QLabel
    pkmntype_label.setPixmap(pkmntypepixmap)
    if len(type) > 1:
        pkmntype_label2.setPixmap(pkmntypepixmap2)
    #Border
    #description_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
    level_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
    base_exp_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
    ability_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
    growth_rate_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
    type_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
    level_label.setFixedWidth(230)
    growth_rate_label.setFixedWidth(230)
    base_exp_label.setFixedWidth(230)
    pkmnimage_label.setFixedHeight(100)
    ability_label.setFixedWidth(230)
    attacks_label.setFixedWidth(230)
    first_layout = QHBoxLayout() #Top Image Left and Direkt Info Right
    TopR_layout_Box = QVBoxLayout() #Top Right Info Direkt Layout
    TopL_layout_Box = QVBoxLayout() #Top Left Pokemon and Direkt Info Layout
    typelayout_widget = QWidget()
    TopL_layout_Box.addWidget(level_label)
    TopL_layout_Box.addWidget(pkmnimage_label)

    TopFirstLayout = QWidget()
    TopFirstLayout.setLayout(first_layout)
    layout.addWidget(name_label)
    layout.addWidget(TopFirstLayout)
    layout.addWidget(description_label)
    #.addWidget(growth_rate_label)
    #.addWidget(base_exp_label)
    typelayout.addWidget(type_label)
    typelayout.addWidget(pkmntype_label)
    pkmntype_label.setAlignment(Qt.AlignCenter)
    pkmntype_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
    if len(type) > 1:
        typelayout.addWidget(pkmntype_label2)
        pkmntype_label2.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        pkmntype_label2.setAlignment(Qt.AlignLeft)
        pkmntype_label2.setAlignment(Qt.AlignBottom)
    typelayout_widget.setLayout(typelayout)
    typelayout_widget.setStyleSheet("border: 0px solid #000000; padding: 0px;")
    typelayout_widget.setFixedWidth(230)
    TopL_layout_Box.addWidget(typelayout_widget)
    TopL_layout_Box.addWidget(ability_label)
    #attackslayout.addWidget(attacks_label)
    attacks_details_button = QPushButton("Attack Details") #add Details to Moves
    qconnect(attacks_details_button.clicked, lambda: attack_details_window(attacks))
    free_pokemon_button = QPushButton("Free Pokemon") #add Details to Moves
    attacks_label.setFixedHeight(150)
    TopR_layout_Box.addWidget(attacks_label)
    TopR_layout_Box.addWidget(attacks_details_button)
    first_layout.addLayout(TopL_layout_Box)
    first_layout.addLayout(TopR_layout_Box)
    layout.addLayout(first_layout)
    attacks_label.setStyleSheet("border: 2px solid white; padding: 5px;")
    #TopR_layout_Box.setStyleSheet("border: 2px solid white; padding: 5px;")
    statstablelayout = QWidget()
    statstablelayout.setLayout(CompleteTable_layout)
    layout.addWidget(statstablelayout)
    statstablelayout.setStyleSheet("border: 2px solid white; padding: 5px;")
    #statstablelayout.setFixedWidth(350)
    statstablelayout.setFixedHeight(200)
    free_pokemon_button = QPushButton("Free Pokemon") #add Details to Moves
    qconnect(free_pokemon_button.clicked, lambda: PokemonFree(name))
    trade_pokemon_button = QPushButton("Trade Pokemon") #add Details to Moves
    qconnect(trade_pokemon_button.clicked, lambda: PokemonTrade(name, id, level, ability, iv, ev, gender, attacks))
    layout.addWidget(trade_pokemon_button)
    layout.addWidget(free_pokemon_button)
    rename_button = QPushButton("Rename Pokemon") #add Details to Moves
    rename_input = QLineEdit()
    rename_input.setPlaceholderText("Enter a new Nickname for your Pokemon")
    qconnect(rename_button.clicked, lambda: rename_pkmn(rename_input.text(),name))
    layout.addWidget(rename_input)
    layout.addWidget(rename_button)
    #qconnect()
    #layout.addLayout(CompleteTable_layout)

    #wpkmn_details.setFixedWidth(500)
    #wpkmn_details.setMaximumHeight(600)

    # align things needed to middle
    pkmnimage_label.setAlignment(Qt.AlignCenter)
    level_label.setAlignment(Qt.AlignCenter)
    growth_rate_label.setAlignment(Qt.AlignCenter)
    base_exp_label.setAlignment(Qt.AlignBottom)
    base_exp_label.setAlignment(Qt.AlignCenter)
    pkmntype_label.setAlignment(Qt.AlignLeft)
    pkmntype_label.setAlignment(Qt.AlignBottom)
    type_label.setAlignment(Qt.AlignCenter)
    type_label.setAlignment(Qt.AlignRight)
    name_label.setAlignment(Qt.AlignCenter)  # Align to the center
    ability_label.setAlignment(Qt.AlignCenter)
    attacks_label.setAlignment(Qt.AlignCenter)
    description_label.setAlignment(Qt.AlignCenter)

    # Set the layout for the dialog
    wpkmn_details.setLayout(layout)

    # Show the dialog
    wpkmn_details.exec_()

def attack_details_window(attacks):
    window = QDialog()
    layout = QVBoxLayout()
    # HTML content
    html_content = """
    <style>
      .pokemon-table {
        width: 100%;
        border-collapse: collapse;
        text-align: left;
        margin-bottom: 20px;
      }

      .pokemon-table th, .pokemon-table td {
        padding: 8px;
        border: 1px solid #ddd; /* light grey border */
      }

      .pokemon-table th {
        background-color: #040D12;
      }

      .pokemon-table tr:nth-child(even) {background-color: #f9f9f9;}

      .pokemon-table .move-name {
        text-align: center;
        font-weight: bold;
      }

      .pokemon-table .basePower {
        font-weight: bold;
        text-align: center;
      }

      .pokemon-table .no-accuracy {
        text-align: center;
        color: yellow;
      }
    </style>
    </head>
    <body>

    <table class="pokemon-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Category</th>
          <th>Power</th>
          <th>Accuracy</th>
          <th>PP</th>
          <th>Description</th>
        </tr>
      </thead>
      <tbody>
    """
    # Loop through the list of attacks and add them to the HTML content
    for attack in attacks:
        move = find_details_move(attack)

        html_content += f"""
        <tr>
          <td class="move-name">{move['name']}</td>
          <td><img src="{type_icon_path(move['type'])}" alt="{move['type']}"/></td>
          <td><img src="{move_category_path(move['category'].lower())}" alt="{move['category']}"/></td>
          <td class="basePower">{move['basePower']}</td>
          <td class="no-accuracy">{move['accuracy']}</td>
          <td>{move['pp']}</td>
          <td>{move['shortDesc']}</td>
        </tr>
        """
    html_content += """
      </tbody>
    </table>

    </body>
    </html>
    """

    # Create a QLabel to display the HTML content
    label = QLabel(html_content)
    label.setAlignment(Qt.AlignTop)  # Align the label's content to the top
    label.setScaledContents(True)  # Enable scaling of the pixmap

    layout.addWidget(label)
    window.setLayout(layout)
    window.exec_()

def type_colors(type):
    type_colors = {
        "Normal": "#A8A77A",
        "Fire": "#EE8130",
        "Water": "#6390F0",
        "Electric": "#F7D02C",
        "Grass": "#7AC74C",
        "Ice": "#96D9D6",
        "Fighting": "#C22E28",
        "Poison": "#A33EA1",
        "Ground": "#E2BF65",
        "Flying": "#A98FF3",
        "Psychic": "#F95587",
        "Bug": "#A6B91A",
        "Rock": "#B6A136",
        "Ghost": "#735797",
        "Dragon": "#6F35FC",
        "Dark": "#705746",
        "Steel": "#B7B7CE",
        "Fairy": "#D685AD"
    }

    return type_colors.get(type, "Unknown")
def type_icon_path(type):
    global addon_dir
    png_file = f"{type}.png"
    icon_path = addon_dir / "pokemon_sprites" / "Types"
    icon_png_file_path = icon_path / png_file
    return icon_png_file_path

def move_category_path(category):
    global addon_dir
    png_file = f"{category}_move.png"
    category_path = addon_dir / "pokemon_sprites" / png_file
    return category_path

def MainPokemon(name, level, id, ability, type, detail_stats, attacks, hp, base_experience, growth_rate, ev, iv, gender):
    # Display the Pokémon image
    global mainpkmn
    global addon_dir
    global currdirname
    global mainpokemon_path
    mainpkmn = 1
    # Capitalize the first letter of the Pokémon's name
    capitalized_name = name.capitalize()
    stats_list = [
        detail_stats["hp"],
        detail_stats["atk"],
        detail_stats["def"],
        detail_stats["spa"],
        detail_stats["spd"],
        detail_stats["spe"],
        detail_stats["xp"]
    ]
    # Create a dictionary to store the Pokémon's data
    main_pokemon_data = []
    showInfo(f"gender {gender}")
    main_pokemon_data = [
        {
            "name": name,
            "gender": gender,
            "level": level,
            "id": id,
            "ability": ability,
            "type": type,
            "stats": detail_stats,
            "ev": ev,
            "iv": iv,
            "attacks": attacks,
            "base_experience": base_experience,
            "current_hp": calculate_hp(detail_stats["hp"],level, ev, iv),
            "growth_rate": growth_rate
        }
    ]

    # Save the caught Pokémon's data to a JSON file
    with open(str(mainpokemon_path), "w") as json_file:
        json.dump(main_pokemon_data, json_file, indent=2)

    showInfo(f"{capitalized_name} has been chosen as your main Pokemon !")

    # create a new menu item, "Show Pokemon Collection"

def PokemonDetailsStats(detail_stats, growth_rate, level):
    global font_file
    global font_name
    CompleteTable_layout = QVBoxLayout()
    experience = find_experience_for_level(growth_rate, level)
    # Stat colors
    stat_colors = {
        "hp": QColor(255, 0, 0),  # Red
        "atk": QColor(255, 165, 0),  # Orange
        "def": QColor(255, 255, 0),  # Yellow
        "spa": QColor(0, 0, 255),  # Blue
        "spd": QColor(0, 128, 0),  # Green
        "spe": QColor(255, 192, 203),  # Pink
        "total": QColor(168, 168, 167),  # Beige
        "xp": QColor(58,155,220)  # lightblue
    }

    #custom font
    custom_font = load_custom_font(font_file, 20)

    # Populate the table and create the stat bars
    for row, (stat, value) in enumerate(detail_stats.items()):
        stat_item2 = QLabel(stat.capitalize())
        max_width_stat_item = 200
        stat_item2.setFixedWidth(max_width_stat_item)
        if stat == "xp":
            experience = int(experience)
            xp = value
            value = int((int(value) / experience) * max_width_stat_item)
        value_item2 = QLabel(str(value))
        if stat == "xp":
            value_item2 = QLabel(str(xp))
        stat_item2.setFont(custom_font)
        value_item2.setFont(custom_font)
        # Create a bar item
        bar_item2 = QLabel()
        pixmap2 = createStatBar(stat_colors.get(stat), value)
        # Convert the QPixmap to an QIcon
        icon = QIcon(pixmap2)
        # Set the QIcon as the background for the QLabel
        bar_item2.setPixmap(icon.pixmap(200, 10))  # Adjust the size as needed
        layout_row = str(f"{row}" + "row")
        layout_row = QHBoxLayout()
        layout_row.addWidget(stat_item2)
        layout_row.addWidget(value_item2)
        layout_row.addWidget(bar_item2)
        stat_item2.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        bar_item2.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        value_item2.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        stat_item2.setAlignment(Qt.AlignCenter)
        bar_item2.setAlignment(Qt.AlignCenter)
        CompleteTable_layout.addLayout(layout_row)

    return CompleteTable_layout

def PokemonTrade(name, id, level, ability, iv, ev, gender, attacks):
    global addon_dir
    pokemon_trade = []
    pokemon_trade = [
        {
            "name": name,
            "level": level,
            "gender": gender,
            "ability": ability,
            "type": type,
            "stats": stats,
            "ev": ev,
            "iv": iv,
            "attacks": attacks,
            "base_experience": base_experience,
            "current_hp": 30,
            "growth_rate": growth_rate
        }
    ]
    # Create a main window
    window = QDialog()
    window.setWindowTitle(f"Trade Pokemon {name}")
    # Create an input field for error code
    trade_code_input = QLineEdit()
    trade_code_input.setPlaceholderText("Enter Pokemon Code you want to Trade for")

    # Create a button to save the input
    trade_button = QPushButton("Trade Pokemon")
    qconnect(trade_button.clicked, lambda: PokemonTradeIn(trade_code_input.text(), name))
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
    #mw.app.clipboard().setText(pokemon_info)
    mw.app.clipboard().setText(f"{info}")

    # Write the Id, EV, IV and Attacks ID into numbers, seperated by ,
    # Place in a QLabel and Copy to clipboard
    # let player place Number in and find additionally needed data from pokedex
    # at last append to pokemon_list
    # check remove mainpokemon
    # remove pokemon from pokemon_list

    # Show the window
    window.exec_()

def find_move_by_num(move_num):
    global moves_file_path
    try:
        with open(moves_file_path, 'r', encoding='utf-8') as json_file:
            moves_data = json.load(json_file)

        # Iterate through each move in the data to find the one with the matching 'num'
        for move in moves_data.values():
            if move.get('num') == move_num:
                return move  # Return the move details if found

        # If the move wasn't found, return a message indicating so
        return showInfo(f"No move found with number: {move_num}")

    except FileNotFoundError:
        return showInfo("The moves file was not found. Please check the file path.")

    except json.JSONDecodeError as e:
        return showInfo(f"Error decoding JSON: {e}")


def find_pokemon_by_id(pokemon_id):
    global pokedex_path
    try:
        # Open and load the pokedex file
        with open(pokedex_path, 'r', encoding='utf-8') as json_file:
            pokedex = json.load(json_file)

        # Search for the Pokemon by ID
        for pokemon_name, details in pokedex.items():
            if details.get('num') == pokemon_id:
                return details  # Return the details if the Pokemon is found

        # If the Pokemon wasn't found, return a message indicating so
        showInfo(f"No Pokemon found with ID: {pokemon_id}")

    except FileNotFoundError:
        showInfo("The pokedex file was not found. Please check the file path.")

    except json.JSONDecodeError as e:
        showInfo(f"Error decoding JSON: {e}")

def trade_pokemon(old_pokemon_name, pokemon_trade):
    global mypokemon_path
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
        if pokemon["name"].lower() == old_pokemon_name.lower():
            pokemon_list[i] = pokemon_trade  # Replace with new Pokemon data
            break
    else:
        showInfo(f"Pokemon named '{old_pokemon_name}' not found.")
        return

    # Write the updated data back to the file
    try:
        with open(mypokemon_path, 'w') as file:
            json.dump(pokemon_list, file, indent=2)
        showInfo(f"{old_pokemon_name} has been traded successfully!")
    except Exception as e:
        showInfo(f"An error occurred while writing to the file: {e}")

    global mainpokemon_path
    # Load the data from the file
    with open(mainpokemon_path, 'r') as file:
        pokemons = json.load(file)

    # Find and remove the Pokemon with the given name
    pokemons = [p for p in pokemons if p['name'] != old_pokemon_name]

    # Write the updated data back to the file
    with open(mainpokemon_path, 'w') as file:
        json.dump(pokemons, file, indent=4)

def PokemonTradeIn(number_code, old_pokemon_name):
    global addon_dir
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
    generation_file = "pokeapi_db.json"
    with open(str(addon_dir / generation_file), "r") as json_file:
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
    showInfo(f"{pokemon_trade}")

    #PokemonFree(old_pokemon_name)
    #global mypokemon_path
    #with open(mypokemon_path, 'r') as file:
    #    pokemon_list = json.load(file)

    #pokemon_list.append(pokemon_trade)
    #for pokemon in pokemon_list:
    #    if pokemon["name"] == old_pokemon_name:
    #        pokemon = pokemon_trade

    # Write the updated data back to the file
    #with open(mypokemon_path, 'w') as file:
    #    json.dump(pokemon_list, file, indent=2)
    trade_pokemon(f"{old_pokemon_name}", pokemon_trade)
    showInfo(f"You have sucessfully traded your {old_pokemon_name} for {name} ")

def PokemonFree(name):
    global mypokemon_path
    global mainpokemon_path
    # Load the data from the file
    with open(mainpokemon_path, 'r') as file:
        pokemon_data = json.load(file)

    for pokemons in pokemon_data:
        pokemon_name = pokemons["name"]

    if pokemon_name != name:
        with open(mypokemon_path, 'r') as file:
            pokemon_list = json.load(file)

        # Find and remove the Pokemon with the given name
        pokemon_list = [p for p in pokemon_list if p['name'] != name]

        # Write the updated data back to the file
        with open(mypokemon_path, 'w') as file:
            json.dump(pokemon_list, file, indent=2)


        # Find and remove the Pokemon with the given name
        pokemon_data = [p for p in pokemons if p['name'] != name]

        # Write the updated data back to the file
        with open(mainpokemon_path, 'w') as file:
            json.dump(pokemon_data, file, indent=2)

        showInfo(f"{name.capitalize()} has been let free.")
    else:
        showWarning("You can't free your Main Pokemon !")

def createStatBar(color, value):
    pixmap = QPixmap(200, 10)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)

    # Draw bar in the background
    painter.setPen(Qt.black)
    painter.setBrush(QColor(0, 0, 0, 200))  # Semi-transparent black
    painter.drawRect(0, 0, 200, 10)

    # Draw the colored bar based on the value
    painter.setBrush(color)
    bar_width = int(value * 1)  # Adjust the width as needed
    painter.drawRect(0, 0, bar_width, 10)

    return pixmap

def load_custom_font(font_file, font_size):
    global addon_dir
    font_path = addon_dir / font_file
    # Register the custom font with its file path
    QFontDatabase.addApplicationFont(str(font_path))
    custom_font = QFont(font_name)  # Use the font family name you specified in the font file
    custom_font.setPointSize(font_size)  # Adjust the font size as needed

    return custom_font

#test functions

def find_experience_for_level(group_growth_rate, level):
    if group_growth_rate == "medium":
        group_growth_rate = "medium-fast"
    elif group_growth_rate == "slow-then-very-fast":
        group_growth_rate = "fluctuating"
    global next_lvl_file_path
    next_lvl_xp_file = 'ExpPokemonAddon.csv'
    # Specify the growth rate and level you're interested in
    growth_rate = f'{group_growth_rate}'
    # Open the CSV file
    csv_file_path = str(next_lvl_file_path)  # Replace 'your_file_path.csv' with the actual path to your CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        # Create a CSV reader
        csv_reader = csv.DictReader(file, delimiter=';')

        # Get the fieldnames from the CSV file
        fieldnames = [field.strip() for field in csv_reader.fieldnames]

        # Iterate through rows and find the experience for the specified growth rate and level
        for row in csv_reader:
            if row[fieldnames[0]] == str(level):  # Use the first fieldname to access the 'Level' column
                experience = row[growth_rate]
                #showInfo((f"Your main Pokemon {mainpokemon_name} Lvl {level} needs {experience} XP to reach the next level."))
                break
        #else:
            #showInfo(f"Level {level} not found in the CSV file.")

        return experience

def find_experience_for_mainpokemon():
    global next_lvl_file_path
    global mainpokemon_growth_rate
    global mainpokemon_level
    global mainpokemon_xp
    if mainpokemon_growth_rate == "medium":
        mainpokemon_growth_rate = "medium-fast"
    level = mainpokemon_level
    next_lvl_xp_file = 'ExpPokemonAddon.csv'
    # Specify the growth rate and level you're interested in
    growth_rate = f'{mainpokemon_growth_rate}'
    # Open the CSV file
    csv_file_path = str(next_lvl_file_path)  # Replace 'your_file_path.csv' with the actual path to your CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        # Create a CSV reader
        csv_reader = csv.DictReader(file, delimiter=';')

        # Get the fieldnames from the CSV file
        fieldnames = [field.strip() for field in csv_reader.fieldnames]

        # Iterate through rows and find the experience for the specified growth rate and level
        for row in csv_reader:
            if row[fieldnames[0]] == str(level):  # Use the first fieldname to access the 'Level' column
                experience = row[growth_rate]
                experience = int(experience)
                experience -= mainpokemon_xp
                showInfo((f"Your main Pokemon {mainpokemon_name} Lvl {level} needs {experience} XP to reach the next level."))
                break
        #else:
            #showInfo(f"Level {level} not found in the CSV file.")

        return experience

class Downloader(QObject):
    progress_updated = pyqtSignal(int)  # Signal to update progress bar
    download_complete = pyqtSignal()  # Signal when download is complete

    def save_to_json(self, pokedex, filename):
        with open(filename, 'w') as json_file:
            json.dump(pokedex, json_file, indent=2)

    def get_pokemon_data(self,pokemon_id):
        url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}/'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to retrieve data for Pokemon with ID {pokemon_id}")
            return None

    def get_pokemon_species_data(self,pokemon_id):
        url = f'https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}/'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to retrieve species data for Pokemon with ID {pokemon_id}")
            return None

    def fetch_pokemon_data(self,url):
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to fetch data from {url}")
            return None

    def create_pokedex(self,pokemon_id):
        pokemon_data = self.get_pokemon_data(pokemon_id)
        species_data = self.get_pokemon_species_data(pokemon_id)
        if pokemon_data and species_data:
            entry = {
                "name": pokemon_data["name"],
                "id": pokemon_id,
                "effort_values": {
                    stat["stat"]["name"]: stat["effort"] for stat in pokemon_data["stats"]
                },
                "base_experience": pokemon_data["base_experience"],
                "height": pokemon_data["height"],
                "weight": pokemon_data["weight"],
                "description": species_data["flavor_text_entries"][0]["flavor_text"].replace("\n", " "),
                "growth_rate": species_data["growth_rate"]["name"]
            }
            self.pokedex.append(entry)

    def download_pokemon_data(self, addon_dir):
        urls = [
            "https://play.pokemonshowdown.com/data/learnsets.json",
            "https://play.pokemonshowdown.com/data/pokedex.json",
            "https://play.pokemonshowdown.com/data/moves.json",
            "POKEAPI"
        ]
        num_files = len(urls)
        for i, url in enumerate(urls, start=1):
            if url != "POKEAPI":
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    file_path = addon_dir / f"{url.split('/')[-1]}"
                    with open(file_path, 'w') as json_file:
                        json.dump(data, json_file, indent=2)
                else:
                    print(f"Failed to download data from {url}")
                progress = int((i / num_files) * 100)
                self.progress_updated.emit(progress)
            else:
                try:
                    self.pokedex = []
                    id = 898
                    for pokemon_id in range(1, id):
                        self.create_pokedex(pokemon_id)
                        progress = int(((pokemon_id / id) + 1) * 100)
                        self.progress_updated.emit(progress)
                    filename = addon_dir / "pokeapi_db.json"
                    with open(filename, 'w') as json_file:
                        json.dump(self.pokedex, json_file, indent=2)
                        self.download_complete.emit()
                except Exception as e:
                    showWarning(f"An error occured {e}")
class LoadingDialog(QDialog):
    def __init__(self, addon_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloading Pokemon Data")
        self.label = QLabel("Downloading... \nThis may take several minutes.", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)
        self.downloader = Downloader()
        self.downloader.progress_updated.connect(self.progress.setValue)
        self.downloader.download_complete.connect(self.on_download_complete)
        self.start_download(addon_dir)

    def start_download(self, addon_dir):
        thread = threading.Thread(target=self.downloader.download_pokemon_data, args=(addon_dir,))
        thread.start()

    def on_download_complete(self):
        self.label.setText("Download complete! You can now close this window.")

def pokeapi_db_downloader():
    global addon_dir
    dlg = LoadingDialog(addon_dir)
    dlg.exec()

def count_images_in_folder(folder_path):
    #Counts the number of images in the specified folder.
    return len([name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))])

def show_agreement_and_downloadsprites():
    # Show the agreement dialog
    dialog = AgreementDialog()
    if dialog.exec_() == QDialog.Accepted:
        # User agreed, proceed with download
        download_sprites()

class SpriteDownloader(QThread):
    progress_updated = pyqtSignal(int)
    download_complete = pyqtSignal()
    def __init__(self, sprites_path, id_to):
        super().__init__()
        self.sprites_path = sprites_path
        self.id_to = id_to
        self.front_dir = os.path.join(self.sprites_path, "front_default")
        self.back_dir = os.path.join(self.sprites_path, "back_default")
        os.makedirs(self.front_dir, exist_ok=True)
        os.makedirs(self.back_dir, exist_ok=True)

    def run(self):
        base_url = "https://pokeapi.co/api/v2/pokemon"
        total_downloaded = 0
        for pokemon_id in range(1, self.id_to + 1):
            if pokemon_id < 5:
                for sprite_type in ["front_default", "back_default"]:
                    url = f"{base_url}/{pokemon_id}"
                    response = requests.get(url)
                    if response.status_code == 200:
                        pokemon_data = response.json()
                        if sprite_type in pokemon_data["sprites"]:
                            sprite_url = pokemon_data["sprites"][sprite_type]
                            response = requests.get(sprite_url)
                            if response.status_code == 200:
                                # Determine the directory to save the image based on sprite type
                                save_dir = self.front_dir if sprite_type == "front_default" else self.back_dir
                                with open(os.path.join(save_dir, f"{pokemon_id}.png"), "wb") as f:
                                    f.write(response.content)
                                    total_downloaded += 1
                                    self.progress_updated.emit(total_downloaded)
            else:
                for sprite_type in ["front_default", "back_default"]:
                    #showInfo("PokemonID - +659")
                    if sprite_type == "front_default":
                        base_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{pokemon_id}.png"
                        response = requests.get(base_url)
                        if response.status_code == 200:
                            save_dir = self.front_dir
                            with open(os.path.join(save_dir, f"{pokemon_id}.png"), "wb") as f:
                                f.write(response.content)
                    elif sprite_type == "back_default":
                        base_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/back/{pokemon_id}.png"
                        response = requests.get(base_url)
                        if response.status_code == 200:
                            save_dir = self.back_dir
                            with open(os.path.join(save_dir, f"{pokemon_id}.png"), "wb") as f:
                                f.write(response.content)
                    total_downloaded += 1
                    self.progress_updated.emit(total_downloaded)
        self.download_complete.emit()

def download_sprites():
    global addon_dir
    # (Your existing setup code)
    sprites_path = str(addon_dir / "pokemon_sprites")
    id_to = 898 #pokeapi free to uses
    total_images_expected = id_to * 2
    max_id = 898 #latest backdefaults
    max_total_images_expected = id_to * 2

    def show_loading_window():
        window = QDialog()
        window.setWindowTitle("Loading Images")
        window.label = QLabel("Loading Images... \n This may take several minutes", window)
        window.label.setAlignment(Qt.AlignCenter)
        window.progress = QProgressBar(window)
        window.progress.setRange(0, total_images_expected)
        layout = QVBoxLayout()
        layout.addWidget(window.label)
        layout.addWidget(window.progress)
        window.setLayout(layout)

        def update_progress(value):
            window.progress.setValue(value)

        def on_download_complete():
            window.label.setText("All Images have been downloaded. Please close this window now.")

        sprite_downloader = SpriteDownloader(sprites_path, id_to)
        sprite_downloader.progress_updated.connect(update_progress)
        sprite_downloader.download_complete.connect(on_download_complete)
        sprite_downloader.start()

        window.exec_()

    show_loading_window()

def show_agreement_and_downloadspritespokeshowdown():
    # Show the agreement dialog
    dialog = AgreementDialog()
    if dialog.exec_() == QDialog.Accepted:
        # User agreed, proceed with download
        download_gifsprites()

class SpriteGifDownloader(QThread):
    progress_updated = pyqtSignal(int)
    download_complete = pyqtSignal()
    def __init__(self, sprites_path, id_to):
        super().__init__()
        self.sprites_path = sprites_path
        self.id_to = id_to
        self.front_dir = os.path.join(self.sprites_path, "front_default_gif")
        self.back_dir = os.path.join(self.sprites_path, "back_default_gif")
        os.makedirs(self.front_dir, exist_ok=True)
        os.makedirs(self.back_dir, exist_ok=True)

    def run(self):
        base_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/"
        total_downloaded = 0
        for pokemon_id in range(1, self.id_to + 1):
            for sprite_type in ["front_showdown", "back_showdown"]:
                front_sprite_url = f"{base_url}other/showdown/{pokemon_id}.gif"
                response = requests.get(front_sprite_url)
                if response.status_code == 200:
                    with open(os.path.join(self.front_dir, f"{pokemon_id}.gif"), 'wb') as file:
                        file.write(response.content)
                total_downloaded += 1
                self.progress_updated.emit(total_downloaded)

                # Download back sprite
                back_sprite_url = f"{base_url}other/showdown/back/{pokemon_id}.gif"
                response = requests.get(back_sprite_url)
                if response.status_code == 200:
                    with open(os.path.join(self.back_dir, f"{pokemon_id}.gif"), 'wb') as file:
                        file.write(response.content)
                total_downloaded += 1
                self.progress_updated.emit(total_downloaded)
        self.download_complete.emit()

def download_gifsprites():
    global addon_dir
    # (Your existing setup code)
    sprites_path = str(addon_dir / "pokemon_sprites")
    id_to = 2034
    total_images_expected = id_to * 2
    max_id = 1017
    max_total_images_expected = id_to * 2

    def show_loading_window():
        window = QDialog()
        window.setWindowTitle("Loading Images")
        window.label = QLabel("Loading Images... \n This may take several minutes", window)
        window.label.setAlignment(Qt.AlignCenter)
        window.progress = QProgressBar(window)
        window.progress.setRange(0, total_images_expected)
        layout = QVBoxLayout()
        layout.addWidget(window.label)
        layout.addWidget(window.progress)
        window.setLayout(layout)

        def update_progress(value):
            window.progress.setValue(value)

        def on_download_complete():
            window.label.setText("All Images have been downloaded. Please close this window now.")

        sprite_downloader = SpriteGifDownloader(sprites_path, id_to)
        sprite_downloader.progress_updated.connect(update_progress)
        sprite_downloader.download_complete.connect(on_download_complete)
        sprite_downloader.start()

        window.exec_()

    show_loading_window()

class ItemSpriteDownloader(QThread):
    progress_updated = pyqtSignal(int)
    download_complete = pyqtSignal()  # Signal to indicate download completion

    def __init__(self, destination_to):
        super().__init__()
        global addon_dir
        self.destination_to = addon_dir / "pokemon_sprites" / "items"
        self.base_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/dream-world/"
        self.item_names = [
        "absorb-bulb.png",
        "aguav-berry.png",
        "air-balloon.png",
        "amulet-coin.png",
        "antidote.png",
        "apicot-berry.png",
        "armor-fossil.png",
        "aspear-berry.png",
        "awakening.png",
        "babiri-berry.png",
        "balm-mushroom.png",
        "belue-berry.png",
        "berry-juice.png",
        "big-mushroom.png",
        "big-nugget.png",
        "big-pearl.png",
        "big-root.png",
        "binding-band.png",
        "black-belt.png",
        "black-flute.png",
        "black-glasses.png",
        "black-sludge.png",
        "blue-flute.png",
        "blue-scarf.png",
        "blue-shard.png",
        "bluk-berry.png",
        "bright-powder.png",
        "bug-gem.png",
        "burn-heal.png",
        "calcium.png",
        "carbos.png",
        "casteliacone.png",
        "cell-battery.png",
        "charcoal.png",
        "charti-berry.png",
        "cheri-berry.png",
        "chesto-berry.png",
        "chilan-berry.png",
        "choice-band.png",
        "choice-scarf.png",
        "choice-specs.png",
        "chople-berry.png",
        "claw-fossil.png",
        "cleanse-tag.png",
        "clever-wing.png",
        "coba-berry.png",
        "colbur-berry.png",
        "comet-shard.png",
        "cornn-berry.png",
        "cover-fossil.png",
        "custap-berry.png",
        "damp-rock.png",
        "dark-gem.png",
        "dawn-stone.png",
        "deep-sea-scale.png",
        "deep-sea-tooth.png",
        "destiny-knot.png",
        "dire-hit.png",
        "dive-ball.png",
        "dome-fossil.png",
        "draco-plate.png",
        "dragon-fang.png",
        "dragon-gem.png",
        "dragon-scale.png",
        "dread-plate.png",
        "dubious-disc.png",
        "durin-berry.png",
        "dusk-ball.png",
        "dusk-stone.png",
        "earth-plate.png",
        "eject-button.png",
        "electirizer.png",
        "electric-gem.png",
        "elixir.png",
        "energy-powder.png",
        "energy-root.png",
        "enigma-berry.png",
        "escape-rope.png",
        "ether.png",
        "everstone.png",
        "eviolite.png",
        "exp-share.png",
        "expert-belt.png",
        "fighting-gem.png",
        "figy-berry.png",
        "fire-gem.png",
        "fire-stone.png",
        "fist-plate.png",
        "flame-orb.png",
        "flame-plate.png",
        "float-stone.png",
        "fluffy-tail.png",
        "flying-gem.png",
        "focus-band.png",
        "focus-sash.png",
        "fresh-water.png",
        "full-heal.png",
        "full-incense.png",
        "full-restore.png",
        "ganlon-berry.png",
        "genius-wing.png",
        "ghost-gem.png",
        "grass-gem.png",
        "great-ball.png",
        "green-scarf.png",
        "green-shard.png",
        "grepa-berry.png",
        "grip-claw.png",
        "ground-gem.png",
        "guard-spec.png",
        "haban-berry.png",
        "hard-stone.png",
        "heal-ball.png",
        "heal-powder.png",
        "health-wing.png",
        "heart-scale.png",
        "heat-rock.png",
        "helix-fossil.png",
        "hondew-berry.png",
        "honey.png",
        "hp-up.png",
        "hyper-potion.png",
        "iapapa-berry.png",
        "ice-gem.png",
        "ice-heal.png",
        "icicle-plate.png",
        "icy-rock.png",
        "insect-plate.png",
        "iron-ball.png",
        "iron-plate.png",
        "iron.png",
        "jaboca-berry.png",
        "kasib-berry.png",
        "kebia-berry.png",
        "kelpsy-berry.png",
        "kings-rock.png",
        "lagging-tail.png",
        "lansat-berry.png",
        "lava-cookie.png",
        "lax-incense.png",
        "leaf-stone.png",
        "leftovers.png",
        "lemonade.png",
        "leppa-berry.png",
        "liechi-berry.png",
        "life-orb.png",
        "light-ball.png",
        "light-clay.png",
        "luck-incense.png",
        "lucky-egg.png",
        "lucky-punch.png",
        "lum-berry.png",
        "luxury-ball.png",
        "macho-brace.png",
        "magmarizer.png",
        "magnet.png",
        "mago-berry.png",
        "magost-berry.png",
        "master-ball.png",
        "max-elixir.png",
        "max-ether.png",
        "max-potion.png",
        "max-repel.png",
        "max-revive.png",
        "meadow-plate.png",
        "mental-herb.png",
        "metal-coat.png",
        "metal-powder.png",
        "metronome.png",
        "micle-berry.png",
        "mind-plate.png",
        "miracle-seed.png",
        "moomoo-milk.png",
        "moon-stone.png",
        "muscle-band.png",
        "muscle-wing.png",
        "mystic-water.png",
        "nanab-berry.png",
        "nest-ball.png",
        "net-ball.png",
        "never-melt-ice.png",
        "nomel-berry.png",
        "normal-gem.png",
        "nugget.png",
        "occa-berry.png",
        "odd-incense.png",
        "old-amber.png",
        "old-gateau.png",
        "oran-berry.png",
        "oval-stone.png",
        "pamtre-berry.png",
        "paralyze-heal.png",
        "pass-orb.png",
        "passho-berry.png",
        "payapa-berry.png",
        "pearl-string.png",
        "pearl.png",
        "pecha-berry.png",
        "persim-berry.png",
        "petaya-berry.png",
        "pinap-berry.png",
        "pink-scarf.png",
        "plume-fossil.png",
        "poison-barb.png",
        "poison-gem.png",
        "poke-ball.png",
        "poke-doll.png",
        "poke-toy.png",
        "pomeg-berry.png",
        "potion.png",
        "power-anklet.png",
        "power-band.png",
        "power-belt.png",
        "power-bracer.png",
        "power-herb.png",
        "power-lens.png",
        "power-weight.png",
        "pp-max.png",
        "pp-up.png",
        "premier-ball.png",
        "pretty-wing.png",
        "prism-scale.png",
        "protector.png",
        "protein.png",
        "psychic-gem.png",
        "pure-incense.png",
        "qualot-berry.png",
        "quick-ball.png",
        "quick-claw.png",
        "quick-powder.png",
        "rabuta-berry.png",
        "rare-bone.png",
        "rare-candy.png",
        "rawst-berry.png",
        "razor-claw.png",
        "razor-fang.png",
        "razz-berry.png",
        "reaper-cloth.png",
        "red-card.png",
        "red-flute.png",
        "red-scarf.png",
        "red-shard.png",
        "relic-band.png",
        "relic-copper.png",
        "relic-crown.png",
        "relic-gold.png",
        "relic-silver.png",
        "relic-statue.png",
        "relic-vase.png",
        "repeat-ball.png",
        "repel.png",
        "resist-wing.png",
        "revival-herb.png",
        "revive.png",
        "rindo-berry.png",
        "ring-target.png",
        "rock-gem.png",
        "rock-incense.png",
        "rocky-helmet.png",
        "root-fossil.png",
        "rose-incense.png",
        "rowap-berry.png",
        "sacred-ash.png",
        "safari-ball.png",
        "salac-berry.png",
        "scope-lens.png",
        "sea-incense.png",
        "sharp-beak.png",
        "shed-shell.png",
        "shell-bell.png",
        "shiny-stone.png",
        "shoal-salt.png",
        "shoal-shell.png",
        "shuca-berry.png",
        "silk-scarf.png",
        "silver-powder.png",
        "sitrus-berry.png",
        "skull-fossil.png",
        "sky-plate.png",
        "smoke-ball.png",
        "smooth-rock.png",
        "soda-pop.png",
        "soft-sand.png",
        "soothe-bell.png",
        "soul-dew.png",
        "spell-tag.png",
        "spelon-berry.png",
        "splash-plate.png",
        "spooky-plate.png",
        "star-piece.png",
        "stardust.png",
        "starf-berry.png",
        "steel-gem.png",
        "stick.png",
        "sticky-barb.png",
        "stone-plate.png",
        "sun-stone.png",
        "super-potion.png",
        "super-repel.png",
        "sweet-heart.png",
        "swift-wing.png",
        "tamato-berry.png",
        "tanga-berry.png",
        "thick-club.png",
        "thunder-stone.png",
        "timer-ball.png",
        "tiny-mushroom.png",
        "toxic-orb.png",
        "toxic-plate.png",
        "twisted-spoon.png",
        "ultra-ball.png",
        "up-grade.png",
        "wacan-berry.png",
        "water-gem.png",
        "water-stone.png",
        "watmel-berry.png",
        "wave-incense.png",
        "wepear-berry.png",
        "white-flute.png",
        "white-herb.png",
        "wide-lens.png",
        "wiki-berry.png",
        "wise-glasses.png",
        "x-accuracy.png",
        "x-attack.png",
        "x-defense.png",
        "x-sp-atk.png",
        "x-sp-def.png",
        "x-speed.png",
        "yache-berry.png",
        "yellow-flute.png",
        "yellow-scarf.png",
        "yellow-shard.png",
        "zap-plate.png",
        "zinc.png",
        "zoom-lens.png"
    ]
        if not os.path.exists(self.destination_to):
            os.makedirs(self.destination_to)

    def run(self):
        total_downloaded = 0
        for item_name in self.item_names:
            item_url = self.base_url + item_name
            response = requests.get(item_url)
            if response.status_code == 200:
                with open(os.path.join(self.destination_to, item_name), 'wb') as file:
                    file.write(response.content)
            total_downloaded += 1
            self.progress_updated.emit(total_downloaded)
        # Emit the download_complete signal at the end of the download process
        self.download_complete.emit()
def download_item_sprites():
    total_images_expected = 336
    global addon_dir
    destination_to = addon_dir / "pokemon_sprites" / "items"

    def show_loading_window():
        window = QDialog()
        window.setWindowTitle("Downloading Item Sprites")
        window.label = QLabel("Downloading... \n This may take several minutes", window)
        window.label.setAlignment(Qt.AlignCenter)
        window.progress = QProgressBar(window)
        window.progress.setRange(0, total_images_expected)
        layout = QVBoxLayout()
        layout.addWidget(window.label)
        layout.addWidget(window.progress)
        window.setLayout(layout)

        def update_progress(value):
            window.progress.setValue(value)

        def on_download_complete():
            window.label.setText("All Images have been downloaded. Please close this window now.")

        sprite_downloader = ItemSpriteDownloader(destination_to)
        sprite_downloader.progress_updated.connect(update_progress)
        sprite_downloader.download_complete.connect(on_download_complete)
        sprite_downloader.start()

        window.exec_()

    show_loading_window()

def show_agreement_and_download():
    # Show the agreement dialog
    dialog = AgreementDialog()
    if dialog.exec_() == QDialog.Accepted:
        # User agreed, proceed with download
        download_item_sprites()

class AgreementDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Setup the dialog layout
        layout = QVBoxLayout()
        # Add a label with the warning message
        title = QLabel("""Please agree to the terms before downloading the information:""")
        subtitle = QLabel("""Terms and Conditions Clause""")
        terms = QLabel("""§1 Disclaimer of Liability
(1) The user acknowledges that the use of the downloaded files is at their own risk. \n The provider assumes no liability for any damages, direct or indirect,\n that may arise from the download or use of such files.
(2) The provider is not responsible for the content of the downloaded files or \n for the legal consequences that may result from the use of the files. \n Each user is obligated to inform themselves about the legality of the use \n before using the files and to use the files only in a manner that does not cause any legal violations.

§2 Copyright Infringements
(1) The user agrees to respect copyright and other protective rights of third parties. \n It is prohibited for the user to download, reproduce, distribute, or make publicly available any copyrighted works \n without the required permission of the rights holder.
(2) In the event of a violation of copyright provisions, the user bears full responsibility and the resulting consequences. \n The provider reserves the right to take appropriate legal action \n in the event of becoming aware of any rights violations and to block access to the services.""")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(terms)
        title.setAlignment(Qt.AlignCenter)
        subtitle.setAlignment(Qt.AlignCenter)
        # Add a checkbox for the user to agree to the terms
        self.checkbox = QCheckBox("I agree to the above named terms.")
        layout.addWidget(self.checkbox)

        # Add a button to proceed
        proceed_button = QPushButton("Proceed")
        proceed_button.clicked.connect(self.on_proceed_clicked)
        layout.addWidget(proceed_button)

        self.setLayout(layout)

    def on_proceed_clicked(self):
        if self.checkbox.isChecked():
            self.accept()  # Close the dialog and return success
        else:
            QMessageBox.warning(self, "Agreement Required", "You must agree to the terms to proceed.")

life_bar_injected = False

if sprites_complete and database_complete != False:
    def reviewer_reset_life_bar_inject():
        global life_bar_injected
        life_bar_injected = False
        #showInfo(f"inject set to {life_bar_injected}")
    def inject_life_bar(web_content, context):
        global life_bar_injected, hp, name, level, id, battle_status
        global frontdefault, addon_dir
        if reviewer_image_gif == False:
            pokemon_imagefile = f'{search_pokedex(name.lower(), "num")}.png' #use for png files
            pokemon_image_file = os.path.join(frontdefault, pokemon_imagefile) #use for png files
        else:
            pokemon_imagefile = f'{search_pokedex(name.lower(), "num")}.gif'
            pokemon_image_file = os.path.join((addon_dir / "pokemon_sprites" / "front_default_gif"), pokemon_imagefile)
        max_hp = calculate_max_hp_wildpokemon()
        pokemon_hp_percent = int((hp / max_hp) * 100)
        is_reviewer = mw.state == "review"
        # Inject CSS and the life bar only if not injected before and in the reviewer
        if not life_bar_injected and is_reviewer:
            css = f"""
            #life-bar {{
                width: {pokemon_hp_percent}%; /* Replace with the actual percentage */
                height: 20px;
                background: linear-gradient(to right, 
                                            rgba(114, 230, 96, 0.7), /* Green with transparency */
                                            rgba(114, 230, 96, 0.7) 100%, /* Continue green to the percentage point */
                                            rgba(54, 54, 56, 0.7) 100%, /* Transition to dark background */
                                            rgba(54, 54, 56, 0.7)); /* Dark background with transparency */
                position: fixed;
                bottom: 10px;
                left: 0px;
                z-index: 9999;
                border-radius: 5px; /* Shorthand for all corners rounded */
                box-shadow: 0 0 10px rgba(0, 255, 0, 0.8), /* Green glow effect */
                            0 0 30px rgba(54, 54, 56, 1);  /* Dark glow effect */
            }}
             #name-display {{
                position: fixed;
                bottom: 40px;
                left: 10px;
                z-index: 9999;
                color: white;
                font-size: 16px;
                background-color: rgb(54,54,56, 0.7);
                text-align: left;
            }}
            #hp-display {{
                position: fixed;
                bottom: 40px;
                right: 10px;
                z-index: 9999;
                color: white;
                font-size: 16px;
                font-weight: bold; /* Make the text bold */
                background-color: rgb(54,54,56,0.7); 
                text-align: right;
            }}
            #PokeImage {{
                position: fixed;
                bottom: 70px; /* Adjust as needed */
                left: 3px;
                z-index: 9999;
                width: 100px; /* Adjust as needed */
                height: 100px; /* Adjust as needed */
                background-size: cover; /* Cover the div area with the image */
            }}
            """
            # background-image: url('{pokemon_image_file}'); Change to your image path */
            # Inject the CSS into the head of the HTML content
            web_content.head += f"<style>{css}</style>"
            # Inject a div element at the end of the body for the life bar
            web_content.body += f'<div id="life-bar"></div>'
            # Inject a div element for the text display
            web_content.body += f'<div id="name-display">{name.capitalize()} LvL: {level}</div>'
            if hp > 0:
                web_content.body += f'{create_status_html(f"{battle_status}")}'
            else:
                web_content.body += f'{create_status_html(f"fainted")}'

            web_content.body += f'<div id="hp-display">HP: {hp}/{max_hp}</div>'
            # Inject a div element at the end of the body for the life bar
            image_base64 = get_image_as_base64(pokemon_image_file)
            web_content.body += f'<div id="PokeImage"><img src="data:image/png;base64,{image_base64}" alt="PokeImage"></div>'
            # Set the flag to True to indicate that the life bar has been injected
            life_bar_injected = True
        return web_content

    def update_life_bar(reviewer, card, ease):
        global hp, name, id, frontdefault, battle_status
        if reviewer_image_gif == False:
            pokemon_imagefile = f'{search_pokedex(name.lower(), "num")}.png'  # use for png files
            pokemon_image_file = os.path.join(frontdefault, pokemon_imagefile)  # use for png files
        else:
            pokemon_imagefile = f'{search_pokedex(name.lower(), "num")}.gif'
            pokemon_image_file = os.path.join((addon_dir / "pokemon_sprites" / "front_default_gif"), pokemon_imagefile)
        image_base64 = get_image_as_base64(pokemon_image_file)
        max_hp = calculate_max_hp_wildpokemon()
        pokemon_hp_percent = int((hp / max_hp) * 100)

        # Update life bar based on ease or any other criteria
        # For example, decrease life by 10% for each card reviewed
        #pokemon_hp -= 10
        # Determine the color based on the percentage
        if pokemon_hp_percent < 25:
            hp_color = "rgba(255, 0, 0, 0.7)"  # Red
        elif pokemon_hp_percent < 50:
            hp_color = "rgba(255, 140, 0, 0.7)"  # Dark Orange
        elif pokemon_hp_percent < 75:
            hp_color = "rgba(255, 255, 0, 0.7)"  # Yellow
        else:
            hp_color = "rgba(114, 230, 96, 0.7)"  # Green

        # Extract RGB values from the hex color code
        #hex_color = hp_color.lstrip('#')
        #rgb_values = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        status_html = ""
        if hp < 1:
            status_html = create_status_html('fainted')
        elif hp > 0:
            status_html = create_status_html(f"{battle_status}")

        # Refresh the reviewer content to apply the updated life bar
        reviewer.web.eval('document.getElementById("life-bar").style.width = "' + str(pokemon_hp_percent) + '%";')
        reviewer.web.eval('document.getElementById("life-bar").style.background = "linear-gradient(to right, ' + str(hp_color) + ', ' + str(hp_color) + ' ' + '100' + '%, ' + 'rgba(54, 54, 56, 0.7)' + '100' + '%, ' + 'rgba(54, 54, 56, 0.7)' + ')";')
        reviewer.web.eval('document.getElementById("life-bar").style.boxShadow = "0 0 10px rgba(' + str(hp_color) + ')";')
        name_display_text = f"{name.capitalize()} Lvl: {level}"
        hp_display_text = f"HP: {hp}/{max_hp}"
        reviewer.web.eval('document.getElementById("name-display").innerText = "' + name_display_text + '";')
        reviewer.web.eval('document.getElementById("hp-display").innerText = "' + hp_display_text + '";')
        new_html_content = f'<img src="data:image/png;base64,{image_base64}" alt="PokeImage">'
        reviewer.web.eval(f'document.getElementById("PokeImage").innerHTML = `{new_html_content}`;')
        reviewer.web.eval(f'document.getElementById("pokestatus").innerHTML = `{status_html}`;')


    # Register the functions for the hooks
    gui_hooks.reviewer_will_end.append(reviewer_reset_life_bar_inject)
    gui_hooks.webview_will_set_content.append(inject_life_bar)
    gui_hooks.reviewer_did_answer_card.append(update_life_bar)

def choose_pokemon(starter_name):
    global mypokemon_path, addon_dir, mainpokemon_path
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
    growth_rate = search_pokeapi_db(f"{name.lower()}", "growth_rate")
    description= search_pokeapi_db(f"{name.lower()}", "description")
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
    caught_pokemon = {
        "name": name,
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
        "evos": evos
    }
    # Load existing Pokémon data if it exists
    if mypokemon_path.is_file():
        with open(mypokemon_path, "r") as json_file:
            caught_pokemon_data = json.load(json_file)
    else:
        caught_pokemon_data = []

    # Append the caught Pokémon's data to the list
    caught_pokemon_data.append(caught_pokemon)
    if mainpokemon_path.is_file():
        # Save the caught Pokémon's data to a JSON file
        with open(str(mainpokemon_path), "w") as json_file:
            json.dump(caught_pokemon_data, json_file, indent=2)
        mainpokemon_name, mainpokemon_id, mainpokemon_ability, mainpokemon_type, mainpokemon_stats, mainpokemon_attacks, mainpokemon_level, mainpokemon_base_experience, mainpokemon_xp, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate, mainpokemon_ev, mainpokemon_iv, mainpokemon_evolutions, mainpokemon_battle_stats, mainpokemon_gender = mainpokemon_data()

    # Save the caught Pokémon's data to a JSON file
    with open(str(mypokemon_path), "w") as json_file:
        json.dump(caught_pokemon_data, json_file, indent=2)

    showInfo(f"{name.capitalize()} has been chosen as Starter Pokemon !")

    starter_window.display_chosen_starter_pokemon(starter_name)

def export_to_pkmn_showdown():
    global mainpokemon_level, mainpokemon_type, mainpokemon_name, mainpokemon_stats, mainpokemon_attacks, mainpokemon_ability, mainpokemon_iv, mainpokemon_ev, mainpokemon_gender
    # Create a main window
    window = QDialog(mw)
    window.setWindowTitle("Export Pokemon to Pkmn Showdown")
    for stat, value in mainpokemon_ev.items():
        if value == 0:
            mainpokemon_ev[stat] += 1
    # Format the Pokemon info
    #pokemon_info = f"{mainpokemon_name}\nAbility: {mainpokemon_ability}\nLevel: {mainpokemon_level}\nType: {mainpokemon_type}\nEVs: {mainpokemon_stats['hp']} HP / {mainpokemon_stats['attack']} Atk / {mainpokemon_stats['defense']} Def / {mainpokemon_stats['special-attack']} SpA / {mainpokemon_stats['special-defense']} SpD / {mainpokemon_stats['speed']} Spe\n IVs: {mainpokemon_iv["hp"]} HP / {mainpokemon_iv["attack"]} Atk / {mainpokemon_iv["defense"]} Def / {mainpokemon_iv["special-attack"]} SpA / {mainpokemon_iv["special-defense"]} SpD / {mainpokemon_iv["speed"]} Spe \n- {mainpokemon_attacks[0]}\n- {mainpokemon_attacks[1]}\n- {mainpokemon_attacks[2]}\n- {mainpokemon_attacks[3]}"
    pokemon_info = "{} ({})\nAbility: {}\nLevel: {}\nType: {}\nEVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe\n IVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe ".format(
        mainpokemon_name,
        mainpokemon_gender,
        mainpokemon_ability,
        mainpokemon_level,
        mainpokemon_type,
        mainpokemon_ev["hp"],
        mainpokemon_ev["atk"],
        mainpokemon_ev["def"],
        mainpokemon_ev["spa"],
        mainpokemon_ev["spd"],
        mainpokemon_ev["spe"],
        mainpokemon_iv["hp"],
        mainpokemon_iv["atk"],
        mainpokemon_iv["def"],
        mainpokemon_iv["spa"],
        mainpokemon_iv["spd"],
        mainpokemon_iv["spe"]
    )
    for attack in mainpokemon_attacks:
        pokemon_info += f"\n- {attack}"
    # Information label
    info = "Pokemon Infos have been Copied to your Clipboard! \nNow simply paste this text into Teambuilder in PokemonShowdown. \nNote: Fight in the [Gen 9] Anything Goes - Battle Mode"
    info += f"\n Your Pokemon is considered Tier: {search_pokedex(mainpokemon_name.lower(), 'tier')} in PokemonShowdown"
    # Create labels to display the text
    label = QLabel(pokemon_info)
    info_label = QLabel(info)

    # Align labels
    label.setAlignment(Qt.AlignCenter)  # Align center
    info_label.setAlignment(Qt.AlignCenter)  # Align center

    # Create a layout and add the labels
    layout = QVBoxLayout()
    layout.addWidget(info_label)
    layout.addWidget(label)

    # Set the layout for the main window
    window.setLayout(layout)

    # Copy text to clipboard in Anki
    mw.app.clipboard().setText(pokemon_info)

    # Show the window
    window.show()

def save_error_code(error_code):
    error_fix_msg = ""
    try:
        # Find the position of the phrase "can't be transferred from Gen"
        index = error_code.find("can't be transferred from Gen")

        # Extract the substring starting from this position
        relevant_text = error_code[index:]

        # Find the first number in the extracted text (assuming it's the generation number)
        generation_number = int(''.join(filter(str.isdigit, relevant_text)))

        # Show the generation number
        #showInfo(f"Please use Gen {str(generation_number)[0]}")
        error_fix_msg += (f"\n Please use Gen {str(generation_number)[0]} or lower")

        index = error_code.find("can't be transferred from Gen")

        # Extract the substring starting from this position
        relevant_text = error_code[index:]

        # Find the first number in the extracted text (assuming it's the generation number)
        generation_number = int(''.join(filter(str.isdigit, relevant_text)))

        error_fix_msg += (f"\n Please use Gen {str(generation_number)[0]} or lower")

    except Exception as e:
        showInfo(f"An error occurred: {e}")

    showInfo(f"{error_fix_msg}")

def export_all_pkmn_showdown():
    # Create a main window
    export_window = QDialog()
    #export_window.setWindowTitle("Export Pokemon to Pkmn Showdown")

    # Information label
    info = "Pokemon Infos have been Copied to your Clipboard! \nNow simply paste this text into Teambuilder in PokemonShowdown. \nNote: Fight in the [Gen 7] Anything Goes - Battle Mode"
    info_label = QLabel(info)

    # Get all pokemon data
    global mypokemon_path
    pokemon_info_complete_text = ""
    try:
        with (open(mypokemon_path, "r") as json_file):
            captured_pokemon_data = json.load(json_file)

            # Check if there are any captured Pokémon
            if captured_pokemon_data:
                # Counter for tracking the column position
                column = 0
                row = 0
                for pokemon in captured_pokemon_data:
                    pokemon_name = pokemon['name']
                    pokemon_level = pokemon['level']
                    pokemon_ability = pokemon['ability']
                    pokemon_type = pokemon['type']
                    pokemon_type_text = pokemon_type[0].capitalize()
                    if len(pokemon_type) > 1:
                        pokemon_type_text = ""
                        pokemon_type_text += f"{pokemon_type[0].capitalize()}"
                        pokemon_type_text += f" {pokemon_type[1].capitalize()}"
                    pokemon_stats = pokemon['stats']
                    pokemon_hp = pokemon_stats["hp"]
                    pokemon_attacks = pokemon['attacks']
                    pokemon_ev = pokemon['ev']
                    pokemon_iv = pokemon['iv']

                    pokemon_info = "\n{} \nAbility: {}\nLevel: {}\nType: {}\nEVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe\n IVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe \n".format(
                        pokemon_name,
                        pokemon_ability.capitalize(),
                        pokemon_level,
                        pokemon_type_text,
                        pokemon_stats["hp"],
                        pokemon_stats["atk"],
                        pokemon_stats["def"],
                        pokemon_stats["spa"],
                        pokemon_stats["spd"],
                        pokemon_stats["spe"],
                        pokemon_iv["hp"],
                        pokemon_iv["atk"],
                        pokemon_iv["def"],
                        pokemon_iv["spa"],
                        pokemon_iv["spd"],
                        pokemon_iv["spe"]
                    )
                    for attack in pokemon_attacks:
                        pokemon_info += f"- {attack}\n"
                    pokemon_info_complete_text += pokemon_info

                    # Create labels to display the text
                    #label = QLabel(pokemon_info_complete_text)
                    # Align labels
                    #label.setAlignment(Qt.AlignCenter)  # Align center
                    info_label.setAlignment(Qt.AlignCenter)  # Align center

                    # Create an input field for error code
                    error_code_input = QLineEdit()
                    error_code_input.setPlaceholderText("Enter Error Code")

                    # Create a button to save the input
                    save_button = QPushButton("Fix Pokemon Export Code")

                    # Create a layout and add the labels, input field, and button
                    layout = QVBoxLayout()
                    layout.addWidget(info_label)
                    #layout.addWidget(label)
                    layout.addWidget(error_code_input)
                    layout.addWidget(save_button)

                    # Copy text to clipboard in Anki
                    mw.app.clipboard().setText(pokemon_info_complete_text)

        save_button.clicked.connect(lambda: save_error_code(error_code_input.text()))

        # Set the layout for the main window
        export_window.setLayout(layout)

        export_window.exec()
    except Exception as e:
        showInfo(f"An error occurred: {e}")

def calc_exp_gain(base_experience, w_pkmn_level):
    exp = int((base_experience * w_pkmn_level) / 7)
    return exp

# Define the function to open the Pokémon Showdown Team Builder
def open_team_builder():
    # Specify the URL of the Pokémon Showdown Team Builder
    team_builder_url = "https://play.pokemonshowdown.com/teambuilder"

    # Open the Team Builder in the default web browser
    QDesktopServices.openUrl(QUrl(team_builder_url))

#def no_hp():
    #if main_window is not None:
        #main_window.death_window()
test = 1
video = False
pkmn_window = False #if fighting window open
first_start = False
class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        #self.update()
    def init_ui(self):
        global test
        global addon_dir
        basic_layout = QVBoxLayout()
        self.setLayout(basic_layout)
        # Set window
        self.setWindowTitle('Pokemon Window')
        # Display the Pokémon image

    def open_dynamic_window(self):
        # Create and show the dynamic window
        global pkmn_window
        if pkmn_window == False:
            self.display_first_encounter()
            pkmn_window = True
        self.show()

    def display_first_start_up(self):
        global first_start, pkmn_window
        if first_start == False:
            # Main window layout
            global addon_dir
            layout = QVBoxLayout()
            image_file = f"ankimon logo.jpg"
            image_path = addon_dir / image_file
            image_label = QLabel()
            pixmap = QPixmap()
            pixmap.load(str(image_path))
            if pixmap.isNull():
                showWarning("Failed to load image")
            else:
                image_label.setPixmap(pixmap)
            scaled_pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
            image_label.setPixmap(scaled_pixmap)
            layout.addWidget(image_label)
            first_start = True
            self.setLayout(layout)
            self.show()
        global pkmn_window
        pkmn_window = True

    def pokemon_display_first_encounter(self):
        # Main window layout
        layout = QVBoxLayout()
        global pokemon_encounter
        global hp, name, id, stats, level, max_hp, base_experience, ev, iv, gender
        global caught_pokemon, message_box_text
        global pkmnimgfolder, backdefault, addon_dir
        global caught
        global mainpkmn, mainpokemon_path
        global mainpokemon_id, mainpokemon_name, mainpokemon_level, mainpokemon_ability, mainpokemon_type, mainpokemon_xp, mainpokemon_stats, mainpokemon_attacks, mainpokemon_base_experience, mainpokemon_ev, mainpokemon_iv, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate
        global battlescene_path, battlescene_path_without_dialog, battlescene_file, battle_ui_path, battle_ui_path_without_dialog
        global attack_counter, merged_pixmap, window
        attack_counter = 0
        # get main pokemon details:
        try:
            mainpokemon_name, mainpokemon_id, mainpokemon_ability, mainpokemon_type, mainpokemon_stats, mainpokemon_attacks, mainpokemon_level, mainpokemon_base_experience, mainpokemon_xp, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate, mainpokemon_ev, mainpokemon_iv, mainpokemon_evolutions, mainpokemon_battle_stats, mainpokemon_gender = mainpokemon_data()
        except Exception as e:
            showWarning(f"an error occured: {e}")
        caught = 0
        id = int(search_pokedex(name.lower(), "num"))
        # Capitalize the first letter of the Pokémon's name
        name = name.capitalize()
        # calculate wild pokemon max hp
        max_hp = calculate_hp(stats["hp"], level, ev, iv)
        message_box_text = (f"A wild {name} appeared !")
        if pokemon_encounter == 0:
            bckgimage_path = battlescene_path / battlescene_file
        elif pokemon_encounter > 0:
            bckgimage_path = battlescene_path_without_dialog / battlescene_file
        def window_show():
            ui_path = battle_ui_path
            pixmap_ui = QPixmap()
            pixmap_ui.load(str(ui_path))

            # Load the background image
            pixmap_bckg = QPixmap()
            pixmap_bckg.load(str(bckgimage_path))

            # Display the Pokémon image
            pkmnimage_file = f"{id}.png"
            pkmnimage_path = frontdefault / pkmnimage_file
            image_label = QLabel()
            pixmap = QPixmap()
            pixmap.load(str(pkmnimage_path))

            # Display the Main Pokémon image
            pkmnimage_file2 = f"{mainpokemon_id}.png"
            pkmnimage_path2 = backdefault / pkmnimage_file2
            pixmap2 = QPixmap()
            pixmap2.load(str(pkmnimage_path2))

            # Calculate the new dimensions to maintain the aspect ratio
            max_width = 150
            original_width = pixmap.width()
            original_height = pixmap.height()
            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pixmap = pixmap.scaled(new_width, new_height)

            # Calculate the new dimensions to maintain the aspect ratio
            max_width = 150
            original_width2 = pixmap2.width()
            original_height2 = pixmap2.height()

            new_width2 = max_width
            new_height2 = (original_height2 * max_width) // original_width2
            pixmap2 = pixmap2.scaled(new_width2, new_height2)

            # Merge the background image and the Pokémon image
            merged_pixmap = QPixmap(pixmap_bckg.size())
            merged_pixmap.fill(Qt.transparent)
            # merge both images together
            painter = QPainter(merged_pixmap)
            # draw background to a specific pixel
            painter.drawPixmap(0, 0, pixmap_bckg)

            def draw_hp_bar(x, y, h, w, hp, max_hp):
                pokemon_hp_percent = (hp / max_hp) * 100
                hp_bar_value = (w * (hp / max_hp))
                # Draw the HP bar
                if pokemon_hp_percent < 25:
                    hp_color = QColor(255, 0, 0)  # Red
                elif pokemon_hp_percent < 50:
                    hp_color = QColor(255, 140, 0)  # Orange
                elif pokemon_hp_percent < 75:
                    hp_color = QColor(255, 255, 0)  # Yellow
                else:
                    hp_color = QColor(110, 218, 163)  # Green
                painter.setBrush(hp_color)
                painter.drawRect(x, y, hp_bar_value, h)

            draw_hp_bar(118, 76, 8, 116, hp, max_hp)  # enemy pokemon hp_bar
            draw_hp_bar(401, 208, 8, 116, mainpokemon_current_hp, mainpokemon_hp)  # main pokemon hp_bar

            painter.drawPixmap(0, 0, pixmap_ui)
            # Find the Pokemon Images Height and Width
            wpkmn_width = (new_width / 2)
            wpkmn_height = new_height
            mpkmn_width = (new_width2 / 2)
            mpkmn_height = new_height2
            # draw pokemon image to a specific pixel
            painter.drawPixmap((410 - wpkmn_width), (170 - wpkmn_height), pixmap)
            painter.drawPixmap((144 - mpkmn_width), (290 - mpkmn_height), pixmap2)

            experience = find_experience_for_level(mainpokemon_growth_rate, mainpokemon_level)
            experience = int(experience)
            mainxp_bar_width = 5
            mainpokemon_xp_value = int((mainpokemon_xp / experience) * 148)
            # Paint XP Bar
            painter.setBrush(QColor(58, 155, 220))
            painter.drawRect(366, 246, mainpokemon_xp_value, mainxp_bar_width)

            # create level text
            lvl = (f"{level}")
            #gender_text = (f"{gender}")
            mainlvl = (f"{mainpokemon_level}")

            # custom font
            custom_font = load_custom_font(font_file, 26)
            msg_font = load_custom_font(font_file, 32)

            # Draw the text on top of the image
            # Adjust the font size as needed
            painter.setFont(custom_font)
            painter.setPen(QColor(31, 31, 39))  # Text color
            painter.drawText(48, 67, f"{name} ({gender})")
            painter.drawText(326, 200, mainpokemon_name)
            painter.drawText(208, 67, lvl)
            #painter.drawText(55, 85, gender_text)
            painter.drawText(490, 199, mainlvl)
            painter.drawText(487, 238, f"{mainpokemon_hp}")
            painter.drawText(442, 238, f"{mainpokemon_current_hp}")
            painter.setFont(msg_font)
            painter.setPen(QColor(240, 240, 208))  # Text color
            painter.drawText(40, 320, message_box_text)
            painter.end()
            # Set the merged image as the pixmap for the QLabel
            image_label.setPixmap(merged_pixmap)
            return image_label, msg_font
        image_label, msg_font = window_show()
        return image_label

    def pokemon_display_battle(self):
        global pokemon_encounter, id
        pokemon_encounter += 1
        if pokemon_encounter == 1:
            bckgimage_path = battlescene_path / battlescene_file
        elif pokemon_encounter > 1:
            bckgimage_path = battlescene_path_without_dialog / battlescene_file
        ui_path = battle_ui_path
        pixmap_ui = QPixmap()
        pixmap_ui.load(str(ui_path))

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        # Display the Pokémon image
        pkmnimage_file = f"{id}.png"
        pkmnimage_path = frontdefault / pkmnimage_file
        image_label = QLabel()
        pixmap = QPixmap()
        pixmap.load(str(pkmnimage_path))

        # Display the Main Pokémon image
        pkmnimage_file2 = f"{mainpokemon_id}.png"
        pkmnimage_path2 = backdefault / pkmnimage_file2
        pixmap2 = QPixmap()
        pixmap2.load(str(pkmnimage_path2))

        # Calculate the new dimensions to maintain the aspect ratio
        max_width = 150
        original_width = pixmap.width()
        original_height = pixmap.height()
        new_width = max_width
        new_height = (original_height * max_width) //original_width
        pixmap = pixmap.scaled(new_width, new_height)

        # Calculate the new dimensions to maintain the aspect ratio
        max_width = 150
        original_width2 = pixmap2.width()
        original_height2 = pixmap2.height()

        new_width2 = max_width
        new_height2 = (original_height2 * max_width) // original_width2
        pixmap2 = pixmap2.scaled(new_width2, new_height2)

        # Merge the background image and the Pokémon image
        merged_pixmap = QPixmap(pixmap_bckg.size())
        merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)

        def draw_hp_bar(x, y, h, w, hp, max_hp):
            pokemon_hp_percent = (hp / max_hp) * 100
            hp_bar_value = (w * (hp / max_hp))
            # Draw the HP bar
            if pokemon_hp_percent < 25:
                hp_color = QColor(255, 0, 0)  # Red
            elif pokemon_hp_percent < 50:
                hp_color = QColor(255, 140, 0)  # Orange
            elif pokemon_hp_percent < 75:
                hp_color = QColor(255, 255, 0)  # Yellow
            else:
                hp_color = QColor(110, 218, 163)  # Green
            painter.setBrush(hp_color)
            painter.drawRect(x, y, hp_bar_value, h)

        draw_hp_bar(118, 76, 8, 116, hp, max_hp)  # enemy pokemon hp_bar
        draw_hp_bar(401, 208, 8, 116, mainpokemon_current_hp, mainpokemon_hp)  # main pokemon hp_bar

        painter.drawPixmap(0, 0, pixmap_ui)
        # Find the Pokemon Images Height and Width
        wpkmn_width = (new_width / 2)
        wpkmn_height = new_height
        mpkmn_width = (new_width2 / 2)
        mpkmn_height = new_height2
        # draw pokemon image to a specific pixel
        painter.drawPixmap((410 - wpkmn_width), (170 - wpkmn_height), pixmap)
        painter.drawPixmap((144 - mpkmn_width), (290 - mpkmn_height), pixmap2)

        experience = find_experience_for_level(mainpokemon_growth_rate, mainpokemon_level)
        experience = int(experience)
        mainxp_bar_width = 5
        mainpokemon_xp_value = int((mainpokemon_xp / experience) * 148)
        # Paint XP Bar
        painter.setBrush(QColor(58, 155, 220))
        painter.drawRect(366, 246, mainpokemon_xp_value, mainxp_bar_width)

        # create level text
        lvl = (f"{level}")
        mainlvl = (f"{mainpokemon_level}")

        # custom font
        custom_font = load_custom_font(font_file, 28)
        msg_font = load_custom_font(font_file, 32)

        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(31, 31, 39))  # Text color
        painter.drawText(48, 67, name)
        painter.drawText(326, 200, mainpokemon_name)
        painter.drawText(208, 67, lvl)
        painter.drawText(490, 199, mainlvl)
        painter.drawText(487, 238, f"{mainpokemon_hp}")
        painter.drawText(442, 238, f"{mainpokemon_current_hp}")
        painter.setFont(msg_font)
        painter.setPen(QColor(240, 240, 208))  # Text color
        painter.drawText(40, 320, message_box_text)
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        image_label.setPixmap(merged_pixmap)
        return image_label

    def pokemon_display_item(self, item):
        global pokemon_encounter
        global addon_dir
        global frontdefault
        bckgimage_path = addon_dir / "pokemon_sprites" / "starter_screen" / "bg.png"
        item_path = addon_dir / "pokemon_sprites" / "items" / f"{item}.png"

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        # Display the Pokémon image
        item_label = QLabel()
        item_pixmap = QPixmap()
        item_pixmap.load(str(item_path))

        def resize_pixmap_img(pixmap):
            max_width = 100
            original_width = pixmap.width()
            original_height = pixmap.height()

            if original_width == 0:
                return pixmap  # Avoid division by zero

            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pixmap2 = pixmap.scaled(new_width, new_height)
            return pixmap2

        item_pixmap = resize_pixmap_img(item_pixmap)

        # Merge the background image and the Pokémon image
        merged_pixmap = QPixmap(pixmap_bckg.size())
        merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)
        #item = str(item)
        if item.endswith("-up") or item.endswith("-max") or item.endswith("protein") or item.endswith("zinc") or item.endswith("carbos") or item.endswith("calcium") or item.endswith("repel") or item.endswith("statue"):
            painter.drawPixmap(200,50,item_pixmap)
        elif item.endswith("soda-pop"):
            painter.drawPixmap(200,30,item_pixmap)
        elif item.endswith("-heal") or item.endswith("awakening") or item.endswith("ether") or item.endswith("leftovers"):
            painter.drawPixmap(200,50,item_pixmap)
        elif item.endswith("-berry") or item.endswith("potion"):
            painter.drawPixmap(200,80,item_pixmap)
        else:
            painter.drawPixmap(200,90,item_pixmap)

        # custom font
        custom_font = load_custom_font(font_file, 26)
        message_box_text = f"You have received a item: {item.capitalize()} !"
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(50, 290, message_box_text)
        custom_font = load_custom_font(font_file, 20)
        painter.setFont(custom_font)
        #painter.drawText(10, 330, "You can look this up in your item bag.")
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        image_label = QLabel()
        image_label.setPixmap(merged_pixmap)

        return image_label

    def pokemon_display_dead_pokemon(self):
        global pokemon_hp, name, id, level, type, caught_pokemon, pkmnimgfolder, frontdefault, addon_dir, caught, pokedex_image_path
        # Create the dialog
        window_title = (f"Would you want let the  wild {name} free or catch the wild {name} ?")
        # Display the Pokémon image
        pkmnimage_file = f"{int(search_pokedex(name.lower(),'num'))}.png"
        pkmnimage_path = addon_dir / frontdefault / pkmnimage_file
        pkmnimage_label = QLabel()
        pkmnpixmap = QPixmap()
        pkmnpixmap.load(str(pkmnimage_path))
        pkmnpixmap_bckg = QPixmap()
        pkmnpixmap_bckg.load(str(pokedex_image_path))
        # Calculate the new dimensions to maintain the aspect ratio
        pkmnpixmap = pkmnpixmap.scaled(230, 230)

        # Create a painter to add text on top of the image
        painter2 = QPainter(pkmnpixmap_bckg)
        painter2.drawPixmap(15,15,pkmnpixmap)
        # Capitalize the first letter of the Pokémon's name
        capitalized_name = name.capitalize()
        # Create level text
        lvl = (f" Level: {level}")

        # Draw the text on top of the image
        font = QFont()
        font.setPointSize(20)  # Adjust the font size as needed
        painter2.setFont(font)
        painter2.drawText(270,107,f"{capitalized_name}")
        font.setPointSize(17)  # Adjust the font size as needed
        painter2.setFont(font)
        painter2.drawText(315,192,f"{lvl}")
        painter2.drawText(322,225,f"Type: {type[0].capitalize()}")
        painter2.setFont(font)
        fontlvl = QFont()
        fontlvl.setPointSize(12)
        painter2.end()

        # Create a QLabel for the capitalized name
        name_label = QLabel(capitalized_name)
        name_label.setFont(font)

        # Create a QLabel for the level
        level_label = QLabel(lvl)
        # Align to the center
        level_label.setFont(fontlvl)

        nickname_input = QLineEdit()
        nickname_input.setPlaceholderText("Choose Nickname")
        nickname_input.setStyleSheet("background-color: rgb(44,44,44);")
        nickname_input.setFixedSize(120, 30)  # Adjust the size as needed

        # Create buttons for catching and killing the Pokémon
        catch_button = QPushButton("Catch Pokémon")
        catch_button.setFixedSize(175, 30)  # Adjust the size as needed
        catch_button.setFont(QFont("Arial", 12))  # Adjust the font size and style as needed
        catch_button.setStyleSheet("background-color: rgb(44,44,44);")
        #catch_button.setFixedWidth(150)
        qconnect(catch_button.clicked, lambda: catch_pokemon(nickname_input.text()))

        kill_button = QPushButton("Kill Pokémon")
        kill_button.setFixedSize(175, 30)  # Adjust the size as needed
        kill_button.setFont(QFont("Arial", 12))  # Adjust the font size and style as needed
        kill_button.setStyleSheet("background-color: rgb(44,44,44);")
        #kill_button.setFixedWidth(150)
        qconnect(kill_button.clicked, kill_pokemon)
        # Set the merged image as the pixmap for the QLabel
        pkmnimage_label.setPixmap(pkmnpixmap_bckg)


        # align things needed to middle
        pkmnimage_label.setAlignment(Qt.AlignCenter)

        return pkmnimage_label, kill_button, catch_button, nickname_input

    # This is a slot function that will be called when the media status changes
    def handleMediaStatusChanged(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            showInfo("Media loaded and ready to play")
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            showInfo("Media playback ended")

    def display_first_encounter(self):
        # pokemon encounter image
        self.clear_layout(self.layout())
        #self.setFixedWidth(556)
        #self.setFixedHeight(371)
        layout = self.layout()
        battle_widget = self.pokemon_display_first_encounter()
        layout.addWidget(battle_widget)
        self.setStyleSheet("background-color: rgb(44,44,44);")
        self.setLayout(layout)
        self.setMaximumWidth(556)
        self.setMaximumHeight(300)

    def display_item(self):
        # pokemon encounter image
        self.clear_layout(self.layout())
        layout = self.layout()
        item_name = random_item()
        item_widget = self.pokemon_display_item(item_name)
        layout.addWidget(item_widget)
        self.setStyleSheet("background-color: rgb(44,44,44);")
        self.setMaximumWidth(512)
        self.setMaximumHeight(320)
        self.setLayout(layout)

    def display_pokemon_death(self):
        # pokemon encounter image
        self.clear_layout(self.layout())
        layout = self.layout()
        pkmnimage_label, kill_button, catch_button, nickname_input = self.pokemon_display_dead_pokemon()
        layout.addWidget(pkmnimage_label)
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.addWidget(kill_button)
        button_layout.addWidget(catch_button)
        button_layout.addWidget(nickname_input)
        button_widget.setLayout(button_layout)
        layout.addWidget(button_widget)
        self.setStyleSheet("background-color: rgb(177,147,209);")
        self.setLayout(layout)
        self.setMaximumWidth(500)
        self.setMaximumHeight(300)

    def keyPressEvent(self, event):
        global test, pokemon_encounter, pokedex_image_path
        # Close the main window when the spacebar is pressed
        if event.key() == Qt.Key.Key_N and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.close()
        #if event.key() == Qt.Key_D:
            #self.setMaximumWidth(590)
            #self.setMaximumHeight(390)
            #self.clear_layout(self.layout())
            #layout = self.layout()
            #battle_widget = self.pokemon_display_battle()
            #layout.addWidget(battle_widget)
            #self.setStyleSheet("background-color: rgb(44,44,44);")
            #self.setLayout(layout)
        #if event.key() == Qt.Key_J:
            #self.display_item()
            #self.setStyleSheet("background-color: rgb(44,44,44);")

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def closeEvent(self,event):
        global pkmn_window
        pkmn_window = False

# Create an instance of the MainWindow
test_window = TestWindow()

class StarterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        #self.update()
    def init_ui(self):
        global test
        basic_layout = QVBoxLayout()
        # Set window
        self.setWindowTitle('Choose a Starter')
        self.setLayout(basic_layout)
        self.starter = False
    def open_dynamic_window(self):
        self.show()
    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    def keyPressEvent(self, event):
        global test, pokemon_encounter, pokedex_image_path
        # Close the main window when the spacebar is pressed
        if event.key() == Qt.Key_G:
            #first encounter image
            if self.starter == False:
                self.display_starter_pokemon()
            elif self.starter == True:
                pass

    def display_starter_pokemon(self):
        self.setMaximumWidth(512)
        self.setMaximumHeight(320)
        self.clear_layout(self.layout())
        layout = self.layout()
        water_start, fire_start, grass_start = get_random_starter()
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
        showInfo("You have chosen your Starter Pokemon ! \n You can now close this window ! \n Please restart your Anki to restart your Pokemon Journey!")

    def pokemon_display_starter_buttons(self, water_start, fire_start, grass_start):
        # Create buttons for catching and killing the Pokémon
        water_starter_button = QPushButton(f"{(water_start).capitalize()}")
        water_starter_button.setFont(QFont("Arial",12))  # Adjust the font size and style as needed
        water_starter_button.setStyleSheet("background-color: rgb(44,44,44);")
        #qconnect(water_starter_button.clicked, choose_pokemon)
        qconnect(water_starter_button.clicked, lambda: choose_pokemon(water_start))

        fire_starter_button = QPushButton(f"{(fire_start).capitalize()}")
        fire_starter_button.setFont(QFont("Arial", 12))  # Adjust the font size and style as needed
        fire_starter_button.setStyleSheet("background-color: rgb(44,44,44);")
        #qconnect(fire_starter_button.clicked, choose_pokemon)
        qconnect(fire_starter_button.clicked, lambda: choose_pokemon(fire_start))
        # Set the merged image as the pixmap for the QLabel

        grass_start_button = QPushButton(f"{(grass_start).capitalize()}")
        grass_start_button.setFont(QFont("Arial", 12))  # Adjust the font size and style as needed
        grass_start_button.setStyleSheet("background-color: rgb(44,44,44);")
        #qconnect(grass_start_button.clicked, choose_pokemon)
        qconnect(grass_start_button.clicked, lambda: choose_pokemon(grass_start))
        # Set the merged image as the pixmap for the QLabel

        return water_starter_button, fire_starter_button, grass_start_button

    def pokemon_display_starter(self, water_start, fire_start, grass_start):
        global pokemon_encounter
        global addon_dir
        global frontdefault
        bckgimage_path = addon_dir / "pokemon_sprites" / "starter_screen" / "bckg.png"
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
        merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)

        painter.drawPixmap(57,-5,water_pixmap)
        painter.drawPixmap(182,-5,fire_pixmap)
        painter.drawPixmap(311,-3,grass_pixmap)

        # custom font
        custom_font = load_custom_font(font_file, 28)
        message_box_text = "Choose your Starter Pokemon"
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(110, 310, message_box_text)
        custom_font = load_custom_font(font_file, 20)
        painter.setFont(custom_font)
        painter.drawText(10, 330, "Press G to change Generation")
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        starter_label = QLabel()
        starter_label.setPixmap(merged_pixmap)

        return starter_label

    def pokemon_display_chosen_starter(self, starter_name):
        global pokemon_encounter
        global addon_dir
        global frontdefault
        bckgimage_path = addon_dir / "pokemon_sprites" / "starter_screen" / "bg.png"
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
        merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)
        painter.drawPixmap(125,10,image_pixmap)

        # custom font
        custom_font = load_custom_font(font_file, 32)
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

class EvoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        #self.open_dynamic_window()
        #self.display_evo_pokemon(name, prevo_name)
    def init_ui(self):
        basic_layout = QVBoxLayout()
        # Set window
        self.setWindowTitle('Your Pokemon is about to Evolve')
        self.setLayout(basic_layout)
    def open_dynamic_window(self):
        self.show()

    def display_evo_pokemon(self, pkmn_name, prevo_name):
        self.clear_layout(self.layout())
        layout = self.layout()
        pkmn_label = self.pokemon_display_evo(pkmn_name, prevo_name)
        layout.addWidget(pkmn_label)
        self.setStyleSheet("background-color: rgb(14,14,14);")
        self.setLayout(layout)
        self.setMaximumWidth(500)
        self.setMaximumHeight(300)
        self.show()

    def pokemon_display_evo(self, pkmn_name, prevo_name):
        global addon_dir
        global frontdefault
        bckgimage_path = addon_dir / "pokemon_sprites" / "starter_screen" / "bg.png"
        id = int(search_pokedex(pkmn_name.lower(), "num"))

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
        merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)
        painter.drawPixmap(125,10,image_pixmap)

        # custom font
        custom_font = load_custom_font(font_file, 20)
        message_box_text = f"{(prevo_name).capitalize()} has evolved to {(pkmn_name).capitalize()} !"
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(40, 290, message_box_text)
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        pkmn_label = QLabel()
        pkmn_label.setPixmap(merged_pixmap)

        return pkmn_label

    def display_pokemon_evo(self, pkmn_name):
        self.setMaximumWidth(600)
        self.setMaximumHeight(530)
        self.clear_layout(self.layout())
        layout = self.layout()
        pokemon_images, evolve_button, dont_evolve_button = self.pokemon_display_evo_pokemon(pkmn_name)
        layout.addWidget(pokemon_images)
        layout.addWidget(evolve_button)
        layout.addWidget(dont_evolve_button)
        self.setStyleSheet("background-color: rgb(44,44,44);")
        self.setLayout(layout)
        self.show()

    def pokemon_display_evo_pokemon(self, pkmn_name):
        global pokemon_hp, name, id, level, caught_pokemon, pkmnimgfolder, frontdefault, addon_dir, caught, evolve_image_path
        global mainpokemon_name, mainpokemon_id
        layout_pokemon = QHBoxLayout()
        # Update mainpokemon_evolution and handle evolution logic
        pokemon_evos = search_pokedex(pkmn_name.lower(), "evos")
        pkmn_id = int(search_pokedex(pkmn_name.lower(), "num"))
        try:
            if len(pokemon_evos) > 1:
                pokemon_evo = random.choice(pokemon_evos)
                pokemon_evo_id = int((search_pokedex(pokemon_evo.lower(), "num")))
            else:
                pokemon_evo = pokemon_evos[0]
                pokemon_evo_id = int((search_pokedex(pokemon_evo.lower(), "num")))
            #for pokemon in pokemon_evo:
                #pokemon_evo_id = (search_pokedex(pokemon.lower(), "num"))
                #min_level = search_pokedex(pokemon.lower(), "evoLevel")
                #if min_level == mainpokemon_level:
                    #showInfo(f"{mainpokemon_name} is about to evolve to {pokemon} at level {min_level}")
        except (IndexError, ValueError, TypeError) as e:
            showInfo(f"Error finding evolution details: {e}")
        window_title = (f"{pkmn_name.capitalize()} is evolving to {pokemon_evo.capitalize()} ?")
        # Display the Pokémon image
        pkmnimage_path = addon_dir / frontdefault / f"{pkmn_id}.png"
        #pkmnimage_path2 = addon_dir / frontdefault / f"{mainpokemon_prevo_id}.png"
        pkmnimage_path2 = addon_dir / frontdefault / f"{(pokemon_evo_id)}.png"
        #pkmnimage_label = QLabel()
        #pkmnimage_label2 = QLabel()
        pkmnpixmap = QPixmap()
        pkmnpixmap.load(str(pkmnimage_path))
        pkmnpixmap2 = QPixmap()
        pkmnpixmap2.load(str(pkmnimage_path2))
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(evolve_image_path))
        # Calculate the new dimensions to maintain the aspect ratio
        max_width = 200
        original_width = pkmnpixmap.width()
        original_height = pkmnpixmap.height()

        if original_width > max_width:
            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pkmnpixmap = pkmnpixmap.scaled(new_width, new_height)


        # Calculate the new dimensions to maintain the aspect ratio
        max_width = 200
        original_width = pkmnpixmap.width()
        original_height = pkmnpixmap.height()

        if original_width > max_width:
            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pkmnpixmap2 = pkmnpixmap2.scaled(new_width, new_height)

        # Merge the background image and the Pokémon image
        merged_pixmap = QPixmap(pixmap_bckg.size())
        merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        painter.drawPixmap(0,0,pixmap_bckg)
        painter.drawPixmap(255,70,pkmnpixmap)
        painter.drawPixmap(255,285,pkmnpixmap2)
        # Draw the text on top of the image
        font = QFont()
        font.setPointSize(12)  # Adjust the font size as needed
        painter.setFont(font)
        #fontlvl = QFont()
        #fontlvl.setPointSize(12)
        # Create a QPen object for the font color
        pen = QPen()
        pen.setColor(Qt.white)
        painter.setPen(pen)
        painter.drawText(150,35,f"{pkmn_name.capitalize()} is evolving to {pokemon_evo.capitalize()}")
        painter.drawText(95,430,"Please Choose to Evolve Your Pokemon or Cancel Evolution")
        # Capitalize the first letter of the Pokémon's name
        #name_label = QLabel(capitalized_name)
        painter.end()
        # Capitalize the first letter of the Pokémon's name

        # Create buttons for catching and killing the Pokémon
        evolve_button = QPushButton("Evolve Pokémon")
        dont_evolve_button = QPushButton("Cancel Evolution")
        qconnect(evolve_button.clicked, lambda: evolve_pokemon(pkmn_name))
        qconnect(dont_evolve_button.clicked, lambda: cancel_evolution(pkmn_name))

        # Set the merged image as the pixmap for the QLabel
        evo_image_label = QLabel()
        evo_image_label.setPixmap(merged_pixmap)

        return evo_image_label, evolve_button, dont_evolve_button

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

# Create an instance of the MainWindow
starter_window = StarterWindow()

evo_window = EvoWindow()
# Erstellen einer Klasse, die von QObject erbt und die eventFilter Methode überschreibt
class MyEventFilter(QObject):
    def eventFilter(self, obj, event):
        if obj is mw and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key.Key_M and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if test_window.isVisible():
                    test_window.close()  # Testfenster schließen, wenn Shift gedrückt wird
                else:
                    global first_start
                    if first_start == False:
                        test_window.display_first_start_up()
                    else:
                        test_window.open_dynamic_window()
        return False  # Andere Event-Handler nicht blockieren

# Erstellen und Installieren des Event Filters
event_filter = MyEventFilter()
mw.installEventFilter(event_filter)

class TableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Pokémon Type Effectiveness Table")
        global addon_dir

        # Create a label and set HTML content
        label = QLabel()
        html_content = self.read_html_file(f"{addon_dir}/eff_chart_html.html")  # Replace with the path to your HTML file
        label.setText(html_content)  # 'html_table' contains the HTML table string
        label.setWordWrap(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
    def read_html_file(self, file_path):
        """Reads an HTML file and returns its content as a string."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    def show_eff_chart(self):
        self.show()

class IDTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Pokémon - Generations and ID")
        global addon_dir

        # Create a label and set HTML content
        label = QLabel()
        html_content = self.read_html_file(f"{addon_dir}/table_gen_id.html")  # Replace with the path to your HTML file
        label.setText(html_content)  # 'html_table' contains the HTML table string
        label.setWordWrap(True)
        label.setStyleSheet("background-color: rgb(44,44,44);")
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

    def read_html_file(self, file_path):
        """Reads an HTML file and returns its content as a string."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def show_gen_chart(self):
        self.show()

if sprites_complete and database_complete!= False:
    if mypokemon_path.is_file() is False:
        starter_window.display_starter_pokemon()
    else:
        with open(mypokemon_path, 'r') as file:
            pokemon_list = json.load(file)
            if not pokemon_list :
                starter_window.display_starter_pokemon()

eff_chart = TableWidget()
gen_id_chart = IDTableWidget()

class License(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AnkiMon License")
        global addon_dir

        # Create a label and set HTML content
        label = QLabel()
        html_content = self.read_html_file(f"{addon_dir}/license.html")  # Replace with the path to your HTML file
        # Create a QScrollArea to enable scrolling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create a layout for the scroll area using QGridLayout
        scroll_layout = QGridLayout()

        # Create a widget to hold the layout
        container = QWidget()

        label.setText(html_content)  # 'html_table' contains the HTML table string
        label.setWordWrap(True)

        # Layout
        #layout = QVBoxLayout()
        scroll_layout.addWidget(label)
        # Set the widget for the scroll area
        scroll_area.setWidget(container)

        # Set the layout for the container
        container.setLayout(scroll_layout)

        # Set the widget for the scroll area
        scroll_area.setWidget(container)

        # Add the scroll area to the dialog
        window_layout = QVBoxLayout()
        window_layout.addWidget(scroll_area)
        self.setLayout(window_layout)
    def read_html_file(self, file_path):
        """Reads an HTML file and returns its content as a string."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    def show_window(self):
        self.show()

license = License()

class Credits(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AnkiMon License")
        global addon_dir

        # Create a label and set HTML content
        label = QLabel()
        html_content = self.read_html_file(f"{addon_dir}/credits.html")  # Replace with the path to your HTML file
        # Create a QScrollArea to enable scrolling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create a layout for the scroll area using QGridLayout
        scroll_layout = QGridLayout()

        # Create a widget to hold the layout
        container = QWidget()

        label.setText(html_content)  # 'html_table' contains the HTML table string
        label.setWordWrap(True)

        # Layout
        #layout = QVBoxLayout()
        scroll_layout.addWidget(label)
        # Set the widget for the scroll area
        scroll_area.setWidget(container)

        # Set the layout for the container
        container.setLayout(scroll_layout)

        # Set the widget for the scroll area
        scroll_area.setWidget(container)

        # Add the scroll area to the dialog
        window_layout = QVBoxLayout()
        window_layout.addWidget(scroll_area)
        self.setLayout(window_layout)
    def read_html_file(self, file_path):
        """Reads an HTML file and returns its content as a string."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    def show_window(self):
        self.show()

credits = Credits()

class ItemWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.read_item_file()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Itembag")
        global addon_dir
        self.layout = QGridLayout()
        self.setLayout(self.layout)

    def renewWidgets(self):
        # Clear the existing widgets from the layout
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        row, col = 0, 0
        max_items_per_row = 2
        max_rows = 4
        for item_name in self.itembag_list:
            if row >= max_rows:
                break
            item_widget = self.ItemLabel(item_name)
            self.layout.addWidget(item_widget, row, col)
            col += 1
            if col >= max_items_per_row:
                row += 1
                col = 0

    def ItemLabel(self, item_name):
        item_file_path = items_path / f"{item_name}.png"
        item_frame = QVBoxLayout() #itemframe
        item_name_label = QLabel(f"{item_name.capitalize()}") #itemname
        item_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_picture_pixmap = QPixmap(str(item_file_path))
        item_picture_label = QLabel()
        item_picture_label.setPixmap(item_picture_pixmap)
        item_picture_label.setStyleSheet("border: 2px solid #3498db; border-radius: 5px; padding: 5px;")
        item_frame.addWidget(item_picture_label)
        item_frame.addWidget(item_name_label)
        use_item_button = QPushButton("Use Item")
        comboBox = QComboBox()
        self.PokemonList(comboBox)
        use_item_button.clicked.connect(lambda: self.Check_Evo_Item(comboBox.currentText(), item_name))
        item_frame.addWidget(use_item_button)
        item_frame.addWidget(comboBox)
        item_frame_widget = QWidget()
        item_frame_widget.setLayout(item_frame)

        return item_frame_widget

    def PokemonList(self, comboBox):
        try:
            with open(mypokemon_path, "r") as json_file:
                captured_pokemon_data = json.load(json_file)
                if captured_pokemon_data:
                    for pokemon in captured_pokemon_data:
                        pokemon_name = pokemon['name']
                        comboBox.addItem(f"{pokemon_name}")
        except:
            pass

    def Check_Evo_Item(self, pkmn_name, item_name):
        try:
            evoName = search_pokedex(pkmn_name.lower(), "evos")
            evoName = f"{evoName[0]}"
            evoItem = search_pokedex(evoName.lower(), "evoItem")
            item_name = item_name.replace("-", " ")  # Remove hyphens from item_name
            evoItem = str(evoItem).lower()
            if evoItem == item_name:  # Corrected this line to assign the item_name to evoItem
                # Perform your action when the item matches the Pokémon's evolution item
                showInfo("Pokemon Evolution is fitting !")
                evo_window.display_pokemon_evo(pkmn_name)
            else:
                showInfo("This Pokemon does not need this item.")
        except Exception as e:
            showWarning(f"{e}")

    def read_item_file(self):
        # Read the list from the JSON file
        with open(itembag_path, 'r') as json_file:
            self.itembag_list = json.load(json_file)

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
        self.show()

item_window = ItemWindow()

class AttackDialog(QDialog):
    def __init__(self, attacks, new_attack):
        super().__init__()
        self.attacks = attacks
        self.new_attack = new_attack
        self.selected_attack = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"Select which Attack to Replace with {self.new_attack}")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Select which Attack to Replace with {self.new_attack}"))
        for attack in self.attacks:
            button = QPushButton(attack)
            button.clicked.connect(self.attackSelected)
            layout.addWidget(button)
        reject_button = QPushButton("Reject Attack")
        reject_button.clicked.connect(self.attackNoneSelected)
        layout.addWidget(reject_button)
        self.setLayout(layout)

    def attackSelected(self):
        sender = self.sender()
        self.selected_attack = sender.text()
        self.accept()

    def attackNoneSelected(self):
        sender = self.sender()
        self.selected_attack = sender.text()
        self.reject()

def report_bug():
    # Specify the URL of the Pokémon Showdown Team Builder
    bug_url = "https://forms.gle/7pJZNcRaUJx5WRybA"

    # Open the Team Builder in the default web browser
    QDesktopServices.openUrl(QUrl(bug_url))

#buttonlayout
mw.pokemenu = QMenu('&Ankimon', mw)
# and add it to the tools menu
mw.form.menubar.addMenu(mw.pokemenu)

if sprites_complete and database_complete != False:
    pokecol_action = QAction("Show Pokemon Collection", mw)
    # set it to call testFunction when it's clicked
    mw.pokemenu.addAction(pokecol_action)
    qconnect(pokecol_action.triggered, ShowPokemonCollection)
    # Make new PokeAnki menu under tools

    test_action10 = QAction("Open Ankimon Window", mw)
    test_action10.triggered.connect(test_window.open_dynamic_window)
    mw.pokemenu.addAction(test_action10)

    test_action15 = QAction("Itembag", mw)
    test_action15.triggered.connect(item_window.show_window)
    mw.pokemenu.addAction(test_action15)

    test_action8 = QAction("Open Pokemon Showdown Teambuilder", mw)
    qconnect(test_action8.triggered, open_team_builder)
    mw.pokemenu.addAction(test_action8)

    test_action6 = QAction("Export Main Pokemon to PkmnShowdown", mw)
    qconnect(test_action6.triggered, export_to_pkmn_showdown)
    mw.pokemenu.addAction(test_action6)

    test_action7 = QAction("Export All Pokemon to PkmnShowdown", mw)
    qconnect(test_action7.triggered, export_all_pkmn_showdown)
    mw.pokemenu.addAction(test_action7)

test_action11 = QAction("Check Effectiveness Chart", mw)
test_action11.triggered.connect(eff_chart.show_eff_chart)
mw.pokemenu.addAction(test_action11)

test_action12 = QAction("Check Generations and Pokemon Chart", mw)
test_action12.triggered.connect(gen_id_chart.show_gen_chart)
mw.pokemenu.addAction(test_action12)

test_action3 = QAction("Download Database Files", mw)
qconnect(test_action3.triggered, pokeapi_db_downloader)
mw.pokemenu.addAction(test_action3)
test_action4 = QAction("Download Sprite Files", mw)
qconnect(test_action4.triggered, show_agreement_and_downloadsprites)
mw.pokemenu.addAction(test_action4)
test_action4 = QAction("Download PokemonShowDownSprites", mw)
qconnect(test_action4.triggered, show_agreement_and_downloadspritespokeshowdown)
mw.pokemenu.addAction(test_action4)
itemspritesdow = QAction("Download Item Sprites", mw)
qconnect(itemspritesdow.triggered, show_agreement_and_download)
mw.pokemenu.addAction(itemspritesdow)

test_action14 = QAction("Credits", mw)
test_action14.triggered.connect(credits.show_window)
mw.pokemenu.addAction(test_action14)

test_action13 = QAction("About and License", mw)
test_action13.triggered.connect(license.show_window)
mw.pokemenu.addAction(test_action13)

test_action16 = QAction("Report Bug", mw)
test_action16.triggered.connect(report_bug)
mw.pokemenu.addAction(test_action16)

if sounds is True:
    def play_sound():
        sounds = [
            'Route 201 (Night)',
            'Route 203 (Day)',
            'Route 203 (Night)',
            'Route 205 (Day)',
            'Route 205 (Night)',
            'Route 206 (Day)',
            'Route 206 (Night)',
            'Route 209 (Day)',
            'Route 209 (Night)',
            'Route 210 (Night)',
            'Route 216 (Night)',
            'Route 225 (Day)',
            'Route 225 (Night)',
            'Route 228 (Day)',
            'Route 228 (Night)'
        ]
        file_name = random.choice(sounds)
        """Play a sound file using Anki's audio system."""
        audio_path = addon_dir / "sounds" / f"{file_name}.wav"
        if not Path(audio_path).is_file():
            showWarning(f"Audio file not found: {audio_path}")
            return

        audio_path = str(audio_path)

        if av_player:
            # Use Anki's newer audio player if available
            av_player.play_file(filename=audio_path)
        elif legacy_play:
            # Fallback to legacy play method
            legacy_play(audio_path)
        else:
            showWarning("No suitable audio player found in Anki.")

        # Estimate sound file duration and set timer
        with wave.open(audio_path, 'r') as file:
                frames = file.getnframes()
                rate = file.getframerate()
                duration = frames / float(rate)
                showInfo(f"{duration}")

        timer_interval = int(duration * 1000)  # Convert duration to milliseconds
        timer.start(timer_interval)  # Restart timer

    test_action14 = QAction("Play Sound", mw)
    test_action14.triggered.connect(play_sound)
    mw.pokemenu.addAction(test_action14)

    # Create a QTimer
    timer = QTimer()

    # Connect the timer's timeout signal to the play_sound function
    timer.timeout.connect(play_sound)

    #https://goo.gl/uhAxsg
    #https://www.reddit.com/r/PokemonROMhacks/comments/9xgl7j/pokemon_sound_effects_collection_over_3200_sfx/
    #https://archive.org/details/pokemon-dp-sound-library-disc-2_202205
