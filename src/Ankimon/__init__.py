# -*- coding: utf-8 -*-

# Ankimon
# Copyright (C) 2024 Unlucky-Life

# This program is free software: you can redistribute it and/or modify
# by the Free Software Foundation
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# Important - If you redistribute it and/or modify this addon - must give contribution in Title and Code
# aswell as ask for permission to modify / redistribute this addon or the code itself

import csv
import json
import os
import platform
import random
import math

from pathlib import Path

#from .install_dependencies import install_package
#install_package("PyQt6")
#from .test import * => added for testing

import aqt
import requests
import uuid
from anki.hooks import addHook, wrap
from aqt import gui_hooks, mw, utils
from aqt.qt import (QAction, QDialog, QFont, QGridLayout, QLabel, QPainter,
                    QPixmap, Qt, QVBoxLayout, QWidget, qconnect)
from aqt.reviewer import Reviewer
from aqt.utils import downArrow, showInfo, showWarning, tr, tooltip
from aqt.utils import *
from aqt.qt import *
from PyQt6 import *
from PyQt6.QtCore import QPoint, QTimer, QThread, QEvent, QObject, QUrl
from PyQt6.QtGui import QIcon, QColor, QPalette, QDesktopServices, QPen, QFontDatabase
from PyQt6.QtWidgets import (QApplication, QDialog, QLabel,
                             QPushButton, QVBoxLayout, QWidget, QMessageBox, QCheckBox, QTextEdit, QHBoxLayout, QComboBox, QLineEdit, QScrollArea, 
                             QFrame, QMenu, QLayout, QProgressBar)

from .resources import *
from .texts import _bottomHTML_template, button_style, \
                    attack_details_window_template, attack_details_window_template_end, \
                    remember_attack_details_window_template, remember_attack_details_window_template_end, \
                    rate_addon_text_label, inject_life_bar_css_1, inject_life_bar_css_2, \
                    thankyou_message_text, dont_show_this_button_text

from .const import gen_ids, status_colors_html, status_colors_label
from .business import get_image_as_base64, \
    split_string_by_length, split_japanese_string_by_length, capitalize_each_word, \
    resize_pixmap_img, type_colors, \
    calc_experience, get_multiplier_stats, get_multiplier_acc_eva, bP_none_moves, \
    calc_exp_gain, \
    read_csv_file, read_descriptions_csv
from .utils import check_folders_exist, check_file_exists, test_online_connectivity, \
    read_local_file, read_github_file, \
    compare_files, write_local_file, random_berries, \
    random_item, random_fossil, count_items_and_rewrite, filter_item_sprites, give_item

try:
    from .functions.pokedex_functions import *
    from .functions.badges_functions import *
    from .functions.battle_functions import *
    from .functions.pokemon_functions import *
    from .functions.create_gui_functions import *
    from .functions.create_css_for_reviewer import create_css_for_reviewer
    from .functions.reviewer_iframe import create_iframe_html, create_head_code
    from .functions.url_functions import *
    from .functions.gui_functions import type_icon_path, move_category_path
    from .gui_classes.pokemon_details import *
    from .functions.trainer_functions import xp_share_gain_exp
except ImportError as e:
    showWarning(f"Error in importing functions library {e}")

from .gui_entities import MovieSplashLabel, UpdateNotificationWindow, AgreementDialog, \
    Version_Dialog, License, Credits, HelpWindow, TableWidget, IDTableWidget, \
    Pokedex_Widget, CheckFiles

from .pyobj.ankimon_tracker import AnkimonTracker
from .pyobj.settings import Settings
from .pyobj.settings_window import SettingsWindow
from .pyobj.data_handler import DataHandler
from .pyobj.data_handler_window import DataHandlerWindow
from .pyobj.ankimon_tracker import AnkimonTracker
from .pyobj.ankimon_tracker_window import AnkimonTrackerWindow
from .pyobj.pokemon_obj import PokemonObject
from .pyobj.InfoLogger import ShowInfoLogger
from .pyobj.trainer_card import TrainerCard
from .pyobj.trainer_card_window import TrainerCardGUI
from .pyobj.ankimon_shop import PokemonShopManager
from .pokedex.pokedex_obj import Pokedex
from .pyobj.sync_pokemon_data import CheckPokemonData
from .pyobj.collection_dialog import PokemonCollectionDialog
from .pyobj.attack_dialog import AttackDialog
from .pyobj.reviewer_obj import Reviewer_Manager
from .pyobj.translator import Translator
from .pyobj.backup_files import run_backup
from .classes.choose_move_dialog import MoveSelectionDialog

class PokemonCollection:
    def __init__(self):
        self.collected_ids = set()
        self.loaded = False

    def add(self, pokemon_id):
        self.collected_ids.add(pokemon_id)

    def is_collected(self, pokemon_id):
        return pokemon_id in self.collected_ids

    def mark_loaded(self):
        self.loaded = True

    def is_loaded(self):
        return self.loaded

pokemon_collection_obj = PokemonCollection()

# start loggerobject for Ankimon
logger = ShowInfoLogger()

data_handler_obj = DataHandler()
data_handler_window = DataHandlerWindow(
    data_handler = data_handler_obj
)
# Create the Settings object
settings_obj = Settings()

# Pass the correct attributes to SettingsWindow
settings_window = SettingsWindow(
    config=settings_obj.config,                 # Use settings_obj.config instead of settings_obj.settings.config
    set_config_callback=settings_obj.set,
    save_config_callback=settings_obj.save_config,
    load_config_callback=settings_obj.load_config
)

#Init Translator
translator = Translator(language=int(settings_obj.get("misc.language", int(9))))

mw.settings_ankimon = settings_window
mw.logger = logger
mw.translator = translator
mw.settings_obj = settings_obj

# Log an startup message
logger.log_and_showinfo('game', translator.translate("startup"))
logger.log_and_showinfo('game', translator.translate("backing_up_files"))

#backup_files
try:
    run_backup()
except:
    logger.log("error", translator.translate("backup_error"))


# Initialize default values for the main Pokémon in a more compact form
default_pokemon_data = {
    "name": "Pikachu", "gender": "M", "level": 5, "id": 1, "ability": "Static", 
    "type": ["Electric"], "stats": {"hp": 20, "atk": 30, "def": 15, "spa": 50, "spd": 40, "spe": 60, "xp": 0}, 
    "ev": {"hp": 0, "atk": 1, "def": 0, "spa": 0, "spd": 0, "spe": 0}, "iv": {"hp": 15, "atk": 20, "def": 10, "spa": 10, "spd": 10, "spe": 10},
    "attacks": ["Thunderbolt", "Quick Attack"], "base_experience": 112, "current_hp": 20, "growth_rate": "medium", "evos": ["Pikachu"]
}

# Check if the main Pokémon file exists and is valid
if mainpokemon_path.is_file():
    with open(mainpokemon_path, "r", encoding="utf-8") as json_file:
        try:
            main_pokemon_data = json.load(json_file)
            mainpokemon_empty = not main_pokemon_data
            # Extract first Pokémon data if available
            main_pokemon = PokemonObject(**main_pokemon_data[0]) if main_pokemon_data else PokemonObject(**default_pokemon_data)
            main_pokemon.xp = main_pokemon.stats["xp"]
            if main_pokemon.current_hp > main_pokemon.max_hp:
                main_pokemon.current_hp = main_pokemon.max_hp
        except json.JSONDecodeError:
            main_pokemon = PokemonObject(**default_pokemon_data)
else:
    mainpokemon_empty = True
    # Initialize with default data if file is empty or invalid
    if mainpokemon_empty:
        main_pokemon = PokemonObject(**default_pokemon_data)

def update_main_pokemon(main_pokemon, mainpokemon_path = mainpokemon_path):
    # Check if the main Pokémon file exists and is valid
    if mainpokemon_path.is_file():
        with open(mainpokemon_path, "r", encoding="utf-8") as json_file:
            try:
                main_pokemon_data = json.load(json_file)
                # Use default values if the file is empty or invalid
                main_pokemon.update_stats(**main_pokemon_data[0])
                max_hp = main_pokemon.calculate_max_hp()
                main_pokemon.max_hp=max_hp
                if main_pokemon_data[0].get("current_hp", max_hp) > max_hp:
                    main_pokemon_data[0]["current_hp"] = max_hp
                main_pokemon.current_hp=main_pokemon_data[0].get("current_hp", max_hp)
                main_pokemon.hp=main_pokemon_data[0].get("current_hp", max_hp)
            except json.JSONDecodeError:
                main_pokemon.update_stats(**default_pokemon_data)
    else:
        # Initialize with default data if file is empty or invalid
        if mainpokemon_empty:
            for key, value in default_pokemon_data.items():
                main_pokemon.update_stats(key, value)
        
enemy_pokemon = PokemonObject(
    name="Rattata",             # Name of the Pokémon
    shiny=False,                # Shiny status (False for normal appearance)
    id=19,                      # ID number
    level=5,                    # Level
    ability="Run Away",         # Ability specific to Rattata
    type="Normal",              # Type (Normal type for Rattata)
    stats = {                     # Base stats for Rattata
      "hp": 39,
      "atk": 52,
      "def": 43,
      "spa": 60,
      "spd": 50,
      "spe": 65,
      "xp": 101
    },
    attacks=["Quick Attack", "Tackle", "Tail Whip"], # Typical moves for Rattata
    base_experience=58,          # Base experience points
    growth_rate="medium-slow",        # Growth rate
    hp=30,                       # Hit points (HP)
    ev={
      "hp": 3,
      "atk": 5,
      "def": 4,
      "spa": 1,
      "spd": 2,
      "spe": 3
    },  # EVs (Effort Values) for stats
    iv={
      "hp": 27,
      "atk": 24,
      "def": 3,
      "spa": 24,
      "spd": 16,
      "spe": 21
    }, # IVs (Individual Values) for stats
    gender="M",                   # Gender
    battle_status="Fighting",    # Status during battle
    xp=0,                         # XP (experience points)
    position=(5, 5)              # Position in battle
)

# Create a sample trainer card to test
trainer_card = TrainerCard(
    logger,
    main_pokemon,
    settings_obj,
    trainer_name=settings_obj.get("trainer.name", "Ash"),
    badge_count=8,
    trainer_id = ''.join(filter(str.isdigit, str(uuid.uuid4()).replace('-', ''))),
    xp=0,
    team="Pikachu (Level 25), Charizard (Level 50), Bulbasaur (Level 15)",
    league = 'Unranked',
)

ankimon_tracker_obj = AnkimonTracker(
    trainer_card=trainer_card,
    settings_obj=settings_obj,
)
# Set Pokémon in the tracker
ankimon_tracker_obj.set_main_pokemon(main_pokemon)
ankimon_tracker_obj.set_enemy_pokemon(enemy_pokemon)

# Initialize the Pokémon Shop Manager
shop_manager = PokemonShopManager(
    logger=logger,
    settings_obj=settings_obj,
    set_callback=settings_obj.set,
    get_callback=settings_obj.get
)

ankimon_tracker_window = AnkimonTrackerWindow(
    tracker = ankimon_tracker_obj
)

# Initialize collected IDs cache
def load_collected_pokemon_ids():
    if pokemon_collection_obj.loaded:
        return  # Already loaded, do nothing
    if mypokemon_path.is_file():
        try:
            with open(mypokemon_path, "r", encoding="utf-8") as f:
                collection = json.load(f)
                pokemon_collection_obj.collected_pokemon_ids = {pkmn["id"] for pkmn in collection}
            pokemon_collection_obj.loaded = True
        except Exception as e:
            logger.log("error", f"Error loading collection cache: {str(e)}")
            pokemon_collection_obj.collected_pokemon_ids = set()
            pokemon_collection_obj.loaded = True  # Prevent repeated attempts if file is bad

# Call this during addon initialization
load_collected_pokemon_ids()

pokedex_window = Pokedex(addon_dir, ankimon_tracker = ankimon_tracker_obj)

#from .download_pokeapi_db import create_pokeapidb
config = mw.addonManager.getConfig(__name__)
#show config .json file

items_list = []
with open(items_list_path, "r", encoding="utf-8") as file:
    items_list = json.load(file)

with open(sound_list_path, "r", encoding="utf-8") as json_file:
    sound_list = json.load(json_file)

ankimon_tracker_obj.pokemon_encouter = 0

"""
get web exports ready for special reviewer look
"""
from aqt.gui_hooks import webview_will_set_content
from aqt.webview import WebContent

# Set up web exports for static files
mw.addonManager.setWebExports(__name__, r"user_files/.*\.(css|js|jpg|gif|html|ttf|png|mp3)")

def on_webview_will_set_content(web_content: WebContent, context) -> None:
    ankimon_package = mw.addonManager.addonFromModule(__name__)
    general_url = f"""/_addons/{ankimon_package}/user_files/web/"""
    head_code = create_head_code(general_url)
    web_content.head += f"<style>{head_code}</style>"
    #add function to reviewer to toggle iframe
    web_content.js.append(f"/_addons/{ankimon_package}/user_files/web/transparent.js")
    web_content.css.append(f"/_addons/{ankimon_package}/user_files/web/styles.css")

def prepare(html, content, context):
    if int(settings_obj.get("gui.show_mainpkmn_in_reviewer", 1)) == 3:
        html_code = create_iframe_html(main_pokemon, enemy_pokemon, settings_obj, textmsg="")
    else:
        html_code = ""
    return html + html_code

webview_will_set_content.append(on_webview_will_set_content)

# check for sprites, data
sound_files = check_folders_exist(pkmnimgfolder, "sounds")
back_sprites = check_folders_exist(pkmnimgfolder, "back_default")
back_default_gif = check_folders_exist(pkmnimgfolder, "back_default_gif")
front_sprites = check_folders_exist(pkmnimgfolder, "front_default")
front_default_gif = check_folders_exist(pkmnimgfolder, "front_default_gif")
item_sprites = check_folders_exist(pkmnimgfolder, "items")
badges_sprites = check_folders_exist(pkmnimgfolder, "badges")

database_complete = all([
        back_sprites, front_sprites, front_default_gif, back_default_gif, item_sprites, badges_sprites
])

if not database_complete:
    dialog = CheckFiles()
    dialog.show()

if mainpokemon_path.is_file():
    with open(mainpokemon_path, "r", encoding="utf-8") as json_file:
        main_pokemon_data = json.load(json_file)
        if not main_pokemon_data or main_pokemon_data is None:
            mainpokemon_empty = True
        else:
            mainpokemon_empty = False

window = None
gender = None

from .config_var import *

check_data = CheckPokemonData(settings_obj, logger)

#If reviewer showed question; start card_timer for answering card
def on_show_question(Card):
    """
    This function is called when a question is shown.
    You can access and manipulate the card object here.
    """
    ankimon_tracker_obj.start_card_timer()  # This line should have 4 spaces of indentation

def on_show_answer(Card):
    """
    This function is called when a question is shown.
    You can access and manipulate the card object here.
    """
    ankimon_tracker_obj.stop_card_timer()  # This line should have 4 spaces of indentation

gui_hooks.reviewer_did_show_question.append(on_show_question)
gui_hooks.reviewer_did_show_answer.append(on_show_answer)

from .hooks import setupHooks

setupHooks(check_data , ankimon_tracker_obj, prepare)

online_connectivity = test_online_connectivity()

