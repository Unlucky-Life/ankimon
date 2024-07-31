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

import base64
import csv
import distutils.dir_util
import json
import os
import pathlib
import platform
import random
import shutil
import sys
import threading
import time
import wave
from pathlib import Path
from typing import List, Optional, Union

import anki
import aqt
import markdown
import requests
from anki.collection import Collection
from anki.hooks import addHook, wrap
from aqt import editor, gui_hooks, mw, utils
from aqt.qt import *
from aqt.qt import (QAction, QDialog, QFont, QGridLayout, QLabel, QPainter,
                    QPixmap, Qt, QVBoxLayout, QWidget)
from aqt.reviewer import Reviewer
from aqt.utils import *
from PyQt6.QtCore import *
#from PyQt6.QtCore import QUrl
from PyQt6.QtGui import *
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWebEngineWidgets import *
from PyQt6.QtWidgets import *
#from PyQt6.QtWidgets import QAction
from PyQt6.QtWidgets import (QApplication, QDialog, QLabel, QMainWindow,
                             QPushButton, QVBoxLayout, QWidget)

#from .download_pokeapi_db import create_pokeapidb
config = mw.addonManager.getConfig(__name__)
#show config .json file

# Find current directory
addon_dir = Path(__file__).parents[0]
currdirname = addon_dir

def check_folders_exist(parent_directory, folder):
    folder_path = os.path.join(parent_directory, folder)
    return os.path.isdir(folder_path)

def check_file_exists(folder, filename):
    file_path = os.path.join(folder, filename)
    return os.path.isfile(file_path)

#safe route for updates
user_path = addon_dir / "user_files"
user_path_data = addon_dir / "user_files" / "data_files"
user_path_sprites = addon_dir / "user_files" / "sprites"

# Assign Pokemon Image folder directory name
pkmnimgfolder = addon_dir / "user_files" / "sprites"
backdefault = addon_dir / "user_files" / "sprites" / "back_default"
frontdefault = addon_dir / "user_files" / "sprites" / "front_default"
#Assign saved Pokemon Directory
mypokemon_path = addon_dir / "user_files" / "mypokemon.json"
mainpokemon_path = addon_dir / "user_files" / "mainpokemon.json"
battlescene_path = addon_dir / "addon_sprites" / "battle_scenes"
battlescene_path_without_dialog = addon_dir / "addon_sprites" / "battle_scenes_without_dialog"
battle_ui_path = addon_dir / "pkmnbattlescene - UI_transp"
type_style_file = addon_dir / "addon_files" / "types.json"
next_lvl_file_path = addon_dir / "addon_files" / "ExpPokemonAddon.csv"
berries_path = addon_dir / "user_files" / "sprites" / "berries"
background_dialog_image_path  = addon_dir / "background_dialog_image.png"
pokedex_image_path = addon_dir / "addon_sprites" / "pokedex_template.jpg"
evolve_image_path = addon_dir / "addon_sprites" / "evo_temp.jpg"
learnset_path = addon_dir / "user_files" / "data_files" / "learnsets.json"
pokedex_path = addon_dir / "user_files" / "data_files" / "pokedex.json"
moves_file_path = addon_dir / "user_files" / "data_files" / "moves.json"
items_path = addon_dir / "user_files" / "sprites" / "items"
badges_path = addon_dir / "user_files" / "sprites" / "badges"
itembag_path = addon_dir / "user_files" / "items.json"
badgebag_path = addon_dir / "user_files" / "badges.json"
pokenames_lang_path = addon_dir / "user_files" / "data_files" / "pokemon_species_names.csv"
pokedesc_lang_path = addon_dir / "user_files" / "data_files" / "pokemon_species_flavor_text.csv"
pokeapi_db_path = user_path_data / "pokeapi_db.json"
starters_path = addon_dir / "addon_files" / "starters.json"
eff_chart_html_path = addon_dir / "addon_files" / "eff_chart_html.html"
effectiveness_chart_file_path = addon_dir / "addon_files" / "eff_chart.json"
table_gen_id_html_path = addon_dir / "addon_files" / "table_gen_id.html"
icon_path = addon_dir / "addon_files" / "pokeball.png"
sound_list_path = addon_dir / "addon_files" / "sound_list.json"
badges_list_path = addon_dir / "addon_files" / "badges.json"
items_list_path = addon_dir / "addon_files" / "items.json"
rate_path = addon_dir / "user_files" / "rate_this.json"
csv_file_items = addon_dir / "user_files" / "data_files" / "item_names.csv"
csv_file_descriptions = addon_dir / "user_files" / "data_files" / "item_flavor_text.csv"


items_list = []
with open(items_list_path, 'r') as file:
    items_list = json.load(file)



#effect sounds paths
hurt_normal_sound_path = addon_dir / "addon_sprites" / "sounds" / "HurtNormal.mp3"
hurt_noteff_sound_path = addon_dir / "addon_sprites" / "sounds" / "HurtNotEffective.mp3"
hurt_supereff_sound_path = addon_dir / "addon_sprites" / "sounds" / "HurtSuper.mp3"
ownhplow_sound_path = addon_dir / "addon_sprites" / "sounds" / "OwnHpLow.mp3"
hpheal_sound_path = addon_dir / "addon_sprites" / "sounds" / "HpHeal.mp3"
fainted_sound_path = addon_dir / "addon_sprites" / "sounds" / "Fainted.mp3"

with open(sound_list_path, 'r') as json_file:
    sound_list = json.load(json_file)

#pokemon species id files
pokemon_species_normal_path = addon_dir / "user_files" / "pkmn_data" / "normal.json"
pokemon_species_legendary_path = addon_dir / "user_files" / "pkmn_data" / "legendary.json"
pokemon_species_ultra_path = addon_dir / "user_files" / "pkmn_data" / "ultra.json"
pokemon_species_mythical_path = addon_dir / "user_files" / "pkmn_data" / "mythical.json"
pokemon_species_baby_path = addon_dir / "user_files" / "pkmn_data" / "baby.json"

# Get the profile folder
profilename = mw.pm.name
#profilefolder = Path(mw.pm.profileFolder())
#mediafolder = Path(mw.col.media.dir())
font_path = addon_dir / "addon_files"

mainpkmn = 0
mainpokemon_hp = 100
#test mainpokemon
#battlescene_file = "pkmnbattlescene.png"
pokemon_encounter = 0

# check for sprites, data
sound_files = check_folders_exist(pkmnimgfolder, "sounds")
back_sprites = check_folders_exist(pkmnimgfolder, "back_default")
back_default_gif = check_folders_exist(pkmnimgfolder, "back_default_gif")
front_sprites = check_folders_exist(pkmnimgfolder, "front_default")
front_default_gif = check_folders_exist(pkmnimgfolder, "front_default_gif")
item_sprites = check_folders_exist(pkmnimgfolder, "items")
badges_sprites = check_folders_exist(pkmnimgfolder, "badges")
berries_sprites = check_folders_exist(addon_dir, "berries")
poke_api_data = check_file_exists(user_path_data, "pokeapi_db.json")
pokedex_data = check_file_exists(user_path_data, "pokedex.json")
learnsets_data = check_file_exists(user_path_data, "learnsets.json")
poke_api_data = check_file_exists(user_path_data, "pokeapi_db.json")
pokedex_data = check_file_exists(user_path_data, "pokedex.json")
moves_data = check_file_exists(user_path_data, "moves.json")

if (
    pokedex_data
    and learnsets_data
    and moves_data
    and back_sprites
    and front_sprites
    and front_default_gif
    and back_default_gif
    and item_sprites
    and badges_sprites == True
):    database_complete = True
else:
    database_complete = False

if database_complete == True:
    owned_pokemon_ids = {}

    def extract_ids_from_file():
        global owned_pokemon_ids, mypokemon_path
        filename = mypokemon_path
        with open(filename, 'r') as file:
            data = json.load(file)
            ids = [character['id'] for character in data]
            owned_pokemon_ids = ids

    extract_ids_from_file()

    def check_pokecoll_in_list(id):
        extract_ids_from_file()
        global owned_pokemon_ids
        pokeball = False
        for num in owned_pokemon_ids:
            if num == id:
                pokeball = True
                break
        return pokeball

class CheckFiles(QDialog):
    def __init__(self):
        super().__init__()
        check_files_message = "Ankimon Files:"
        if database_complete != True:
            check_files_message += " \n Resource Files incomplete. \n  Please go to Ankimon => 'Download Resources' to download the needed files"
        check_files_message += "\n Once all files have been downloaded: Restart Anki"
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

if mainpokemon_path.is_file():
    with open(mainpokemon_path, "r") as json_file:
        main_pokemon_data = json.load(json_file)
        if not main_pokemon_data or main_pokemon_data is None:
            mainpokemon_empty = True
        else:
            mainpokemon_empty = False

window = None
gender = None
card_counter = -1
item_receive_value = random.randint(30, 120)
system_name = platform.system()

if system_name == "Windows" or system_name == "Linux":
    system = "win_lin"
elif system_name == "Darwin":
    # Open file explorer at the specified path in macOS
    system = "mac"
pop_up_dialog_message_on_defeat = config["pop_up_dialog_message_on_defeat"]
reviewer_text_message_box = config["reviewer_text_message_box"]
reviewer_text_message_box_time = config["reviewer_text_message_box_time"] #time in seconds for text message
reviewer_text_message_box_time = reviewer_text_message_box_time * 1000 #times 1000 for s => ms
cards_per_round = config["cards_per_round"]
reviewer_image_gif = config["reviewer_image_gif"]
sounds = config["sounds"]
battle_sounds = config["battle_sounds"]
language = config["language"]
ankimon_key = config["key_for_opening_closing_ankimon"]
show_mainpkmn_in_reviewer = config["show_mainpkmn_in_reviewer"] #0 is off, 1 normal, 2 battle mode
xp_bar_config = config["xp_bar_config"]
review_hp_bar_thickness = config["review_hp_bar_thickness"] #2 = 8px, 3# 12px, 4# 16px, 5# 20px
hp_bar_thickness = review_hp_bar_thickness * 4
hp_bar_config = config["hp_bar_config"] #2 = 8px, 3# 12px, 4# 16px, 5# 20px
xp_bar_location = config["xp_bar_location"] #1 top, 2 = bottom
ssh = config["ssh"] #for eduroam users - false ; default: true
dmg_in_reviewer = config["dmg_in_reviewer"] #default: false; true = mainpokemon is getting damaged in reviewer for false answers
animate_time = config["animate_time"] #default: true; false = animate for 0.8 seconds
view_main_front = config["view_main_front"] #default: true => -1; false = 1
gif_in_collection = config["gif_in_collection"] #default: true => -1; false = 1
sound_effects = config["sound_effects"] #default: false; true = sound_effects on
styling_in_reviewer = config["styling_in_reviewer"] #default: true; false = no styling in reviewer
no_more_news = config["YouShallNotPass_Ankimon_News"] #default: false; true = no more news
automatic_battle = config["automatic_battle"] #default: 0; 1 = catch_pokemon; 2 = defeat_pokemon
defeat_shortcut = config["defeat_key"] #default: 5; ; Else if not 5 => controll + Key for capture
catch_shortcut = config["catch_key"] #default: 6; Else if not 6 => controll + Key for capture
reviewer_buttons = config["pokemon_buttons"] #default: true; false = no pokemon buttons in reviewer
remove_levelcap = config["misc.remove_level_cap"] #default: false; true = no more news


if sound_effects is True:
    from . import playsound

if view_main_front is True and reviewer_image_gif is True:
    view_main_front = -1
else:
    view_main_front = 1

if animate_time is True:
    animate_time = 0.8
else:
    animate_time = 0

if xp_bar_location == 1:
    xp_bar_location = "top"
    xp_bar_spacer = 0
elif xp_bar_location == 2:
    xp_bar_location = "bottom"
    xp_bar_spacer = 20

if xp_bar_config is False:
    xp_bar_spacer = 0

if hp_bar_config != True:
    hp_only_spacer = 15
    wild_hp_spacer = 65
else:
    hp_only_spacer = 0
    wild_hp_spacer = 0

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
        qconnect(self.sync_local_button.clicked, self.sync_data_to_ankiweb)
        qconnect(self.sync_ankiweb_button.clicked, self.sync_data_to_local)
        # Create a QVBoxLayout instance
        self.layout = QVBoxLayout()
        # Add the QLabel and QPushButtons to the layout
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.sync_local_button)
        self.layout.addWidget(self.sync_ankiweb_button)
        # Set the dialog's layout
        self.setLayout(self.layout)

    def get_pokemon_data(self):
        with open(str(self.mypokemon_path), 'r', encoding='utf-8') as file:
            self.pokemon_collection_sync_data = json.load(file)
        with open(str(self.mainpokemon_path), 'r', encoding='utf-8') as file:
            self.mainpokemon_sync_data = json.load(file)

    def sync_pokemons(self):
        self.mainpokemon_web_data = self.config.get('mainpokemon', '')
        self.pokemon_collection_web_data = self.config.get('pokemon_collection', '')
        #showInfo("Pokémon data synced.")
        #showInfo(f"Mainpokemon {mainpokemon}")
        #showInfo(f"Pokémon Collection {pokemon_collection}")    #function to sync pokemon data to ankiweb and local files
        
        self.get_pokemon_data()

        if self.mainpokemon_web_data != self.mainpokemon_sync_data or self.pokemon_collection_web_data != self.pokemon_collection_sync_data:
            # Show dialog window with two buttons
            self.show()
    
    def sync_data_to_local(self):
        with open(str(self.mypokemon_path), 'w', encoding='utf-8') as file:
            json.dump(self.pokemon_collection_web_data, file, ensure_ascii=False, indent=4)
        with open(str(self.mainpokemon_path), 'w', encoding='utf-8') as file:
            json.dump(self.mainpokemon_web_data, file, ensure_ascii=False, indent=4)
        showInfo("Ankiweb Data synced to local.")
        self.close()
    
    def sync_data_to_ankiweb(self):
        self.config["pokemon_collection"] = self.pokemon_collection_sync_data
        self.config["mainpokemon"] = self.mainpokemon_sync_data
        mw.addonManager.writeConfig(__name__, self.config)
        #config["mainpokemon"] = []
        #config["pokemon_collection"] = []
        showInfo("Local Data synced to AnkiWeb.")
        self.close()

    def sync_on_anki_close(self):
        tooltip("Syncing PokemonData to AnkiWeb")
        self.get_pokemon_data()
        self.config["pokemon_collection"] = self.pokemon_collection_sync_data
        self.config["mainpokemon"] = self.mainpokemon_sync_data
        mw.addonManager.writeConfig(__name__, self.config)

    def modify_json_configuration_on_save(self, text: str) -> str:
        try:
            # Load the JSON text
            config = json.loads(text)
            # Iterate through the configuration and update fields
            #for key in config:
                #if key not in ["mainPokemon", "pokemon_collection"]:
                    #pass
            self.get_pokemon_data()
            # Set mainPokemon and pokemon_collection to predefined values
            config["pokemon_collection"] = self.pokemon_collection_sync_data
            config["mainpokemon"] = self.mainpokemon_sync_data
            self.config = config
            tooltip("Saved Ankimon Configuration, Please Restart Anki")

            # Convert the modified JSON object back to a string
            modified_text = json.dumps(config, indent=4)
            return modified_text

        except json.JSONDecodeError:
            # Handle JSON decoding errors
            print("Invalid JSON format")
            return text

check_data = CheckPokemonData(mainpokemon_path, mypokemon_path, config)

gui_hooks.addon_config_editor_will_save_json.append(check_data.modify_json_configuration_on_save)
gui_hooks.sync_did_finish.append(check_data.sync_on_anki_close)

#dont show all mainpokemon and mypokemon information in config

# Define the hook function
def addon_config_editor_will_display_json(text: str) -> str:
    """
    This function modifies the JSON configuration text before displaying it to the user.
    It replaces the values for the keys "pokemon_collection" and "mainpokemon".
    
    Args:
        text (str): The JSON configuration text.
    
    Returns:
        str: The modified JSON configuration text.
    """
    try:
        # Parse the JSON text
        config = json.loads(text)
        
        if "pokemon_collection" in config:
            del config["pokemon_collection"]
        if "mainpokemon" in config:
            del config["mainpokemon"]
        
        # Convert back to JSON string
        modified_text = json.dumps(config, indent=4)
        return modified_text
    except json.JSONDecodeError:
        # Handle JSON parsing error
        return text
    
#On Save on Config, accept new config and add pokemon collection and mainpokemon to it
gui_hooks.addon_config_editor_will_save_json.append(check_data.modify_json_configuration_on_save)
gui_hooks.addon_config_editor_will_display_json.append(addon_config_editor_will_display_json)

try:
    def test_online_connectivity(url='https://raw.githubusercontent.com/Unlucky-Life/ankimon/main/update_txt.md', timeout=5):
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
except:
    online_connectivity = False

#Connect to GitHub and Check for Notification and HelpGuideChanges
try:
    if ssh != False:
        # Function to check if the content of the two files is the same
        def compare_files(local_content, github_content):
            return local_content == github_content

        # Function to read the content of the local file
        def read_local_file(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            except FileNotFoundError:
                return None

        # Function to write content to a local file
        def write_local_file(file_path, content):
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)

        # Function to check if the file exists on GitHub and read its content
        def read_github_file(url):
            response = requests.get(url)
                
            if response.status_code == 200:
                # File exists, parse the Markdown content
                content = response.text
                html_content = markdown.markdown(content)
                return content, html_content
            else:
                return None, None
            
    if online_connectivity != False:
        if ssh != False:
            # Custom Dialog class
            class UpdateNotificationWindow(QDialog):
                def __init__(self, content):
                    super().__init__()
                    global icon_path
                    self.setWindowTitle("Ankimon Notifications")
                    self.setGeometry(100, 100, 600, 400)

                    layout = QVBoxLayout()
                    self.text_edit = QTextEdit()
                    self.text_edit.setReadOnly(True)
                    self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
                    self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # For horizontal scrollbar, if you want it off
                    self.text_edit.setHtml(content)
                    layout.addWidget(self.text_edit)
                    self.setWindowIcon(QIcon(str(icon_path)))

                    self.setLayout(layout)

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
        showInfo(f"Error in try connect to GitHub: {e}")

##HelpGuide
class HelpWindow(QDialog):
    def __init__(self):
        super().__init__()
        html_content = " "
        global icon_path
        help_local_file_path = addon_dir / "HelpInfos.html"
        try:
            if online_connectivity != False:
                # URL of the file on GitHub
                help_local_file_path = addon_dir / "HelpInfos.html"
                help_github_url = "https://raw.githubusercontent.com/Unlucky-Life/ankimon/main/src/Ankimon/HelpInfos.html"
                # Path to the local file
                local_content = read_local_file(help_local_file_path)
                # Read content from GitHub
                github_content, github_html_content = read_github_file(help_github_url)
                if local_content is not None and compare_files(local_content, github_content):
                    html_content = github_html_content
                else: 
                    # Download new content from GitHub
                    if github_content is not None:
                        # Write new content to the local file
                        write_local_file(help_local_file_path, github_content)
                        html_content = github_html_content
            else:
                help_local_file_path = addon_dir / "HelpInfos.html"
                local_content = read_local_file(help_local_file_path)
                html_content = local_content
        except:
            showWarning("Failed to retrieve Ankimon HelpGuide from GitHub.")
            local_content = read_local_file(help_local_file_path)
            html_content = local_content
        self.setWindowTitle("Ankimon HelpGuide")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setHtml(html_content)
        layout.addWidget(self.text_edit)
        self.setWindowIcon(QIcon(str(icon_path)))
        self.setLayout(layout)