#Connect to GitHub and Check for Notification and HelpGuideChanges
try:           
    if online_connectivity and ssh != False:
        # URL of the file on GitHub
        github_url = "https://raw.githubusercontent.com/Unlucky-Life/ankimon/main/update_txt.md"
        # Path to the local file
        local_file_path = addon_dir / "updateinfos.md"
        # Read content from GitHub
        github_content, github_html_content = read_github_file(github_url)
        # Read content from the local file
        local_content = read_local_file(local_file_path)
        # If local content exists and is the same as GitHub content, do not open dialog
        if local_content is not None and compare_files(local_content, github_content):
            pass
        else:
            # Download new content from GitHub
            if github_content is not None:
                # Write new content to the local file
                write_local_file(local_file_path, github_content)
                dialog = UpdateNotificationWindow(github_html_content)
                if no_more_news is False:
                    dialog.exec()
            else:
                showWarning("Failed to retrieve Ankimon content from GitHub.")
except Exception as e:
    if ssh != False:
        logger.log_and_showinfo("info",f"Error in try connect to GitHub: {e}")

def open_help_window(online_connectivity):
    try:
        # TODO: online_connectivity must be a function?
        # TODO: HelpWindow constructor must be empty?
        help_dialog = HelpWindow(online_connectivity)
        help_dialog.exec()
    except:
        showWarning("Error in opening HelpGuide")
        
try:
    from anki.sound import SoundOrVideoTag
    from aqt.sound import av_player
    legacy_play = None
    from . import audios
except (ImportError, ModuleNotFoundError):
    showWarning("Sound import error occured.")
    from anki.sound import play as legacy_play
    av_player = None


def play_effect_sound(sound_type):
    sound_effects = settings_obj.get("audio.sound_effects", False)
    if sound_effects is True:
        audio_path = None
        if sound_type == "HurtNotEffective":
            audio_path = hurt_noteff_sound_path
        elif sound_type == "HurtNormal":
            audio_path = hurt_normal_sound_path
        elif sound_type == "HurtSuper":
            audio_path = hurt_supereff_sound_path
        elif sound_type == "OwnHpLow":
            audio_path = ownhplow_sound_path
        elif sound_type == "HpHeal":
            audio_path = hpheal_sound_path
        elif sound_type == "Fainted":
            audio_path = fainted_sound_path

        if not audio_path.is_file():
            return
        else:   
            audio_path = Path(audio_path)
            #threading.Thread(target=playsound.playsound, args=(audio_path,)).start()
            audios.will_use_audio_player()
            audios.audio(audio_path)
    else:
        pass

def play_sound():
    if settings_obj.get("audio.sounds", False) is True:
        file_name = f"{enemy_pokemon.id}.ogg"
        audio_path = addon_dir / "user_files" / "sprites" / "sounds" / file_name
        if audio_path.is_file():
            audio_path = Path(audio_path)
            audios.will_use_audio_player()
            audios.audio(audio_path)


gen_config = []
for i in range(1,10):
    gen_config.append(config[f"misc.gen{i}"])

def check_id_ok(id_num):
    if isinstance(id_num, int):
        pass
    elif isinstance(id_num, list):
        if len(id_num) > 0:
            id_num = id_num[0]
        else:
            return False
    # Determine the generation of the given ID
    if id_num < 898:
        generation = 0
        for gen, max_id in gen_ids.items():
            if id_num <= max_id:
                generation = int(gen.split('_')[1])
                break

        if generation == 0:
            return False  # ID does not belong to any generation

        return gen_config[generation - 1]
    else:
        return False

def special_pokemon_names_for_pokedex_to_poke_api_db(name):
    global pokedex_to_poke_api_db
    return pokedex_to_poke_api_db.get(name, name)

def answerCard_before(filter, reviewer, card):
	utils.answBtnAmt = reviewer.mw.col.sched.answerButtons(card)
	return filter

# Globale Variable für die Zählung der Bewertungen

def answerCard_after(rev, card, ease):
    maxEase = rev.mw.col.sched.answerButtons(card)
    aw = aqt.mw.app.activeWindow() or aqt.mw
    # Aktualisieren Sie die Zählung basierend auf der Bewertung
    if ease == 1:
        ankimon_tracker_obj.review("again")
    elif ease == maxEase - 2:
        ankimon_tracker_obj.review("hard")
    elif ease == maxEase - 1:
        ankimon_tracker_obj.review("good")
    elif ease == maxEase:
        ankimon_tracker_obj.review("easy")
    else:
        # default behavior for unforeseen cases
        tooltip("Error in ColorConfirmation: Couldn't interpret ease")
    ankimon_tracker_obj.reset_card_timer()


aqt.gui_hooks.reviewer_will_answer_card.append(answerCard_before)
aqt.gui_hooks.reviewer_did_answer_card.append(answerCard_after)


if database_complete:
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
        # Load the JSON file
        with open(learnset_path, "r", encoding="utf-8") as file:
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

if database_complete:
    def get_levelup_move_for_pokemon(pokemon_name, level):
        """
        Get a random move learned by a Pokémon at a specific level and lower, excluding moves that can be learned at a higher level.

        Args:
            pokemon_name (str): The name of the Pokémon.
            level (int): The level at which to check for moves.

        Returns:
            str: A random move and its highest level.
        """
        # Load the JSON file
        with open(learnset_path, "r", encoding="utf-8") as file:
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
            return eligible_moves

caught_pokemon = {} #pokemon not caught

def check_min_generate_level(name):
    evoType = search_pokedex(name.lower(), "evoType")
    evoLevel = search_pokedex(name.lower(), "evoLevel")
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

def customCloseTooltip(tooltipLabel):
	if tooltipLabel:
		try:
			tooltipLabel.deleteLater()
		except:
			# already deleted as parent window closed
			pass
		tooltipLabel = None

def tooltipWithColour(msg, color, x=0, y=20, xref=1, parent=None, width=0, height=0, centered=False):
    period = int(settings_obj.get("gui.reviewer_text_message_box_time", 3) * 1000) #time for pop up message
    class CustomLabel(QLabel):
        def mousePressEvent(self, evt):
            evt.accept()
            self.hide()
    aw = parent or QApplication.activeWindow()
    if aw is None:
        return
    
    if color == "#6A4DAC":
        y_offset = 40
    elif color == "#F7DC6F":
        y_offset = -40
    elif color == "#F0B27A":
        y_offset = -40
    elif color == "#D2B4DE":
        y_offset = -40
    else:
        y_offset = 0

    if reviewer_text_message_box != False:
        x = aw.mapToGlobal(QPoint(x + round(aw.width() / 2), 0)).x()
        y = aw.mapToGlobal(QPoint(0, aw.height() - (180 + y_offset))).y()
        lab = CustomLabel(aw)
        lab.setFrameShape(QFrame.Shape.StyledPanel)
        lab.setLineWidth(2)
        lab.setWindowFlags(Qt.WindowType.ToolTip)
        lab.setText(msg)
        lab.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)
        
        if width > 0:
            lab.setFixedWidth(width)
        if height > 0:
            lab.setFixedHeight(height)
        
        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(color))
        p.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
        lab.setPalette(p)
        lab.show()
        lab.move(QPoint(x - round(lab.width() * 0.5 * xref), y))    
        try:
            QTimer.singleShot(period, lambda: lab.hide())
        except:
            QTimer.singleShot(3000, lambda: lab.hide())
        logger.log_and_showinfo("game", msg)

# Your random Pokémon generation function using the PokeAPI
if database_complete:
    def generate_random_pokemon():
        # Fetch random Pokémon data from Generation
        # Load the JSON file with Pokémon data
        ankimon_tracker_obj.pokemon_encounter = 0
        ankimon_tracker_obj.cards_battle_round = 0
        tier = "Normal"
        #generation_file = ("pokeapi_db.json")
        try:
            id, tier = choose_random_pkmn_from_tier()
            #test_ids = [719]
            #id = random.choice(test_ids)
            name = search_pokedex_by_id(id)
            gender = "N"
            shiny = shiny_chance()
            if name is list:
                name = name[0]
            try:
                min_level = int(check_min_generate_level(str(name.lower())))
            except:
                generate_random_pokemon()
            var_level = 3
            if main_pokemon.level or main_pokemon.level != None:
                try:
                    level = random.randint((main_pokemon.level - (random.randint(0, var_level))), (main_pokemon.level + (random.randint(0, var_level))))  # Random level between 1 and 100
                    if main_pokemon.level == 100:
                        level = 100
                    if level < 0:
                        level = 1
                except Exception as e:
                    showWarning(f"Error in generate random pokemon{e}")
                    main_pokemon.level = 5
                    level = 5
            else:
                level = 5
                min_level = 0
            if min_level is None or not min_level or main_pokemon.level is None or not main_pokemon.level:
                level = 5
                min_level = 0
            if min_level < level:
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
                    ability = translator.translate("no_ability")
                # Check if there are numeric abilities
                if numeric_abilities:
                    # Convert the filtered abilities dictionary values to a list
                    abilities_list = list(numeric_abilities.values())
                    # Select a random ability from the list
                    ability = random.choice(abilities_list)
                else:
                    # Set to "No Ability" if there are no numeric abilities
                    ability = translator.translate("no_ability")
                # ability = abilities.get("0", "No ability")
                # if ability == "No ability":
                #    ability = abilities.get("H", None)
                type = search_pokedex(name, "types")
                stats = search_pokedex(name, "baseStats")
                enemy_attacks_list = get_all_pokemon_moves(name, level)
                enemy_attacks = []
                if len(enemy_attacks_list) <= 4:
                    enemy_attacks = enemy_attacks_list
                else:
                    enemy_attacks = random.sample(enemy_attacks_list, 4)
                base_experience = search_pokeapi_db_by_id(id, "base_experience")
                growth_rate = search_pokeapi_db_by_id(id, "growth_rate")
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
                battle_stats = stats
                battle_status = "fighting"
                ev_yield = search_pokeapi_db_by_id(id, "effort_values")
                return name, id, level, ability, type, stats, enemy_attacks, base_experience, growth_rate, ev, iv, gender, battle_status, battle_stats, tier, ev_yield, shiny
            else:
                return generate_random_pokemon()  # Return the result of the recursive call
        except FileNotFoundError:
            logger.log_and_showinfo("info","Error - Can't open the JSON File.")
            # Set the layout for the dialog

def kill_pokemon():
    try:
        trainer_card.gain_xp(enemy_pokemon.tier, settings_obj.get("controls.allow_to_choose_moves", False))
        
        # Calculate experience based on whether moves are chosen manually
        if settings_obj.get("controls.allow_to_choose_moves", False):
            exp = calc_experience(main_pokemon.base_experience, enemy_pokemon.level) * 0.5
        else:
            exp = calc_experience(main_pokemon.base_experience, enemy_pokemon.level)
        
        # Ensure exp is at least 1 and round up if it's a decimal
        if exp < 1:
            exp = 1
        elif isinstance(exp, float) and not exp.is_integer():
            exp = math.ceil(exp)
        
        # Handle XP share logic
        xp_share_individual_id = settings_obj.get("trainer.xp_share", None)
        if xp_share_individual_id:
            exp = xp_share_gain_exp(logger, settings_obj, evo_window, main_pokemon.id, exp, xp_share_individual_id)
        
        # Save main Pokémon's progress
        main_pokemon.level = save_main_pokemon_progress(
            mainpokemon_path,
            main_pokemon.level,
            main_pokemon.name,
            main_pokemon.base_experience,
            main_pokemon.growth_rate,
            exp
        )
        
        ankimon_tracker_obj.general_card_count_for_battle = 0
        
        # Show a new random Pokémon if the test window is visible
        if test_window.isVisible():
            new_pokemon()
    except Exception as e:
        showWarning(f"Error occured in killing enemy pokemon: {e}")


def display_dead_pokemon():
    level = enemy_pokemon.level
    id = enemy_pokemon.id

    # Create the dialog
    w_dead_pokemon = QDialog(mw)
    w_dead_pokemon.setWindowTitle(translator.translate("enemy_pokemon_defeat_text", enemy_pokemon_name={enemy_pokemon.name}))
    # Create a layout for the dialog
    layout2 = QVBoxLayout()
    # Display the Pokémon image
    pkmnimage_file = f"{id}.png"
    pkmnimage_path = frontdefault / pkmnimage_file
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
    capitalized_name = enemy_pokemon.name.capitalize()
    # Create level text

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
    level_label = QLabel(f" {translator.translate('level')}: {level}")
    # Align to the center
    level_label.setFont(fontlvl)

    # Create buttons for catching and killing the Pokémon
    catch_button = QPushButton(translator.translate("catch_button"))
    kill_button = QPushButton(translator.translate("defeat_button"))
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
    pkmnimage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align to the center

    # Set the layout for the dialog
    w_dead_pokemon.setLayout(layout2)

    if w_dead_pokemon is not None:
        # Close the existing dialog if it's open
        w_dead_pokemon.accept()
    # Show the dialog
    result = w_dead_pokemon.exec()
    # Check the result to determine if the user closed the dialog
    if result == QDialog.Rejected:
        w_dead_pokemon = None  # Reset the global window reference

def modify_percentages(total_reviews, daily_average, player_level):
    """
    Modify Pokémon encounter percentages based on total reviews, player level, event modifiers, and main Pokémon level.
    """
    # Start with the base percentages
    percentages = {"Baby": 2, "Legendary": 0.5, "Mythical": 0.2, "Normal": 92.3, "Ultra": 5}

    # Adjust percentages based on total reviews relative to the daily average
    review_ratio = total_reviews / daily_average if daily_average > 0 else 0

    # Adjust for review progress
    if review_ratio < 0.4:
        percentages["Normal"] += percentages.pop("Baby", 0) + percentages.pop("Legendary", 0) + \
                                 percentages.pop("Mythical", 0) + percentages.pop("Ultra", 0)
    elif review_ratio < 0.6:
        percentages["Baby"] += 2
        percentages["Normal"] -= 2
    elif review_ratio < 0.8:
        percentages["Ultra"] += 3
        percentages["Normal"] -= 3
    else:
        percentages["Legendary"] += 2
        percentages["Ultra"] += 3
        percentages["Normal"] -= 5

    # Restrict access to certain tiers based on main Pokémon level
    if main_pokemon.level:
        # Define level thresholds for each tier
        level_thresholds = {
            "Ultra": 30,  # Example threshold for Ultra Pokémon
            "Legendary": 50,  # Example threshold for Legendary Pokémon
            "Mythical": 75  # Example threshold for Mythical Pokémon
        }

        for tier in ["Ultra", "Legendary", "Mythical"]:
            if main_pokemon.level < level_thresholds.get(tier, float("inf")):
                percentages[tier] = 0  # Set percentage to 0 if the level requirement isn't met

    # Example modification based on player level
    if player_level:
        adjustment = 5  # Adjustment value for the example
        if player_level > 10:
            for tier in percentages:
                if tier == "Normal":
                    percentages[tier] = max(percentages[tier] - adjustment, 0)
                else:
                    percentages[tier] = percentages.get(tier, 0) + adjustment
                    
    # Normalize percentages to ensure they sum to 100
    total = sum(percentages.values())
    for tier in percentages:
        percentages[tier] = (percentages[tier] / total) * 100 if total > 0 else 0

    return percentages

def get_tier(total_reviews, player_level=1, event_modifier=None):
    daily_average = settings_obj.get('daily_average', 100)
    percentages = modify_percentages(total_reviews, daily_average, player_level)
    
    tiers = list(percentages.keys())
    probabilities = list(percentages.values())
    
    choice = random.choices(tiers, probabilities, k=1)
    return choice[0]

def choose_random_pkmn_from_tier():
    total_reviews = ankimon_tracker_obj.total_reviews
    trainer_level = trainer_card.level
    try:
        tier = get_tier(total_reviews, trainer_level)
        id = get_pokemon_id_by_tier(tier)
        return id, tier
    except Exception as e:
        showWarning(translator.translate("error_occured", error="choose_random_pkmn_from_tier"))

def get_pokemon_id_by_tier(tier):
    id_species_path = None
    if tier == "Normal":
        id_species_path = pokemon_species_normal_path
    elif tier == "Baby":
        id_species_path = pokemon_species_baby_path
    elif tier == "Ultra":
        id_species_path = pokemon_species_ultra_path
    elif tier == "Legendary":
        id_species_path = pokemon_species_legendary_path
    elif tier == "Mythical":
        id_species_path = pokemon_species_mythical_path

    with open(id_species_path, "r", encoding="utf-8") as file:
        id_data = json.load(file)

    # Select a random Pokemon ID from those in the tier
    random_pokemon_id = random.choice(id_data)
    return random_pokemon_id

def save_caught_pokemon(nickname):
    # Create a dictionary to store the Pokémon's data
    # add all new values like hp as max_hp, evolution_data, description and growth rate
    global achievements
    if enemy_pokemon.tier != None:
        if enemy_pokemon.tier == "Normal":
            check = check_for_badge(achievements,17)
            if check is False:
                achievements = receive_badge(17,achievements)
                test_window.display_badge(17)
        elif enemy_pokemon.tier == "Baby":
            check = check_for_badge(achievements,18)
            if check is False:
                achievements = receive_badge(18,achievements)
                test_window.display_badge(18)
        elif enemy_pokemon.tier == "Ultra":
            check = check_for_badge(achievements,8)
            if check is False:
                achievements = receive_badge(8,achievements)
                test_window.display_badge(8)
        elif enemy_pokemon.tier == "Legendary":
            check = check_for_badge(achievements,9)
            if check is False:
                achievements = receive_badge(9,achievements)
                test_window.display_badge(9)
        elif enemy_pokemon.tier == "Mythical":
            check = check_for_badge(achievements,10)
            if check is False:
                achievements = receive_badge(10,achievements)
                test_window.display_badge(10)

    caught_pokemon = create_caught_pokemon(enemy_pokemon, nickname)
    # Load existing Pokémon data if it exists
    if mypokemon_path.is_file():
        with open(mypokemon_path, "r", encoding="utf-8") as json_file:
            caught_pokemon_data = json.load(json_file)
    else:
        caught_pokemon_data = []

    # Append the caught Pokémon's data to the list
    caught_pokemon_data.append(caught_pokemon)

    # Save the caught Pokémon's data to a JSON file
    with open(str(mypokemon_path), "w") as json_file:
        json.dump(caught_pokemon_data, json_file, indent=2)

def save_main_pokemon_progress(mainpokemon_path, mainpokemon_level, mainpokemon_name, mainpokemon_base_experience, mainpokemon_growth_rate, exp):    
    ev_yield = enemy_pokemon.ev_yield
    experience = int(find_experience_for_level(main_pokemon.growth_rate, main_pokemon.level, settings_obj.get("misc.remove_level_cap", False)))
    if remove_levelcap is True:
        main_pokemon.xp += exp
        level_cap = None
    elif mainpokemon_level != 100:
            main_pokemon.xp += exp
            level_cap = 100
    if mainpokemon_path.is_file():
        with open(mainpokemon_path, "r", encoding="utf-8") as json_file:
            main_pokemon_data = json.load(json_file)
    else:
        showWarning(translator.translate("missing_mainpokemon_data"))
    while int(find_experience_for_level(main_pokemon.growth_rate, main_pokemon.level, settings_obj.get("misc.remove_level_cap", False))) < int(main_pokemon.xp) and (level_cap is None or main_pokemon.level < level_cap):
        main_pokemon.level += 1
        msg = ""
        msg += f"Your {main_pokemon.name} is now level {main_pokemon.level} !"
        color = "#6A4DAC" #pokemon leveling info color for tooltip
        global achievements
        check = check_for_badge(achievements,5)
        if check is False:
            achievements = receive_badge(5,achievements)
            test_window.display_badge(5)
        try:
            tooltipWithColour(msg, color)
        except:
            pass
        if settings_obj.get('gui.pop_up_dialog_message_on_defeat', True) is True:
            logger.log_and_showinfo("info",f"{msg}")
        main_pokemon.xp = int(max(0, int(main_pokemon.xp) - int(experience)))
        evo_id = check_evolution_for_pokemon(main_pokemon.individual_id, main_pokemon.id, main_pokemon.level, evo_window, main_pokemon.everstone)
        if evo_id is not None:
            msg += translator.translate("pokemon_about_to_evolve", main_pokemon_name=main_pokemon.name, evo_pokemon_name=return_name_for_id(evo_id).capitalize(), main_pokemon_level=main_pokemon.level)
            logger.log_and_showinfo("info",f"{msg}")
            color = "#6A4DAC"
            try:
                tooltipWithColour(msg, color)
            except:
                pass
                    #evo_window.display_pokemon_evo(main_pokemon.name.lower())
        for mainpkmndata in main_pokemon_data:
            if mainpkmndata["name"] == main_pokemon.name.capitalize():
                attacks = mainpkmndata["attacks"]
                new_attacks = get_levelup_move_for_pokemon(main_pokemon.name.lower(),int(main_pokemon.level))
                if new_attacks:
                    msg = ""
                    msg += translator.translate("mainpokemon_can_learn_new_attack", main_pokemon_name=main_pokemon.name.capitalize())
                for new_attack in new_attacks:
                    if len(attacks) < 4 and new_attack not in attacks:
                        attacks.append(new_attack)
                        msg += translator.translate("mainpokemon_learned_new_attack", new_attack_name=new_attack, main_pokemon_name=main_pokemon.name.capitalize())
                        color = "#6A4DAC"
                        tooltipWithColour(msg, color)
                        if settings_obj.get('gui.pop_up_dialog_message_on_defeat', True) is True:
                            logger.log_and_showinfo("info",f"{msg}")
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
                                logger.log_and_showinfo("info",
                                    f"Replaced '{selected_attack}' with '{new_attack}'")
                            else:
                                logger.log_and_showinfo("info",f"'{selected_attack}' not found in the list")
                        else:
                            # Handle the case where the user cancels the dialog
                            logger.log_and_showinfo("info",f"{new_attack} will be discarded.")
                mainpkmndata["attacks"] = attacks
                break
    msg = ""
    msg += translator.translate("mainpokemon_gained_xp", main_pokemon_name=main_pokemon.name, exp=exp, experience_till_next_level=experience, main_pokemon_xp=main_pokemon.xp)
    color = "#6A4DAC" #pokemon leveling info color for tooltip
    try:
        tooltipWithColour(msg, color)
    except:
        pass
    if settings_obj.get('gui.pop_up_dialog_message_on_defeat', True) is True:
        logger.log_and_showinfo("info",f"{msg}")
    # Load existing Pokémon data if it exists

    for mainpkmndata in main_pokemon_data:
        mainpkmndata["stats"]["xp"] = int(main_pokemon.xp)
        mainpkmndata["level"] = int(main_pokemon.level)
        mainpkmndata["ev"]["hp"] += ev_yield["hp"]
        mainpkmndata["ev"]["atk"] += ev_yield["attack"]
        mainpkmndata["ev"]["def"] += ev_yield["defense"]
        mainpkmndata["ev"]["spa"] += ev_yield["special-attack"]
        mainpkmndata["ev"]["spd"] += ev_yield["special-defense"]
        mainpkmndata["ev"]["spe"] += ev_yield["speed"]
        mainpkmndata["current_hp"] = int(main_pokemon.hp)
        main_pokemon.friendship += random.randint(5, 9)
        if main_pokemon.friendship > 255:
            main_pokemon.friendship = 255
        mainpkmndata["friendship"] = main_pokemon.friendship 
        mainpkmndata["pokemon_defeated"] += 1
    mypkmndata = mainpkmndata
    mainpkmndata = [mainpkmndata]
    # Save the caught Pokémon's data to a JSON file
    with open(str(mainpokemon_path), "w") as json_file:
        json.dump(mainpkmndata, json_file, indent=2)

    # Load data from the output JSON file
    with open(str(mypokemon_path), "r", encoding="utf-8") as output_file:
        mypokemondata = json.load(output_file)

        # Find and replace the specified Pokémon's data in mypokemondata
        for index, pokemon_data in enumerate(mypokemondata):
            if pokemon_data.get("individual_id") == main_pokemon.individual_id:  # Match by individual_id
                mypokemondata[index] = mypkmndata  # Replace with new data
                break

        # Save the modified data to the output JSON file
        with open(str(mypokemon_path), "w") as output_file:
            json.dump(mypokemondata, output_file, indent=2)

    return main_pokemon.level

def evolve_pokemon(individual_id, prevo_name, evo_id, evo_name):
    global achievements
    try:
        with open(mypokemon_path, "r", encoding="utf-8") as json_file:
            captured_pokemon_data = json.load(json_file)
            pokemon = None
            if captured_pokemon_data:
                for pokemon_data in captured_pokemon_data:
                    if pokemon_data['individual_id'] == individual_id:
                        pokemon = pokemon_data
                        if pokemon is not None:
                            prevo_id = pokemon["id"]
                            pokemon["name"] = evo_name.capitalize()
                            pokemon["id"] = evo_id
                            pokemon["type"] = search_pokedex(evo_name.lower(), "types")
                            pokemon["evos"] = []
                            attacks = pokemon["attacks"]
                            new_attacks = get_random_moves_for_pokemon(evo_name.lower(), int(pokemon["level"]))
                            for new_attack in new_attacks:
                                if new_attack not in new_attacks:
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
                                                logger.log_and_showinfo("info",translator.translate("replaced_selected_attack", selected_attack=selected_attack, new_attack=new_attack))
                                            else:
                                                logger.log_and_showinfo("info",translator.translate("selected_attack_not_found", selected_attack=selected_attack))
                                        else:
                                            # Handle the case where the user cancels the dialog
                                            logger.log_and_showinfo("info",translator.translate("no_attack_selected"))
                            pokemon["attacks"] = attacks
                            stats = search_pokedex(evo_name.lower(), "baseStats")
                            pokemon["stats"] = stats
                            pokemon["stats"]["xp"] = 0
                            hp_stat = int(stats['hp'])
                            hp = calculate_hp(hp_stat, level, ev, iv)
                            pokemon["current_hp"] = int(hp)
                            pokemon["growth_rate"] = search_pokeapi_db_by_id(evo_id,"growth_rate")
                            pokemon["base_experience"] = search_pokeapi_db_by_id(evo_id,"base_experience")
                            abilities = search_pokedex(evo_name.lower(), "abilities")
                            numeric_abilities = None
                            try:
                                numeric_abilities = {k: v for k, v in abilities.items() if k.isdigit()}
                            except:
                                ability = translator.translate("no_ability")
                            if numeric_abilities:
                                abilities_list = list(numeric_abilities.values())
                                pokemon["ability"] = random.choice(abilities_list)
                            else:
                                pokemon["ability"] = translator.translate("no_ability")
                            with open(str(mypokemon_path), "r", encoding="utf-8") as output_file:
                                mypokemondata = json.load(output_file)
                                # Find and replace the specified Pokémon's data in mypokemondata
                                for index, pokemon_data in enumerate(mypokemondata):
                                    if pokemon_data["individual_id"] == individual_id:
                                        mypokemondata[index] = pokemon
                                        break
                                        # Save the modified data to the output JSON file
                                with open(str(mypokemon_path), "w") as output_file:
                                    json.dump(mypokemondata, output_file, indent=2)
                            with open(str(mainpokemon_path), "r", encoding="utf-8") as output_file:
                                mainpokemon_data = json.load(output_file)
                                # Find and replace the specified Pokémon's data in mypokemondata
                                for index, pokemon_data in enumerate(mainpokemon_data):
                                    if pokemon_data["individual_id"] == individual_id:
                                        mypokemondata[index] = pokemon
                                        break
                                    else:
                                        pass
                                            # Save the modified data to the output JSON file
                                with open(str(mainpokemon_path), "w") as output_file:
                                        pokemon = [pokemon]
                                        json.dump(pokemon, output_file, indent=2)
                            logger.log_and_showinfo("info",translator.translate("mainpokemon_has_evolved", prevo_name=prevo_name, evo_name=evo_name))
    except Exception as e:
        showWarning(f"{e}")
    try:#Update Main Pokemon Object
        if main_pokemon.individual_id == individual_id:
            update_main_pokemon(main_pokemon)
            class Container(object):
                pass
            reviewer = Container()
            reviewer.web = mw.reviewer.web
            reviewer_obj.update_life_bar(reviewer, 0, 0)
            if test_window.isVisible() is True:
                test_window.display_first_encounter()
    except Exception as e:
        showWarning(f"Error occured in updating main_pokemon obj. {e}")
    evo_window.display_evo_pokemon(prevo_id, evo_id)
    check = check_for_badge(achievements,16)
    if check is False:
        receive_badge(16,achievements)
        test_window.display_badge(16)

def cancel_evolution(individual_id, prevo_name):
    ev_yield = enemy_pokemon.ev_yield
    # Load existing Pokémon data if it exists
    if mainpokemon_path.is_file():
        with open(mainpokemon_path, "r", encoding="utf-8") as json_file:
            main_pokemon_data = json.load(json_file)
            for pokemon in main_pokemon_data:
                if pokemon["individual_id"] == individual_id:
                    attacks = pokemon["attacks"]
                    new_attacks = get_random_moves_for_pokemon(prevo_name.lower(), int(main_pokemon.level))
                    for new_attack in new_attacks:
                        if new_attack not in attacks:
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
                                        logger.log_and_showinfo("info",translator.translate("replaced_selected_attack", selected_attack=selected_attack, new_attack=new_attack))
                                    else:
                                        logger.log_and_showinfo("info",translator.translate("selected_attack_not_found", selected_attack=selected_attack))
                                else:
                                    # Handle the case where the user cancels the dialog
                                    logger.log_and_showinfo("info",translator.translate("no_attack_selected"))
                    break
            for mainpkmndata in main_pokemon_data:
                mainpkmndata["stats"]["xp"] = int(main_pokemon.xp)
                mainpkmndata["level"] = int(main_pokemon.level)
                mainpkmndata["current_hp"] = int(main_pokemon.hp)
                mainpkmndata["ev"]["hp"] += ev_yield["hp"]
                mainpkmndata["ev"]["atk"] += ev_yield["attack"]
                mainpkmndata["ev"]["def"] += ev_yield["defense"]
                mainpkmndata["ev"]["spa"] += ev_yield["special-attack"]
                mainpkmndata["ev"]["spd"] += ev_yield["special-defense"]
                mainpkmndata["ev"]["spe"] += ev_yield["speed"]
                mainpkmndata["attacks"] = attacks
                mainpkmndata["everstone"] = False
    mypkmndata = mainpkmndata
    mainpkmndata = [mainpkmndata]
    # Save the caught Pokémon's data to a JSON file
    with open(str(mainpokemon_path), "w") as json_file:
        json.dump(mainpkmndata, json_file, indent=2)

        # Load data from the output JSON file
    with open(str(mypokemon_path), "r", encoding="utf-8") as output_file:
        mypokemondata = json.load(output_file)

        # Find and replace the specified Pokémon's data in mypokemondata
        for index, pokemon_data in enumerate(mypokemondata):
            if pokemon_data["individual_id"] == individual_id:
                mypokemondata[index] = mypkmndata
                break
        # Save the modified data to the output JSON file
        with open(str(mypokemon_path), "w") as output_file:
            json.dump(mypokemondata, output_file, indent=2)