def open_help_window():
    try:
        help_dialog = HelpWindow()
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
    global effect_sound_timer, sound_effects, hurt_normal_sound_path, hurt_noteff_sound_path, hurt_supereff_sound_path, ownhplow_sound_path, hpheal_sound_path, fainted_sound_path
    
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
    global sounds
    if sounds is True:
        global id, addon_dir
        #id = search_pokedex(name.lower(), "id")
        file_name = f"{id}.ogg"
        #file_name = f"{name.lower()}.mp3"
        audio_path = addon_dir / "user_files" / "sprites" / "sounds" / file_name
        if audio_path.is_file():
            audio_path = Path(audio_path)
            audios.will_use_audio_player()
            audios.audio(audio_path)

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

#count index - count 2 cards - easy = 20, good = 10, hard = 5, again = 0
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
    elif name == "mime jr.":
        return "mimejr"
    elif name == "nidoran♂":
        return "nidoranm"
    elif name == "nidoran":
        return "nidoranf"
    elif name == "keldeo[e]":
        return "keldeo"
    elif name == "mew[e]":
        return "mew"
    elif name == "deoxys[e]":
        return "deoxys"
    elif name == "jirachi[e]":
        return "jirachi"
    elif name == "arceus[e]":
        return "arceus"
    elif name == "shaymin[e]":
        return "shaymin-land"
    elif name == "darkrai [e]":
        return "darkrai"
    elif name == "manaphy[e]":
        return "manaphy"
    elif name == "phione[e]":
        return "phione"
    elif name == "celebi[e]":
        return "celebi"
    elif name == "magearna[e]":
        return "magearna"
    elif name == "type: null":
        return "typenull"
    else:
        #showWarning("Error in Handling Pokémon name")
        return name

def special_pokemon_names_for_pokedex_to_poke_api_db(name):
    global pokedex_to_poke_api_db
    return pokedex_to_poke_api_db.get(name, name)

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
        card_ratings_count["Again"] += 1
    elif ease == maxEase - 2:
        card_ratings_count["Hard"] += 1
    elif ease == maxEase - 1:
        card_ratings_count["Good"] += 1
    elif ease == maxEase:
        card_ratings_count["Easy"] += 1
    else:
        # default behavior for unforeseen cases
        tooltip("Error in ColorConfirmation: Couldn't interpret ease")

aqt.gui_hooks.reviewer_did_answer_card.append(answerCard_after)