def catch_pokemon(nickname):
  try:
    ankimon_tracker_obj.caught += 1
    if ankimon_tracker_obj.caught == 1:
        pokemon_collection_obj.collected_pokemon_ids.add(enemy_pokemon.id)  # Update cache
        if nickname is None or not nickname:  # Wenn None oder leer
            save_caught_pokemon(nickname)
        else:
            save_caught_pokemon(enemy_pokemon.name)
        ankimon_tracker_obj.general_card_count_for_battle = 0
        msg = translator.translate("caught_wild_pokemon", enemy_pokemon_name=enemy_pokemon.name.capitalize())
        if settings_obj.get('gui.pop_up_dialog_message_on_defeat', True) is True:
            logger.log_and_showinfo("info",f"{msg}") # Display a message when the Pokémon is caught
        color = "#6A4DAC" #pokemon leveling info color for tooltip
        try:
            tooltipWithColour(msg, color)
        except:
            pass
        new_pokemon()  # Show a new random Pokémon
    else:
        if settings_obj.get('gui.pop_up_dialog_message_on_defeat', True) is True:
            logger.log_and_showinfo("info",translator.translate("already_caught_pokemon")) # Display a message when the Pokémon is caught
  except Exception as e:
        showWarning(f"Error occured while catching enemy Pokemon: {e}")

def get_random_starter():
    category = "Starter"
    try:
        # Reload the JSON data from the file
        with open(str(starters_path), "r", encoding="utf-8") as file:
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
            random_gen = random.randint(0, 6)
            water_start = f"{water_starter[random_gen]}"
            fire_start = f"{fire_starter[random_gen]}"
            grass_start = f"{grass_starter[random_gen]}"
            return water_start, fire_start, grass_start
    except Exception as e:
        showWarning(f"Error in get_random_starter: {e}")
        return None, None, None

def new_pokemon():
    try:
        # new pokemon
        gender = None
        name, id, level, ability, type, stats, enemy_attacks, base_experience, growth_rate, ev, iv, gender, battle_status, battle_stats, tier, ev_yield, shiny = generate_random_pokemon()
        pokemon_data = {
            'name': name,
            'id': id,
            'level': level,
            'ability': ability,
            'type': type,
            'stats': stats,
            'attacks': enemy_attacks,
            'base_experience': base_experience,
            'growth_rate': growth_rate,
            'ev': ev,
            'iv': iv,
            'gender': gender,
            'battle_status': battle_status,
            'battle_stats': battle_stats,
            'tier': tier,
            'ev_yield': ev_yield,
            'shiny': shiny
        }
        enemy_pokemon.update_stats(**pokemon_data)
        ankimon_tracker_obj.randomize_battle_scene()
        max_hp = enemy_pokemon.calculate_max_hp()
        enemy_pokemon.current_hp = max_hp
        enemy_pokemon.hp = max_hp
        enemy_pokemon.max_hp = max_hp
        #reset mainpokemon hp
        if test_window is not None:
            test_window.display_first_encounter()
        class Container(object):
            pass
        reviewer = Container()
        reviewer.web = mw.reviewer.web
        reviewer_obj.update_life_bar(reviewer, 0, 0)
    except Exception as e:
        showWarning(f"An error occurred while generating new Pokemon: {str(e)}") 
            
def mainpokemon_data():
    try:
        with (open(str(mainpokemon_path), "r", encoding="utf-8") as json_file):
                main_pokemon_datalist = json.load(json_file)
                main_pokemon_data = []
                for main_pokemon_data in main_pokemon_datalist:
                    mainpokemon_name = main_pokemon_data["name"]
                    if not main_pokemon_data.get('nickname') or main_pokemon_data.get('nickname') is None:
                            mainpokemon_nickname = None
                    else:
                        mainpokemon_nickname = main_pokemon_data['nickname']
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
                    
                    return mainpokemon_name, mainpokemon_id, mainpokemon_ability, mainpokemon_type, mainpokemon_stats, mainpokemon_attacks, mainpokemon_level, mainpokemon_base_experience, mainpokemon_xp, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate, mainpokemon_ev, mainpokemon_iv, mainpokemon_evolutions, mainpokemon_battle_stats, mainpokemon_gender, mainpokemon_nickname
    except Exception as e:
            logger.log("error", f"{e} error has come up in the main_pokemon function.")
#get main pokemon details:
if database_complete:
    try:
        mainpokemon_name, mainpokemon_id, mainpokemon_ability, mainpokemon_type, mainpokemon_stats, mainpokemon_attacks, mainpokemon_level, mainpokemon_base_experience, mainpokemon_xp, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate, mainpokemon_ev, mainpokemon_iv, mainpokemon_evolutions, mainpokemon_battle_stats, mainpokemon_gender, mainpokemon_nickname = mainpokemon_data()
        starter = True
    except Exception:
        starter = False
        mainpokemon_level = 5
    name, id, level, ability, type, stats, enemy_attacks, base_experience, growth_rate, ev, iv, gender, battle_status, battle_stats, tier, ev_yield, shiny = generate_random_pokemon()
    pokemon_data = {
        'name': name,
        'id': id,
        'level': level,
        'ability': ability,
        'type': type,
        'stats': stats,
        'attacks': enemy_attacks,
        'base_experience': base_experience,
        'growth_rate': growth_rate,
        'ev': ev,
        'iv': iv,
        'gender': gender,
        'battle_status': battle_status,
        'battle_stats': battle_stats,
        'tier': tier,
        'ev_yield': ev_yield,
        'shiny': shiny
    }
    enemy_pokemon.update_stats(**pokemon_data)
    max_hp = enemy_pokemon.calculate_max_hp()
    enemy_pokemon.current_hp = max_hp
    enemy_pokemon.hp = max_hp
    enemy_pokemon.max_hp = max_hp
    ankimon_tracker_obj.randomize_battle_scene()

cry_counter = 0

reviewer_obj = Reviewer_Manager(
    settings_obj=settings_obj,
    main_pokemon=main_pokemon,
    enemy_pokemon=enemy_pokemon,
    ankimon_tracker=ankimon_tracker_obj,
)

# Hook into Anki's card review event
def on_review_card(*args):
    try:
        battle_status = enemy_pokemon.battle_status
        multiplier = ankimon_tracker_obj.multiplier
        mainpokemon_type = main_pokemon.type
        mainpokemon_name = main_pokemon.name

        global battle_sounds
        global achievements
        # Increment the counter when a card is reviewed
        attack_counter = ankimon_tracker_obj.attack_counter
        ankimon_tracker_obj.cards_battle_round += 1
        ankimon_tracker_obj.cry_counter += 1
        cry_counter = ankimon_tracker_obj.cry_counter
        card_counter = ankimon_tracker_obj.card_counter
        dmg = 0
        reviewer_obj.seconds = 0
        reviewer_obj.myseconds = 0
        ankimon_tracker_obj.general_card_count_for_battle += 1
        if battle_sounds == True and ankimon_tracker_obj.general_card_count_for_battle == 1:
            play_sound()
        #test achievment system
        if card_counter == 100:
            check = check_for_badge(achievements,1)
            if check is False:
                achievements = receive_badge(1,achievements)
                test_window.display_badge(1)
        elif card_counter == 200:
            check = check_for_badge(achievements,2)
            if check is False:
                achievements = receive_badge(2,achievements)
                test_window.display_badge(2)
        elif card_counter == 300:
                check = check_for_badge(achievements,3)
                if check is False:
                    achievements = receive_badge(3,achievements)
                    test_window.display_badge(3)
        elif card_counter == 500:
                check = check_for_badge(achievements,4)
                if check is False:
                    receive_badge(4,achievements)
                    test_window.display_badge(4)
        if card_counter == ankimon_tracker_obj.item_receive_value:
            test_window.display_item()
            check = check_for_badge(achievements,6)
            if check is False:
                receive_badge(6,achievements)
                test_window.display_badge(6)
        if ankimon_tracker_obj.cards_battle_round >= int(settings_obj.get("battle.cards_per_round", 2)):
            ankimon_tracker_obj.cards_battle_round = 0
            ankimon_tracker_obj.attack_counter = 0
            slp_counter = 0
            ankimon_tracker_obj.pokemon_encouter += 1
            multiplier = int(ankimon_tracker_obj.multiplier)
            msg = ""
            msg += f"{multiplier}x {translator.translate('multiplier')}"
            #failed card = enemy attack
            if ankimon_tracker_obj.pokemon_encouter > 0 and enemy_pokemon.hp > 0 and dmg_in_reviewer is True and multiplier < 1:
                msg += " \n "
                try:
                    max_attempts = 3  # Set the maximum number of attempts
                    for _ in range(max_attempts):
                        rand_enemy_atk = random.choice(enemy_pokemon.attacks)
                        enemy_move = find_details_move(rand_enemy_atk)
                        
                        if enemy_move is not None:
                            break  # Exit the loop if a valid enemy_move is found
                    msg += translator.translate("pokemon_chose_attack", pokemon_name=enemy_pokemon.name.capitalize(), pokemon_attack=rand_enemy_atk.capitalize())
                    e_move_category = enemy_move.get("category")
                    e_move_acc = enemy_move.get("accuracy")
                    if e_move_acc is True:
                        e_move_acc = 100
                    elif e_move_acc != 0:
                        e_move_acc = 100 / e_move_acc
                    if random.random() > e_move_acc:
                        msg += "\n" + translator.translate("move_has_missed")
                    else:
                        if e_move_category == "Status":
                            color = "#F7DC6F"
                            msg = effect_status_moves(rand_enemy_atk, enemy_pokemon.stats, main_pokemon.stats, msg, main_pokemon.name , enemy_pokemon.name)
                        elif e_move_category == "Physical" or e_move_category == "Special":
                            critRatio = enemy_move.get("critRatio", 1)
                            if e_move_category == "Physical":
                                color = "#F0B27A"
                            elif e_move_category == "Special":
                                color = "#D2B4DE"
                            if enemy_move["basePower"] == 0:
                                enemy_dmg = bP_none_moves(enemy_move)
                                main_pokemon.hp -= int(enemy_dmg)
                                if enemy_dmg == 0:
                                    msg += "\n" + translator.translate("move_has_missed")
                            else:
                                if e_move_category == "Special":
                                    def_stat = main_pokemon.stats["spd"]
                                    atk_stat = enemy_pokemon.stats["spa"]
                                elif e_move_category == "Physical":
                                    def_stat = main_pokemon.stats["def"]
                                    atk_stat = enemy_pokemon.stats["atk"]
                                enemy_dmg = int(calc_atk_dmg(enemy_pokemon.level ,(multiplier * 2),enemy_move["basePower"], atk_stat, def_stat, enemy_pokemon.type, enemy_move["type"],mainpokemon_type, critRatio))
                                if enemy_dmg == 0:
                                    enemy_dmg = 1
                                main_pokemon.hp -= enemy_dmg
                                if enemy_dmg > 0:
                                    reviewer_obj.myseconds = settings_obj.compute_special_variable("animate_time")
                                    if multiplier < 1:
                                        play_effect_sound("HurtNormal")
                                else:
                                    reviewer_obj.myseconds = 0
                                msg += translator.translate("dmg_dealt", dmg=enemy_dmg, pokemon_name=main_pokemon.name.capitalize())
                except:
                    enemy_dmg = 0
                    rand_enemy_atk = random.choice(enemy_pokemon.attacks)
                    enemy_move = find_details_move(rand_enemy_atk)
                    e_move_category = enemy_move.get("category")
                    if e_move_category == "Status":
                            color = "#F7DC6F"
                            msg = effect_status_moves(rand_enemy_atk, enemy_pokemon.stats, main_pokemon.stats, msg, main_pokemon.name , enemy_pokemon.name)
                    elif e_move_category == "Physical" or e_move_category == "Special":
                        if e_move_category == "Special":
                            def_stat = main_pokemon.stats["spd"]
                            atk_stat = enemy_pokemon.stats["spa"]
                        elif e_move_category == "Physical":
                            def_stat = main_pokemon.stats["def"]
                            atk_stat = enemy_pokemon.stats["atk"]                        
                        enemy_dmg = int(calc_atk_dmg(enemy_pokemon.level,(multiplier * 2),random.randint(60, 100), atk_stat, def_stat, enemy_pokemon.type, "Normal", mainpokemon_type, critRatio))
                        if enemy_dmg == 0:
                            enemy_dmg = 1
                        main_pokemon.hp -= enemy_dmg
                    if enemy_dmg > 0:
                        reviewer_obj.myseconds = settings_obj.compute_special_variable("animate_time")
                        if multiplier < 1:
                            play_effect_sound("HurtNormal")
                    else:
                        reviewer_obj.myseconds = 0
                        msg += translator.translate("dmg_dealt", dmg=enemy_dmg, pokemon_name=main_pokemon.name.capitalize())
    
            # if enemy pokemon hp < 0 - attack enemy pokemon
            if ankimon_tracker_obj.pokemon_encouter > 0 and main_pokemon.hp > 0 and enemy_pokemon.hp > 0:
                dmg = 0
                random_attack = random.choice(main_pokemon.attacks)
                if settings_obj.get("controls.allow_to_choose_moves", False) == True:
                    dialog = MoveSelectionDialog(main_pokemon.attacks)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        if dialog.selected_move:
                            random_attack = dialog.selected_move
                msg += "\n"
                msg += translator.translate("pokemon_chose_attack", pokemon_name=main_pokemon.name.capitalize(), pokemon_attack=random_attack.capitalize())
                move = find_details_move(random_attack)
                category = move.get("category")
                acc = move.get("accuracy")
                if battle_status != "fighting":
                    msg, acc, battle_status, enemy_pokemon.stats = status_effect(enemy_pokemon, move, slp_counter, msg, acc)
                if acc is True:
                    acc = 100
                if acc != 0:
                    calc_acc = 100 / acc
                else:
                    calc_acc = 0
                if battle_status == "slp":
                    calc_acc = 0
                    msg += "\n" + translator.translate("pokemon_asleep", pokemon_name=enemy_pokemon.name.capitalize())
                    #slp_counter -= 1
                elif battle_status == "par":
                    msg += "\n" + translator.translate("pokemon_is_paralyzed", pokemon_name=enemy_pokemon.name.capitalize())
                    missing_chance = 1 / 4
                    random_number = random.random()
                    if random_number < missing_chance:
                        acc = 0
                if random.random() > calc_acc:
                    msg += "\n" + translator.translate("move_has_missed")
                else:
                    if category == "Status":
                        color = "#F7DC6F"
                        msg = effect_status_moves(random_attack, main_pokemon.stats, enemy_pokemon.stats, msg, enemy_pokemon.name, main_pokemon.name)
                    elif category == "Physical" or category == "Special":
                        try:
                            critRatio = move.get("critRatio", 1)
                            if category == "Physical":
                                color = "#F0B27A"
                            elif category == "Special":
                                color = "#D2B4DE"
                            if move["basePower"] == 0:
                                dmg = bP_none_moves(move)
                                enemy_pokemon.hp -= dmg
                                if dmg == 0:
                                    msg += "\n" + translator.translate("move_has_missed")
                                    #dmg = 1
                            else:
                                if category == "Special":
                                    def_stat = enemy_pokemon.stats["spd"]
                                    atk_stat = main_pokemon.stats["spa"]
                                elif category == "Physical":
                                    def_stat = enemy_pokemon.stats["def"]
                                    atk_stat = main_pokemon.stats["atk"]
                                dmg = int(calc_atk_dmg(main_pokemon.level, multiplier, move["basePower"], atk_stat, def_stat, main_pokemon.type, move["type"],enemy_pokemon.type, critRatio))
                                if dmg == 0:
                                    dmg = 1
                                enemy_pokemon.hp -= dmg
                                msg += translator.translate("dmg_dealt", dmg=dmg, pokemon_name=enemy_pokemon.name.capitalize())
                                move_stat = move.get("status", None)
                                secondary = move.get("secondary", None)
                                if secondary is not None:
                                    bat_status = move.get("secondary", None).get("status", None)
                                    if bat_status is not None:
                                        move_with_status(move, move_stat, secondary)
                                if move_stat is not None:
                                    move_with_status(move, move_stat, secondary)
                                if dmg == 0:
                                    msg += "\n" + translator.translate("move_has_missed")
                        except:
                            if category == "Special":
                                def_stat = enemy_pokemon.stats["spd"]
                                atk_stat = main_pokemon.stats["spa"]
                            elif category == "Physical":
                                def_stat = enemy_pokemon.stats["def"]
                                atk_stat = main_pokemon.stats["atk"]
                            dmg = int(calc_atk_dmg(main_pokemon.level, multiplier,random.randint(60, 100), atk_stat, def_stat, main_pokemon.type, "Normal",enemy_pokemon.type, critRatio))
                            enemy_pokemon.hp -= dmg
                        if enemy_pokemon.hp < 0:
                            enemy_pokemon.hp = 0
                            msg += translator.translate("pokemon_fainted", enemy_pokemon_name=enemy_pokemon.name.capitalize())
                            
                    tooltipWithColour(msg, color)
                    if dmg > 0:
                        reviewer_obj.seconds = int(settings_obj.compute_special_variable("animate_time"))
                        if multiplier == 1:
                            play_effect_sound("HurtNormal")
                        elif multiplier < 1:
                            play_effect_sound("HurtNotEffective")
                        elif multiplier > 1:
                            play_effect_sound("HurtSuper")
                    else:
                        reviewer_obj.seconds = 0

            if enemy_pokemon.hp < 1:
                enemy_pokemon.hp = 0
                
                # New automatic battle handling
                auto_battle_setting = int(settings_obj.get("battle.automatic_battle", 0))
                
                value = settings_obj.get("battle.automatic_battle", "0")
                try:
                    auto_battle_setting = int(value)
                except ValueError:
                    auto_battle_setting = 0  # fallback

                if auto_battle_setting == 3:  # Catch if uncollected
                    enemy_id = enemy_pokemon.id
                    # Check cache instead of file
                    if enemy_id not in pokemon_collection_obj.collected_pokemon_ids or enemy_pokemon.shiny:
                        catch_pokemon("")
                    else:
                        kill_pokemon()
                    ankimon_tracker_obj.general_card_count_for_battle = 0
                    new_pokemon()
                
                elif auto_battle_setting == 1:  # Existing auto-catch
                    catch_pokemon("")
                    ankimon_tracker_obj.general_card_count_for_battle = 0
                    new_pokemon()
                
                elif auto_battle_setting == 2:  # Existing auto-defeat
                    kill_pokemon()
                    new_pokemon()
                    ankimon_tracker_obj.general_card_count_for_battle = 0
                
        if cry_counter == 10 and battle_sounds is True:
            cry_counter = 0
            play_sound()
        if main_pokemon.hp < 1:
            msg = translator.translate("pokemon_fainted", enemy_pokemon_name=enemy_pokemon.name.capitalize(), main_pokemon_name=main_pokemon.name.capitalize())
            play_effect_sound("Fainted")
            new_pokemon()
            #mainpokemon_data()
            main_pokemon.hp = main_pokemon.max_hp
            color = "#E12939"
            tooltipWithColour(msg, color)
        class Container(object):
            pass
        reviewer = Container()
        reviewer.web = mw.reviewer.web
        reviewer_obj.update_life_bar(reviewer, 0, 0)
        if test_window is not None:
            test_window.display_battle()
    except Exception as e:
        showWarning(f"An error occurred in reviewer: {str(e)}")

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
    if target == "self":
        for boost, stage in boosts.items():
            stat = get_multiplier_stats(stage)
            mainpokemon_stats[boost] = mainpokemon_stats.get(boost, 0) * stat
            msg += f" {main_pokemon.name.capitalize()}'s "
            if stage < 0:
                msg += f"{boost.capitalize()} {translator.translate('stat_decreased')}."
            elif stage > 0:
                msg += f"{boost.capitalize()} {translator.translate('stat_increased')}."
    elif target in ["normal", "allAdjacentFoes"]:
        for boost, stage in boosts.items():
            stat = get_multiplier_stats(stage)
            stats[boost] = stats.get(boost, 0) * stat
            msg += f" {name.capitalize()}'s "
            if stage < 0:
                msg += f"{boost.capitalize()} {translator.translate('stat_decreased')}."
            elif stage > 0:
                msg += f"{boost.capitalize()} {translator.translate('stat_increased')}."
    return msg

def move_with_status(move, move_stat, status):
    global battle_status
    target = move.get("target")
    bat_status = move.get("secondary", None).get("status", None)
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

# Connect the hook to Anki's review event
gui_hooks.reviewer_did_answer_card.append(on_review_card)

def MainPokemon(pokemon_data, main_pokemon = main_pokemon):
    # Capitalize the first letter of the Pokémon's name
    # Create a dictionary to store the Pokémon's data
    main_pokemon_data = []
    main_pokemon_data.append({key: value for key, value in pokemon_data.items()})
    capitalized_name = main_pokemon.name.capitalize()

    # Save the caught Pokémon's data to a JSON file
    with open(str(mainpokemon_path), "w") as json_file:
        json.dump(main_pokemon_data, json_file, indent=2)

    logger.log_and_showinfo("info",translator.translate("picked_main_pokemon", main_pokemon_name=capitalized_name))
    #mainpokemon_data()
    update_main_pokemon(main_pokemon, mainpokemon_path)
    class Container(object):
        pass
    reviewer = Container()
    reviewer.web = mw.reviewer.web
    reviewer_obj.update_life_bar(reviewer, 0, 0)
    if test_window.isVisible() is True:
        test_window.display_first_encounter()

pokecollection_win = PokemonCollectionDialog(logger=logger, settings_obj=settings_obj, mainpokemon_function = MainPokemon, main_pokemon = main_pokemon)

life_bar_injected = False

def animate_pokemon():
    reviewer_obj.seconds = 2
    reviewer = mw.reviewer
    reviewer.web = mw.reviewer.web
    reviewer.web.eval(f'document.getElementById("PokeImage").style="animation: shake {reviewer_obj.seconds}s ease;"')
    if show_mainpkmn_in_reviewer is True:
        reviewer.web.eval(f'document.getElementById("MyPokeImage").style="animation: shake {reviewer_obj.myseconds}s ease;"')
   
def choose_pokemon(starter_name): 
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
        "evos": evos
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

    logger.log_and_showinfo("info",f"{name.capitalize()} has been chosen as Starter Pokemon !")

    starter_window.display_chosen_starter_pokemon(starter_name)

def save_fossil_pokemon(pokemon_id):
    # Create a dictionary to store the Pokémon's data
    # add all new values like hp as max_hp, evolution_data, description and growth rate
    name = search_pokedex_by_id(pokemon_id)
    id = pokemon_id
    stats = search_pokedex(name, "baseStats")
    abilities = search_pokedex(name, "abilities")
    evos = search_pokedex(name, "evos")
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
    type = search_pokedex(name, "types")
    name = search_pokedex(name, "name")
    generation_file = "pokeapi_db.json"
    growth_rate = search_pokeapi_db_by_id(id, "growth_rate")
    base_experience = search_pokeapi_db_by_id(id, "base_experience")
    description= search_pokeapi_db_by_id(id, "description")
    level = 5
    attacks = get_random_moves_for_pokemon(name, level)
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
        with open(mypokemon_path, "r", encoding="utf-8") as json_file:
            caught_pokemon_data = json.load(json_file)
    else:
        caught_pokemon_data = []

    # Append the caught Pokémon's data to the list
    caught_pokemon_data.append(caught_pokemon)
    # Save the caught Pokémon's data to a JSON file
    with open(str(mypokemon_path), "w") as json_file:
        json.dump(caught_pokemon_data, json_file, indent=2)

def export_to_pkmn_showdown():
    # Create a main window
    window = QDialog(mw)
    window.setWindowTitle("Export Pokemon to Pkmn Showdown")
    for stat, value in main_pokemon.ev.items():
        if value == 0:
            main_pokemon.ev[stat] += 1
    # Format the Pokemon info
    pokemon_info = "{} ({})\nAbility: {}\nLevel: {}\nType: {}\nEVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe\n IVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe ".format(
        main_pokemon.name,
        main_pokemon.gender,
        main_pokemon.ability,
        main_pokemon.level,
        main_pokemon.type,
        main_pokemon.ev["hp"],
        main_pokemon.ev["atk"],
        main_pokemon.ev["def"],
        main_pokemon.ev["spa"],
        main_pokemon.ev["spd"],
        main_pokemon.ev["spe"],
        main_pokemon.iv["hp"],
        main_pokemon.iv["atk"],
        main_pokemon.iv["def"],
        main_pokemon.iv["spa"],
        main_pokemon.iv["spd"],
        main_pokemon.iv["spe"]
    )
    for attack in main_pokemon.attacks:
        pokemon_info += f"\n- {attack}"
    # Information label
    info = "Pokemon Infos have been Copied to your Clipboard! \nNow simply paste this text into Teambuilder in PokemonShowdown. \nNote: Fight in the [Gen 9] Anything Goes - Battle Mode"
    info += f"\n Your Pokemon is considered Tier: {search_pokedex(main_pokemon.name.lower(), 'tier')} in PokemonShowdown"
    # Create labels to display the text
    label = QLabel(pokemon_info)
    info_label = QLabel(info)

    # Align labels
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align center
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align center

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
        error_fix_msg += (f"\n Please use Gen {str(generation_number)[0]} or lower")

        index = error_code.find("can't be transferred from Gen")

        # Extract the substring starting from this position
        relevant_text = error_code[index:]

        # Find the first number in the extracted text (assuming it's the generation number)
        generation_number = int(''.join(filter(str.isdigit, relevant_text)))

        error_fix_msg += (f"\n Please use Gen {str(generation_number)[0]} or lower")

    except Exception as e:
        logger.log_and_showinfo("info",f"An error occurred: {e}")

    logger.log_and_showinfo("info",f"{error_fix_msg}")