def get_image_as_base64(path):
    with open(path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

if database_complete != False:
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
    
    def get_all_pokemon_moves(pk_name, level):
        """
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
        pk_name = pk_name.lower()

        # Retrieve the learnset for the specified Pokémon
        pokemon_learnset = learnsets.get(pk_name, {})

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

            # Pick up to 4 random moves and append them to the attacks list
            for move, highest_level in moves_and_levels_list:
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
    if not pokemon:
        genders = ["M", "F"]
        gender = random.choice(genders)
        return gender

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

if database_complete != False:
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

def split_japanese_string_by_length(input_string, max_length):
    max_length = 30
    current_length = 0
    current_line = ""

    for char in input_string:
        if current_length + 1 <= max_length:
            current_line += char
            current_length += 1
        else:
            yield current_line
            current_line = char
            current_length = 1

    if current_line:  # Ensure the last line is also yielded
        yield current_line

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
        # add item to item list
        with open(itembag_path, 'r') as json_file:
            itembag_list = json.load(json_file)
            itembag_list.append(item_name)
        with open(itembag_path, 'w') as json_file:
            json.dump(itembag_list, json_file)
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
        with open(itembag_path, 'r') as json_file:
            itembag_list = json.load(json_file)
            itembag_list.append(fossil_name)
        with open(itembag_path, 'w') as json_file:
            json.dump(itembag_list, json_file, indent=2)
        return fossil_name

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

caught_pokemon = {} #pokemon not caught

def check_min_generate_level(pkmn_name):
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
    period = reviewer_text_message_box_time #time for pop up message
    global reviewer_text_message_box
    class CustomLabel(QLabel):
        def mousePressEvent(self, evt):
            evt.accept()
            self.hide()
    aw = parent or QApplication.activeWindow()
    if aw is None:
        return
    else:
        if reviewer_text_message_box != False:
            # Assuming closeTooltip() and customCloseTooltip() are defined elsewhere
            closeTooltip()
            x = aw.mapToGlobal(QPoint(x + round(aw.width() / 2), 0)).x()
            y = aw.mapToGlobal(QPoint(0, aw.height() - 180)).y()
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
            QTimer.singleShot(period, lambda: lab.hide())

pokemon_species = None
# Your random Pokémon generation function using the PokeAPI
if database_complete != False:
    def generate_random_pokemon():
        # Fetch random Pokémon data from Generation
        # Load the JSON file with Pokémon data
        global addon_dir
        global pokemon_encounter
        global hp, gender, name, enemy_attacks
        global mainpokemon_level
        global pokemon_species
        global cards_per_round
        pokemon_encounter = 0
        pokemon_species = None
        #generation_file = ("pokeapi_db.json")
        try:
            id, pokemon_species = choose_random_pkmn_from_tier()
            #test_ids = [719]
            #id = random.choice(test_ids)
            name = search_pokedex_by_id(id)

            if name is list:
                name = name[0]
            try:
                min_level = int(check_min_generate_level(str(name.lower())))
            except:
                generate_random_pokemon()
            var_level = 3
            if mainpokemon_level or mainpokemon_level != None:
                try:
                    level = random.randint((mainpokemon_level - (random.randint(0, var_level))), (mainpokemon_level + (random.randint(0, var_level))))  # Random level between 1 and 100
                    if mainpokemon_level == 100:
                        level = 100
                    if level < 0:
                        level = 1
                except Exception as e:
                    showWarning(f"Error in generate random pokemon{e}")
                    mainpokemon_level = 5
                    level = 5
            else:
                level = 5
                min_level = 0
            if min_level is None or not min_level or mainpokemon_level is None or not mainpokemon_level:
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
                enemy_attacks_list = get_all_pokemon_moves(name, level)
                enemy_attacks = []
                if len(enemy_attacks_list) <= 4:
                    enemy_attacks = enemy_attacks_list
                else:
                    enemy_attacks = random.sample(enemy_attacks_list, 4)
                base_experience = search_pokeapi_db_by_id(id, "base_experience")
                growth_rate = search_pokeapi_db_by_id(id, "growth_rate")
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
                battle_stats = stats
                battle_status = "fighting"
                try:
                    hp_stat = int(stats['hp'])
                except Exception as e:
                    showInfo(f"Error occured: {e}")
                hp = calculate_hp(hp_stat, level, ev, iv)
                max_hp = hp
                global ev_yield
                ev_yield = search_pokeapi_db_by_id(id, "effort_values")
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
    global general_card_count_for_battle
    general_card_count_for_battle = 0
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
    kill_button = QPushButton("Defeat Pokémon")
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

def choose_random_pkmn_from_tier():
    global cards_per_round, card_counter
    possible_tiers = []
    try:
        if card_counter < (40*cards_per_round):
            possible_tiers.append("Normal")
        elif card_counter < (50*cards_per_round):
            possible_tiers.extend(["Baby", "Normal", "Normal", "Normal", "Normal", "Normal", "Normal", "Normal"])
        elif card_counter < (65*cards_per_round):
            possible_tiers.extend(["Baby", "Normal", "Normal", "Normal", "Normal", "Normal", "Normal", "Normal", "Ultra"])
        elif card_counter < (90*cards_per_round):
            possible_tiers.extend(["Baby", "Legendary", "Normal", "Normal", "Normal", "Normal", "Normal", "Normal", "Ultra", "Ultra"])
        else:
            possible_tiers.extend(["Baby", "Legendary", "Mythical", "Normal", "Normal", "Normal", "Normal", "Normal", "Normal", "Normal", "Ultra", "Ultra"])
        tier = random.choice(possible_tiers)
        id, pokemon_species = get_pokemon_id_by_tier(tier)
        return id, pokemon_species
    except:
        showWarning(f" An error occured with generating following Pkmn Info: {id}{pokemon_species} \n Please post this error message over the Report Bug Issue")

def get_pokemon_id_by_tier(tier):
    global pokemon_species_normal_path, pokemon_species_baby_path, pokemon_species_mythical_path, pokemon_species_ultra_path, pokemon_species_legendary_path
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

    with open(id_species_path, 'r') as file:
        id_data = json.load(file)

    pokemon_species = f"{tier}"
    # Select a random Pokemon ID from those in the tier
    random_pokemon_id = random.choice(id_data)
    return random_pokemon_id, pokemon_species

def save_caught_pokemon(nickname):
    # Create a dictionary to store the Pokémon's data
    # add all new values like hp as max_hp, evolution_data, description and growth rate
    global achievements
    global pokemon_species
    if pokemon_species != None:
        if pokemon_species == "Normal":
            check = check_for_badge(achievements,17)
            if check is False:
                achievements = receive_badge(17,achievements)
                test_window.display_badge(17)
        elif pokemon_species == "Baby":
            check = check_for_badge(achievements,18)
            if check is False:
                achievements = receive_badge(18,achievements)
                test_window.display_badge(18)
        elif pokemon_species == "Ultra":
            check = check_for_badge(achievements,8)
            if check is False:
                achievements = receive_badge(8,achievements)
                test_window.display_badge(8)
        elif pokemon_species == "Legendary":
            check = check_for_badge(achievements,9)
            if check is False:
                achievements = receive_badge(9,achievements)
                test_window.display_badge(9)
        elif pokemon_species == "Mythical":
            check = check_for_badge(achievements,10)
            if check is False:
                achievements = receive_badge(10,achievements)
                test_window.display_badge(10)

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
                if move is None:
                    move_name = move_name.replace(" ", "")
                    try:
                        move = moves_data.get(move_name.lower())
                        return move
                    except:
                        showInfo(f"Can't find the attack {move_name} in the database.")
                        move = moves_data.get("tackle")
                        return move
    except FileNotFoundError:
        showInfo("Moves Data File Missing!\nPlease Download Moves Data")
        return None
    except json.JSONDecodeError as e:
        showInfo(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        showWarning(f"There is an issue in find_details_move{e}")

def save_main_pokemon_progress(mainpokemon_path, mainpokemon_level, mainpokemon_name, mainpokemon_base_experience, mainpokemon_growth_rate, exp):
    global mainpokemon_current_hp, mainpokemon_ev, ev_yield, mainpokemon_evolution, mainpokemon_xp, pop_up_dialog_message_on_defeat
    experience = find_experience_for_level(mainpokemon_growth_rate, mainpokemon_level)
    if remove_levelcap is True:
        mainpokemon_xp += exp
        level_cap = None
    elif mainpokemon_level != 100:
            mainpokemon_xp += exp
            level_cap = 100
    if mainpokemon_path.is_file():
        with open(mainpokemon_path, "r") as json_file:
            main_pokemon_data = json.load(json_file)
    else:
        showWarning("Missing Mainpokemon Data !")
    while int(experience) < int(mainpokemon_xp) and (level_cap is None or mainpokemon_level < level_cap):
        mainpokemon_level += 1
        msg = ""
        msg += f"Your {mainpokemon_name} is now level {mainpokemon_level} !"
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
        if pop_up_dialog_message_on_defeat is True:
            showInfo(f"{msg}")
        mainpokemon_xp = int(mainpokemon_xp) - int(experience)
        name = f"{mainpokemon_name}"
        # Update mainpokemon_evolution and handle evolution logic
        mainpokemon_evolution = search_pokedex(name.lower(), "evos")
        if mainpokemon_evolution:
            for pokemon in mainpokemon_evolution:
                min_level = search_pokedex(pokemon.lower(), "evoLevel")
                if min_level == mainpokemon_level:
                    msg = ""
                    msg += f"{mainpokemon_name} is about to evolve to {pokemon} at level {min_level}"
                    showInfo(f"{msg}")
                    color = "#6A4DAC"
                    try:
                        tooltipWithColour(msg, color)
                    except:
                        pass
                    evo_window.display_pokemon_evo(mainpokemon_name.lower())
                else:
                    for mainpkmndata in main_pokemon_data:
                        if mainpkmndata["name"] == mainpokemon_name.capitalize():
                            attacks = mainpkmndata["attacks"]
                            new_attacks = get_levelup_move_for_pokemon(mainpokemon_name.lower(),int(mainpokemon_level))
                            if new_attacks:
                                msg = ""
                                msg += f"Your {mainpokemon_name.capitalize()} can learn a new attack !"
                            for new_attack in new_attacks:
                                if len(attacks) < 4:
                                    attacks.append(new_attack)
                                    msg += f"\n Your {mainpokemon_name.capitalize()} has learned {new_attack} !"
                                    color = "#6A4DAC"
                                    tooltipWithColour(msg, color)
                                    if pop_up_dialog_message_on_defeat is True:
                                        showInfo(f"{msg}")
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
                                        showInfo(f"{new_attack} will be discarded.")
                            mainpkmndata["attacks"] = attacks
                            break
        else:
            for mainpkmndata in main_pokemon_data:
                if mainpkmndata["name"] == mainpokemon_name.capitalize():
                    attacks = mainpkmndata["attacks"]
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
        msg = ""
        msg += f"Your {mainpokemon_name} has gained {exp} XP.\n {experience} exp is needed for next level \n Your pokemon currently has {mainpokemon_xp}"
        color = "#6A4DAC" #pokemon leveling info color for tooltip
        try:
            tooltipWithColour(msg, color)
        except:
            pass
        if pop_up_dialog_message_on_defeat is True:
            showInfo(f"{msg}")
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
    global achievements
    try:
        evoName = search_pokedex(pkmn_name.lower(), "evos")
        evoName = f"{evoName[0]}"
        with open(mypokemon_path, "r") as json_file:
            captured_pokemon_data = json.load(json_file)
            pokemon = None
            if captured_pokemon_data:
                for pokemon_data in captured_pokemon_data:
                    if pokemon_data['name'] == pkmn_name.capitalize():
                        pokemon = pokemon_data
                        if pokemon is not None:
                            pokemon["name"] = evoName.capitalize()
                            evoId = int(search_pokedex(evoName.lower(), "num"))
                            pokemon["id"] = evoId
                            # pokemon["ev"] = ev
                            # pokemon["iv"] = iv
                            pokemon["type"] = search_pokedex(evoName.lower(), "types")
                            pokemon["evos"] = []
                            attacks = pokemon["attacks"]
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
                            #pokemon["gender"] = pick_random_gender(evoName.lower()) dont replace gender
                            pokemon["growth_rate"] = search_pokeapi_db_by_id(evoId,"growth_rate")
                            pokemon["base_experience"] = search_pokeapi_db_by_id(evoId,"base_experience")
                            #pokemon["growth_rate"] = search_pokeapi_db(evoName.lower(), "growth_rate")
                            #pokemon["base_experience"] = search_pokeapi_db(evoName.lower(), "base_experience")
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
    check = check_for_badge(achievements,16)
    if check is False:
        receive_badge(16,achievements)
        test_window.display_badge(16)

def cancel_evolution(pkmn_name):
    global mainpokemon_current_hp, mainpokemon_ev, ev_yield, mainpokemon_evolutions
    # Load existing Pokémon data if it exists
    if mainpokemon_path.is_file():
        with open(mainpokemon_path, "r") as json_file:
            main_pokemon_data = json.load(json_file)
            for pokemon in main_pokemon_data:
                if pokemon["name"] == pkmn_name.capitalize():
                    attacks = pokemon["attacks"]
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
    global pokemon_hp, name, ability, enemy_attacks, type, stats, base_experience, level, growth_rate, gender, id, iv, pop_up_dialog_message_on_defeat
    global mypokemon_path, caught
    caught += 1
    if caught == 1:
        name = name.capitalize()
        if nickname is None or not nickname:  # Wenn None oder leer
            save_caught_pokemon(nickname)
        else:
            save_caught_pokemon(name)
        global general_card_count_for_battle
        general_card_count_for_battle = 0
        msg = f"You caught {name}!"
        if pop_up_dialog_message_on_defeat is True:
            showInfo(f"{msg}") # Display a message when the Pokémon is caught
        color = "#6A4DAC" #pokemon leveling info color for tooltip
        try:
            tooltipWithColour(msg, color)
        except:
            pass
        new_pokemon()  # Show a new random Pokémon
    else:
        if pop_up_dialog_message_on_defeat is True:
            showInfo("You have already caught the pokemon. Please close this window!") # Display a message when the Pokémon is caught

def get_random_starter():
    global addon_dir, starters_path    # event if pokemon
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
            random_gen = random.randint(0, 6)
            water_start = f"{water_starter[random_gen]}"
            fire_start = f"{fire_starter[random_gen]}"
            grass_start = f"{grass_starter[random_gen]}"
            return water_start, fire_start, grass_start
    except Exception as e:
        showWarning(f"Error in get_random_starter: {e}")
        return None, None, None


def calculate_max_hp_wildpokemon():
    global stats, level, ev, iv
    wild_pk_max_hp = calculate_hp(stats["hp"], level, ev, iv)
    return wild_pk_max_hp

def new_pokemon():
    global name, id, level, hp, max_hp, ability, type, enemy_attacks, attacks, base_experience, stats, battlescene_file, ev, iv, gender, battle_status
    # new pokemon
    gender = None
    name, id, level, ability, type, stats, enemy_attacks, base_experience, growth_rate, hp, max_hp, ev, iv, gender, battle_status, battle_stats = generate_random_pokemon()
    battlescene_file = random_battle_scene()
    max_hp = calculate_hp(stats["hp"], level, ev, iv)
    #reset mainpokemon hp
    if test_window is not None:
        test_window.display_first_encounter()
    class Container(object):
        pass
    reviewer = Container()
    reviewer.web = mw.reviewer.web
    update_life_bar(reviewer, 0, 0)

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
    pokemon_name = special_pokemon_names_for_min_level(pokemon_name)
    with open(str(pokedex_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            if pokemon_name in pokedex_data:
                pokemon_info = pokedex_data[pokemon_name]
                var = pokemon_info.get(variable, None)
                return var
            else:
                return []

def search_pokedex_by_name_for_id(pokemon_name, variable):
    global pokedex_path
    pokemon_name = special_pokemon_names_for_min_level(pokemon_name)
    with open(str(pokedex_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            if pokemon_name in pokedex_data:
                pokemon_info = pokedex_data[pokemon_name]
                var = pokemon_info.get("num", None)
                return var
            else:
                return None

def search_pokedex_by_id(pokemon_id):
    global pokedex_path
    with open(str(pokedex_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file) 
            for entry_name, attributes in pokedex_data.items():
                if attributes['num'] == pokemon_id:
                    return entry_name
    return 'Pokémon not found'

def get_pokemon_diff_lang_name(pokemon_id):
    global language
    global pokenames_lang_path
    with open(pokenames_lang_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row if there is one
        for row in reader:
            # Assuming the CSV structure is: pokemon_species_id,local_language_id,name,genus
            species_id, lang_id, name, genus = row
            if int(species_id) == pokemon_id and int(lang_id) == language:
                return name
    return "No Translation in this language"  # Return None if no match is found

def get_pokemon_descriptions(species_id):
    global language
    global pokedesc_lang_path
    descriptions = []  # Initialize an empty list to store matching descriptions
    with open(pokedesc_lang_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if int(row['species_id']) == species_id and int(row['language_id']) == language:
                # Replace control characters for readability, if necessary
                flavor_text = row['flavor_text'].replace('\x0c', ' ')
                descriptions.append(flavor_text)  # Add the matching description to the list
    if descriptions:
        if len(descriptions) > 1:
            return random.choice(descriptions)
        else:
            return descriptions
    else:
        ["Description not found."]

def search_pokeapi_db(pkmn_name,variable):
    global addon_dir
    global pokeapi_db_path
    with open(str(pokeapi_db_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            for pokemon_data in pokedex_data:
                name = pokemon_data["name"]
                if pokemon_data["name"] == pkmn_name:
                    var = pokemon_data.get(variable, None)
                    return var
            else:
                return None

def search_pokeapi_db_by_id(pkmn_id,variable):
    global addon_dir
    global pokeapi_db_path
    with open(str(pokeapi_db_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            for pokemon_data in pokedex_data:
                if pokemon_data["id"] == pkmn_id:
                    var = pokemon_data.get(variable, None)
                    return var
            else:
                return None
            
def mainpokemon_data():
    global mainpkmn
    global mainpokemon_name, mainpokemon_id, mainpokemon_ability, mainpokemon_type, mainpokemon_stats, mainpokemon_attacks, mainpokemon_level, mainpokemon_base_experience, mainpokemon_xp, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate, mainpokemon_ev, mainpokemon_iv, mainpokemon_evolutions, mainpokemon_battle_stats, mainpokemon_gender, mainpokemon_nickname
    mainpkmn = 1
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
    except:
            pass
#get main pokemon details:
if database_complete != False:
    try:
        mainpokemon_name, mainpokemon_id, mainpokemon_ability, mainpokemon_type, mainpokemon_stats, mainpokemon_attacks, mainpokemon_level, mainpokemon_base_experience, mainpokemon_xp, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate, mainpokemon_ev, mainpokemon_iv, mainpokemon_evolutions, mainpokemon_battle_stats, mainpokemon_gender, mainpokemon_nickname = mainpokemon_data()
        starter = True
    except Exception as e:
        starter = False
        mainpokemon_level = 5
    name, id, level, ability, type, stats, enemy_attacks, base_experience, growth_rate, hp, max_hp, ev, iv, gender, battle_status, battle_stats = generate_random_pokemon()
    battlescene_file = random_battle_scene()

def get_effectiveness(move_type):
    global mainpokemon_type, effectiveness_chart_file_path, type
    move_type = move_type.capitalize()
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
                return eff_value
            else:
                effective_txt = effectiveness_text(effectiveness_values[0])
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
        effective_txt = "was effective."
        #return None
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
general_card_count_for_battle = 0
cry_counter = 0
seconds = 0
myseconds = 0
# Hook into Anki's card review event
def on_review_card(*args):
    try:
        global reviewed_cards_count, card_ratings_count, card_counter, general_card_count_for_battle, cry_counter, battle_sounds
        global hp, stats, type, battle_status, name, battle_stats, enemy_attacks, level
        global pokemon_encounter, mainpokemon_hp, seconds, myseconds, animate_time
        global mainpokemon_xp, mainpokemon_current_hp, mainpokemon_attacks, mainpokemon_level, mainpokemon_stats, mainpokemon_type, mainpokemon_name, mainpokemon_battle_stats, mainpokemon_ev, mainpokemon_iv
        global attack_counter
        global pkmn_window
        global achievements
        # Increment the counter when a card is reviewed
        reviewed_cards_count += 1
        card_counter += 1
        cry_counter += 1
        dmg = 0
        seconds = 0
        myseconds = 0
        general_card_count_for_battle += 1
        if battle_sounds == True and general_card_count_for_battle == 1:
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
        if card_counter == item_receive_value:
            test_window.display_item()
            check = check_for_badge(achievements,6)
            if check is False:
                receive_badge(6,achievements)
                test_window.display_badge(6)
        if reviewed_cards_count >= cards_per_round:
            reviewed_cards_count = 0
            attack_counter = 0
            slp_counter = 0
            pokemon_encounter += 1
            multiplier = calc_multiply_card_rating()
            msg = ""
            msg += f"{multiplier}x Multiplier"
            #failed card = enemy attack
            if pokemon_encounter > 0 and hp > 0 and dmg_in_reviewer is True and multiplier < 1:
                msg += f" \n "
                try:
                    max_attempts = 3  # Set the maximum number of attempts
                    for _ in range(max_attempts):
                        rand_enemy_atk = random.choice(enemy_attacks)
                        enemy_move = find_details_move(rand_enemy_atk)
                        
                        if enemy_move is not None:
                            break  # Exit the loop if a valid enemy_move is found
                    msg += f"{name.capitalize()} chose {rand_enemy_atk.capitalize()} !"
                    e_move_category = enemy_move.get("category")
                    e_move_acc = enemy_move.get("accuracy")
                    if e_move_acc is True:
                        e_move_acc = 100
                    elif e_move_acc != 0:
                        e_move_acc = 100 / e_move_acc
                    if random.random() > e_move_acc:
                        msg += "\n Move has missed !"
                    else:
                        if e_move_category == "Status":
                            color = "#F7DC6F"
                            msg = effect_status_moves(rand_enemy_atk, stats, mainpokemon_stats, msg, mainpokemon_name , name)
                        elif e_move_category == "Physical" or e_move_category == "Special":
                            critRatio = enemy_move.get("critRatio", 1)
                            if e_move_category == "Physical":
                                color = "#F0B27A"
                            elif e_move_category == "Special":
                                color = "#D2B4DE"
                            if enemy_move["basePower"] == 0:
                                enemy_dmg = bP_none_moves(enemy_move)
                                mainpokemon_hp -= int(enemy_dmg)
                                if enemy_dmg == 0:
                                    msg += "\n Move has missed !"
                            else:
                                if e_move_category == "Special":
                                    def_stat = mainpokemon_stats["spd"]
                                    atk_stat = stats["spa"]
                                elif e_move_category == "Physical":
                                    def_stat = mainpokemon_stats["def"]
                                    atk_stat = stats["atk"]
                                enemy_dmg = int(calc_atk_dmg(level,(multiplier * 2),enemy_move["basePower"], atk_stat, def_stat, type, enemy_move["type"],mainpokemon_type, critRatio))
                                if enemy_dmg == 0:
                                    enemy_dmg = 1
                                mainpokemon_hp -= enemy_dmg
                                if enemy_dmg > 0:
                                    myseconds = animate_time
                                    if multiplier < 1:
                                        play_effect_sound("HurtNormal")
                                else:
                                    myseconds = 0
                                msg += f" {enemy_dmg} dmg is dealt to {mainpokemon_name.capitalize()}."
                except:
                    enemy_dmg = 0
                    rand_enemy_atk = random.choice(enemy_attacks)
                    enemy_move = find_details_move(rand_enemy_atk)
                    e_move_category = enemy_move.get("category")
                    if e_move_category == "Status":
                            color = "#F7DC6F"
                            msg = effect_status_moves(rand_enemy_atk, stats, mainpokemon_stats, msg, mainpokemon_name , name)
                    elif e_move_category == "Physical" or e_move_category == "Special":
                        if e_move_category == "Special":
                            def_stat = mainpokemon_stats["spd"]
                            atk_stat = stats["spa"]
                        elif e_move_category == "Physical":
                            def_stat = mainpokemon_stats["def"]
                            atk_stat = stats["atk"]                        
                        enemy_dmg = int(calc_atk_dmg(level,(multiplier * 2),random.randint(60, 100), atk_stat, def_stat, type, "Normal", mainpokemon_type, critRatio))
                        if enemy_dmg == 0:
                            enemy_dmg = 1
                        mainpokemon_hp -= enemy_dmg
                    if enemy_dmg > 0:
                        myseconds = animate_time
                        if multiplier < 1:
                            play_effect_sound("HurtNormal")
                    else:
                        myseconds = 0
                    msg += f" {enemy_dmg} dmg is dealt to {mainpokemon_name.capitalize()}."
    
            # If 10 or more cards have been reviewed, show the random Pokémon
            if pokemon_encounter > 0 and hp > 0:
                dmg = 0
                random_attack = random.choice(mainpokemon_attacks)
                msg += f"\n {mainpokemon_name} has chosen {random_attack.capitalize()} !"
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
                    msg += "\n Move has missed !"
                else:
                    if category == "Status":
                        color = "#F7DC6F"
                        msg = effect_status_moves(random_attack, mainpokemon_stats, stats, msg, name, mainpokemon_name)
                    elif category == "Physical" or category == "Special":
                        try:
                            critRatio = move.get("critRatio", 1)
                            if category == "Physical":
                                color = "#F0B27A"
                            elif category == "Special":
                                color = "#D2B4DE"
                            if move["basePower"] == 0:
                                dmg = bP_none_moves(move)
                                hp -= dmg
                                if dmg == 0:
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
                                    msg += " \n Move has missed !"
                        except:
                            if category == "Special":
                                def_stat = stats["spd"]
                                atk_stat = mainpokemon_stats["spa"]
                            elif category == "Physical":
                                def_stat = stats["def"]
                                atk_stat = mainpokemon_stats["atk"]
                            dmg = int(calc_atk_dmg(mainpokemon_level, multiplier,random.randint(60, 100), atk_stat, def_stat, mainpokemon_type, "Normal",type, critRatio))
                            hp -= dmg
                        if hp < 0:
                            hp = 0
                            msg += f" {name.capitalize()} has fainted"
                    tooltipWithColour(msg, color)
                    if dmg > 0:
                        seconds = animate_time
                        if multiplier == 1:
                            play_effect_sound("HurtNormal")
                        elif multiplier < 1:
                            play_effect_sound("HurtNotEffective")
                        elif multiplier > 1:
                            play_effect_sound("HurtSuper")
                    else:
                        seconds = 0
            else:
                if pkmn_window is True:
                    test_window.display_pokemon_death()
                else:
                    if automatic_battle != 0:
                        if automatic_battle == 1:
                            catch_pokemon("")
                            general_card_count_for_battle = 0
                        elif automatic_battle == 2:
                            kill_pokemon()
                            new_pokemon()
                            general_card_count_for_battle = 0
            if pkmn_window is True:
                if hp > 0:
                    test_window.display_first_encounter()
                elif hp < 1:
                    hp = 0
                    test_window.display_pokemon_death()
                    general_card_count_for_battle = 0
            elif pkmn_window is False:
                if hp < 1:
                    hp = 0
                    if automatic_battle != 0:
                        if automatic_battle == 1:
                            catch_pokemon("")
                            general_card_count_for_battle = 0
                        elif automatic_battle == 2:
                            kill_pokemon()
                            new_pokemon()
                            general_card_count_for_battle = 0
            # Reset the counter
            reviewed_cards_count = 0
        if cry_counter == 10 and battle_sounds is True:
            cry_counter = 0
            play_sound()
        if mainpokemon_hp < 1:
            msg = f"Your {mainpokemon_name} has been defeated and the wild {name} has fled!"
            play_effect_sound("Fainted")
            new_pokemon()
            mainpokemon_data()
            color = "#E12939"
            tooltipWithColour(msg, color)
    except Exception as e:
        showWarning(f"An error occured in reviewer: {e}")


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
    global show_mainpkmn_in_reviewer, hp_bar_thickness, xp_bar_spacer
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
        if show_mainpkmn_in_reviewer == 2:
            html = f"""
            <div id=pokestatus style="
                position: fixed;
                bottom: {140 + xp_bar_spacer + hp_bar_thickness}px; /* Adjust as needed */
                right: 1%;
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
        elif show_mainpkmn_in_reviewer == 1:
            html = f"""
            <div id=pokestatus style="
                position: fixed;
                bottom: {40 + hp_bar_thickness + xp_bar_spacer}px; /* Adjust as needed */
                right: 15%;
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
        elif show_mainpkmn_in_reviewer == 0:
            html = f"""
            <div id=pokestatus style="
                position: fixed;
                bottom: {40 + hp_bar_thickness}px; /* Adjust as needed */
                left: 160px;
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
        if damage is None:
            damage = 5
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
            msg += f" {mainpokemon_name.capitalize()}'s "
            if stage < 0:
                msg += f"{boost.capitalize()} is decreased."
            elif stage > 0:
                msg += f"{boost.capitalize()} is increased."
    elif target in ["normal", "allAdjacentFoes"]:
        for boost, stage in boosts.items():
            stat = get_multiplier_stats(stage)
            stats[boost] = stats.get(boost, 0) * stat
            msg += f" {name.capitalize()}'s "
            if stage < 0:
                msg += f"{boost.capitalize()} is decreased."
            elif stage > 0:
                msg += f"{boost.capitalize()} is increased."
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
gui_hooks.reviewer_did_answer_card.append(on_review_card)

from PyQt6 import *
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QSplashScreen


class MovieSplashLabel(QLabel):
    def __init__(self, gif_path, parent=None):
        super().__init__(parent)
        self.movie = QMovie(gif_path)
        self.movie.jumpToFrame(0)
        self.setMovie(self.movie)
        self.movie.frameChanged.connect(self.repaint)

    def showEvent(self, event):
        self.movie.start()

    def hideEvent(self, event):
        self.movie.stop()


class PokemonCollectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.setup_ui()

    def showEvent(self, event):
        # Call refresh_pokemon_collection when the dialog is shown
        self.refresh_pokemon_collection()
    
    def refresh_pokemon_collection(self):
        # Clear previous contents
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        if self.sort_checkbox.isChecked():
            self.sort_pokemon()
        else:
            self.setup_ui()

    def setup_ui(self):

        try:
            with open(mypokemon_path, "r") as json_file:
                captured_pokemon_data = json.load(json_file)
                if captured_pokemon_data:
                    row, column = 0, 0
                    for position, pokemon in enumerate(captured_pokemon_data):
                        pokemon_container = QWidget()
                        image_label = QLabel()
                        pixmap = QPixmap()
                        pokemon_id = pokemon['id']
                        pokemon_name = pokemon['name']
                        if not pokemon.get('nickname') or pokemon.get('nickname') is None:
                            pokemon_nickname = None
                        else:
                            pokemon_nickname = pokemon['nickname']
                        pokemon_gender = pokemon['gender']
                        pokemon_level = pokemon['level']
                        pokemon_ability = pokemon['ability']
                        pokemon_type = pokemon['type']
                        pokemon_stats = pokemon['stats']
                        pokemon_hp = pokemon_stats["hp"],
                        pokemon_attacks = pokemon['attacks']
                        pokemon_base_experience = pokemon['base_experience']
                        pokemon_growth_rate = pokemon['growth_rate']
                        pokemon_ev = pokemon['ev']
                        pokemon_iv = pokemon['iv']
                        pokemon_description = search_pokeapi_db_by_id(pokemon_id, "description")
                        if gif_in_collection is True:
                            pkmn_image_path = str(user_path_sprites / "front_default_gif" / f"{pokemon_id}.gif")
                            splash_label = MovieSplashLabel(pkmn_image_path)
                        else:
                            pkmn_image_path = str(frontdefault / f"{pokemon_id}.png")
                        pixmap.load(pkmn_image_path)

                        # Calculate the new dimensions to maintain the aspect ratio
                        max_width = 300
                        max_height = 230
                        original_width = pixmap.width()
                        original_height = pixmap.height()

                        if original_width > max_width:
                            new_width = max_width
                            new_height = (original_height * max_width) // original_width
                            pixmap = pixmap.scaled(new_width, new_height)

                        painter = QPainter(pixmap)

                        if pokemon_gender == "M":
                            gender_symbol = "♂"
                        elif pokemon_gender == "F":
                            gender_symbol = "♀"
                        elif pokemon_gender == "N":
                            gender_symbol = ""
                        else:
                            gender_symbol = ""

                        if pokemon_nickname is None:
                            capitalized_name = f"{get_pokemon_diff_lang_name(int(pokemon_id)).capitalize()} {gender_symbol}"
                        else:
                            capitalized_name = f"{pokemon_nickname.capitalize()} {gender_symbol}"
                        lvl = (f" Level: {pokemon_level}")
                        type_txt = "Type: "
                        for type in pokemon_type:
                            type_txt += f" {type.capitalize()}"
                        ability_txt = (f" Ability: {pokemon_ability.capitalize()}")

                        font = QFont()
                        font.setPointSize(12)
                        painter.setFont(font)
                        fontpkmnspec = QFont()
                        fontpkmnspec.setPointSize(8)
                        painter.end()

                        name_label = QLabel(capitalized_name)
                        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                        name_label.setFont(font)

                        level_label = QLabel(lvl)
                        level_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                        level_label.setFont(fontpkmnspec)

                        type_label = QLabel(type_txt)
                        type_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                        type_label.setFont(fontpkmnspec)

                        ability_label = QLabel(ability_txt)
                        ability_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                        ability_label.setFont(fontpkmnspec)

                        image_label.setPixmap(pixmap)

                        pokemon_button = QPushButton("Show me Details")
                        pokemon_button.setIconSize(pixmap.size())
                        if len(pokemon_type) > 1:
                            pokemon_button.clicked.connect(lambda state, name=pokemon_name, level=pokemon_level, id=pokemon_id, ability=pokemon_ability, type=[pokemon_type[0], pokemon_type[1]], detail_stats=pokemon_stats, attacks=pokemon_attacks, base_experience=pokemon_base_experience, growth_rate=pokemon_growth_rate, description=pokemon_description, gender=pokemon_gender, nickname=pokemon_nickname, position=position: PokemonCollectionDetails(name, level, id, ability, type, detail_stats, attacks, base_experience, growth_rate, description, gender, nickname, position))
                        else:
                            pokemon_button.clicked.connect(lambda state, name=pokemon_name, level=pokemon_level, id=pokemon_id, ability=pokemon_ability, type=[pokemon_type[0]], detail_stats=pokemon_stats, attacks=pokemon_attacks, base_experience=pokemon_base_experience, growth_rate=pokemon_growth_rate, description=pokemon_description, gender=pokemon_gender, nickname=pokemon_nickname, position=position: PokemonCollectionDetails(name, level, id, ability, type, detail_stats, attacks, base_experience, growth_rate, description, gender, nickname, position))

                        choose_pokemon_button = QPushButton("Pick as main Pokemon")
                        choose_pokemon_button.setIconSize(pixmap.size())
                        choose_pokemon_button.clicked.connect(lambda state, name=pokemon_name, nickname=pokemon_nickname, level=pokemon_level, id=pokemon_id, ability=pokemon_ability, type=pokemon_type, detail_stats=pokemon_stats, attacks=pokemon_attacks, hp=pokemon_hp, base_experience=pokemon_base_experience, growth_rate=pokemon_growth_rate, ev=pokemon_ev, iv=pokemon_iv, gender=pokemon_gender: MainPokemon(name, nickname, level, id, ability, type, detail_stats, attacks, hp, base_experience, growth_rate, ev, iv, gender))

                        container_layout = QVBoxLayout()
                        container_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
                        if gif_in_collection is True:
                            container_layout.addWidget(splash_label)
                            splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        else:
                            container_layout.addWidget(image_label)
                            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        container_layout.addWidget(name_label)
                        container_layout.addWidget(level_label)
                        container_layout.addWidget(type_label)
                        container_layout.addWidget(ability_label)
                        container_layout.addWidget(pokemon_button)
                        container_layout.addWidget(choose_pokemon_button)
                        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        ability_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                        pokemon_container.setLayout(container_layout)
                        self.scroll_layout.addWidget(pokemon_container, row, column)
                        column += 1
                        if column >= 3:
                            column = 0
                            row += 1

                    self.container.setLayout(self.scroll_layout)
                    self.scroll_area.setWidget(self.container)
                    self.layout.addWidget(self.scroll_area)
                    self.setLayout(self.layout)
                else:
                    self.layout.addWidget(QLabel("You haven't captured any Pokémon yet."))
        except FileNotFoundError:
            self.layout.addWidget(QLabel(f"Can't open the Saving File. {mypokemon_path}"))

    def filter_pokemon(self):
        if not self.sort_checkbox.isChecked():
            type_index = self.type_combo.currentIndex()
            type_text = self.type_combo.currentText()
            search_text = self.search_edit.text().lower()
            generation_index = self.generation_combo.currentIndex()
            # Clear previous contents
            for i in reversed(range(self.scroll_layout.count())):
                widget = self.scroll_layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()
            try:
                with open(mypokemon_path, "r") as json_file:
                    captured_pokemon_data = json.load(json_file)
                    if captured_pokemon_data:
                        row, column = 0, 0
                        for position, pokemon in enumerate(captured_pokemon_data):
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

                                # Display the Pokémon
                                pokemon_container = QWidget()
                                image_label = QLabel()
                                pixmap = QPixmap()
                                pokemon_id = pokemon['id']
                                pokemon_name = pokemon['name']
                                if not pokemon.get('nickname') or pokemon.get('nickname') is None:
                                    pokemon_nickname = None
                                else:
                                    pokemon_nickname = pokemon['nickname']
                                pokemon_gender = pokemon['gender']
                                pokemon_level = pokemon['level']
                                pokemon_ability = pokemon['ability']
                                pokemon_stats = pokemon['stats']
                                pokemon_hp = pokemon_stats["hp"],
                                pokemon_attacks = pokemon['attacks']
                                pokemon_base_experience = pokemon['base_experience']
                                pokemon_growth_rate = pokemon['growth_rate']
                                pokemon_ev = pokemon['ev']
                                pokemon_iv = pokemon['iv']
                                pokemon_description = search_pokeapi_db_by_id(pokemon_id, "description")
                                if gif_in_collection is True:
                                    pkmn_image_path = str(user_path_sprites / "front_default_gif" / f"{pokemon_id}.gif")
                                    splash_label = MovieSplashLabel(pkmn_image_path)
                                else:
                                    pkmn_image_path = str(frontdefault / f"{pokemon_id}.png")
                                pixmap.load(pkmn_image_path)

                                # Calculate the new dimensions to maintain the aspect ratio
                                max_width = 300
                                max_height = 230
                                original_width = pixmap.width()
                                original_height = pixmap.height()

                                if original_width > max_width:
                                    new_width = max_width
                                    new_height = (original_height * max_width) // original_width
                                    pixmap = pixmap.scaled(new_width, new_height)

                                painter = QPainter(pixmap)

                                if pokemon_gender == "M":
                                    gender_symbol = "♂"
                                elif pokemon_gender == "F":
                                    gender_symbol = "♀"
                                elif pokemon_gender == "N":
                                    gender_symbol = ""
                                else:
                                    gender_symbol = ""

                                if pokemon_nickname is None:
                                    capitalized_name = f"{get_pokemon_diff_lang_name(int(pokemon_id)).capitalize()} {gender_symbol}"
                                else:
                                    capitalized_name = f"{pokemon_nickname.capitalize()} {gender_symbol}"
                                lvl = (f" Level: {pokemon_level}")
                                type_txt = "Type: "
                                for type in pokemon_type:
                                    type_txt += f" {type.capitalize()}"
                                ability_txt = (f" Ability: {pokemon_ability.capitalize()}")

                                font = QFont()
                                font.setPointSize(12)
                                painter.setFont(font)
                                fontpkmnspec = QFont()
                                fontpkmnspec.setPointSize(8)
                                painter.end()

                                name_label = QLabel(capitalized_name)
                                name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                                name_label.setFont(font)

                                level_label = QLabel(lvl)
                                level_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                                level_label.setFont(fontpkmnspec)

                                type_label = QLabel(type_txt)
                                type_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                                type_label.setFont(fontpkmnspec)

                                ability_label = QLabel(ability_txt)
                                ability_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                                ability_label.setFont(fontpkmnspec)

                                image_label.setPixmap(pixmap)

                                pokemon_button = QPushButton("Show me Details")
                                pokemon_button.setIconSize(pixmap.size())
                                if len(pokemon_type) > 1:
                                    pokemon_button.clicked.connect(lambda state, name=pokemon_name, level=pokemon_level, id=pokemon_id, ability=pokemon_ability, type=[pokemon_type[0], pokemon_type[1]], detail_stats=pokemon_stats, attacks=pokemon_attacks, base_experience=pokemon_base_experience, growth_rate=pokemon_growth_rate, description=pokemon_description, gender=pokemon_gender, nickname=pokemon_nickname, position=position: PokemonCollectionDetails(name, level, id, ability, type, detail_stats, attacks, base_experience, growth_rate, description, gender, nickname, position))
                                else:
                                    pokemon_button.clicked.connect(lambda state, name=pokemon_name, level=pokemon_level, id=pokemon_id, ability=pokemon_ability, type=[pokemon_type[0]], detail_stats=pokemon_stats, attacks=pokemon_attacks, base_experience=pokemon_base_experience, growth_rate=pokemon_growth_rate, description=pokemon_description, gender=pokemon_gender, nickname=pokemon_nickname, position=position: PokemonCollectionDetails(name, level, id, ability, type, detail_stats, attacks, base_experience, growth_rate, description, gender, nickname, position))

                                choose_pokemon_button = QPushButton("Pick as main Pokemon")
                                choose_pokemon_button.setIconSize(pixmap.size())
                                choose_pokemon_button.clicked.connect(lambda state, name=pokemon_name, nickname=pokemon_nickname, level=pokemon_level, id=pokemon_id, ability=pokemon_ability, type=pokemon_type, detail_stats=pokemon_stats, attacks=pokemon_attacks, hp=pokemon_hp, base_experience=mainpokemon_base_experience, growth_rate=pokemon_growth_rate, ev=pokemon_ev, iv=pokemon_iv, gender=pokemon_gender: MainPokemon(name, nickname, level, id, ability, type, detail_stats, attacks, hp, base_experience, growth_rate, ev, iv, gender))

                                container_layout = QVBoxLayout()
                                container_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
                                if gif_in_collection is True:
                                    container_layout.addWidget(splash_label)
                                    splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                                else:
                                    container_layout.addWidget(image_label)
                                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                                container_layout.addWidget(name_label)
                                container_layout.addWidget(level_label)
                                container_layout.addWidget(type_label)
                                container_layout.addWidget(ability_label)
                                container_layout.addWidget(pokemon_button)
                                container_layout.addWidget(choose_pokemon_button)
                                type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                                name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                                level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                                ability_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                                pokemon_container.setLayout(container_layout)
                                self.scroll_layout.addWidget(pokemon_container, row, column)
                                column += 1
                                if column >= 3:
                                    column = 0
                                    row += 1
                        self.container.setLayout(self.scroll_layout)
                        self.scroll_area.setWidget(self.container)
                        self.layout.addWidget(self.scroll_area)
                        self.setLayout(self.layout)                        
                    else:
                        self.layout.addWidget(QLabel("You haven't captured any Pokémon yet."))
            except FileNotFoundError:
                self.layout.addWidget(QLabel(f"Can't open the Saving File. {mypokemon_path}"))
        else:
            self.sort_pokemon()
    
    def sort_pokemon(self):
        search_text = self.search_edit.text().lower()
        generation_index = self.generation_combo.currentIndex()
        type_index = self.type_combo.currentIndex()
        type_text = self.type_combo.currentText()
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        try:
            with open(mypokemon_path, "r") as json_file:
                captured_pokemon_data = json.load(json_file)
                pokemon_widgets = []

                for position, pokemon in enumerate(captured_pokemon_data):
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

                        # Create the Pokémon widget
                        pokemon_container = QWidget()
                        image_label = QLabel()
                        pixmap = QPixmap()
                        pokemon_name = pokemon['name']
                        pokemon_nickname = pokemon.get('nickname')
                        pokemon_gender = pokemon['gender']
                        pokemon_level = pokemon['level']
                        pokemon_ability = pokemon['ability']
                        pokemon_stats = pokemon['stats']
                        pokemon_hp = pokemon_stats["hp"]
                        pokemon_attacks = pokemon['attacks']
                        pokemon_base_experience = pokemon['base_experience']
                        pokemon_growth_rate = pokemon['growth_rate']
                        pokemon_ev = pokemon['ev']
                        pokemon_iv = pokemon['iv']
                        pokemon_description = search_pokeapi_db_by_id(pokemon_id, "description")

                        if gif_in_collection:
                            pkmn_image_path = str(user_path_sprites / "front_default_gif" / f"{pokemon_id}.gif")
                            splash_label = MovieSplashLabel(pkmn_image_path)
                        else:
                            pkmn_image_path = str(frontdefault / f"{pokemon_id}.png")
                        pixmap.load(pkmn_image_path)

                        # Calculate the new dimensions to maintain the aspect ratio
                        max_width = 300
                        max_height = 230
                        original_width = pixmap.width()
                        original_height = pixmap.height()

                        if original_width > max_width:
                            new_width = max_width
                            new_height = (original_height * max_width) // original_width
                            pixmap = pixmap.scaled(new_width, new_height)

                        painter = QPainter(pixmap)

                        gender_symbol = ""
                        if pokemon_gender == "M":
                            gender_symbol = "♂"
                        elif pokemon_gender == "F":
                            gender_symbol = "♀"

                        capitalized_name = f"{pokemon_nickname.capitalize() if pokemon_nickname else get_pokemon_diff_lang_name(int(pokemon_id)).capitalize()} {gender_symbol}"
                        lvl = f" Level: {pokemon_level}"
                        type_txt = "Type: " + " ".join(type.capitalize() for type in pokemon_type)
                        ability_txt = f" Ability: {pokemon_ability.capitalize()}"

                        font = QFont()
                        font.setPointSize(12)
                        painter.setFont(font)
                        fontpkmnspec = QFont()
                        fontpkmnspec.setPointSize(8)
                        painter.end()

                        name_label = QLabel(capitalized_name)
                        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                        name_label.setFont(font)

                        level_label = QLabel(lvl)
                        level_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                        level_label.setFont(fontpkmnspec)

                        type_label = QLabel(type_txt)
                        type_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                        type_label.setFont(fontpkmnspec)

                        ability_label = QLabel(ability_txt)
                        ability_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                        ability_label.setFont(fontpkmnspec)

                        image_label.setPixmap(pixmap)

                        pokemon_button = QPushButton("Show me Details")
                        pokemon_button.setIconSize(pixmap.size())
                        if len(pokemon_type) > 1:
                            pokemon_button.clicked.connect(lambda state, name=pokemon_name, level=pokemon_level, id=pokemon_id, ability=pokemon_ability, type=[pokemon_type[0], pokemon_type[1]], detail_stats=pokemon_stats, attacks=pokemon_attacks, base_experience=pokemon_base_experience, growth_rate=pokemon_growth_rate, description=pokemon_description, gender=pokemon_gender, nickname=pokemon_nickname, position=position: PokemonCollectionDetails(name, level, id, ability, type, detail_stats, attacks, base_experience, growth_rate, description, gender, nickname, position))
                        else:
                            pokemon_button.clicked.connect(lambda state, name=pokemon_name, level=pokemon_level, id=pokemon_id, ability=pokemon_ability, type=[pokemon_type[0]], detail_stats=pokemon_stats, attacks=pokemon_attacks, base_experience=pokemon_base_experience, growth_rate=pokemon_growth_rate, description=pokemon_description, gender=pokemon_gender, nickname=pokemon_nickname, position=position: PokemonCollectionDetails(name, level, id, ability, type, detail_stats, attacks, base_experience, growth_rate, description, gender, nickname, position))

                        choose_pokemon_button = QPushButton("Pick as main Pokemon")
                        choose_pokemon_button.setIconSize(pixmap.size())
                        choose_pokemon_button.clicked.connect(lambda state, name=pokemon_name, nickname=pokemon_nickname, level=pokemon_level, id=pokemon_id, ability=pokemon_ability, type=pokemon_type, detail_stats=pokemon_stats, attacks=pokemon_attacks, hp=pokemon_hp, base_experience=mainpokemon_base_experience, growth_rate=pokemon_growth_rate, ev=pokemon_ev, iv=pokemon_iv, gender=pokemon_gender: MainPokemon(name, nickname, level, id, ability, type, detail_stats, attacks, hp, base_experience, growth_rate, ev, iv, gender))

                        container_layout = QVBoxLayout()
                        container_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
                        if gif_in_collection is True:
                            container_layout.addWidget(splash_label)
                            splash_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        else:
                            container_layout.addWidget(image_label)
                            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        container_layout.addWidget(name_label)
                        container_layout.addWidget(level_label)
                        container_layout.addWidget(type_label)
                        container_layout.addWidget(ability_label)
                        container_layout.addWidget(pokemon_button)
                        container_layout.addWidget(choose_pokemon_button)
                        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        ability_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                        pokemon_container.setLayout(container_layout)
                        
                        # Append to the list with its id
                        pokemon_widgets.append((pokemon_id, pokemon_container))
                
                # Sort the widgets by pokemon id
                pokemon_widgets.sort(key=lambda x: x[0])
                
                # Add the sorted widgets to the layout
                row = 0
                column = 0
                for _, widget in pokemon_widgets:
                    self.scroll_layout.addWidget(widget, row, column)
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


pokecollection_win = PokemonCollectionDialog()

def rename_pkmn(nickname, pkmn_name, position):
    try:
        with open(mypokemon_path, "r") as json_file:
            captured_pokemon_data = json.load(json_file)
            pokemon = None
            if captured_pokemon_data:
                for index, pokemon_data in enumerate(captured_pokemon_data):
                    if index == position:
                        pokemon = pokemon_data
                        if pokemon is not None:
                            pokemon["nickname"] = nickname
                            # Load data from the output JSON file
                            with open(str(mypokemon_path), "r") as output_file:
                                mypokemondata = json.load(output_file)
                                # Find and replace the specified Pokémon's data in mypokemondata
                                for index, pokemon_data in enumerate(mypokemondata):
                                    mypokemondata[position] = pokemon
                                    break
                                        # Save the modified data to the output JSON file
                                with open(str(mypokemon_path), "w") as output_file:
                                    json.dump(mypokemondata, output_file, indent=2)
                                showInfo(f"Your {pkmn_name.capitalize()} has been renamed to {nickname}!")
                                pokecollection_win.refresh_pokemon_collection()
    except Exception as e:
        showWarning(f"An error occured: {e}")

def PokemonCollectionDetails(name, level, id, ability, type, detail_stats, attacks, base_experience, growth_rate, description, gender, nickname, position):
    global frontdefault, type_style_file, language, icon_path, gif_in_collection
    # Create the dialog
    try:
        lang_name = get_pokemon_diff_lang_name(int(id)).capitalize()
        lang_desc = get_pokemon_descriptions(int(id))
        description = lang_desc
        wpkmn_details = QDialog(mw)
        if nickname is None:
            wpkmn_details.setWindowTitle(f"Infos to : {lang_name} ")
        else:
            wpkmn_details.setWindowTitle(f"Infos to : {nickname} ({lang_name}) ")

        wpkmn_details.setFixedWidth(500)
        wpkmn_details.setMaximumHeight(400)

        # Create a layout for the dialog
        layout = QVBoxLayout()
        typelayout = QHBoxLayout()
        attackslayout = QVBoxLayout()
        # Display the Pokémon image
        pkmnimage_label = QLabel()
        pkmnpixmap = QPixmap()
        if gif_in_collection is True:
            pkmnimage_path = str(user_path_sprites / "front_default_gif" / f"{int(id)}.gif")
            pkmnimage_label = MovieSplashLabel(pkmnimage_path)
        else:
            pkmnimage_path = str(frontdefault / f"{int(id)}.png")
            pkmnpixmap.load(str(pkmnimage_path))
            # Calculate the new dimensions to maintain the aspect ratio
            max_width = 150
            original_width = pkmnpixmap.width()
            original_height = pkmnpixmap.height()
            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pkmnpixmap = pkmnpixmap.scaled(new_width, new_height)
        typeimage_file = f"{type[0]}.png"
        typeimage_path = addon_dir / "addon_sprites" / "Types" / typeimage_file
        pkmntype_label = QLabel()
        pkmntypepixmap = QPixmap()
        pkmntypepixmap.load(str(typeimage_path))
        if len(type) > 1:
            type_image_file2 = f"{type[1]}.png"
            typeimage_path2 = addon_dir / "addon_sprites" / "Types" / type_image_file2
            pkmntype_label2 = QLabel()
            pkmntypepixmap2 = QPixmap()
            pkmntypepixmap2.load(str(typeimage_path2))
        

        # Create a painter to add text on top of the image
        painter2 = QPainter(pkmnpixmap)

        #custom font
        custom_font = load_custom_font(int(20))

        # Capitalize the first letter of the Pokémon's name
        if nickname is None:
            capitalized_name = f"{lang_name.capitalize()}"
        else:
            capitalized_name = f"{nickname} ({lang_name.capitalize()})"
        # Create level text
        if (
            language == 11
            or language == 12
            or language == 4
            or language == 3
            or language == 2
            or language == 1
        ):
            result = list(split_string_by_length(description, 30))
        else:
            result = list(split_string_by_length(description, 55))
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
        namefont = load_custom_font(int(30))
        namefont.setUnderline(True)
        painter2.setFont(namefont)
        font = load_custom_font(int(20))
        painter2.end()

        # Convert gender name to symbol - this function is from Foxy-null
        if gender == "M":
            gender_symbol = "♂"
        elif gender == "F":
            gender_symbol = "♀"
        elif gender == "N":
            gender_symbol = ""
        else:
            gender_symbol = ""  # None

        # Create a QLabel for the capitalized name
        name_label = QLabel(f"{capitalized_name} - {gender_symbol}")
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
        if language == 1:
            description_font = load_custom_font(int(20))
        else:
            description_font = load_custom_font(int(15))
        description_label.setFont(description_font)
        #stats_label = QLabel(stats_txt)

        # Set the merged image as the pixmap for the QLabel
        if gif_in_collection is False:
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
        pkmntype_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pkmntype_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        if len(type) > 1:
            typelayout.addWidget(pkmntype_label2)
            pkmntype_label2.setStyleSheet("border: 0px solid #000000; padding: 0px;")
            pkmntype_label2.setAlignment(Qt.AlignmentFlag.AlignLeft)
            pkmntype_label2.setAlignment(Qt.AlignmentFlag.AlignBottom)
        typelayout_widget.setLayout(typelayout)
        typelayout_widget.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        typelayout_widget.setFixedWidth(230)
        TopL_layout_Box.addWidget(typelayout_widget)
        TopL_layout_Box.addWidget(ability_label)
        #attackslayout.addWidget(attacks_label)
        attacks_details_button = QPushButton("Attack Details") #add Details to Moves
        qconnect(attacks_details_button.clicked, lambda: attack_details_window(attacks))
        remember_attacks_details_button = QPushButton("Remember Attacks") #add Details to Moves
        all_attacks = get_all_pokemon_moves(name, level)
        qconnect(remember_attacks_details_button.clicked, lambda: remember_attack_details_window(id, attacks, all_attacks))
        
        #free_pokemon_button = QPushButton("Release Pokemon") #add Details to Moves unneeded button
        attacks_label.setFixedHeight(150)
        TopR_layout_Box.addWidget(attacks_label)
        TopR_layout_Box.addWidget(attacks_details_button)
        TopR_layout_Box.addWidget(remember_attacks_details_button)
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
        free_pokemon_button = QPushButton("Release Pokemon") #add Details to Moves
        qconnect(free_pokemon_button.clicked, lambda: PokemonFree(position, name))
        trade_pokemon_button = QPushButton("Trade Pokemon") #add Details to Moves
        qconnect(trade_pokemon_button.clicked, lambda: PokemonTrade(name, id, level, ability, iv, ev, gender, attacks, position))
        layout.addWidget(trade_pokemon_button)
        layout.addWidget(free_pokemon_button)
        rename_button = QPushButton("Rename Pokemon") #add Details to Moves
        rename_input = QLineEdit()
        rename_input.setPlaceholderText("Enter a new Nickname for your Pokemon")
        qconnect(rename_button.clicked, lambda: rename_pkmn(rename_input.text(),name, position))
        layout.addWidget(rename_input)
        layout.addWidget(rename_button)
        #qconnect()
        #layout.addLayout(CompleteTable_layout)

        #wpkmn_details.setFixedWidth(500)
        #wpkmn_details.setMaximumHeight(600)

        # align things needed to middle
        pkmnimage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        growth_rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        base_exp_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        base_exp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pkmntype_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        pkmntype_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        type_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align to the center
        ability_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        attacks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set the layout for the dialog
        wpkmn_details.setLayout(layout)

        # Show the dialog
        wpkmn_details.setWindowIcon(QIcon(str(icon_path))) # Add a Pokeball icon
        # Show the dialog
        wpkmn_details.exec()
    except Exception as e:
        showWarning(f"Error occured in Pokemon Details Button: {e}")

def attack_details_window(attacks):
    global icon_path
    window = QDialog()
    window.setWindowIcon(QIcon(str(icon_path)))
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
        if move is None:
            attack = attack.replace(" ", "")
            try:
                move = find_details_move(attack)
            except:
                showInfo(f"Can't find the attack {attack} in the database.")
                move = find_details_move("tackle")
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
    label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align the label's content to the top
    label.setScaledContents(True)  # Enable scaling of the pixmap

    layout.addWidget(label)
    window.setLayout(layout)
    window.exec()

def remember_attack_details_window(id, attack_set, all_attacks):
    global icon_path
    window = QDialog()
    window.setWindowIcon(QIcon(str(icon_path)))
    layout = QHBoxLayout()
    window.setWindowTitle("Remember Attacks")  # Optional: Set a window title
    # Outer layout contains everything
    outer_layout = QVBoxLayout(window)

    # Create a scroll area that will contain our main layout
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    # Main widget that contains the content
    content_widget = QWidget()
    layout = QHBoxLayout(content_widget)  # The main layout is now set on this widget

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
    for attack in all_attacks:
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
    label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align the label's content to the top
    label.setScaledContents(True)  # Enable scaling of the pixmap
    attack_layout = QVBoxLayout()
    for attack in all_attacks:
        move = find_details_move(attack)
        remember_attack_button = QPushButton(f"Remember {attack}") #add Details to Moves
        remember_attack_button.clicked.connect(lambda checked, a=attack: remember_attack(id, attack_set, a))
        attack_layout.addWidget(remember_attack_button)
    attack_layout_widget = QWidget()
    attack_layout_widget.setLayout(attack_layout)
    # Add the label and button layout widget to the main layout
    layout.addWidget(label)
    layout.addWidget(attack_layout_widget)

    # Set the main widget with content as the scroll area's widget
    scroll_area.setWidget(content_widget)

    # Add the scroll area to the outer layout
    outer_layout.addWidget(scroll_area)

    window.setLayout(outer_layout)
    window.resize(1000, 400)  # Optional: Set a default size for the window
    window.exec()

def remember_attack(id, attacks, new_attack):
    global mainpokemon_path
    if mainpokemon_path.is_file():
        with open(mainpokemon_path, "r") as json_file:
            main_pokemon_data = json.load(json_file)
        for mainpkmndata in main_pokemon_data:
            if mainpkmndata["id"] == id:
                mainpokemon_name = mainpkmndata["name"]
                attacks = mainpkmndata["attacks"]
                if new_attack:
                    msg = ""
                    msg += f"Your {mainpkmndata['name'].capitalize()} can learn a new attack !"
                    if len(attacks) < 4:
                            attacks.append(new_attack)
                            msg += f"\n Your {mainpkmndata['name'].capitalize()} has learned {new_attack} !"
                            showInfo(f"{msg}")
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
                                    showInfo(f"Replaced '{selected_attack}' with '{new_attack}'")
                                else:
                                    # Handle the case where the user cancels the dialog
                                    showInfo(f"{new_attack} will be discarded.")
                mainpkmndata["attacks"] = attacks
                mypkmndata = mainpkmndata
                mainpkmndata = [mainpkmndata]
                # Save the caught Pokémon's data to a JSON file
                with open(str(mainpokemon_path), "w") as json_file:
                    json.dump(mainpkmndata, json_file, indent=2)
                
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
            else:
                showInfo("Please Select this Pokemon first as Main Pokemon ! \n Only Mainpokemons can re-learn attacks!")
    else:
        showWarning("Missing Mainpokemon Data !")
    
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
    icon_path = addon_dir / "addon_sprites" / "Types"
    icon_png_file_path = icon_path / png_file
    return icon_png_file_path

def move_category_path(category):
    global addon_dir
    png_file = f"{category}_move.png"
    category_path = addon_dir / "addon_sprites" / png_file
    return category_path

def MainPokemon(name, nickname, level, id, ability, type, detail_stats, attacks, hp, base_experience, growth_rate, ev, iv, gender):
    # Display the Pokémon image
    global mainpkmn, addon_dir, currdirname, mainpokemon_path
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
    main_pokemon_data = [
        {
            "name": name,
            "nickname": nickname,
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
    new_pokemon() #new pokemon if you change your pokemon
    mainpokemon_data()
    if pkmn_window is True:
        test_window.display_first_encounter()
	
def PokemonDetailsStats(detail_stats, growth_rate, level):
    
    
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
    custom_font = load_custom_font(int(20))

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
        stat_item2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bar_item2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        CompleteTable_layout.addLayout(layout_row)

    return CompleteTable_layout

def PokemonTrade(name, id, level, ability, iv, ev, gender, attacks, position):
    global addon_dir
    global mainpokemon_path
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
        #mw.app.clipboard().setText(pokemon_info)
        mw.app.clipboard().setText(f"{info}")

        # Write the Id, EV, IV and Attacks ID into numbers, seperated by ,
        # Place in a QLabel and Copy to clipboard
        # let player place Number in and find additionally needed data from pokedex
        # at last append to pokemon_list
        # check remove mainpokemon
        # remove pokemon from pokemon_list

        # Show the window
        window.exec()
    else:
        showWarning("You cant trade your Main Pokemon ! \n Please pick a different Main Pokemon and then you can trade this one.")

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

def trade_pokemon(old_pokemon_name, pokemon_trade, position):
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
        pokemon_list[position] = pokemon_trade  # Replace with new Pokemon data
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

def PokemonTradeIn(number_code, old_pokemon_name, position):
    if len(number_code) > 15:
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
        global pokeapi_db_path
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
        #showInfo(f"{pokemon_trade}")

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
        trade_pokemon(f"{old_pokemon_name}", pokemon_trade, position)
        showInfo(f"You have sucessfully traded your {old_pokemon_name} for {name} ")
    else:
        showWarning("Please enter a valid Code !")


def PokemonFree(position, name):
    global mypokemon_path
    global mainpokemon_path

    # Confirmation dialog
    reply = QMessageBox.question(None, "Confirm Release", 
                                 f"Are you sure you want to release {name}?", 
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                 QMessageBox.StandardButton.No)

    if reply == QMessageBox.StandardButton.No:
        showInfo("Release cancelled.")
        return

    # Load the data from the file
    with open(mainpokemon_path, 'r') as file:
        pokemon_data = json.load(file)

    found = False
    for pokemons in pokemon_data:
        if pokemons["name"] == name:
            found = True
            break

    if not found:
        with open(mypokemon_path, 'r') as file:
            pokemon_list = json.load(file)

        # Find and remove the Pokemon with the given name
        #pokemon_list = [p for p in pokemon_list if p['name'] != name]
        pokemon_list.pop(position)

        # Write the updated data back to the file
        with open(mypokemon_path, 'w') as file:
            json.dump(pokemon_list, file, indent=2)
        showInfo(f"{name.capitalize()} has been let free.")
        pokecollection_win.refresh_pokemon_collection()
    else:
        showWarning("You can't free your Main Pokemon!")

def createStatBar(color, value):
    pixmap = QPixmap(200, 10)
    #pixmap.fill(Qt.transparent)
    pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
    painter = QPainter(pixmap)

    # Draw bar in the background
    painter.setPen(QColor(Qt.GlobalColor.black))
    # new change due to pyqt6.6.1
    painter.setBrush(QColor(0, 0, 0, 200))  # Semi-transparent black
    painter.drawRect(0, 0, 200, 10)

    # Draw the colored bar based on the value
    painter.setBrush(color)
    bar_width = int(value * 1)  # Adjust the width as needed
    painter.drawRect(0, 0, bar_width, 10)

    return pixmap

def load_custom_font(font_size):
    global font_path, language
    if language == 1:
        font_file = "pkmn_w.ttf"
        font_file_path = font_path / font_file
        font_size = (font_size * 1) / 2
        if font_file_path.exists():
            font_name = "PKMN Western"
        else:
            font_name = "Early GameBoy"
            font_file = "Early GameBoy.ttf"
            font_size = (font_size * 5) / 7
    else:
        font_name = "Early GameBoy"
        font_file = "Early GameBoy.ttf"
        font_size = (font_size * 2) / 5

    # Register the custom font with its file path
    QFontDatabase.addApplicationFont(str(font_path / font_file))
    custom_font = QFont(font_name)  # Use the font family name you specified in the font file
    custom_font.setPointSize(int(font_size))  # Adjust the font size as needed

    return custom_font

#test functions

def find_experience_for_level(group_growth_rate, level):
    global remove_levelcap
    if level > 100 and remove_levelcap is False:
    	level = 100
    if group_growth_rate == "medium":
        group_growth_rate = "medium-fast"
    elif group_growth_rate == "slow-then-very-fast":
        group_growth_rate = "fluctuating"
    elif group_growth_rate == "fast-then-very-slow":
        group_growth_rate = "fluctuating"
    global next_lvl_file_path
    # Specify the growth rate and level you're interested in
    growth_rate = f'{group_growth_rate}'
    if level < 100:
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
                    break

            return experience
    elif level > 99:
        if group_growth_rate == "erractic":
            if level < 50:
                experience = (level ** 3) * (100 - level) // 50
            elif 50 <= level < 68:
                experience = (level ** 3) * (150 - level) // 100
            elif 68 <= level:
                experience = (level ** 3) * (1911 - 10 * level) // 500
            else:
                experience = (level ** 3) * (160 - level) // 100
        elif group_growth_rate == "fluctuating":
            if level < 15:
                experience = (level ** 3) * (level // 3 + 24) // 50
            elif 15 <= level < 36:
                experience = (level ** 3) * (level + 14) // 50
            elif 36 <= level:
                experience = (level ** 3) * (level // 2 + 32) // 50
        elif group_growth_rate == "fast":
            experience = (4 * (level ** 3)) // 5
        elif group_growth_rate == "medium-fast":
            experience = level ** 3
        elif group_growth_rate == "medium":
            experience = level ** 3
        elif group_growth_rate == "medium-slow":
            experience = (6 * (level ** 3)) // 5 - 15 * (level ** 2) + 100 * level - 140
        elif group_growth_rate == "slow":
            experience = (5 * (level ** 3)) // 4
        return experience

class Downloader(QObject):
    progress_updated = pyqtSignal(int)  # Signal to update progress bar
    download_complete = pyqtSignal()  # Signal when download is complete
    downloading_badges_sprites_txt = pyqtSignal()  # Signal when download is complete
    downloading_sprites_txt = pyqtSignal()  # Signal when download is complete
    downloading_sounds_txt = pyqtSignal()  # Signal when download is complete
    downloading_item_sprites_txt = pyqtSignal()  # Signal when download is complete
    downloading_data_txt = pyqtSignal()  # Signal when download is complete
    downloading_gif_sprites_txt = pyqtSignal()

    def __init__(self, addon_dir, parent=None):
        super().__init__(parent)
        self.addon_dir = Path(addon_dir)
        self.pokedex = []
        global user_path_data, user_path_sprites, pkmnimgfolder, backdefault, frontdefault, sound_list, items_list
        self.items_destination_to = user_path_sprites / "items"
        self.badges_destination_to = user_path_sprites / "badges"
        self.sounds_destination_to = user_path_sprites / "sounds"
        self.front_dir = os.path.join(user_path_sprites, "front_default")
        self.back_dir = os.path.join(user_path_sprites, "back_default")
        self.front_gif_dir = os.path.join(user_path_sprites, "front_default_gif")
        self.back_gif_dir = os.path.join(user_path_sprites, "back_default_gif")
        self.user_path_data = user_path_data
        self.badges_base_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/"
        self.item_base_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/dream-world/"
        self.sounds_base_url = "https://veekun.com/dex/media/pokemon/cries/"
        #self.sound_names = sound_list
        self.sound_names = list(range(1, 722))
        #self.item_names = items_list
        self.item_name = ["absorb-bulb"]
        if not os.path.exists(self.items_destination_to):
            os.makedirs(self.items_destination_to)
        if not os.path.exists(self.badges_destination_to):
            os.makedirs(self.badges_destination_to)
        if not os.path.exists(self.sounds_destination_to):
            os.makedirs(self.sounds_destination_to)
        if not os.path.exists(self.front_dir):
            os.makedirs(self.front_dir)
        if not os.path.exists(self.back_dir):
            os.makedirs(self.back_dir)
        if not os.path.exists(self.user_path_data):
            os.makedirs(self.user_path_data)
        if not os.path.exists(self.back_gif_dir):
            os.makedirs(self.back_gif_dir)
        if not os.path.exists(self.front_gif_dir):
            os.makedirs(self.front_gif_dir)       

        self.urls = [
                "https://play.pokemonshowdown.com/data/learnsets.json",
                "https://play.pokemonshowdown.com/data/pokedex.json",
                "https://play.pokemonshowdown.com/data/moves.json",
                "POKEAPI"
        ]
        self.csv_url = [
                "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/item_names.csv",
                "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/pokemon_species_flavor_text.csv",
                "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/pokemon_species_names.csv",
                "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/move_flavor_text.csv",
                "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/pokemon.csv",
                "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/pokemon_stats.csv"
        ]

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
                "growth_rate": species_data["growth_rate"]["name"]
            }
            self.pokedex.append(entry)

    def download_pokemon_data(self):
        try:
            global user_path_sprites, pkmnimgfolder, backdefault, frontdefault, pokeapi_db_path
            num_files = len(self.urls)
            self.downloading_data_txt.emit()
            for i, url in enumerate(self.urls, start=1):
                if url != "POKEAPI":
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        file_path = self.user_path_data / f"{url.split('/')[-1]}"
                        with open(file_path, 'w') as json_file:
                            json.dump(data, json_file, indent=2)
                    else:
                       print(f"Failed to download data from {url}")  # Replace with a signal if needed
                    progress = int((i / num_files) * 100)
                    self.progress_updated.emit(progress)
                else:  # Handle "POKEAPI" case
                    self.pokedex = []
                    id = 899  # Assuming you want to fetch data for 898 Pokemon
                    for pokemon_id in range(1, id):
                        self.create_pokedex(pokemon_id)
                        progress = int((pokemon_id / id) * 100)
                        self.progress_updated.emit(progress)
                    self.save_to_json(self.pokedex, pokeapi_db_path)
            num_files = len(self.csv_url)
            for i, url in enumerate(self.csv_url, start=1):
                with requests.get(url, stream=True) as r:
                    file_path = self.addon_dir / "user_files" / "data_files" / f"{url.split('/')[-1]}"
                    with open(file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192): 
                            f.write(chunk)
                progress = int((i / num_files) * 100)
                self.progress_updated.emit(progress)
            total_downloaded = 0
            self.downloading_sounds_txt.emit()
            num_sound_files = len(self.sound_names)
            i = 0
            for sound in self.sound_names:
                i += 1
                sound = f"{sound}.ogg"
                sounds_url = self.sounds_base_url + sound
                response = requests.get(sounds_url)
                if response.status_code == 200:
                    with open(os.path.join(self.sounds_destination_to, sound), 'wb') as file:
                        file.write(response.content)
                progress = int((i / num_sound_files) * 100)
                self.progress_updated.emit(progress)
            self.downloading_gif_sprites_txt.emit()
            self.download_complete.emit()
        except Exception as e:
            showWarning(f"An error occurred: {e}")  # Replace with a signal if needed

class LoadingDialog(QDialog):
    def __init__(self, addon_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloading Resources")
        self.label = QLabel("Downloading... \nThis may take several minutes.", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)
        self.start_download(addon_dir)

    def start_download(self, addon_dir):
        self.thread = QThread()
        self.downloader = Downloader(addon_dir)
        self.downloader.moveToThread(self.thread)
        self.thread.started.connect(self.downloader.download_pokemon_data)
        self.downloader.progress_updated.connect(self.progress.setValue)
        self.downloader.downloading_data_txt.connect(self.downloading_data_txt)
        self.downloader.downloading_sprites_txt.connect(self.downloading_sprite_txt)
        self.downloader.downloading_item_sprites_txt.connect(self.downloading_item_sprites_txt)
        self.downloader.downloading_badges_sprites_txt.connect(self.downloading_badges_sprites_txt)
        self.downloader.downloading_sounds_txt.connect(self.downloading_sounds_txt)
        self.downloader.downloading_gif_sprites_txt.connect(self.downloading_gif_sprites_txt)
        self.downloader.progress_updated.connect(self.progress.setValue)
        self.downloader.download_complete.connect(self.on_download_complete)
        self.downloader.download_complete.connect(self.thread.quit)
        self.downloader.download_complete.connect(self.downloader.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_download_complete(self):
        self.label.setText("Download complete! You can now close this window.")
    
    def downloading_data_txt(self):
        self.label.setText("Now Downloading Data Files")

    def downloading_sprite_txt(self):
        self.label.setText("Now Downloading Sprite Files")

    def downloading_sounds_txt(self):
        self.label.setText("Now Downloading Sound Files")
        
    def downloading_item_sprites_txt(self):
        self.label.setText("Now Downloading Item Sprites...")

    def downloading_badges_sprites_txt(self):
        self.label.setText("Now Downloading Badges...")
        
    def downloading_gif_sprites_txt(self):
        self.label.setText("Now Downloading Gif Sprites...")

def show_agreement_and_download_database():
    # Show the agreement dialog
    dialog = AgreementDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        #pyqt6.6.1 difference
        # User agreed, proceed with download
        pokeapi_db_downloader()

def pokeapi_db_downloader():
    global addon_dir
    dlg = LoadingDialog(addon_dir)
    dlg.exec()

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
(2) In the event of a violation of copyright provisions, the user bears full responsibility and the resulting consequences. \n The provider reserves the right to take appropriate legal action \n in the event of becoming aware of any rights violations and to block access to the services.
                       
Check out https://pokeapi.co/docs/v2#fairuse and https://github.com/smogon/pokemon-showdown for more information.
                       """)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(terms)
         # Ensure the terms QLabel is readable and scrolls if necessary
        terms.setWordWrap(True)
        terms.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
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

def animate_pokemon():
    seconds = 2
    from aqt import mw
    reviewer = mw.reviewer
    reviewer.web = mw.reviewer.web
    reviewer.web.eval(f'document.getElementById("PokeImage").style="animation: shake {seconds}s ease;"')
    if show_mainpkmn_in_reviewer is True:
        reviewer.web.eval(f'document.getElementById("MyPokeImage").style="animation: shake {myseconds}s ease;"')
   
if database_complete != False and mainpokemon_empty is False:
    def reviewer_reset_life_bar_inject():
        global life_bar_injected
        life_bar_injected = False
    def inject_life_bar(web_content, context):
        global life_bar_injected, hp, name, level, id, battle_status, show_mainpkmn_in_reviewer, mainpokemon_xp, icon_path
        global frontdefault, backdefault, addon_dir, user_path_sprites, mainpokemon_id, mainpokemon_name, mainpokemon_level, mainpokemon_hp, mainpokemon_stats, mainpokemon_ev, mainpokemon_iv, mainpokemon_growth_rate
        global hp_bar_thickness, xp_bar_config, xp_bar_location, hp_bar_config, xp_bar_spacer, hp_only_spacer, wild_hp_spacer, seconds, myseconds, view_main_front, styling_in_reviewer

        experience_for_next_lvl = find_experience_for_level(mainpokemon_growth_rate, mainpokemon_level)
        if reviewer_image_gif == False:
            pokemon_imagefile = f'{search_pokedex(name.lower(), "num")}.png' #use for png files
            pokemon_image_file = os.path.join(frontdefault, pokemon_imagefile) #use for png files
            if show_mainpkmn_in_reviewer > 0:
                main_pkmn_imagefile = f'{mainpokemon_id}.png' #use for png files
                main_pkmn_imagefile_path = os.path.join(backdefault, main_pkmn_imagefile) #use for png files
        else:
            pokemon_imagefile = f'{search_pokedex(name.lower(), "num")}.gif'
            pokemon_image_file = os.path.join((user_path_sprites / "front_default_gif"), pokemon_imagefile)
            if show_mainpkmn_in_reviewer > 0:
                main_pkmn_imagefile = f'{mainpokemon_id}.gif'
                if view_main_front == -1:
                    gif_type = "front_default_gif" 
                else:
                    gif_type = "back_default_gif"
                main_pkmn_imagefile_path = os.path.join((user_path_sprites / f"{gif_type}"), main_pkmn_imagefile)
        if show_mainpkmn_in_reviewer > 0:
            mainpkmn_max_hp = calculate_hp(mainpokemon_stats["hp"], mainpokemon_level, mainpokemon_ev, mainpokemon_iv)
            mainpkmn_hp_percent = int((mainpokemon_hp / mainpkmn_max_hp) * 50)
            max_hp = calculate_max_hp_wildpokemon()
            pokemon_hp_percent = int((hp / max_hp) * 50)
        else:    
            max_hp = calculate_max_hp_wildpokemon()
            pokemon_hp_percent = int((hp / max_hp) * 100)
        is_reviewer = mw.state == "review"
        # Inject CSS and the life bar only if not injected before and in the reviewer
        pokeball = check_pokecoll_in_list(search_pokedex(name.lower(), "num"))
        if not life_bar_injected and is_reviewer:
            css = """
            """
            if show_mainpkmn_in_reviewer == 0:
                css += f"""
                #life-bar {{
                width: {pokemon_hp_percent}%; /* Replace with the actual percentage */
                height: {hp_bar_thickness}px;
                background: linear-gradient(to right, 
                                            rgba(114, 230, 96, 0.7), /* Green with transparency */
                                            rgba(114, 230, 96, 0.7) 100%, /* Continue green to the percentage point */
                                            rgba(54, 54, 56, 0.7) 100%, /* Transition to dark background */
                                            rgba(54, 54, 56, 0.7)); /* Dark background with transparency */
                position: fixed;
                bottom: {10 + xp_bar_spacer}px;
                left: 0px;
                z-index: 9999;
                border-radius: 5px; /* Shorthand for all corners rounded */
                box-shadow: 0 0 10px rgba(0, 255, 0, 0.8), /* Green glow effect */
                            0 0 30px rgba(54, 54, 56, 1);  /* Dark glow effect */
                }}
                #hp-display {{
                position: fixed;
                bottom: {40 + xp_bar_spacer}px;
                right: 10px;
                z-index: 9999;
                color: white;
                font-size: 16px;
                font-weight: bold; /* Make the text bold */
                background-color: rgb(54,54,56,0.7); 
                text-align: right;
                }}
                #name-display {{
                position: fixed;
                bottom: {40 + xp_bar_spacer}px;
                left: 10px;
                z-index: 9999;
                color: white;
                font-size: 16px;
                background-color: rgb(54,54,56, 0.7);
                text-align: left;
                }}
                #PokeImage {{
                    position: fixed;
                    bottom: {30 + xp_bar_spacer + hp_bar_thickness}px; /* Adjust as needed */
                    left: 3px;
                    z-index: 9999;
                    width: 100px; /* Adjust as needed */
                    height: 100px; /* Adjust as needed */
                    background-size: cover; /* Cover the div area with the image */
                }}
                """
                css += f"""
                    #PokeIcon {{
                    position: fixed;
                    bottom: {85 + xp_bar_spacer}px; /* Adjust as needed */
                    left: 90px;
                    z-index: 9999;
                    width: 25px; /* Adjust as needed */
                    height: 25px; /* Adjust as needed */
                    }}
                    """
            elif show_mainpkmn_in_reviewer == 2:
                css += f"""
                #life-bar {{
                width: {pokemon_hp_percent}%; /* Replace with the actual percentage */
                height: {hp_bar_thickness}px;
                background: linear-gradient(to right, 
                                            rgba(114, 230, 96, 0.7), /* Green with transparency */
                                            rgba(114, 230, 96, 0.7) 100%, /* Continue green to the percentage point */
                                            rgba(54, 54, 56, 0.7) 100%, /* Transition to dark background */
                                            rgba(54, 54, 56, 0.7)); /* Dark background with transparency */
                position: fixed;
                bottom: {130 + xp_bar_spacer}px;
                right: 0px;
                z-index: 9999;
                border-radius: 5px; /* Shorthand for all corners rounded */
                box-shadow: 0 0 10px rgba(0, 255, 0, 0.8), /* Green glow effect */
                            0 0 30px rgba(54, 54, 56, 1);  /* Dark glow effect */
                }}
                #mylife-bar {{
                width: {mainpkmn_hp_percent}%; /* Replace with the actual percentage */
                height: {hp_bar_thickness}px;
                background: linear-gradient(to right, 
                                            rgba(114, 230, 96, 0.7), /* Green with transparency */
                                            rgba(114, 230, 96, 0.7) 100%, /* Continue green to the percentage point */
                                            rgba(54, 54, 56, 0.7) 100%, /* Transition to dark background */
                                            rgba(54, 54, 56, 0.7)); /* Dark background with transparency */
                position: fixed;
                bottom: {25 + xp_bar_spacer}px;
                left: 0px;
                z-index: 9999;
                border-radius: 5px; /* Shorthand for all corners rounded */
                box-shadow: 0 0 10px rgba(0, 255, 0, 0.8), /* Green glow effect */
                            0 0 30px rgba(54, 54, 56, 1);  /* Dark glow effect */
                }}
                #myhp-display {{
                position: fixed;
                bottom: {25 + xp_bar_spacer + hp_bar_thickness}px;
                right: {40 + hp_only_spacer}%;
                z-index: 9999;
                color: white;
                font-size: 16px;
                font-weight: bold; /* Make the text bold */
                background-color: rgb(54,54,56,0.7); 
                text-align: right;
                }}
                #myname-display {{
                position: fixed;
                bottom: {25 + xp_bar_spacer + hp_bar_thickness}px;
                left: 10px;
                z-index: 9999;
                color: white;
                font-size: 16px;
                background-color: rgb(54,54,56, 0.7);
                text-align: left;
                }}
                #MyPokeImage {{
                    position: fixed;
                    bottom: {50 + xp_bar_spacer + hp_bar_thickness}px; /* Adjust as needed */
                    left: 15px;
                    z-index: 9999;
                    background-size: contain;
                    background-repeat: no-repeat;
                    background-position: bottom;
                    transform: scaleX({view_main_front});
                }}
                #hp-display {{
                position: fixed;
                bottom: {160 - wild_hp_spacer + xp_bar_spacer}px;
                left: {50 + hp_only_spacer}%;
                z-index: 9999;
                color: white;
                font-size: 16px;
                font-weight: bold; /* Make the text bold */
                background-color: rgb(54,54,56,0.7); 
                text-align: right;
                }}
                #name-display {{
                position: fixed;
                bottom: {20 + xp_bar_spacer}px;
                right: 10px;
                z-index: 9999;
                color: white;
                font-size: 16px;
                background-color: rgb(54,54,56, 0.7);
                text-align: right;
                }}
                #PokeImage {{
                    position: fixed;
                    bottom: {30 + xp_bar_spacer}px; /* Adjust as needed */
                    right: 3px;
                    z-index: 9999;
                    width: 100px; /* Adjust as needed */
                    height: 100px; /* Adjust as needed */
                    background-size: cover; /* Cover the div area with the image */
                }}"""
                css += f"""
                    #PokeIcon {{
                        position: fixed;
                        bottom: {8 + xp_bar_spacer}px; /* Adjust as needed */
                        right: 20%;
                        z-index: 9999;
                        width: 25px; /* Adjust as needed */
                        height: 25px; /* Adjust as needed */
                        background-size: cover; /* Cover the div area with the image */
                    }}
                    """
            elif show_mainpkmn_in_reviewer == 1:
                css += f"""
                #life-bar {{
                width: {pokemon_hp_percent}%; /* Replace with the actual percentage */
                height: {hp_bar_thickness}px;
                background: linear-gradient(to right, 
                                            rgba(114, 230, 96, 0.7), /* Green with transparency */
                                            rgba(114, 230, 96, 0.7) 100%, /* Continue green to the percentage point */
                                            rgba(54, 54, 56, 0.7) 100%, /* Transition to dark background */
                                            rgba(54, 54, 56, 0.7)); /* Dark background with transparency */
                position: fixed;
                bottom: {10 + xp_bar_spacer}px;
                right: 0px;
                z-index: 9999;
                border-radius: 5px; /* Shorthand for all corners rounded */
                box-shadow: 0 0 10px rgba(0, 255, 0, 0.8), /* Green glow effect */
                            0 0 30px rgba(54, 54, 56, 1);  /* Dark glow effect */
                }}
                #mylife-bar {{
                width: {mainpkmn_hp_percent}%; /* Replace with the actual percentage */
                height: {hp_bar_thickness}px;
                background: linear-gradient(to right, 
                                            rgba(114, 230, 96, 0.7), /* Green with transparency */
                                            rgba(114, 230, 96, 0.7) 100%, /* Continue green to the percentage point */
                                            rgba(54, 54, 56, 0.7) 100%, /* Transition to dark background */
                                            rgba(54, 54, 56, 0.7)); /* Dark background with transparency */
                position: fixed;
                bottom: {10 + xp_bar_spacer}px;
                left: 0px;
                z-index: 9999;
                border-radius: 5px; /* Shorthand for all corners rounded */
                box-shadow: 0 0 10px rgba(0, 255, 0, 0.8), /* Green glow effect */
                            0 0 30px rgba(54, 54, 56, 1);  /* Dark glow effect */
                }}
                #myhp-display {{
                position: fixed;
                bottom: {15 + xp_bar_spacer + hp_bar_thickness}px;
                right: {55}%;
                z-index: 9999;
                color: white;
                font-size: 16px;
                font-weight: bold; /* Make the text bold */
                background-color: rgb(54,54,56,0.7); 
                text-align: right;
                }}
                #myname-display {{
                position: fixed;
                bottom: {15 + xp_bar_spacer + hp_bar_thickness}px;
                left: 10px;
                z-index: 9999;
                color: white;
                font-size: 16px;
                background-color: rgb(54,54,56, 0.7);
                text-align: left;
                }}
                #MyPokeImage {{
                    position: fixed;
                    bottom: {50 + xp_bar_spacer + hp_bar_thickness}px; /* Adjust as needed */
                    left: 3px;
                    z-index: 9999;
                    background-size: contain;
                    background-repeat: no-repeat;
                    background-position: bottom;
                    transform: scaleX({view_main_front});
                }}
                #hp-display {{
                position: fixed;
                bottom: {15 + xp_bar_spacer + hp_bar_thickness}px;
                left: {55}%;
                z-index: 9999;
                color: white;
                font-size: 16px;
                font-weight: bold; /* Make the text bold */
                background-color: rgb(54,54,56,0.7); 
                text-align: right;
                }}
                #name-display {{
                position: fixed;
                bottom: {15 + xp_bar_spacer + hp_bar_thickness}px;
                right: 10px;
                z-index: 9999;
                color: white;
                font-size: 16px;
                background-color: rgb(54,54,56, 0.7);
                text-align: right;
                }}
                #PokeImage {{
                    position: fixed;
                    bottom: {30 + xp_bar_spacer + hp_bar_thickness}px; /* Adjust as needed */
                    right: 3px;
                    z-index: 9999;
                    width: 100px; /* Adjust as needed */
                    height: 100px; /* Adjust as needed */
                    background-size: cover; /* Cover the div area with the image */
                }}"""
                css += f"""
                    #PokeIcon {{
                        position: fixed;
                        bottom: {8 + xp_bar_spacer + hp_bar_thickness}px; /* Adjust as needed */
                        right: 20%;
                        z-index: 9999;
                        width: 25px; /* Adjust as needed */
                        height: 25px; /* Adjust as needed */
                        background-size: cover; /* Cover the div area with the image */
                    }}
                    """

            if xp_bar_config is True:
                css += f"""
                #xp-bar {{
                width: {int((mainpokemon_xp / int(experience_for_next_lvl)) * 100)}%; /* Replace with the actual percentage */
                height: 10px;
                background: linear-gradient(to right, 
                                            rgba(0, 191, 255, 0.7), /* Light Blue with transparency */
                                            rgba(0, 191, 255, 0.7) 100%, /* Continue light blue to the percentage point */
                                            rgba(25, 25, 112, 0.7) 100%, /* Transition to dark blue background */
                                            rgba(25, 25, 112, 0.7)); /* Dark blue background with transparency */
                position: fixed;
                {xp_bar_location}: 0px;
                left: 0px;
                z-index: 9999;
                border-radius: 5px; /* Shorthand for all corners rounded */
                box-shadow: 0 0 10px rgba(0, 191, 255, 0.8), /* Light blue glow effect */
                            0 0 30px rgba(25, 25, 112, 1);  /* Dark blue glow effect */
                }}
                #next_lvl_text {{
                position: fixed;
                {xp_bar_location}: 13px;
                right: 15px;
                z-index: 9999;
                color: white;
                font-size: 10px;
                background-color: rgb(54,54,56, 0.7);
                text-align: right;
                }}
                #xp_text {{
                position: fixed;
                {xp_bar_location}: 13px;
                left: 15px;
                z-index: 9999;
                color: white;
                font-size: 10px;
                background-color: rgb(54,54,56, 0.7);
                text-align: right;
                }}
                """
            css += f"""
            @keyframes shake {{
                0% {{ transform: translateX(0) rotateZ(0); filter: drop-shadow(0 0 10px rgba(255, 0, 0, 0.5)); }}
                10% {{ transform: translateX(-10%) rotateZ(-5deg); }}
                20% {{ transform: translateX(10%) rotateZ(5deg); }}
                30% {{ transform: translateX(-10%) rotateZ(-5deg); }}
                40% {{ transform: translateX(10%) rotateZ(5deg); }}
                50% {{ transform: translateX(-10%) rotateZ(-5deg); }}
                60% {{ transform: translateX(10%) rotateZ(5deg); }}
                70% {{ transform: translateX(-10%) rotateZ(-5deg); }}
                80% {{ transform: translateX(10%) rotateZ(5deg); }}
                90% {{ transform: translateX(-10%) rotateZ(-5deg); }}
                100% {{ transform: translateX(100vw); filter: drop-shadow(0 0 10px rgba(255, 0, 0, 0.5)); }}
            }}
            """
            css += f"""
            #pokebackground {{
                color: white;
                background-color: blue;
                z-index: 99999;
            }}
            """
            # background-image: url('{pokemon_image_file}'); Change to your image path */
            if styling_in_reviewer is True:
                # Inject the CSS into the head of the HTML content
                web_content.head += f"<style>{css}</style>"
                # Inject a div element at the end of the body for the life bar
                #web_content.body += f'<div id="pokebackground">' try adding backgroudns to battle
                if hp_bar_config is True:
                    web_content.body += f'<div id="life-bar"></div>'
                if xp_bar_config is True:
                    web_content.body += f'<div id="xp-bar"></div>'
                    web_content.body += f'<div id="next_lvl_text">Next Level</div>'
                    web_content.body += f'<div id="xp_text">XP</div>'
                # Inject a div element for the text display
                web_content.body += f'<div id="name-display">{name.capitalize()} LvL: {level}</div>'
                if hp > 0:
                    web_content.body += f'{create_status_html(f"{battle_status}")}'
                else:
                    web_content.body += f'{create_status_html(f"fainted")}'

                web_content.body += f'<div id="hp-display">HP: {hp}/{max_hp}</div>'
                # Inject a div element at the end of the body for the life bar
                image_base64 = get_image_as_base64(pokemon_image_file)
                web_content.body += f'<div id="PokeImage"><img src="data:image/png;base64,{image_base64}" alt="PokeImage style="animation: shake 0s ease;"></div>'
                if show_mainpkmn_in_reviewer > 0:
                    image_base64_mypkmn = get_image_as_base64(main_pkmn_imagefile_path)
                    web_content.body += f'<div id="MyPokeImage"><img src="data:image/png;base64,{image_base64_mypkmn}" alt="MyPokeImage" style="animation: shake 0s ease;"></div>'
                    web_content.body += f'<div id="myname-display">{mainpokemon_name.capitalize()} LvL: {mainpokemon_level}</div>'
                    web_content.body += f'<div id="myhp-display">HP: {mainpokemon_hp}/{mainpkmn_max_hp}</div>'
                    # Inject a div element at the end of the body for the life bar
                    if hp_bar_config is True:
                        web_content.body += f'<div id="mylife-bar"></div>'
                # Set the flag to True to indicate that the life bar has been injected
                if pokeball == True:
                    icon_base_64 = get_image_as_base64(icon_path)
                    web_content.body += f'<div id="PokeIcon"><img src="data:image/png;base64,{icon_base_64}" alt="PokeIcon"></div>'
                else:
                    web_content.body += f'<div id="PokeIcon"></div>'
                web_content.body += '</div>'
                life_bar_injected = True
        return web_content

    def update_life_bar(reviewer, card, ease):
        global hp, name, id, frontdefault, battle_status, user_path_sprites, show_mainpkmn_in_reviewer, mainpokemon_hp, mainpokemon_id, mainpokemon_name, mainpokemon_level, mainpokemon_stats, mainpokemon_ev, mainpokemon_iv, mainpokemon_xp, xp_bar_config
        global mainpokemon_level, icon_path, empty_icon_path, seconds, myseconds, view_main_front, pokeball, styling_in_reviewer
        pokeball = check_pokecoll_in_list(search_pokedex(name.lower(), "num"))
        if reviewer_image_gif == False:
            pokemon_imagefile = f'{search_pokedex(name.lower(), "num")}.png' #use for png files
            pokemon_image_file = os.path.join(frontdefault, pokemon_imagefile) #use for png files
            if show_mainpkmn_in_reviewer > 0:
                main_pkmn_imagefile = f'{mainpokemon_id}.png' #use for png files
                main_pkmn_imagefile_path = os.path.join(backdefault, main_pkmn_imagefile) #use for png files
        else:
            pokemon_imagefile = f'{search_pokedex(name.lower(), "num")}.gif'
            pokemon_image_file = os.path.join((user_path_sprites / "front_default_gif"), pokemon_imagefile)
            if show_mainpkmn_in_reviewer > 0:
                main_pkmn_imagefile = f'{mainpokemon_id}.gif'
                if view_main_front == -1:
                    gif_type = "front_default_gif" 
                else:
                    gif_type = "back_default_gif"
                main_pkmn_imagefile_path = os.path.join((user_path_sprites / f"{gif_type}"), main_pkmn_imagefile)
        if show_mainpkmn_in_reviewer > 0:
            mainpkmn_max_hp = calculate_hp(mainpokemon_stats["hp"], mainpokemon_level, mainpokemon_ev, mainpokemon_iv)
            mainpkmn_hp_percent = int((mainpokemon_hp / mainpkmn_max_hp) * 50)
            max_hp = calculate_max_hp_wildpokemon()
            pokemon_hp_percent = int((hp / max_hp) * 50)
            image_base64_mainpkmn = get_image_as_base64(main_pkmn_imagefile_path)
        else:    
            max_hp = calculate_max_hp_wildpokemon()
            pokemon_hp_percent = int((hp / max_hp) * 100)
        image_base64 = get_image_as_base64(pokemon_image_file)
        # Determine the color based on the percentage
        if hp < int(0.25 * max_hp):
            hp_color = "rgba(255, 0, 0, 0.7)"  # Red
        elif hp < int(0.5 * max_hp):
            hp_color = "rgba(255, 140, 0, 0.7)"  # Dark Orange
        elif hp < int(0.75 * max_hp):
            hp_color = "rgba(255, 255, 0, 0.7)"  # Yellow
        else:
            hp_color = "rgba(114, 230, 96, 0.7)"  # Green

        if show_mainpkmn_in_reviewer > 0:
            if mainpokemon_hp < int(0.25 * mainpkmn_max_hp):
                myhp_color = "rgba(255, 0, 0, 0.7)"  # Red
            elif mainpokemon_hp < int(0.5 * mainpkmn_max_hp):
                myhp_color = "rgba(255, 140, 0, 0.7)"  # Dark Orange
            elif mainpokemon_hp < int(0.75 * mainpkmn_max_hp):
                myhp_color = "rgba(255, 255, 0, 0.7)"  # Yellow
            else:
                myhp_color = "rgba(114, 230, 96, 0.7)"  # Green
        # Extract RGB values from the hex color code
        #hex_color = hp_color.lstrip('#')
        #rgb_values = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
        status_html = ""
        if hp < 1:
            status_html = create_status_html('fainted')
        elif hp > 0:
            status_html = create_status_html(f"{battle_status}")
        if styling_in_reviewer is True:
            # Refresh the reviewer content to apply the updated life bar
            reviewer.web.eval('document.getElementById("life-bar").style.width = "' + str(pokemon_hp_percent) + '%";')
            reviewer.web.eval('document.getElementById("life-bar").style.background = "linear-gradient(to right, ' + str(hp_color) + ', ' + str(hp_color) + ' ' + '100' + '%, ' + 'rgba(54, 54, 56, 0.7)' + '100' + '%, ' + 'rgba(54, 54, 56, 0.7)' + ')";')
            reviewer.web.eval('document.getElementById("life-bar").style.boxShadow = "0 0 10px ' + hp_color + ', 0 0 30px rgba(54, 54, 56, 1)";');
            if xp_bar_config is True:
                experience_for_next_lvl = find_experience_for_level(mainpokemon_growth_rate, mainpokemon_level)
                xp_bar_percent = int((mainpokemon_xp / int(experience_for_next_lvl)) * 100)
                reviewer.web.eval('document.getElementById("xp-bar").style.width = "' + str(xp_bar_percent) + '%";')
            name_display_text = f"{name.capitalize()} LvL: {level}"
            hp_display_text = f"HP: {hp}/{max_hp}"
            reviewer.web.eval('document.getElementById("name-display").innerText = "' + name_display_text + '";')
            reviewer.web.eval('document.getElementById("hp-display").innerText = "' + hp_display_text + '";')
            new_html_content = f'<img src="data:image/png;base64,{image_base64}" alt="PokeImage" style="animation: shake {seconds}s ease;">'
            reviewer.web.eval(f'document.getElementById("PokeImage").innerHTML = `{new_html_content}`;')
            if pokeball == True:
                image_icon_path = get_image_as_base64(icon_path)
                pokeicon_html = f'<img src="data:image/png;base64,{image_icon_path}" alt="PokeIcon">'
            else:
                pokeicon_html = ''
            reviewer.web.eval(f'document.getElementById("PokeIcon").innerHTML = `{pokeicon_html}`;')
            reviewer.web.eval(f'document.getElementById("pokestatus").innerHTML = `{status_html}`;')
            if show_mainpkmn_in_reviewer > 0:
                new_html_content_mainpkmn = f'<img src="data:image/png;base64,{image_base64_mainpkmn}" alt="MyPokeImage" style="animation: shake {myseconds}s ease;">'
                main_name_display_text = f"{mainpokemon_name.capitalize()} LvL: {mainpokemon_level}"
                main_hp_display_text = f"HP: {mainpokemon_hp}/{mainpkmn_max_hp}"
                reviewer.web.eval('document.getElementById("mylife-bar").style.width = "' + str(mainpkmn_hp_percent) + '%";')
                reviewer.web.eval('document.getElementById("mylife-bar").style.background = "linear-gradient(to right, ' + str(myhp_color) + ', ' + str(myhp_color) + ' ' + '100' + '%, ' + 'rgba(54, 54, 56, 0.7)' + '100' + '%, ' + 'rgba(54, 54, 56, 0.7)' + ')";')
                reviewer.web.eval('document.getElementById("mylife-bar").style.boxShadow = "0 0 10px ' + myhp_color + ', 0 0 30px rgba(54, 54, 56, 1)";');
                reviewer.web.eval(f'document.getElementById("MyPokeImage").innerHTML = `{new_html_content_mainpkmn}`;')
                reviewer.web.eval('document.getElementById("myname-display").innerText = "' + main_name_display_text + '";')
                reviewer.web.eval('document.getElementById("myhp-display").innerText = "' + main_hp_display_text + '";')

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
    global pokeapi_db_path
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
    # Save the caught Pokémon's data to a JSON file
    with open(str(mainpokemon_path), "w") as json_file:
        json.dump(caught_pokemon_data, json_file, indent=2)
    mainpokemon_name, mainpokemon_id, mainpokemon_ability, mainpokemon_type, mainpokemon_stats, mainpokemon_attacks, mainpokemon_level, mainpokemon_base_experience, mainpokemon_xp, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate, mainpokemon_ev, mainpokemon_iv, mainpokemon_evolutions, mainpokemon_battle_stats, mainpokemon_gender, mainpokemon_nickname = mainpokemon_data()

    # Save the caught Pokémon's data to a JSON file
    with open(str(mypokemon_path), "w") as json_file:
        json.dump(caught_pokemon_data, json_file, indent=2)

    showInfo(f"{name.capitalize()} has been chosen as Starter Pokemon !")

    starter_window.display_chosen_starter_pokemon(starter_name)

def save_outside_pokemon(pokemon_name, pokemon_id):
    global mypokemon_path, addon_dir, mainpokemon_path
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
    global pokeapi_db_path
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
        with open(mypokemon_path, "r") as json_file:
            caught_pokemon_data = json.load(json_file)
    else:
        caught_pokemon_data = []

    # Append the caught Pokémon's data to the list
    caught_pokemon_data.append(caught_pokemon)
    # Save the caught Pokémon's data to a JSON file
    with open(str(mypokemon_path), "w") as json_file:
        json.dump(caught_pokemon_data, json_file, indent=2)

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
                    pokemon_info += f"\n"
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
        showInfo(f"An error occurred: {e}")

def flex_pokemon_collection():
    # Create a main window
    export_window = QDialog()
    #export_window.setWindowTitle("Export Pokemon to Pkmn Showdown")

    # Information label
    info = "Pokemon Infos have been Copied to your Clipboard! \nNow simply paste this text into https://pokepast.es/.\nAfter pasting the infos in your clipboard and submitting the needed infos on the right,\n you will receive a link to send friends to flex."
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
                    pokemon_info += f"\n"
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
        showInfo(f"An error occurred: {e}")

def open_browser_window():
    # Open the Pokémon Showdown Team Builder in the default web browser
    url = "https://pokepast.es/"
    QDesktopServices.openUrl(QUrl(url))

def calc_exp_gain(base_experience, w_pkmn_level):
    exp = int((base_experience * w_pkmn_level) / 7)
    return exp

# Define the function to open the Pokémon Showdown Team Builder
def open_team_builder():
    # Specify the URL of the Pokémon Showdown Team Builder
    team_builder_url = "https://play.pokemonshowdown.com/teambuilder"

    # Open the Team Builder in the default web browser
    QDesktopServices.openUrl(QUrl(team_builder_url))

def rate_addon_url():
    # Specify the URL of the Pokémon Showdown Team Builder
    rating_url = "https://ankiweb.net/shared/review/1908235722"

    # Open the Team Builder in the default web browser
    QDesktopServices.openUrl(QUrl(rating_url))

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
        global addon_dir, icon_path
        layout = QVBoxLayout()
        # Main window layout
        global addon_dir
        layout = QVBoxLayout()
        image_file = f"ankimon_logo.png"
        image_path = str(addon_dir) + "/" + image_file
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
        # Set window
        self.setWindowTitle('Ankimon Window')
        self.setWindowIcon(QIcon(str(icon_path))) # Add a Pokeball icon
        # Display the Pokémon image

    def open_dynamic_window(self):
        # Create and show the dynamic window
        try:
            global pkmn_window
            if pkmn_window == False:
                self.display_first_encounter()
                pkmn_window = True
            self.show()
        except Exception as e:
            showWarning(f"Following Error occured when opening window: {e}")

    def display_first_start_up(self):
        global first_start, pkmn_window
        if first_start == False:
            from aqt import mw

            # Get the geometry of the main screen
            main_screen_geometry = mw.geometry()
            # Calculate the position to center the ItemWindow on the main screen
            x = main_screen_geometry.center().x() - self.width() / 2
            y = main_screen_geometry.center().y() - self.height() / 2
            self.setGeometry(x, y, 256, 256 )
            self.move(x,y)
            self.show()
            first_start = True
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
        global battlescene_path, battlescene_path_without_dialog, battlescene_file, battle_ui_path
        global attack_counter, merged_pixmap, window
        attack_counter = 0
        caught = 0
        id = int(search_pokedex(name.lower(), "num"))
        # Capitalize the first letter of the Pokémon's name
        lang_name = get_pokemon_diff_lang_name(int(id))
        name = name.capitalize()
        # calculate wild pokemon max hp
        max_hp = calculate_hp(stats["hp"], level, ev, iv)
        mainpkmn_max_hp = calculate_hp(mainpokemon_stats["hp"], mainpokemon_level, mainpokemon_ev, mainpokemon_iv)
        message_box_text = (f"A wild {lang_name.capitalize()} appeared !")
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
            #merged_pixmap.fill(Qt.transparent)
            merged_pixmap.fill(QColor(0, 0, 0, 0))
            # RGBA where A (alpha) is 0 for full transparency
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
            draw_hp_bar(401, 208, 8, 116, mainpokemon_hp, mainpkmn_max_hp)  # main pokemon hp_bar

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
            custom_font = load_custom_font(int(26))
            msg_font = load_custom_font(int(32))
            mainpokemon_lang_name = get_pokemon_diff_lang_name(int(mainpokemon_id))
            # Draw the text on top of the image
            # Adjust the font size as needed
            painter.setFont(custom_font)
            painter.setPen(QColor(31, 31, 39))  # Text color
            painter.drawText(48, 67, f"{lang_name} {gender_symbol}")
            painter.drawText(326, 200, mainpokemon_lang_name)
            painter.drawText(208, 67, lvl)
            #painter.drawText(55, 85, gender_text)
            painter.drawText(490, 199, mainlvl)
            painter.drawText(487, 238, f"{mainpkmn_max_hp}")
            painter.drawText(442, 238, f"{mainpokemon_hp}")
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
        #merged_pixmap.fill(Qt.transparent)
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
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
        custom_font = load_custom_font(int(28))
        msg_font = load_custom_font(int(32))

        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(31, 31, 39))  # Text color
        lang_name = get_pokemon_diff_lang_name(int(id))
        painter.drawText(48, 67, lang_name)
        mainpokemon_lang_name = get_pokemon_diff_lang_name(int(mainpokemon_id))
        painter.drawText(326, 200, mainpokemon_lang_name)
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
        global pokemon_encounter, user_path_sprites
        global addon_dir
        global frontdefault
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
        custom_font = load_custom_font(int(26))
        message_box_text = f"You have received a item: {item.capitalize()} !"
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(50, 290, message_box_text)
        custom_font = load_custom_font(int(20))
        painter.setFont(custom_font)
        #painter.drawText(10, 330, "You can look this up in your item bag.")
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        image_label = QLabel()
        image_label.setPixmap(merged_pixmap)

        return image_label

    def pokemon_display_badge(self, badge_number):
        try:
            global pokemon_encounter, addon_dir, badges_path, badges
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
            custom_font = load_custom_font(int(20))
            message_box_text = f"You have received a badge for:"
            message_box_text2 = f"{badges[str(badge_number)]}!"
            # Draw the text on top of the image
            # Adjust the font size as needed
            painter.setFont(custom_font)
            painter.setPen(QColor(255,255,255))  # Text color
            painter.drawText(120, 270, message_box_text)
            painter.drawText(140, 290, message_box_text2)
            custom_font = load_custom_font(int(20))
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
        global pokemon_hp, name, id, level, type, caught_pokemon, pkmnimgfolder, frontdefault, addon_dir, caught, pokedex_image_path
        # Create the dialog
        lang_name = get_pokemon_diff_lang_name(int(id))
        window_title = (f"Would you want let the  wild {lang_name} free or catch the wild {lang_name} ?")
        # Display the Pokémon image
        pkmnimage_file = f"{int(search_pokedex(name.lower(),'num'))}.png"
        pkmnimage_path = frontdefault / pkmnimage_file
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
        capitalized_name = lang_name.capitalize()
        # Create level text
        lvl = (f" Level: {level}")

        # Draw the text on top of the image
        font = QFont()
        font.setPointSize(20)  # Adjust the font size as needed
        painter2.setFont(font)
        painter2.drawText(270,107,f"{lang_name}")
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

        kill_button = QPushButton("Defeat Pokémon")
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

    def rate_display_item(self, item):
        Receive_Window = QDialog(mw)
        layout = QHBoxLayout()
        item_name = item
        item_widget = self.pokemon_display_item(item_name)
        layout.addWidget(item_widget)
        Receive_Window.setStyleSheet("background-color: rgb(44,44,44);")
        Receive_Window.setMaximumWidth(512)
        Receive_Window.setMaximumHeight(320)
        Receive_Window.setLayout(layout)
        Receive_Window.show()
    
    def display_item(self):
        Receive_Window = QDialog(mw)
        layout = QHBoxLayout()
        item_name = random_item()
        item_widget = self.pokemon_display_item(item_name)
        layout.addWidget(item_widget)
        Receive_Window.setStyleSheet("background-color: rgb(44,44,44);")
        Receive_Window.setMaximumWidth(512)
        Receive_Window.setMaximumHeight(320)
        Receive_Window.setLayout(layout)
        Receive_Window.show()

    def display_badge(self, badge_num):
        Receive_Window = QDialog(mw)
        Receive_Window.setWindowTitle("You have received a Badge!")
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

    def keyPressEvent(self, event):
        global test, pokemon_encounter, pokedex_image_path, system, ankimon_key
        open_window_key = getattr(Qt.Key, 'Key_' + ankimon_key.upper())
        if system == "mac":
            if event.key() == open_window_key and event.modifiers() == Qt.KeyboardModifier.MetaModifier:
                self.close()
        else:
            if event.key() == open_window_key and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.close()

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

#Test window
def rate_this_addon():
    global rate_this, rate_path, itembag_path
    # Load rate data
    with open(rate_path, 'r') as file:
        rate_data = json.load(file)
        rate_this = rate_data.get("rate_this", False)
    
    # Check if rating is needed
    if not rate_this:
        rate_window = QDialog()
        rate_window.setWindowTitle("Please Rate this Addon!")
        
        layout = QVBoxLayout(rate_window)
        
        text_label = QLabel("""Thanks for using Ankimon! 
                            \nI would like Ankimon to be known even more in the community, 
                            \nand a rating would be amazing. Letting others know what you think of the addon.
                            \nThis takes less than a minute.

                            \nIf you do not want to rate this addon. Feel free to press: I dont want to rate this addon.
                            """)
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
            thx_label = QLabel("""
            Thank you for Rating this Addon !
                               
            Please exit this window!
            """)
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
            showInfo("""This Pop Up wont turn up on startup anymore.
            If you decide to rate this addon later on.
            You can go to Ankimon => Rate This.
            Anyway, have fun playing !
            """)

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
                with open(itembag_path, 'r') as json_file:
                    itembag_list = json.load(json_file)
                    itembag_list.append("potion")
                with open(itembag_path, 'w') as json_file:
                    json.dump(itembag_list, json_file)
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


if database_complete is True:
    with open(badgebag_path, 'r') as json_file:
        badge_list = json.load(json_file)
        if len(badge_list) > 2:
            rate_this_addon()

#Badges needed for achievements:
with open(badges_list_path, 'r') as json_file:
    badges = json.load(json_file)

achievements = {str(i): False for i in range(1, 69)}

def check_badges(achievements):
        with open(badgebag_path, 'r') as json_file:
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
        showInfo("You have chosen your Starter Pokemon ! \n You can now close this window ! \n Please restart your Anki to restart your Pokemon Journey!")
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
        showInfo("You have received your Fossil Pokemon ! \n You can now close this window !")
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
        global pokemon_encounter
        global addon_dir
        global frontdefault
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
        custom_font = load_custom_font(int(28))
        message_box_text = "Choose your Starter Pokemon"
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(110, 310, message_box_text)
        custom_font = load_custom_font(int(20))
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
        custom_font = load_custom_font(int(32))
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
        global pokemon_encounter
        global addon_dir
        global frontdefault
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
        custom_font = load_custom_font(int(32))
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
        global addon_dir, frontdefault
        bckgimage_path = addon_dir / "addon_sprites" / "starter_screen" / "bg.png"
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
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        #merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)
        painter.drawPixmap(125,10,image_pixmap)

        # custom font
        custom_font = load_custom_font(int(20))
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
        except (IndexError, ValueError, TypeError) as e:
            showInfo(f"Error finding evolution details: {e}")
        window_title = (f"{pkmn_name.capitalize()} is evolving to {pokemon_evo.capitalize()} ?")
        # Display the Pokémon image
        pkmnimage_path = frontdefault / f"{pkmn_id}.png"
        #pkmnimage_path2 = addon_dir / frontdefault / f"{mainpokemon_prevo_id}.png"
        pkmnimage_path2 = frontdefault / f"{(pokemon_evo_id)}.png"
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
        if not (obj is mw and event.type() == QEvent.Type.KeyPress):
            return False # Andere Event-Handler nicht blockieren
        global system, ankimon_key, hp
        open_window_key = getattr(Qt.Key, 'Key_' + ankimon_key.upper())
        control_modifier = Qt.KeyboardModifier.MetaModifier if system == "mac" else Qt.KeyboardModifier.ControlModifier
        if event.key() == open_window_key and event.modifiers() == control_modifier:
            if test_window.isVisible():
                test_window.close()  # Testfenster schließen, wenn Shift gedrückt wird
            else:
                if first_start == False:
                    test_window.display_first_start_up()
                else:
                    test_window.open_dynamic_window()

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
        global eff_chart_html_path

        # Create a label and set HTML content
        label = QLabel()
        html_content = self.read_html_file(f"{eff_chart_html_path}")  # Replace with the path to your HTML file
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

class Pokedex_Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.read_poke_coll()
        self.initUI()

    def read_poke_coll(self):
        global mypokemon_path
        with (open(mypokemon_path, "r") as json_file):
            self.captured_pokemon_data = json.load(json_file)

    def initUI(self):
        self.setWindowTitle("Pokédex")
        global addon_dir

        # Create a label and set HTML content
        label = QLabel()
        pokedex_html_template = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pokédex</title>
        <style>
        .pokedex-table { width: 100%; border-collapse: collapse; }
        .pokedex-table th, .pokedex-table td { border: 1px solid #ddd; text-align: left; padding: 8px; }
        .pokedex-table tr:nth-child(even) { background-color: #f2f2f2; }
        .pokedex-table th { padding-top: 12px; padding-bottom: 12px; background-color: #4CAF50; color: white; }
        .pokemon-image { height: 50px; width: 50px; }
        .pokemon-gray { filter: grayscale(100%); }
        </style>
        </head>
        <body>
        <table class="pokedex-table">
        <tr>
            <th>No.</th>
            <th>Name</th>
            <th>Image</th>
        </tr>
        <!-- Table Rows Will Go Here -->
        </table>
        </body>
        </html>
        '''
        # Extract the IDs of the Pokémon listed in the JSON file
        self.available_pokedex_ids = {pokemon['id'] for pokemon in self.captured_pokemon_data}

        # Now we generate the HTML rows for each Pokémon in the range 1-898, graying out those not in the JSON file
        table_rows = [self.generate_table_row(i, i not in self.available_pokedex_ids) for i in range(1, 899)]

        # Combine the HTML template with the generated rows
        html_content = pokedex_html_template.replace('<!-- Table Rows Will Go Here -->', ''.join(table_rows))

        #html_content = self.read_html_file(f"{pokedex_html_path}")  # Replace with the path to your HTML file
        label.setText(html_content)  # 'html_table' contains the HTML table string
        label.setWordWrap(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

    # Helper function to generate table rows
    def generate_table_row(self, pokedex_number, is_gray):
        name = f"Pokemon #{pokedex_number}" # Placeholder, actual name should be fetched from a database or API
        image_class = "pokemon-gray" if is_gray else ""
        return f'''
        <tr>
            <td>{pokedex_number}</td>
            <td>{name}</td>
            <td><img src="{pokedex_number}.png" alt="{name}" class="pokemon-image {image_class}" /></td>
        </tr>
        '''

    def read_html_file(self, file_path):
        """Reads an HTML file and returns its content as a string."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
        
    def show_pokedex(self):
        self.read_poke_coll()
        self.show()

class IDTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Pokémon - Generations and ID")
        global table_gen_id_html_path
        # Create a label and set HTML content
        label = QLabel()
        html_content = self.read_html_file(f"{table_gen_id_html_path}")  # Replace with the path to your HTML file
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

if database_complete!= False:
    if mypokemon_path.is_file() is False:
        starter_window.display_starter_pokemon()
    else:
        with open(mypokemon_path, 'r') as file:
            pokemon_list = json.load(file)
            if not pokemon_list :
                starter_window.display_starter_pokemon()

eff_chart = TableWidget()
pokedex = Pokedex_Widget()
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
        global icon_path
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
        
        self.evolution_items = {

        }
        
        self.tm_hm_list = {

        }

        self.setWindowIcon(QIcon(str(icon_path))) # Add a Pokeball icon
        self.setWindowTitle("Itembag")
        self.layout = QVBoxLayout()  # Main layout is now a QVBoxLayout

        # Search Filter
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search Items...")
        self.search_edit.returnPressed.connect(self.filter_items)
        #self.search_edit.textChanged.connect(self.filter_pokemon)
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
            for item_name in self.itembag_list:
                item_widget = self.ItemLabel(item_name)
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

        if not self.itembag_list:  # Simplified check
            empty_label = QLabel("Empty Search")
            self.contentLayout.addWidget(empty_label, 1, 1)
        else:
            # Filter items based on category index
            if category_index == 1:  # Heal items
                filtered_items = [item_name for item_name in self.itembag_list if item_name in self.fossil_pokemon and search_text in item_name.lower()]
            elif category_index == 2:  # Heal items
                filtered_items = [item_name for item_name in self.itembag_list if item_name in self.tm_hm_list and search_text in item_name.lower()]
            elif category_index == 3:
                filtered_items = [item_name for item_name in self.itembag_list if item_name in self.hp_heal_items and search_text in item_name.lower()]
            elif category_index == 4:
                filtered_items = [item_name for item_name in self.itembag_list if item_name in self.evolution_items and search_text in item_name.lower()]
            else:
                filtered_items = [item_name for item_name in self.itembag_list if search_text in item_name.lower()]

            for item_name in filtered_items:
                item_widget = self.ItemLabel(item_name)
                self.contentLayout.addWidget(item_widget, row, col)
                col += 1
                if col >= max_items_per_row:
                    row += 1
                    col = 0

    def ItemLabel(self, item_name):
        item_file_path = items_path / f"{item_name}.png"
        item_frame = QVBoxLayout() #itemframe
        info_item_button = QPushButton("More Info")
        info_item_button.clicked.connect(lambda: self.more_info_button_act(item_name))
        item_name_for_label = item_name.replace("-", " ")   # Remove hyphens from item_name
        item_name_label = QLabel(f"{item_name_for_label.capitalize()}") #itemname
        item_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_picture_pixmap = QPixmap(str(item_file_path))
        item_picture_label = QLabel()
        item_picture_label.setPixmap(item_picture_pixmap)
        item_picture_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_frame.addWidget(item_picture_label)
        item_frame.addWidget(item_name_label)
        item_name = item_name.lower()
        if item_name in self.hp_heal_items :
            use_item_button = QPushButton("Heal Mainpokemon")
            global mainpokemon_name
            hp_heal = self.hp_heal_items[item_name]
            use_item_button.clicked.connect(lambda: self.Check_Heal_Item(mainpokemon_name, hp_heal, item_name))
        elif item_name in self.fossil_pokemon:
            fossil_id = self.fossil_pokemon[item_name]
            fossil_pokemon_name = search_pokedex_by_id(fossil_id)
            use_item_button = QPushButton(f"Evolve Fossil to {fossil_pokemon_name.capitalize()}")
            use_item_button.clicked.connect(lambda: self.Evolve_Fossil(item_name, fossil_id, fossil_pokemon_name))
        else:
            use_item_button = QPushButton("Evolve Pokemon")
            use_item_button.clicked.connect(lambda: self.Check_Evo_Item(comboBox.currentText(), item_name))
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
            with open(mypokemon_path, "r") as json_file:
                captured_pokemon_data = json.load(json_file)
                if captured_pokemon_data:
                    for pokemon in captured_pokemon_data:
                        pokemon_name = pokemon['name']
                        comboBox.addItem(f"{pokemon_name}")
        except:
            pass
    
    def Evolve_Fossil(self, item_name, fossil_id, fossil_poke_name):
        starter_window.display_fossil_pokemon(fossil_id, fossil_poke_name)
        save_outside_pokemon(fossil_poke_name, fossil_id)
        self.delete_item(item_name)


    def delete_item(self, item_name):
        self.read_item_file()
        if item_name in self.itembag_list:
            self.itembag_list.remove(item_name)
        self.write_item_file()
        self.renewWidgets()

    def Check_Heal_Item(self, pkmn_name, heal_points, item_name):
        global achievments
        check = check_for_badge(achievements,20)
        if check is False:
            receive_badge(20,achievements)
            test_window.display_badge(20)
        global mainpokemon_hp, mainpokemon_stats, mainpokemon_level, mainpokemon_ev, mainpokemon_iv
        mainpkmn_max_hp = calculate_hp(mainpokemon_stats["hp"], mainpokemon_level, mainpokemon_ev, mainpokemon_iv)
        if item_name == "fullrestore" or "maxpotion":
            heal_points = mainpkmn_max_hp
        mainpokemon_hp += heal_points
        if mainpokemon_hp > (mainpkmn_max_hp + 1):
            mainpokemon_hp = mainpkmn_max_hp
        self.delete_item(item_name)
        play_effect_sound("HpHeal")
        showInfo(f"{pkmn_name} was healed for {heal_points}")

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
    
    def write_item_file(self):
        with open(itembag_path, 'w') as json_file:
            json.dump(self.itembag_list, json_file)

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
        from aqt import mw

        # Get the geometry of the main screen
        main_screen_geometry = mw.geometry()
        
        # Calculate the position to center the ItemWindow on the main screen
        x = main_screen_geometry.center().x() - self.width() / 2
        y = main_screen_geometry.center().y() - self.height() / 2
        
        # Move the ItemWindow to the calculated position
        self.move(x, y)
        
        self.show()

    def more_info_button_act(self, item_name):
        description = get_id_and_description_by_item_name(item_name)
        showInfo(f"{description}")
    