def export_all_pkmn_showdown():
    # Create a main window
    export_window = QDialog()
    #export_window.setWindowTitle("Export Pokemon to Pkmn Showdown")

    # Information label
    info = "Pokemon Infos have been Copied to your Clipboard! \nNow simply paste this text into Teambuilder in PokemonShowdown. \nNote: Fight in the [Gen 7] Anything Goes - Battle Mode"
    info_label = QLabel(info)

    # Get all pokemon data
    pokemon_info_complete_text = ""
    try:
        with (open(mypokemon_path, "r", encoding="utf-8") as json_file):
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

                    pokemon_info = "{} \nAbility: {}\nLevel: {}\nType: {}\nEVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe\n IVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe \n".format(
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
                    pokemon_info += "\n"
                    pokemon_info_complete_text += pokemon_info

                    # Create labels to display the text
                    #label = QLabel(pokemon_info_complete_text)
                    # Align labels
                    #label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align center
                    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align center

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
        logger.log_and_showinfo("info",f"An error occurred: {e}")

def flex_pokemon_collection():
    # Create a main window
    export_window = QDialog()
    #export_window.setWindowTitle("Export Pokemon to Pkmn Showdown")

    # Information label
    info = "Pokemon Infos have been Copied to your Clipboard! \nNow simply paste this text into https://pokepast.es/.\nAfter pasting the infos in your clipboard and submitting the needed infos on the right,\n you will receive a link to send friends to flex."
    info_label = QLabel(info)

# Get all pokemon data
    pokemon_info_complete_text = ""
    try:
        with (open(mypokemon_path, "r", encoding="utf-8") as json_file):
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

                    pokemon_info = "{} \nAbility: {}\nLevel: {}\nType: {}\nEVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe\n IVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe \n".format(
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
                    pokemon_info += "\n"
                    pokemon_info_complete_text += pokemon_info

                    # Create labels to display the text
                    #label = QLabel(pokemon_info_complete_text)
                    # Align labels
                    #label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align center
                    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align center

                    # Create a layout and add the labels, input field, and button
                    layout = QVBoxLayout()
                    layout.addWidget(info_label)
                    #layout.addWidget(label)

                    # Copy text to clipboard in Anki
                    mw.app.clipboard().setText(pokemon_info_complete_text)
        #save_button.clicked.connect(lambda: save_error_code(error_code_input.text()))
        # Set the layout for the main window
        open_browser_for_pokepaste = QPushButton("Open Pokepaste")
        open_browser_for_pokepaste.clicked.connect(open_browser_window)
        layout.addWidget(open_browser_for_pokepaste)

        export_window.setLayout(layout)

        export_window.exec()
    except Exception as e:
        logger.log_and_showinfo("info",f"An error occurred: {e}")

video = False
first_start = False

class TestWindow(QWidget):
    def __init__(self, main_pokemon, enemy_pokemon, settings_obj, parent=mw):
        super().__init__()
        self.setWindowFlag(Qt.WindowType.Tool)
        self.pkmn_window = False #if fighting window open
        self.first_start = False
        self.enemy_pokemon = enemy_pokemon
        self.main_pokemon = main_pokemon
        self.settings = settings_obj
        self.test = 1
        self.default_path = f"{pkmnimgfolder}/front_default/substitute.png"
        self.init_ui()
        #self.update()

    def init_ui(self):
        layout = QVBoxLayout()
        # Main window layout
        layout = QVBoxLayout()
        image_file = "ankimon_logo.png"
        image_path = str(addon_dir) + "/" + image_file
        image_label = QLabel()
        pixmap = QPixmap()
        pixmap.load(str(image_path))
        if pixmap.isNull():
            showWarning("Failed to load Ankimon Logo image")
        else:
            image_label.setPixmap(pixmap)
        scaled_pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
        image_label.setPixmap(scaled_pixmap)
        layout.addWidget(image_label)
        self.first_start = True
        self.setLayout(layout)
        # Set window
        self.setWindowTitle('Ankimon Window')
        self.setWindowIcon(QIcon(str(icon_path))) # Add a Pokeball icon
        # Display the Pokémon image

    def open_dynamic_window(self):
        # Create and show the dynamic window
        try:
            if self.pkmn_window == False:
                self.display_first_encounter()
                self.pkmn_window = True
            #self.show()
            if self.isVisible():
                self.close()  # Testfenster schließen, wenn Shift gedrückt wird
            else:
                self.show()
        except Exception as e:
            showWarning(f"Following Error occured when opening window: {e}")

    def display_first_start_up(self):
        if self.first_start == False:
            # Get the geometry of the main screen
            main_screen_geometry = mw.geometry()
            # Calculate the position to center the ItemWindow on the main screen
            x = int(main_screen_geometry.center().x() - self.width() / 2)
            y = int(main_screen_geometry.center().y() - self.height() / 2)
            self.setGeometry(x, y, 256, 256 )
            self.move(x,y)
            self.show()
            self.first_start = True
        self.pkmn_window = True

    def pokemon_display_first_encounter(self):
        # Main window layout
        layout = QVBoxLayout()
        global message_box_text
        global merged_pixmap, window

        ankimon_tracker_obj.attack_counter = 0
        ankimon_tracker_obj.caught = 0

        # Capitalize the first letter of the Pokémon's name
        lang_name = get_pokemon_diff_lang_name(int(self.enemy_pokemon.id), int(settings_obj.get('misc.language')))
        # calculate wild pokemon max hp
        message_box_text = f"{mw.translator.translate('wild_pokemon_appeared', enemy_pokemon_name=lang_name.capitalize())}"
        if ankimon_tracker_obj.pokemon_encouter == 0:
            bckgimage_path = battlescene_path / ankimon_tracker_obj.battlescene_file
        elif ankimon_tracker_obj.pokemon_encouter > 0:
            bckgimage_path = battlescene_path_without_dialog / ankimon_tracker_obj.battlescene_file
        msg_font = load_custom_font(int(32), int(settings_obj.get("misc.language",11)))
        image_label, msg_font = self.window_show(bckgimage_path, lang_name)
        return image_label

    def window_show(self, bckgimage_path, lang_name):
        ui_path = battle_ui_path
        pixmap_ui = QPixmap()
        pixmap_ui.load(str(ui_path))

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        # Display the Pokémon image
        image_label = QLabel()
        pixmap = QPixmap()
        try:
            pixmap.load(str(self.enemy_pokemon.get_sprite_path('front', 'png')))
        except:
            pixmap.load(str(self.default_path))

        # Display the Main Pokémon image
        pixmap2 = QPixmap()
        try:
            pixmap2.load(str(self.main_pokemon.get_sprite_path('back', 'png')))
        except:
            pixmap2.load(str(self.default_path))

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
        #merged_pixmap.fill(Qt.transparent)
        merged_pixmap.fill(QColor(0, 0, 0, 0))
        # RGBA where A (alpha) is 0 for full transparency
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)

        painter = self.draw_hp_bar(118, 76, 8, 116, self.enemy_pokemon.hp, self.enemy_pokemon.max_hp, painter)  # enemy pokemon hp_bar
        painter = self.draw_hp_bar(401, 208, 8, 116, self.main_pokemon.hp, self.main_pokemon.max_hp, painter)  # main pokemon hp_bar

        painter.drawPixmap(0, 0, pixmap_ui)
        # Find the Pokemon Images Height and Width
        wpkmn_width = (new_width // 2)
        wpkmn_height = new_height
        mpkmn_width = (new_width2 // 2)
        mpkmn_height = new_height2
        # draw pokemon image to a specific pixel
        painter.drawPixmap((410 - wpkmn_width), (170 - wpkmn_height), pixmap)
        painter.drawPixmap((144 - mpkmn_width), (290 - mpkmn_height), pixmap2)

        experience = int(find_experience_for_level(self.main_pokemon.growth_rate, self.main_pokemon.level, settings_obj.get("misc.remove_level_cap", False)))
        mainxp_bar_width = 5
        mainpokemon_xp_value = int((self.main_pokemon.xp / experience) * 148)
        # Paint XP Bar
        painter.setBrush(QColor(58, 155, 220))
        painter.drawRect(int(366), int(246), int(mainpokemon_xp_value), int(mainxp_bar_width))

        # Convert gender name to symbol - this function is from Foxy-null
        if gender == "M":
            gender_symbol = "♂"
        elif gender == "F":
            gender_symbol = "♀"
        elif gender == "N":
            gender_symbol = ""
        else:
            gender_symbol = ""  # None

        # custom font
        custom_font = load_custom_font(int(26), int(settings_obj.get("misc.language",11)))
        msg_font = load_custom_font(int(32), int(settings_obj.get("misc.language",11)))
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(31, 31, 39))  # Text color
        enemy_name = get_pokemon_diff_lang_name(int(self.enemy_pokemon.id), int(settings_obj.get('misc.language')))
        main_name = get_pokemon_diff_lang_name(int(self.main_pokemon.id), int(settings_obj.get('misc.language')))

        if self.enemy_pokemon.shiny:
            enemy_name += " 🌠 "

        if self.main_pokemon.shiny:
            main_name += " 🌠 "

        painter.drawText(48, 67, enemy_name)
        painter.drawText(326, 200, main_name)

        painter.drawText(208, 67, f"{self.enemy_pokemon.level}")
        #painter.drawText(55, 85, gender_text)
        painter.drawText(490, 199, f"{self.main_pokemon.level}")
        hp_text = str(self.main_pokemon.hp)
        max_hp_text = str(self.main_pokemon.max_hp)

        hp_x = 442 if int(self.main_pokemon.hp) < 100 else 430 # Shift left if 3 digits
        max_hp_x = 487 if int(self.main_pokemon.max_hp) < 100 else 480  # Shift left if 3 digits

        painter.drawText(max_hp_x, 238, max_hp_text)
        painter.drawText(hp_x, 238, hp_text)
        painter.setFont(msg_font)
        painter.setPen(QColor(240, 240, 208))  # Text color
        painter.drawText(40, 320, message_box_text)
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        image_label.setPixmap(merged_pixmap)
        return image_label, msg_font

    def draw_hp_bar(self, x, y, h, w, hp, max_hp, painter):
        pokemon_hp_percent = int((hp / max_hp) * 100)
        hp_bar_value = int(w * (hp / max_hp))
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
        painter.drawRect(int(x), int(y), int(hp_bar_value), int(h))
        return painter

    def pokemon_display_battle(self):
        ankimon_tracker_obj.pokemon_encouter += 1
        if ankimon_tracker_obj.pokemon_encouter == 1:
            bckgimage_path = battlescene_path / ankimon_tracker_obj.battlescene_file
        elif ankimon_tracker_obj.pokemon_encouter > 1:
            bckgimage_path = battlescene_path_without_dialog / ankimon_tracker_obj.battlescene_file
        ui_path = battle_ui_path
        pixmap_ui = QPixmap()
        pixmap_ui.load(str(ui_path))

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        image_label = QLabel()

        # Display the Pokémon image
        pixmap = QPixmap()
        try:
            pixmap.load(str(self.enemy_pokemon.get_sprite_path('front', 'png')))
        except:
            pixmap.load(str(self.default_path))

        # Display the Main Pokémon image
        pixmap2 = QPixmap()
        try:
            pixmap2.load(str(self.main_pokemon.get_sprite_path('back', 'png')))
        except:
            pixmap2.load(str(self.default_path))

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
        #merged_pixmap.fill(Qt.transparent)
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)

        painter = self.draw_hp_bar(118, 76, 8, 116, self.enemy_pokemon.hp, self.enemy_pokemon.max_hp, painter)  # enemy pokemon hp_bar
        painter = self.draw_hp_bar(401, 208, 8, 116, self.main_pokemon.hp, self.main_pokemon.max_hp, painter)  # main pokemon hp_bar

        painter.drawPixmap(0, 0, pixmap_ui)
        # Find the Pokemon Images Height and Width
        wpkmn_width = (new_width // 2)
        wpkmn_height = new_height
        mpkmn_width = (new_width2 // 2)
        mpkmn_height = new_height2
        # draw pokemon image to a specific pixel
        painter.drawPixmap((410 - wpkmn_width), (170 - wpkmn_height), pixmap)
        painter.drawPixmap((144 - mpkmn_width), (290 - mpkmn_height), pixmap2)

        experience = int(find_experience_for_level(self.main_pokemon.growth_rate, self.main_pokemon.level, settings_obj.get("misc.remove_level_cap", False)))
        mainxp_bar_width = 5
        mainpokemon_xp_value = int((self.main_pokemon.xp / experience) * 148)
        # Paint XP Bar
        painter.setBrush(QColor(58, 155, 220))
        painter.drawRect(int(366), int(246), int(mainpokemon_xp_value), int(mainxp_bar_width))

        # custom font
        custom_font = load_custom_font(int(26), int(settings_obj.get("misc.language",11)))
        msg_font = load_custom_font(int(28), int(settings_obj.get("misc.language",11)))

        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(31, 31, 39))  # Text color
        enemy_name = get_pokemon_diff_lang_name(int(self.enemy_pokemon.id), int(settings_obj.get('misc.language')))
        main_name = get_pokemon_diff_lang_name(int(self.main_pokemon.id), int(settings_obj.get('misc.language')))

        if self.enemy_pokemon.shiny:
            enemy_name += f" 🌠"  # Green sparkle

        if self.main_pokemon.shiny:
            main_name += f" 🌠"  # Green sparkles

        painter.drawText(48, 67, enemy_name)
        painter.drawText(326, 200, main_name)
        painter.drawText(208, 67, f"{self.enemy_pokemon.level}")
        painter.drawText(490, 199, f"{self.main_pokemon.level}")
        hp_text = str(self.main_pokemon.hp)
        max_hp_text = str(self.main_pokemon.max_hp)

        hp_x = 442 if int(self.main_pokemon.hp) < 100 else 430 # Shift left if 3 digits
        max_hp_x = 487 if int(self.main_pokemon.max_hp) < 100 else 480  # Shift left if 3 digits

        painter.drawText(max_hp_x, 238, max_hp_text)
        painter.drawText(hp_x, 238, hp_text)
        painter.setFont(msg_font)
        painter.setPen(QColor(240, 240, 208))  # Text color
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        image_label.setPixmap(merged_pixmap)
        return image_label

    def pokemon_display_item(self, item):
        bckgimage_path =  addon_dir / "addon_sprites" / "starter_screen" / "bg.png"
        item_path = user_path_sprites / "items" / f"{item}.png"

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
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        #merged_pixmap.fill(Qt.transparent)
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
        custom_font = load_custom_font(int(26), int(settings_obj.get("misc.language",11)))
        message_box_text = f"{translator.translate('received_an_item', item_name=item.capitalize())} !"
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(50, 290, message_box_text)
        custom_font = load_custom_font(int(20), int(settings_obj.get("misc.language",11)))
        painter.setFont(custom_font)
        #painter.drawText(10, 330, "You can look this up in your item bag.")
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        image_label = QLabel()
        image_label.setPixmap(merged_pixmap)

        return image_label

    def pokemon_display_badge(self, badge_number):
        try:
            global badges
            bckgimage_path = addon_dir / "addon_sprites" / "starter_screen" / "bg.png"
            badge_path = addon_dir / "user_files" / "sprites" / "badges" / f"{badge_number}.png"

            # Load the background image
            pixmap_bckg = QPixmap()
            pixmap_bckg.load(str(bckgimage_path))

            # Display the Pokémon image
            item_pixmap = QPixmap()
            item_pixmap.load(str(badge_path))

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
            merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
            #merged_pixmap.fill(Qt.transparent)
            # merge both images together
            painter = QPainter(merged_pixmap)
            # draw background to a specific pixel
            painter.drawPixmap(0, 0, pixmap_bckg)
            #item = str(item)
            painter.drawPixmap(200,90,item_pixmap)

            # custom font
            custom_font = load_custom_font(int(20), int(settings_obj.get("misc.language",11)))
            message_box_text = translator.translate("received_a_badge")
            message_box_text2 = f"{badges[str(badge_number)]}!"
            # Draw the text on top of the image
            # Adjust the font size as needed
            painter.setFont(custom_font)
            painter.setPen(QColor(255,255,255))  # Text color
            painter.drawText(120, 270, message_box_text)
            painter.drawText(140, 290, message_box_text2)
            custom_font = load_custom_font(int(20), int(settings_obj.get("misc.language",11)))
            painter.setFont(custom_font)
            #painter.drawText(10, 330, "You can look this up in your item bag.")
            painter.end()
            # Set the merged image as the pixmap for the QLabel
            image_label = QLabel()
            image_label.setPixmap(merged_pixmap)

            return image_label
        except Exception as e:
            showWarning(f"An error occured in badges window {e}")

    def pokemon_display_dead_pokemon(self):
        caught = ankimon_tracker_obj.caught
        id = self.enemy_pokemon.id
        level = self.enemy_pokemon.level
        type = self.enemy_pokemon.type
        # Create the dialog
        lang_name = get_pokemon_diff_lang_name(int(id), int(settings_obj.get('misc.language')))
        self.setWindowTitle(f"{translator.translate('catch_or_free', enemy_pokemon_name=lang_name.capitalize())}")
        # Display the Pokémon image
        pkmnimage_file = f"{int(search_pokedex(self.enemy_pokemon.name.lower(),'num'))}.png"
        pkmnimage_path = frontdefault / pkmnimage_file
        pkmnimage_label = QLabel()
        pkmnpixmap = QPixmap()
        try:
            pkmnpixmap.load(str(pkmnimage_path))
        except:
            pkmnpixmap.load(str(self.default_path))
        pkmnpixmap_bckg = QPixmap()
        try:
            pkmnpixmap_bckg.load(str(pokedex_image_path))
        except:
            pkmnpixmap_bckg.load(str(self.default_path))
        # Calculate the new dimensions to maintain the aspect ratio
        pkmnpixmap = pkmnpixmap.scaled(230, 230)

        # Create a painter to add text on top of the image
        painter2 = QPainter(pkmnpixmap_bckg)
        painter2.drawPixmap(15,15,pkmnpixmap)
        # Create level text

        # Draw the text on top of the image
        font = QFont()
        font.setPointSize(20)  # Adjust the font size as needed
        painter2.setFont(font)
        painter2.drawText(270,107,f"{lang_name}")
        font.setPointSize(17)  # Adjust the font size as needed
        painter2.setFont(font)
        painter2.drawText(315,192,f"Level: {level}")
        painter2.drawText(322, 225, f"Type: {type[0].capitalize() if len(type) < 2 else type[1].capitalize()}")
        painter2.setFont(font)
        fontlvl = QFont()
        fontlvl.setPointSize(12)
        painter2.end()

        # Create a QLabel for the capitalized name
        name_label = QLabel(lang_name.capitalize())
        name_label.setFont(font)

        # Create a QLabel for the level
        level_label = QLabel(f"Level: {level}")
        # Align to the center
        level_label.setFont(fontlvl)

        nickname_input = QLineEdit()
        nickname_input.setPlaceholderText(translator.translate("choose_nickname"))
        nickname_input.setStyleSheet("background-color: rgb(44,44,44);")
        nickname_input.setFixedSize(120, 30)  # Adjust the size as needed

        # Create buttons for catching and killing the Pokémon
        catch_button = QPushButton(translator.translate("catch_button"))
        catch_button.setFixedSize(175, 30)  # Adjust the size as needed
        catch_button.setFont(QFont("Arial", 12))  # Adjust the font size and style as needed
        catch_button.setStyleSheet("background-color: rgb(44,44,44);")
        #catch_button.setFixedWidth(150)
        qconnect(catch_button.clicked, lambda: catch_pokemon(nickname_input.text()))

        kill_button = QPushButton(translator.translate("defeat_button"))
        kill_button.setFixedSize(175, 30)  # Adjust the size as needed
        kill_button.setFont(QFont("Arial", 12))  # Adjust the font size and style as needed
        kill_button.setStyleSheet("background-color: rgb(44,44,44);")
        #kill_button.setFixedWidth(150)
        qconnect(kill_button.clicked, kill_pokemon)
        # Set the merged image as the pixmap for the QLabel
        pkmnimage_label.setPixmap(pkmnpixmap_bckg)


        # align things needed to middle
        pkmnimage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        return pkmnimage_label, kill_button, catch_button, nickname_input

    def display_first_encounter(self):
        # pokemon encounter image
        self.clear_layout(self.layout())
        #self.setFixedWidth(556)
        #self.setFixedHeight(371)
        layout = self.layout()
        battle_widget = self.pokemon_display_first_encounter()
        #battle_widget.setScaledContents(True) #scalable ankimon window
        layout.addWidget(battle_widget)
        self.setStyleSheet("background-color: rgb(44,44,44);")
        self.setLayout(layout)
        self.setMaximumWidth(556)
        self.setMaximumHeight(300)

    def display_battle(self):
        # pokemon encounter image
        self.clear_layout(self.layout())
        #self.setFixedWidth(556)
        #self.setFixedHeight(371)
        layout = self.layout()
        battle_widget = self.pokemon_display_battle()
        #battle_widget.setScaledContents(True) #scalable ankimon window
        layout.addWidget(battle_widget)
        self.setStyleSheet("background-color: rgb(44,44,44);")
        self.setLayout(layout)
        self.setMaximumWidth(556)
        self.setMaximumHeight(300)

    def rate_display_item(self, item):
        Receive_Window = QDialog(mw)
        layout = QHBoxLayout()
        item_widget = self.pokemon_display_item(item)
        layout.addWidget(item_widget)
        Receive_Window.setStyleSheet("background-color: rgb(44,44,44);")
        Receive_Window.setMaximumWidth(512)
        Receive_Window.setMaximumHeight(320)
        Receive_Window.setLayout(layout)
        Receive_Window.show()
    
    def display_item(self):
        Receive_Window = QDialog(mw)
        layout = QHBoxLayout()
        item_widget = self.pokemon_display_item(random_item())
        layout.addWidget(item_widget)
        Receive_Window.setStyleSheet("background-color: rgb(44,44,44);")
        Receive_Window.setMaximumWidth(512)
        Receive_Window.setMaximumHeight(320)
        Receive_Window.setLayout(layout)
        Receive_Window.show()

    def display_badge(self, badge_num):
        Receive_Window = QDialog(mw)
        Receive_Window.setWindowTitle(translator.translate("received_a_badge"))
        layout = QHBoxLayout()
        badge_widget = self.pokemon_display_badge(badge_num)
        layout.addWidget(badge_widget)
        Receive_Window.setStyleSheet("background-color: rgb(44,44,44);")
        Receive_Window.setMaximumWidth(512)
        Receive_Window.setMaximumHeight(320)
        Receive_Window.setLayout(layout)
        Receive_Window.show()

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

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def closeEvent(self,event):
        self.pkmn_window = False

# Create an instance of the MainWindow
test_window = TestWindow(main_pokemon, enemy_pokemon, settings_obj)

#Test window
def rate_this_addon():
    global rate_this
    # Load rate data
    with open(rate_path, "r", encoding="utf-8") as file:
        rate_data = json.load(file)
        rate_this = rate_data.get("rate_this", False)
    
    # Check if rating is needed
    if not rate_this:
        rate_window = QDialog()
        rate_window.setWindowTitle("Please Rate this Addon!")
        
        layout = QVBoxLayout(rate_window)
        
        text_label = QLabel(rate_addon_text_label)
        layout.addWidget(text_label)
        
        # Rate button
        rate_button = QPushButton("Rate Now")
        dont_show_button = QPushButton("I dont want to rate this addon.")

        def support_button_click():
            support_url = "https://ko-fi.com/unlucky99"
            QDesktopServices.openUrl(QUrl(support_url))
        
        def thankyou_message():
            thankyou_window = QDialog()
            thankyou_window.setWindowTitle("Thank you !") 
            thx_layout = QVBoxLayout(thankyou_window)
            thx_label = QLabel(thankyou_message_text)
            thx_layout.addWidget(thx_label)
            # Support button
            support_button = QPushButton("Support the Author")
            support_button.clicked.connect(support_button_click)
            thx_layout.addWidget(support_button)
            thankyou_window.setModal(True)
            thankyou_window.exec()
        
        def dont_show_this_button():
            rate_window.close()
            rate_data["rate_this"] = True
            # Save the updated data back to the file
            with open(rate_path, 'w') as file:
                json.dump(rate_data, file, indent=4)
            logger.log_and_showinfo("info",dont_show_this_button_text)

        def rate_this_button():
            rate_window.close()
            rate_url = "https://ankiweb.net/shared/review/1908235722"
            QDesktopServices.openUrl(QUrl(rate_url))
            thankyou_message()
            rate_data["rate_this"] = True
            # Save the updated data back to the file
            with open(rate_path, 'w') as file:
                json.dump(rate_data, file, indent=4)
                test_window.rate_display_item("potion")
                # add item to item list
                give_item("potion")
        rate_button.clicked.connect(rate_this_button)
        layout.addWidget(rate_button)

        dont_show_button.clicked.connect(dont_show_this_button)
        layout.addWidget(dont_show_button)
        
        # Support button
        support_button = QPushButton("Support the Author")
        support_button.clicked.connect(support_button_click)
        layout.addWidget(support_button)
        
        # Make the dialog modal to wait for user interaction
        rate_window.setModal(True)
        
        # Execute the dialog
        rate_window.exec()


if database_complete:
    with open(badgebag_path, "r", encoding="utf-8") as json_file:
        badge_list = json.load(json_file)
        if len(badge_list) > 2:
            rate_this_addon()

#Badges needed for achievements:
with open(badges_list_path, "r", encoding="utf-8") as json_file:
    badges = json.load(json_file)

achievements = {str(i): False for i in range(1, 69)}

def check_badges(achievements):
        with open(badgebag_path, "r", encoding="utf-8") as json_file:
            badge_list = json.load(json_file)
            for badge_num in badge_list:
                achievements[str(badge_num)] = True
        return achievements

def check_for_badge(achievements, rec_badge_num):
        achievements = check_badges(achievements)
        if achievements[str(rec_badge_num)] is False:
            got_badge = False
        else:
            got_badge = True
        return got_badge
        
def save_badges(badges_collection):
        with open(badgebag_path, 'w') as json_file:
            json.dump(badges_collection, json_file)

achievements = check_badges(achievements)

def receive_badge(badge_num,achievements):
    achievements = check_badges(achievements)
    #for badges in badge_list:
    achievements[str(badge_num)] = True
    badges_collection = []
    for num in range(1,69):
        if achievements[str(num)] is True:
            badges_collection.append(int(num))
    save_badges(badges_collection)
    return achievements


class StarterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        #self.update()

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
        logger.log_and_showinfo("info","You have chosen your Starter Pokemon ! \n You can now close this window ! \n Please restart your Anki to restart your Pokemon Journey!")
        global achievments
        check = check_for_badge(achievements,7)
        if check is False:
            receive_badge(7,achievements)
            test_window.display_badge(7)
    
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
        logger.log_and_showinfo("info","You have received your Fossil Pokemon ! \n You can now close this window !")
        global achievments
        check = check_for_badge(achievements,19)
        if check is False:
            receive_badge(19,achievements)
            test_window.display_badge(19)

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
        custom_font = load_custom_font(int(28), int(settings_obj.get("misc.language",11)))
        message_box_text = "Choose your Starter Pokemon"
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(110, 310, message_box_text)
        custom_font = load_custom_font(int(20), int(settings_obj.get("misc.language",11)))
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
        custom_font = load_custom_font(int(32), int(settings_obj.get("misc.language",11)))
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
        custom_font = load_custom_font(int(32), int(settings_obj.get("misc.language",11)))
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

class EvoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.logger = logger

    def init_ui(self):
        basic_layout = QVBoxLayout()
        self.setWindowTitle('Your Pokemon is about to Evolve')
        self.setLayout(basic_layout)

    def open_dynamic_window(self):
        self.show()

    def display_evo_pokemon(self, prevo_id, evo_id):
        self.clear_layout(self.layout())
        layout = self.layout()
        pkmn_label = self.pokemon_display_evo(prevo_id, evo_id)
        layout.addWidget(pkmn_label)
        self.setStyleSheet("background-color: rgb(14,14,14);")
        self.setLayout(layout)
        self.setMaximumWidth(500)
        self.setMaximumHeight(300)
        self.show()

    def pokemon_display_evo(self, prevo_id, evo_id):
        bckgimage_path = addon_dir / "addon_sprites" / "starter_screen" / "bg.png"
        prevo_name = return_name_for_id(prevo_id)
        evo_name = return_name_for_id(evo_id)

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        # Display the Pokémon image
        image_path = frontdefault / f"{evo_id}.png"
        image_label = QLabel()
        image_pixmap = QPixmap()
        image_pixmap.load(str(image_path))
        image_pixmap = resize_pixmap_img(image_pixmap, 250)

        # Merge the background image and the Pokémon image
        merged_pixmap = QPixmap(pixmap_bckg.size())
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        #merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)
        painter.drawPixmap(125,10,image_pixmap)

        # custom font
        custom_font = load_custom_font(int(20), int(settings_obj.get("misc.language",11)))
        message_box_text = f"{(prevo_name).capitalize()} has evolved to {(evo_name).capitalize()} !"
        self.logger.log("game", message_box_text)
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

    def display_pokemon_evo(self, individual_id, prevo_id, evo_id):
        self.setMaximumWidth(600)
        self.setMaximumHeight(530)
        self.clear_layout(self.layout())
        layout = self.layout()
        pokemon_images, evolve_button, dont_evolve_button = self.pokemon_display_evo_pokemon(individual_id, prevo_id, evo_id)
        layout.addWidget(pokemon_images)
        layout.addWidget(evolve_button)
        layout.addWidget(dont_evolve_button)
        self.setStyleSheet("background-color: rgb(44,44,44);")
        self.setLayout(layout)
        self.show()

    def pokemon_display_evo_pokemon(self, individual_id, prevo_id, evo_id):
        # Update mainpokemon_evolution and handle evolution logic
        prevo_name = return_name_for_id(prevo_id)
        evo_name = return_name_for_id(evo_id)
        
        # Display the Pokémon image
        pkmnimage_path = frontdefault / f"{prevo_id}.png"
        pkmnimage_path2 = frontdefault / f"{(evo_id)}.png"
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
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        #merged_pixmap.fill(Qt.transparent)
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
        pen.setColor(QColor(255, 255, 255))
        painter.setPen(pen)
        painter.drawText(150,35,f"{prevo_name.capitalize()} is evolving to {evo_name.capitalize()}")
        painter.drawText(95,430,"Please Choose to Evolve Your Pokemon or Cancel Evolution")
        # Capitalize the first letter of the Pokémon's name
        #name_label = QLabel(capitalized_name)
        painter.end()
        # Capitalize the first letter of the Pokémon's name

        # Create buttons for catching and killing the Pokémon
        evolve_button = QPushButton("Evolve Pokémon")
        dont_evolve_button = QPushButton("Cancel Evolution")
        qconnect(evolve_button.clicked, lambda: evolve_pokemon(individual_id, prevo_name, evo_id, evo_name))
        qconnect(dont_evolve_button.clicked, lambda: cancel_evolution(individual_id, prevo_id))

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

if database_complete:
    if mypokemon_path.is_file() is False:
        starter_window.display_starter_pokemon()
    else:
        with open(mypokemon_path, "r", encoding="utf-8") as file:
            pokemon_list = json.load(file)
            if not pokemon_list :
                starter_window.display_starter_pokemon()

eff_chart = TableWidget()
pokedex = Pokedex_Widget()
gen_id_chart = IDTableWidget()

license = License()

credits = Credits()

count_items_and_rewrite(itembag_path)

UserRole = 1000  # Define custom role

class ItemWindow(QWidget):
    def __init__(self, logger, main_pokemon, enemy_pokemon, itembag_path):
        super().__init__()
        self.itembag_path = itembag_path
        self.logger=logger
        self.read_item_file()
        self.initUI()
        self.main_pokemon = main_pokemon
        self.enemy_pokemon = enemy_pokemon

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
            'premier-ball': 8,    # Same as Poké Ball, but it’s a special ball
            'quick-ball': 13,     # High chance if used at the start of battle
            'repeat-ball': 12,    # Higher chance on Pokémon that have been caught before
            'safari-ball': 8,     # Used in Safari Zone, with a fixed catch rate
            'smoke-ball': 1,      # Used to flee from wild battles, no catch chance
            'timer-ball': 13,     # Higher chance the longer the battle goes
            'ultra-ball': 13      # Increased catch rate (original was 10, now 13)
        }
        
        self.evolution_items = {}
        self.tm_hm_list = {}

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
        self.contentWidget.setLayout(self.contentLayout)

        # Add the content widget to the scroll area
        self.scrollArea.setWidget(self.contentWidget)

        # Add the scroll area to the main layout
        self.layout.addWidget(self.scrollArea)
        self.setLayout(self.layout)
        self.resize(600, 500)

    def renewWidgets(self):
        self.read_item_file()
        # Clear the existing widgets from the content layout
        for i in reversed(range(self.contentLayout.count())):
            widget = self.contentLayout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        row, col = 0, 0
        max_items_per_row = 3

        if not self.itembag_list:  # Simplified check
            empty_label = QLabel("You don't own any items yet.")
            self.contentLayout.addWidget(empty_label, 1, 1)
        else:
            for item in self.itembag_list:
                item_widget = self.ItemLabel(item["item"], item["quantity"])
                self.contentLayout.addWidget(item_widget, row, col)
                col += 1
                if col >= max_items_per_row:
                    row += 1
                    col = 0
    
    def filter_items(self):
        self.read_item_file()
        search_text = self.search_edit.text().lower()
        category_index = self.category.currentIndex()
        # Clear the existing widgets from the content layout
        for i in reversed(range(self.contentLayout.count())):
            widget = self.contentLayout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        row, col = 0, 0
        max_items_per_row = 3

        try:
            if not self.itembag_list:  # Simplified check
                empty_label = QLabel("Empty Search")
                self.contentLayout.addWidget(empty_label, 1, 1)
            else:
                # Filter items based on category index
                if category_index == 1:  # Fossils
                    filtered_items = [
                        item for item in self.itembag_list 
                        if isinstance(item, dict) and "item" in item and item["item"] in self.fossil_pokemon and search_text in item["item"].lower()
                    ]
                elif category_index == 2:  # TMs and HMs
                    filtered_items = [
                        item for item in self.itembag_list 
                        if isinstance(item, dict) and "item" in item and item["item"] in self.tm_hm_list and search_text in item["item"].lower()
                    ]
                elif category_index == 3:  # Heal items
                    filtered_items = [
                        item for item in self.itembag_list 
                        if isinstance(item, dict) and "item" in item and item["item"] in self.hp_heal_items and search_text in item["item"].lower()
                    ]
                elif category_index == 4:  # Evolution items
                    filtered_items = [
                        item for item in self.itembag_list 
                        if isinstance(item, dict) and "item" in item and item["item"] in self.evolution_items and search_text in item["item"].lower()
                    ]
                elif category_index == 5: # Pokeballs
                    filtered_items = [
                        item for item in self.itembag_list 
                        if isinstance(item, dict) and "item" in item and item["item"] in self.pokeball_chances and search_text in item["item"].lower()
                    ]
                else:
                    filtered_items = [item for item in self.itembag_list if search_text in item["item"].lower()]
        except Exception as e:
            filtered_items = []    
            self.logger.log_and_showinfo("error", f"Error filtering items: {e}")

        for item in filtered_items:
            item_widget = self.ItemLabel(item["item"], item["quantity"])
            self.contentLayout.addWidget(item_widget, row, col)
            col += 1
            if col >= max_items_per_row:
                row += 1
                col = 0

    def ItemLabel(self, item_name, quantity):
        item_file_path = items_path / f"{item_name}.png"
        item_frame = QVBoxLayout()  # itemframe
        info_item_button = QPushButton("More Info")
        info_item_button.clicked.connect(lambda: self.more_info_button_act(item_name))
        item_name_for_label = item_name.replace("-", " ")  # Remove hyphens from item_name
        item_name_label = QLabel(f"{item_name_for_label.capitalize()} x{quantity}")  # Display quantity
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
            use_item_button.clicked.connect(lambda: self.Check_Heal_Item(self.main_pokemon.name, hp_heal, item_name))
        elif item_name in self.fossil_pokemon:
            fossil_id = self.fossil_pokemon[item_name]
            fossil_pokemon_name = search_pokedex_by_id(fossil_id)
            use_item_button = QPushButton(f"Evolve Fossil to {fossil_pokemon_name.capitalize()}")
            use_item_button.clicked.connect(lambda: self.Evolve_Fossil(item_name, fossil_id, fossil_pokemon_name))
        elif item_name in self.pokeball_chances:
            use_item_button = QPushButton("Try catching wild Pokemon")
            use_item_button.clicked.connect(lambda: self.Handle_Pokeball(item_name))
        else:
            use_item_button = QPushButton("Evolve Pokemon")
            use_item_button.clicked.connect(
                lambda: self.Check_Evo_Item(comboBox.itemData(comboBox.currentIndex(), role=UserRole), comboBox.itemData(comboBox.currentIndex(), role=UserRole + 1), item_name)
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
                        id = pokemon.get('id', None)
                        if individual_id and id:  # Ensure the ID exists
                            # Add Pokémon name to comboBox
                            comboBox.addItem(pokemon_name)
                            # Store both individual_id and id as separate data using roles
                            comboBox.setItemData(comboBox.count() - 1, individual_id, role=UserRole)
                            comboBox.setItemData(comboBox.count() - 1, id, role=UserRole + 1)
        except Exception as e:
            self.logger.log_and_showinfo("error", f"Error loading Pokémon list: {e}")
            
    def Evolve_Fossil(self, item_name, fossil_id, fossil_poke_name):
        starter_window.display_fossil_pokemon(fossil_id, fossil_poke_name)
        save_fossil_pokemon(fossil_id)
        self.delete_item(item_name)
    
    def modified_pokeball_chances(self, item_name, catch_chance):
        # Adjust catch chance based on Pokémon type and Poké Ball
        if item_name == 'net-ball' and ('water' in self.enemy_pokemon.type or 'bug' in self.enemy_pokemon.type):
            catch_chance += 10  # Additional 10% for Water or Bug-type Pokémon
            self.logger.log("game",f"{item_name} gets a bonus for Water/Bug-type Pokémon!")
        
        elif item_name == 'iron-ball' and 'steel' in self.enemy_pokemon.type:
            catch_chance += 10  # Additional 10% for Steel-type Pokémon
            self.logger.log("game",f"{item_name} gets a bonus for Steel-type Pokémon!")
        
        elif item_name == 'dive-ball' and 'water' in self.enemy_pokemon.type:
            catch_chance += 10  # Additional 10% for Water-type Pokémon
            self.logger.log("game",f"{item_name} gets a bonus for Water-type Pokémon!")

        return catch_chance

    def Handle_Pokeball(self, item_name):
        # Check if the item exists in the pokeball chances
        if item_name in self.pokeball_chances:
            catch_chance = self.pokeball_chances[item_name]
            catch_chance = self.modified_pokeball_chances(item_name, catch_chance)
            
            # Simulate catching the Pokémon based on the catch chance
            if random.randint(1, 100) <= catch_chance:
                # Pokémon caught successfully
                self.logger.log_and_showinfo("info",f"{item_name} successfully caught the Pokémon!")
                self.delete_item(item_name)  # Delete the Poké Ball after use
            else:
                # Pokémon was not caught
                self.logger.log_and_showinfo("info",f"{item_name} failed to catch the Pokémon.")
                self.delete_item(item_name)  # Still delete the Poké Ball after use
        else:
            self.logger.log_and_showinfo("error",f"{item_name} is not a valid Poké Ball!")

    def delete_item(self, item_name):
        self.read_item_file()
        
        for item in self.itembag_list:
            # Check if the item exists and if the name matches
            if item['item'] == item_name:
                # Decrease the quantity by 1
                item['quantity'] -= 1
                
                # If quantity reaches 0, remove the item from the list
                if item['quantity'] == 0:
                    self.itembag_list.remove(item)
        
        self.write_item_file()
        self.renewWidgets()

    def Check_Heal_Item(self, prevo_name, heal_points, item_name):
        global achievments
        check = check_for_badge(achievements,20)
        if check is False:
            receive_badge(20,achievements)
            test_window.display_badge(20)
        if item_name == "fullrestore" or "maxpotion":
            heal_points = self.main_pokemon.max_hp
        self.main_pokemon.hp += heal_points
        if self.main_pokemon.hp > (self.main_pokemon.max_hp):
            self.main_pokemon.hp = self.main_pokemon.max_hp
        self.delete_item(item_name)
        play_effect_sound("HpHeal")
        self.logger.log_and_showinfo("info",f"{prevo_name} was healed for {heal_points}")

    def Check_Evo_Item(self, individual_id, prevo_id, item_name):
        try:
            item_id = return_id_for_item_name(item_name)
            evo_id = check_evolution_by_item(prevo_id, item_id)
            if evo_id is not None:
                # Perform your action when the item matches the Pokémon's evolution item
                self.logger.log_and_showinfo("info","Pokemon Evolution is fitting !")
                evo_window.display_pokemon_evo(individual_id, prevo_id, evo_id )
            else:
                self.logger.log_and_showinfo("info","This Pokemon does not need this item.")
        except Exception as e:
            showWarning(f"{e}")
    
    def write_item_file(self):
        with open(itembag_path, 'w') as json_file:
            json.dump(self.itembag_list, json_file)

    def read_item_file(self):
        """
        Reads the list from the JSON file. If the file contains malformed items,
        it tries to fix them by converting strings to the correct structure.
        """
        try:
            with open(self.itembag_path, "r", encoding="utf-8") as json_file:
                self.itembag_list = json.load(json_file)
        except json.JSONDecodeError:
            self.logger.log("error", "Malformed JSON detected. Attempting to fix.")
            self.itembag_list = self._fix_and_load_items()
            self.write_item_file()

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

    def more_info_button_act(self, item_name):
        description = get_id_and_description_by_item_name(item_name)
        self.logger.log_and_showinfo("info",f"{description}")


def get_id_and_description_by_item_name(item_name):
    item_name = capitalize_each_word(item_name)
    item_id_mapping = read_csv_file(csv_file_items)
    item_id = item_id_mapping.get(item_name.lower())
    if item_id is None:
        return None, None
    descriptions = read_descriptions_csv(csv_file_descriptions)
    key = (item_id, 11, 9)  # Assuming version_group_id 11 and language_id 9
    description = descriptions.get(key, None)
    return description
    
item_window = ItemWindow(
    logger=logger,
    main_pokemon=main_pokemon,
    enemy_pokemon=enemy_pokemon,
    itembag_path=itembag_path
)

class AchievementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.read_item_file()
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QIcon(str(icon_path)))
        self.setWindowTitle("Achievements")
        self.layout = QVBoxLayout()  # Main layout is now a QVBoxLayout

        # Create the scroll area and its properties
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)

        # Create a widget and layout for content inside the scroll area
        self.contentWidget = QWidget()
        self.contentLayout = QGridLayout()  # The layout for items
        self.contentWidget.setLayout(self.contentLayout)

        # Add the content widget to the scroll area
        self.scrollArea.setWidget(self.contentWidget)

        # Add the scroll area to the main layout
        self.layout.addWidget(self.scrollArea)
        self.setLayout(self.layout)

    def renewWidgets(self):
        self.read_item_file()
        # Clear the existing widgets from the layout
        for i in reversed(range(self.contentLayout.count())):
            widget = self.contentLayout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        row, col = 0, 0
        max_items_per_row = 4
        if self.badge_list is None or not self.badge_list:  # Wenn None oder leer
            empty_label = QLabel("You dont own any badges yet.")
            self.contentLayout.addWidget(empty_label, 1, 1)
        else:
            for badge_num in self.badge_list:
                item_widget = self.BadgesLabel(badge_num)
                self.contentLayout.addWidget(item_widget, row, col)
                col += 1
                if col >= max_items_per_row:
                    row += 1
                    col = 0
        self.resize(700, 400)

    def BadgesLabel(self, badge_num):
        badge_path = badges_path / f"{str(badge_num)}.png"
        frame = QVBoxLayout() #itemframe
        achievement_description = f"{(badges[str(badge_num)])}"
        badges_name_label = QLabel(f"{achievement_description}")
        badges_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if badge_num < 15:
            border_width = 93  # Example width
            border_height = 93  # Example height
            border_color = QColor('black')
            border_pixmap = QPixmap(border_width, border_height)
            border_pixmap.fill(border_color)
            desired_width = 89  # Example width
            desired_height = 89  # Example height
            background_color = QColor('white')
            background_pixmap = QPixmap(desired_width, desired_height)
            background_pixmap.fill(background_color)
            picture_pixmap = QPixmap(str(badge_path))
            painter = QPainter(border_pixmap)
            painter.drawPixmap(2, 2, background_pixmap)
            painter.drawPixmap(5,5, picture_pixmap)
            painter.end()  # Finish drawing
            picture_label = QLabel()
            picture_label.setPixmap(border_pixmap)
        else:
            picture_pixmap = QPixmap(str(badge_path))
            # Scale the QPixmap to fit within a maximum size while maintaining the aspect ratio
            max_width, max_height = 100, 100  # Example maximum sizes
            scaled_pixmap = picture_pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            picture_label = QLabel()
            picture_label.setPixmap(scaled_pixmap)
        picture_label.setStyleSheet("border: 2px solid #3498db; border-radius: 5px; padding: 5px;")
        picture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame.addWidget(picture_label)
        frame.addWidget(badges_name_label)
        frame_widget = QWidget()
        frame_widget.setLayout(frame)

        return frame_widget

    def read_item_file(self):
        # Read the list from the JSON file
        with open(badgebag_path, "r", encoding="utf-8") as json_file:
            self.badge_list = json.load(json_file)

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

achievement_bag = AchievementWindow()

version_dialog = Version_Dialog()

#buttonlayout
from .menu_buttons import create_menu_actions

# Create menu actions
# Create menu actions
actions = create_menu_actions(
    database_complete,
    online_connectivity,
    pokecollection_win,
    item_window,
    test_window,
    achievement_bag,
    open_team_builder,
    export_to_pkmn_showdown,
    export_all_pkmn_showdown,
    flex_pokemon_collection,
    eff_chart,
    gen_id_chart,
    credits,
    license,
    open_help_window,
    report_bug,
    rate_addon_url,
    version_dialog,
    trainer_card,
    ankimon_tracker_window,
    logger,
    data_handler_window,
    settings_window,
    shop_manager,
    pokedex_window,
    settings_obj.get("controls.key_for_opening_closing_ankimon","Ctrl+Shift+P"),
    join_discord_url,
    open_leaderboard_url,
    settings_obj
)

    #https://goo.gl/uhAxsg
    #https://www.reddit.com/r/PokemonROMhacks/comments/9xgl7j/pokemon_sound_effects_collection_over_3200_sfx/
    #https://archive.org/details/pokemon-dp-sound-library-disc-2_202205
    #https://www.sounds-resource.com/nintendo_switch/pokemonswordshield/