def read_csv_file(csv_file):
    item_id_mapping = {}
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            item_id_mapping[row['name'].lower()] = int(row['item_id'])
    return item_id_mapping

def capitalize_each_word(item_name):
    # Replace hyphens with spaces and capitalize each word
    return ' '.join(word.capitalize() for word in item_name.replace("-", " ").split())

def read_descriptions_csv(csv_file):
    descriptions = {}
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            item_id = int(row[0])
            version_group_id = int(row[1])
            language_id = int(row[2])
            description = row[3].strip('"')
            key = (item_id, version_group_id, language_id)
            descriptions[key] = description
    return descriptions

def get_id_and_description_by_item_name(item_name):
    global csv_file_descriptions, csv_file_items
    item_name = capitalize_each_word(item_name)
    item_id_mapping = read_csv_file(csv_file_items)
    item_id = item_id_mapping.get(item_name.lower())
    if item_id is None:
        return None, None
    descriptions = read_descriptions_csv(csv_file_descriptions)
    key = (item_id, 11, 9)  # Assuming version_group_id 11 and language_id 9
    description = descriptions.get(key, None)
    return description
    
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


class AchievementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.read_item_file()
        self.initUI()

    def initUI(self):
        global addon_dir, icon_path
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
        with open(badgebag_path, 'r') as json_file:
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
        from aqt import mw

        # Get the geometry of the main screen
        main_screen_geometry = mw.geometry()
        
        # Calculate the position to center the ItemWindow on the main screen
        x = main_screen_geometry.center().x() - self.width() / 2
        y = main_screen_geometry.center().y() - self.height() / 2
        
        # Move the ItemWindow to the calculated position
        self.move(x, y)
        
        self.show()