# Define lists to hold hook functions
catch_pokemon_hooks = []
defeat_pokemon_hooks = []

# Function to add hooks to catch_pokemon event
def add_catch_pokemon_hook(func):
    catch_pokemon_hooks.append(func)

# Function to add hooks to defeat_pokemon event
def add_defeat_pokemon_hook(func):
    defeat_pokemon_hooks.append(func)

# Custom function that triggers the catch_pokemon hook
def CatchPokemonHook():
    if enemy_pokemon.hp < 1:
        catch_pokemon("")
    for hook in catch_pokemon_hooks:
        hook()

# Custom function that triggers the defeat_pokemon hook
def DefeatPokemonHook():
    if enemy_pokemon.hp < 1:
        kill_pokemon()
        new_pokemon()
    for hook in defeat_pokemon_hooks:
        hook()

# Hook to expose the function
def on_profile_loaded():
    mw.defeatpokemon = DefeatPokemonHook
    mw.catchpokemon = CatchPokemonHook
    mw.add_catch_pokemon_hook = add_catch_pokemon_hook
    mw.add_defeat_pokemon_hook = add_defeat_pokemon_hook

# Add hook to run on profile load
addHook("profileLoaded", on_profile_loaded)

def catch_shorcut_function():
    if enemy_pokemon.hp > 1:
        tooltip("You only catch a pokemon once its fained !")
    else:
        catch_pokemon("")

def defeat_shortcut_function():
    if enemy_pokemon.hp > 1:
        tooltip("Wild pokemon has to be fainted to defeat it !")
    else:
        kill_pokemon()
        new_pokemon()

catch_shortcut = catch_shortcut.lower()
defeat_shortcut = defeat_shortcut.lower()
#// adding shortcuts to _shortcutKeys function in anki
def _shortcutKeys_wrap(self, _old):
    original = _old(self)
    original.append((catch_shortcut, lambda: catch_shorcut_function()))
    original.append((defeat_shortcut, lambda: defeat_shortcut_function()))
    return original

Reviewer._shortcutKeys = wrap(Reviewer._shortcutKeys, _shortcutKeys_wrap, 'around')

if reviewer_buttons is True:
    #// Choosing styling for review other buttons in reviewer bottombar based on chosen style
    Review_linkHandelr_Original = Reviewer._linkHandler
    # Define the HTML and styling for the custom button
    def custom_button():
        return f"""<button title="Shortcut key: C" onclick="pycmd('catch');" {button_style}>Catch</button>"""

    # Update the link handler function to handle the custom button action
    def linkHandler_wrap(reviewer, url):
        if url == "catch":
            catch_shorcut_function()
        elif url == "defeat":
            defeat_shortcut_function()
        else:
            Review_linkHandelr_Original(reviewer, url)

    def _bottomHTML(self) -> str:
        return _bottomHTML_template % dict(
            edit=tr.studying_edit(),
            editkey=tr.actions_shortcut_key(val="E"),
            more=tr.studying_more(),
            morekey=tr.actions_shortcut_key(val="M"),
            downArrow=downArrow(),
            time=self.card.time_taken() // 1000,
            CatchKey=tr.actions_shortcut_key(val=f"{catch_shortcut}"),
            DefeatKey=tr.actions_shortcut_key(val=f"{defeat_shortcut}"),
        )

    # Replace the current HTML with the updated HTML
    Reviewer._bottomHTML = _bottomHTML  # Assuming you have access to self in this context
    # Replace the original link handler function with the modified one
    Reviewer._linkHandler = linkHandler_wrap

if settings_obj.get("misc.discord_rich_presence",False) == True:
    from .functions.discord_function import *  # Import necessary functions for Discord integration

    client_id = '1319014423876075541'  # Replace with your actual client ID
    large_image_url = "https://raw.githubusercontent.com/Unlucky-Life/ankimon/refs/heads/main/src/Ankimon/ankimon_logo.png"  # URL for the large image
    mw.ankimon_presence = DiscordPresence(client_id, large_image_url, ankimon_tracker_obj, logger, settings_obj)  # Establish connection and get the presence instance

    # Hook functions for Anki
    def on_reviewer_initialized(rev, card, ease):
        if mw.ankimon_presence:
            if mw.ankimon_presence.loop is False:
                mw.ankimon_presence.loop = True
                mw.ankimon_presence.start()
        else:
            client_id = '1319014423876075541'  # Replace with your actual client ID
            large_image_url = "https://raw.githubusercontent.com/Unlucky-Life/ankimon/refs/heads/main/src/Ankimon/ankimon_logo.png"  # URL for the large image
            mw.ankimon_presence = DiscordPresence(client_id, large_image_url, ankimon_tracker_obj, logger, settings_obj)  # Establish connection and get the presence instance
            mw.ankimon_presence.loop = True
            mw.ankimon_presence.start()
            
    def on_reviewer_will_end(*args):
        mw.ankimon_presence.loop = False
        mw.ankimon_presence.stop_presence()

    # Register the hook functions with Anki's GUI hooks
    gui_hooks.reviewer_did_answer_card.append(on_reviewer_initialized)
    gui_hooks.reviewer_will_end.append(mw.ankimon_presence.stop_presence)
    gui_hooks.sync_did_finish.append(mw.ankimon_presence.stop)