def report_bug():
    # Specify the URL of the Pokémon Showdown Team Builder
    bug_url = "https://github.com/Unlucky-Life/ankimon/issues"

    # Open the Team Builder in the default web browser
    QDesktopServices.openUrl(QUrl(bug_url))

achievement_bag = AchievementWindow()

# Custom Dialog class
class Version_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        global icon_path
        self.setWindowTitle("Ankimon Notifications")
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # For horizontal scrollbar, if you want it off
        self.local_file_path = addon_dir / "update_notes.md"
        self.local_content = read_local_file(self.local_file_path)
        self.html_content = markdown.markdown(self.local_content)
        self.text_edit.setHtml(self.html_content)
        layout.addWidget(self.text_edit)
        self.setWindowIcon(QIcon(str(icon_path)))
        self.setLayout(layout)
    
    def open(self):
        self.exec()

version_dialog = Version_Dialog()

#buttonlayout
mw.pokemenu = QMenu('&Ankimon', mw)
# and add it to the tools menu
mw.form.menubar.addMenu(mw.pokemenu)

if database_complete != False:
    pokecol_action = QAction("Show Pokemon Collection", mw)
    # set it to call testFunction when it's clicked
    mw.pokemenu.addAction(pokecol_action)
    qconnect(pokecol_action.triggered, pokecollection_win.show)
    # Make new PokeAnki menu under tools

    test_action10 = QAction("Open Ankimon Window", mw)
    #test_action10.triggered.connect(test_window.open_dynamic_window)
    mw.pokemenu.addAction(test_action10)
    qconnect(test_action10.triggered, test_window.open_dynamic_window)

    test_action15 = QAction("Itembag", mw)
    test_action15.triggered.connect(item_window.show_window)
    mw.pokemenu.addAction(test_action15)

    achievement_bag_action = QAction("Achievements", mw)
    achievement_bag_action.triggered.connect(achievement_bag.show_window)
    mw.pokemenu.addAction(achievement_bag_action)

    test_action8 = QAction("Open Pokemon Showdown Teambuilder", mw)
    qconnect(test_action8.triggered, open_team_builder)
    mw.pokemenu.addAction(test_action8)

    test_action6 = QAction("Export Main Pokemon to PkmnShowdown", mw)
    qconnect(test_action6.triggered, export_to_pkmn_showdown)
    mw.pokemenu.addAction(test_action6)

    test_action7 = QAction("Export All Pokemon to PkmnShowdown", mw)
    qconnect(test_action7.triggered, export_all_pkmn_showdown)
    mw.pokemenu.addAction(test_action7)

    flex_pokecoll_action = QAction("Export All Pokemon to PokePast for flexing", mw)
    qconnect(flex_pokecoll_action.triggered, flex_pokemon_collection)
    mw.pokemenu.addAction(flex_pokecoll_action)
    

test_action11 = QAction("Check Effectiveness Chart", mw)
test_action11.triggered.connect(eff_chart.show_eff_chart)
mw.pokemenu.addAction(test_action11)

test_action12 = QAction("Check Generations and Pokemon Chart", mw)
test_action12.triggered.connect(gen_id_chart.show_gen_chart)
mw.pokemenu.addAction(test_action12)

test_action3 = QAction("Download Resources", mw)
qconnect(test_action3.triggered, show_agreement_and_download_database)
mw.pokemenu.addAction(test_action3)

test_action14 = QAction("Credits", mw)
test_action14.triggered.connect(credits.show_window)
mw.pokemenu.addAction(test_action14)

test_action13 = QAction("About and License", mw)
test_action13.triggered.connect(license.show_window)
mw.pokemenu.addAction(test_action13)

help_action = QAction("Open Help Guide", mw)
help_action.triggered.connect(open_help_window)
mw.pokemenu.addAction(help_action)

test_action16 = QAction("Report Bug", mw)
test_action16.triggered.connect(report_bug)
mw.pokemenu.addAction(test_action16)

rate_action = QAction("Rate This", mw)
rate_action.triggered.connect(rate_addon_url)
mw.pokemenu.addAction(rate_action)

version_action = QAction("Version", mw)
version_action.triggered.connect(version_dialog.open)
mw.pokemenu.addAction(version_action)

    #https://goo.gl/uhAxsg
    #https://www.reddit.com/r/PokemonROMhacks/comments/9xgl7j/pokemon_sound_effects_collection_over_3200_sfx/
    #https://archive.org/details/pokemon-dp-sound-library-disc-2_202205
    #https://www.sounds-resource.com/nintendo_switch/pokemonswordshield/

from anki.hooks import addHook
# addHook to function to Ankimote
from aqt import mw
from aqt.utils import showInfo

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
    global hp
    if hp < 1:
        catch_pokemon("")
    for hook in catch_pokemon_hooks:
        hook()

# Custom function that triggers the defeat_pokemon hook
def DefeatPokemonHook():
    global hp
    if hp < 1:
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

from anki.cards import Card
from aqt import mw  # Importing the main Anki window object
from aqt import gui_hooks
from aqt.reviewer import Reviewer
from aqt.utils import downArrow, shortcut, showInfo


def catch_shorcut_function():
    if hp > 1:
        tooltip("You only catch a pokemon once its fained !")
    else:
        catch_pokemon("")

def defeat_shortcut_function():
    if hp > 1:
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
    button_style = """
    .button_style {
        position: absolute;
        white-space: nowrap;
        font-size: small;
        right: 0px;
        transform: translate(-50%, -100%);
        font-weight: normal;
        display: inline-block;
        }
    """
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
        return """
        <center id=outer>
        <table id=innertable width=100%% cellspacing=0 cellpadding=0>
        <tr>
        <td align=start valign=top class=stat>
        <button title="%(editkey)s" onclick="pycmd('edit');">%(edit)s</button></td>
        <td align=center valign=top id=middle>
        </td>
        <td align=center valign=top class=stat>
        <button title="%(CatchKey)s" onclick="pycmd('catch');">Catch Pokemon</button>
        <button title="%(DefeatKey)s" onclick="pycmd('defeat');">Defeat Pokemon</button>
        </td>
        <td align=end valign=top class=stat>
        <button title="%(morekey)s" onclick="pycmd('more');">%(more)s %(downArrow)s</button>
        <span id=time class=stattxt></span>
        </td>
        </tr>
        </table>
        </center>
        <script>
        time = %(time)d;
        timerStopped = false;
        </script>
        """ % dict(
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
