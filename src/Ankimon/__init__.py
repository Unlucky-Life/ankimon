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

import os, sys
from aqt.utils import *
from typing import Optional
from aqt.qt import *
import anki
import threading
from anki.hooks import addHook, wrap
from aqt.reviewer import Reviewer
from aqt import mw, editor, gui_hooks
from aqt.qt import QDialog, QGridLayout, QLabel, QPixmap, QPainter, QFont, Qt, QVBoxLayout, QWidget, QAction
import random
import csv
from aqt.qt import *
import requests
import json
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import *
#from PyQt6.QtWidgets import QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QLabel, QWidget
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
#from PyQt6.QtCore import QUrl
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
#from .download_pokeapi_db import create_pokeapidb
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
mypokemon_path = addon_dir / "user_files" / "mypokemon.json"
mainpokemon_path = addon_dir / "user_files" / "mainpokemon.json"
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
id_species_path = addon_dir / "species_with_ids.json"
species_path = addon_dir / "species.json"
items_path = addon_dir / "pokemon_sprites" / "items"
badges_path = addon_dir / "pokemon_sprites" / "badges"
itembag_path = addon_dir / "user_files" / "items.json"
badgebag_path = addon_dir / "user_files" / "badges.json"
pokenames_lang_path = addon_dir / "user_files" / "pokemon_species_names.csv"
pokedesc_lang_path = addon_dir / "user_files" / "pokemon_species_flavor_text.csv"

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
item_sprites = check_folders_exist(pkmnimgfolder, "items")
badges_sprites = check_folders_exist(pkmnimgfolder, "badges")
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
if pokedex_data and learnsets_data and all_species and poke_api_data and badges_sprites and item_sprites == True:
    database_complete = True
else:
    database_complete = False

class CheckFiles(QDialog):
    def __init__(self):
        super().__init__()
        check_files_message = "Ankimon Files:"
        if sprites_complete != True:
            check_files_message += " \n Sprite Files incomplete. \n  Please go to Ankimon => 'Download Sprite Files' to download the needed files"
        if item_sprites and badges_sprites != True:
            check_files_message += " \n Item and Badges Sprite Files incomplete. \n  Please go to Ankimon => 'Download Sounds, Badges and Item Sprites' to download the needed files"
        if database_complete != True:
            check_files_message += " \n File Collection incomplete. \n  Please go to Ankimon => 'Download Database Files' to download the needed files"
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
elif sprites_complete != True:
    dialog.show()

window = None
gender = None
card_counter = -1
item_receive_value = random.randint(30, 120)
only_online_sprites = config["only_use_online_sprites"]
cards_per_round = config["cards_per_round"]
reviewer_image_gif = config["reviewer_image_gif"]
sounds = config["sounds"]
battle_sounds = config["battle_sounds"]
language = config["language"]

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
if online_connectivity != False:
    import markdown

    # Custom Dialog class
    class UpdateNotificationWindow(QDialog):
        def __init__(self, content):
            super().__init__()

            self.setWindowTitle("Ankimon Notifications")
            self.setGeometry(100, 100, 600, 400)

            layout = QVBoxLayout()
            self.text_edit = QTextEdit()
            self.text_edit.setReadOnly(True)
            self.text_edit.setHtml(content)
            layout.addWidget(self.text_edit)

            self.setLayout(layout)

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
        #showInfo("Local file is up to date.")
        pass
    else:
        # Download new content from GitHub
        if github_content is not None:
            # Write new content to the local file
            write_local_file(local_file_path, github_content)
            dialog = UpdateNotificationWindow(github_html_content)
            dialog.exec()
        else:
            showWarning("Failed to retrieve Ankimon content from GitHub.")


try:
    from aqt.sound import av_player
    from anki.sound import SoundOrVideoTag
    legacy_play = None
except (ImportError, ModuleNotFoundError):
    showWarning("Sound import error occured.")
    from anki.sound import play as legacy_play
    av_player = None

sounds=True
sound_list = ['ababo.mp3', 'abomasnow-mega.mp3', 'abomasnow.mp3', 'abra.mp3', 'absol-mega.mp3', 'absol.mp3', 'accelgor.mp3', 'aegislash.mp3', 'aerodactyl-mega.mp3', 'aerodactyl.mp3', 'aggron-mega.mp3', 'aggron.mp3', 'aipom.mp3', 'alakazam-mega.mp3', 'alakazam.mp3', 'alcremie.mp3', 'alomomola.mp3', 'altaria-mega.mp3', 'altaria.mp3', 'amaura.mp3', 'ambipom.mp3', 'amoonguss.mp3', 'ampharos-mega.mp3', 'ampharos.mp3', 'annihilape.mp3', 'anorith.mp3', 'appletun.mp3', 'applin.mp3', 'araquanid.mp3', 'arbok.mp3', 'arboliva.mp3', 'arcanine.mp3', 'arceus.mp3', 'archaludon.mp3', 'archen.mp3', 'archeops.mp3', 'arctibax.mp3', 'arctovish.mp3', 'arctozolt.mp3', 'argalis.mp3', 'arghonaut.mp3', 'ariados.mp3', 'armaldo.mp3', 'armarouge.mp3', 'aromatisse.mp3', 'aron.mp3', 'arrokuda.mp3', 'articuno.mp3', 'astrolotl.mp3', 'audino-mega.mp3', 'audino.mp3', 'aurorus.mp3', 'aurumoth.mp3', 'avalugg.mp3', 'axew.mp3', 'azelf.mp3', 'azumarill.mp3', 'azurill.mp3', 'bagon.mp3', 'baltoy.mp3', 'banette-mega.mp3', 'banette.mp3', 'barbaracle.mp3', 'barboach.mp3', 'barraskewda.mp3', 'basculegion.mp3', 'basculin.mp3', 'bastiodon.mp3', 'baxcalibur.mp3', 'bayleef.mp3', 'beartic.mp3', 'beautifly.mp3', 'beedrill-mega.mp3', 'beedrill.mp3', 'beheeyem.mp3', 'beldum.mp3', 'bellibolt.mp3', 'bellossom.mp3', 'bellsprout.mp3', 'bergmite.mp3', 'bewear.mp3', 'bibarel.mp3', 'bidoof.mp3', 'binacle.mp3', 'bisharp.mp3', 'blacephalon.mp3', 'blastoise-mega.mp3', 'blastoise.mp3', 'blaziken-mega.mp3', 'blaziken.mp3', 'blipbug.mp3', 'blissey.mp3', 'blitzle.mp3', 'boldore.mp3', 'boltund.mp3', 'bombirdier.mp3', 'bonsly.mp3', 'bouffalant.mp3', 'bounsweet.mp3', 'braixen.mp3', 'brambleghast.mp3', 'bramblin.mp3', 'brattler.mp3', 'braviary.mp3', 'breezi.mp3', 'breloom.mp3', 'brionne.mp3', 'bronzong.mp3', 'bronzor.mp3', 'brutebonnet.mp3', 'bruxish.mp3', 'budew.mp3', 'buizel.mp3', 'bulbasaur.mp3', 'buneary.mp3', 'bunnelby.mp3', 'burmy.mp3', 'butterfree.mp3', 'buzzwole.mp3', 'cacnea.mp3', 'cacturne.mp3', 'caimanoe.mp3', 'calyrex-ice.mp3', 'calyrex-shadow.mp3', 'calyrex.mp3', 'camerupt-mega.mp3', 'camerupt.mp3', 'capsakid.mp3', 'carbink.mp3', 'caribolt.mp3', 'carkol.mp3', 'carnivine.mp3', 'carracosta.mp3', 'carvanha.mp3', 'cascoon.mp3', 'castform.mp3', 'caterpie.mp3', 'cawdet.mp3', 'cawmodore.mp3', 'celebi.mp3', 'celesteela.mp3', 'centiskorch.mp3', 'ceruledge.mp3', 'cetitan.mp3', 'cetoddle.mp3', 'chandelure.mp3', 'chansey.mp3', 'charcadet.mp3', 'charizard-megax.mp3', 'charizard-megay.mp3', 'charizard.mp3', 'charjabug.mp3', 'charmander.mp3', 'charmeleon.mp3', 'chatot.mp3', 'cherrim.mp3', 'cherubi.mp3', 'chesnaught.mp3', 'chespin.mp3', 'chewtle.mp3', 'chienpao.mp3', 'chikorita.mp3', 'chimchar.mp3', 'chimecho.mp3', 'chinchou.mp3', 'chingling.mp3', 'chiyu.mp3', 'chromera.mp3', 'cinccino.mp3', 'cinderace.mp3', 'clamperl.mp3', 'clauncher.mp3', 'clawitzer.mp3', 'claydol.mp3', 'clefable.mp3', 'clefairy.mp3', 'cleffa.mp3', 'clobbopus.mp3', 'clodsire.mp3', 'cloyster.mp3', 'coalossal.mp3', 'cobalion.mp3', 'cofagrigus.mp3', 'colossoil.mp3', 'combee.mp3', 'combusken.mp3', 'comfey.mp3', 'conkeldurr.mp3', 'copperajah.mp3', 'coribalis.mp3', 'corphish.mp3', 'corsola.mp3', 'corviknight.mp3', 'corvisquire.mp3', 'cosmoem.mp3', 'cosmog.mp3', 'cottonee.mp3', 'crabominable.mp3', 'crabrawler.mp3', 'cradily.mp3', 'cramorant-gorging.mp3', 'cramorant-gulping.mp3', 'cramorant.mp3', 'cranidos.mp3', 'crawdaunt.mp3', 'cresselia.mp3', 'croagunk.mp3', 'crobat.mp3', 'crocalor.mp3', 'croconaw.mp3', 'crucibelle-mega.mp3', 'crucibelle.mp3', 'crustle.mp3', 'cryogonal.mp3', 'cubchoo.mp3', 'cubone.mp3', 'cufant.mp3', 'cupra.mp3', 'cursola.mp3', 'cutiefly.mp3', 'cyclizar.mp3', 'cyclohm.mp3', 'cyndaquil.mp3', 'dachsbun.mp3', 'darkrai.mp3', 'darmanitan.mp3', 'dartrix.mp3', 'darumaka.mp3', 'decidueye.mp3', 'dedenne.mp3', 'deerling.mp3', 'deino.mp3', 'delcatty.mp3', 'delibird.mp3', 'delphox.mp3', 'deoxys.mp3', 'dewgong.mp3', 'dewott.mp3', 'dewpider.mp3', 'dhelmise.mp3', 'dialga.mp3', 'diancie-mega.mp3', 'diancie.mp3', 'diggersby.mp3', 'diglett.mp3', 'dipplin.mp3', 'ditto.mp3', 'dodrio.mp3', 'doduo.mp3', 'dolliv.mp3', 'dondozo.mp3', 'donphan.mp3', 'dorsoil.mp3', 'dottler.mp3', 'doublade.mp3', 'dracovish.mp3', 'dracozolt.mp3', 'dragalge.mp3', 'dragapult.mp3', 'dragonair.mp3', 'dragonite.mp3', 'drakloak.mp3', 'drampa.mp3', 'drapion.mp3', 'dratini.mp3', 'drednaw.mp3', 'dreepy.mp3', 'drifblim.mp3', 'drifloon.mp3', 'drilbur.mp3', 'drizzile.mp3', 'drowzee.mp3', 'druddigon.mp3', 'dubwool.mp3', 'ducklett.mp3', 'dudunsparce.mp3', 'dugtrio.mp3', 'dunsparce.mp3', 'duohm.mp3', 'duosion.mp3', 'duraludon.mp3', 'durant.mp3', 'dusclops.mp3', 'dusknoir.mp3', 'duskull.mp3', 'dustox.mp3', 'dwebble.mp3', 'eelektrik.mp3', 'eelektross.mp3', 'eevee-starter.mp3', 'eevee.mp3', 'eiscue-noice.mp3', 'eiscue.mp3', 'ekans.mp3', 'eldegoss.mp3', 'electabuzz.mp3', 'electivire.mp3', 'electrelk.mp3', 'electrike.mp3', 'electrode.mp3', 'elekid.mp3', 'elgyem.mp3', 'embirch.mp3', 'emboar.mp3', 'emolga.mp3', 'empoleon.mp3', 'enamorus-therian.mp3', 'enamorus.mp3', 'entei.mp3', 'equilibra.mp3', 'escavalier.mp3', 'espathra.mp3', 'espeon.mp3', 'espurr.mp3', 'eternatus-eternamax.mp3', 'eternatus.mp3', 'excadrill.mp3', 'exeggcute.mp3', 'exeggutor.mp3', 'exploud.mp3', 'falinks.mp3', 'farfetchd.mp3', 'farigiraf.mp3', 'fawnifer.mp3', 'fearow.mp3', 'feebas.mp3', 'fennekin.mp3', 'feraligatr.mp3', 'ferroseed.mp3', 'ferrothorn.mp3', 'fezandipiti.mp3', 'fidgit.mp3', 'fidough.mp3', 'finizen.mp3', 'finneon.mp3', 'flaaffy.mp3', 'flabebe.mp3', 'flamigo.mp3', 'flapple.mp3', 'flarelm.mp3', 'flareon.mp3', 'fletchinder.mp3', 'fletchling.mp3', 'flittle.mp3', 'floatoy.mp3', 'floatzel.mp3', 'floette-eternal.mp3', 'floette.mp3', 'floragato.mp3', 'florges.mp3', 'fluttermane.mp3', 'flygon.mp3', 'fomantis.mp3', 'foongus.mp3', 'forretress.mp3', 'fraxure.mp3', 'frigibax.mp3', 'frillish.mp3', 'froakie.mp3', 'frogadier.mp3', 'froslass.mp3', 'frosmoth.mp3', 'fuecoco.mp3', 'furfrou.mp3', 'furret.mp3', 'gabite.mp3', 'gallade-mega.mp3', 'gallade.mp3', 'galvantula.mp3', 'garbodor.mp3', 'garchomp-mega.mp3', 'garchomp.mp3', 'gardevoir-mega.mp3', 'gardevoir.mp3', 'garganacl.mp3', 'gastly.mp3', 'gastrodon.mp3', 'genesect.mp3', 'gengar-mega.mp3', 'gengar.mp3', 'geodude.mp3', 'gholdengo.mp3', 'gible.mp3', 'gigalith.mp3', 'gimmighoul-roaming.mp3', 'gimmighoul.mp3', 'girafarig.mp3', 'giratina.mp3', 'glaceon.mp3', 'glalie-mega.mp3', 'glalie.mp3', 'glameow.mp3', 'glastrier.mp3', 'gligar.mp3', 'glimmet.mp3', 'glimmora.mp3', 'gliscor.mp3', 'gloom.mp3', 'gogoat.mp3', 'golbat.mp3', 'goldeen.mp3', 'golduck.mp3', 'golem.mp3', 'golett.mp3', 'golisopod.mp3', 'golurk.mp3', 'goodra.mp3', 'goomy.mp3', 'gorebyss.mp3', 'gossifleur.mp3', 'gothita.mp3', 'gothitelle.mp3', 'gothorita.mp3', 'gougingfire.mp3', 'gourgeist-super.mp3', 'gourgeist.mp3', 'grafaiai.mp3', 'granbull.mp3', 'grapploct.mp3', 'graveler.mp3', 'greattusk.mp3', 'greavard.mp3', 'greedent.mp3', 'greninja.mp3', 'grimer.mp3', 'grimmsnarl.mp3', 'grookey.mp3', 'grotle.mp3', 'groudon-primal.mp3', 'groudon.mp3', 'grovyle.mp3', 'growlithe.mp3', 'grubbin.mp3', 'grumpig.mp3', 'gulpin.mp3', 'gumshoos.mp3', 'gurdurr.mp3', 'guzzlord.mp3', 'gyarados-mega.mp3', 'gyarados.mp3', 'hakamoo.mp3', 'happiny.mp3', 'hariyama.mp3', 'hatenna.mp3', 'hatterene.mp3', 'hattrem.mp3', 'haunter.mp3', 'hawlucha.mp3', 'haxorus.mp3', 'heatmor.mp3', 'heatran.mp3', 'heliolisk.mp3', 'helioptile.mp3', 'hemogoblin.mp3', 'heracross-mega.mp3', 'heracross.mp3', 'herdier.mp3', 'hippopotas.mp3', 'hippowdon.mp3', 'hitmonchan.mp3', 'hitmonlee.mp3', 'hitmontop.mp3', 'honchkrow.mp3', 'honedge.mp3', 'hooh.mp3', 'hoopa-unbound.mp3', 'hoopa.mp3', 'hoothoot.mp3', 'hoppip.mp3', 'horsea.mp3', 'houndoom-mega.mp3', 'houndoom.mp3', 'houndour.mp3', 'houndstone.mp3', 'huntail.mp3', 'hydrapple.mp3', 'hydreigon.mp3', 'hypno.mp3', 'igglybuff.mp3', 'illumise.mp3', 'impidimp.mp3', 'incineroar.mp3', 'indeedee-f.mp3', 'indeedee.mp3', 'infernape.mp3', 'inkay.mp3', 'inteleon.mp3', 'ironboulder.mp3', 'ironbundle.mp3', 'ironcrown.mp3', 'ironhands.mp3', 'ironjugulis.mp3', 'ironleaves.mp3', 'ironmoth.mp3', 'ironthorns.mp3', 'irontreads.mp3', 'ironvaliant.mp3', 'ivysaur.mp3', 'jangmoo.mp3', 'jellicent.mp3', 'jigglypuff.mp3', 'jirachi.mp3', 'jolteon.mp3', 'joltik.mp3', 'jumbao.mp3', 'jumpluff.mp3', 'justyke.mp3', 'jynx.mp3', 'kabuto.mp3', 'kabutops.mp3', 'kadabra.mp3', 'kakuna.mp3', 'kangaskhan-mega.mp3', 'kangaskhan.mp3', 'karrablast.mp3', 'kartana.mp3', 'kecleon.mp3', 'keldeo.mp3', 'kerfluffle.mp3', 'kilowattrel.mp3', 'kingambit.mp3', 'kingdra.mp3', 'kingler.mp3', 'kirlia.mp3', 'kitsunoh.mp3', 'klang.mp3', 'klawf.mp3', 'kleavor.mp3', 'klefki.mp3', 'klink.mp3', 'klinklang.mp3', 'koffing.mp3', 'komala.mp3', 'kommoo.mp3', 'koraidon.mp3', 'krabby.mp3', 'kricketot.mp3', 'kricketune.mp3', 'krilowatt.mp3', 'krokorok.mp3', 'krookodile.mp3', 'kubfu.mp3', 'kyogre-primal.mp3', 'kyogre.mp3', 'kyurem-black.mp3', 'kyurem-white.mp3', 'kyurem.mp3', 'lairon.mp3', 'lampent.mp3', 'landorus-therian.mp3', 'landorus.mp3', 'lanturn.mp3', 'lapras.mp3', 'larvesta.mp3', 'larvitar.mp3', 'latias-mega.mp3', 'latias.mp3', 'latios-mega.mp3', 'latios.mp3', 'leafeon.mp3', 'leavanny.mp3', 'lechonk.mp3', 'ledian.mp3', 'ledyba.mp3', 'lickilicky.mp3', 'lickitung.mp3', 'liepard.mp3', 'lileep.mp3', 'lilligant.mp3', 'lillipup.mp3', 'linoone.mp3', 'litleo.mp3', 'litten.mp3', 'litwick.mp3', 'lokix.mp3', 'lombre.mp3', 'lopunny-mega.mp3', 'lopunny.mp3', 'lotad.mp3', 'loudred.mp3', 'lucario-mega.mp3', 'lucario.mp3', 'ludicolo.mp3', 'lugia.mp3', 'lumineon.mp3', 'lunala.mp3', 'lunatone.mp3', 'lurantis.mp3', 'luvdisc.mp3', 'luxio.mp3', 'luxray.mp3', 'lycanroc-dusk.mp3', 'lycanroc-midnight.mp3', 'lycanroc.mp3', 'mabosstiff.mp3', 'machamp.mp3', 'machoke.mp3', 'machop.mp3', 'magby.mp3', 'magcargo.mp3', 'magearna.mp3', 'magikarp.mp3', 'magmar.mp3', 'magmortar.mp3', 'magnemite.mp3', 'magneton.mp3', 'magnezone.mp3', 'makuhita.mp3', 'malaconda.mp3', 'malamar.mp3', 'mamoswine.mp3', 'manaphy.mp3', 'mandibuzz.mp3', 'manectric-mega.mp3', 'manectric.mp3', 'mankey.mp3', 'mantine.mp3', 'mantyke.mp3', 'maractus.mp3', 'mareanie.mp3', 'mareep.mp3', 'marill.mp3', 'marowak.mp3', 'marshadow.mp3', 'marshtomp.mp3', 'maschiff.mp3', 'masquerain.mp3', 'maushold-four.mp3', 'maushold.mp3', 'mawile-mega.mp3', 'mawile.mp3', 'medicham-mega.mp3', 'medicham.mp3', 'meditite.mp3', 'meganium.mp3', 'melmetal.mp3', 'meloetta.mp3', 'meltan.mp3', 'meowscarada.mp3', 'meowstic.mp3', 'meowth.mp3', 'mesprit.mp3', 'metagross-mega.mp3', 'metagross.mp3', 'metang.mp3', 'metapod.mp3', 'mew.mp3', 'mewtwo-megax.mp3', 'mewtwo-megay.mp3', 'mewtwo.mp3', 'miasmaw.mp3', 'miasmite.mp3', 'mienfoo.mp3', 'mienshao.mp3', 'mightyena.mp3', 'milcery.mp3', 'milotic.mp3', 'miltank.mp3', 'mimejr.mp3', 'mimikyu.mp3', 'minccino.mp3', 'minior.mp3', 'minun.mp3', 'miraidon.mp3', 'misdreavus.mp3', 'mismagius.mp3', 'mollux.mp3', 'moltres.mp3', 'monferno.mp3', 'monohm.mp3', 'morelull.mp3', 'morgrem.mp3', 'morpeko-hangry.mp3', 'morpeko.mp3', 'mothim.mp3', 'mrmime.mp3', 'mrrime.mp3', 'mudbray.mp3', 'mudkip.mp3', 'mudsdale.mp3', 'muk.mp3', 'mumbao.mp3', 'munchlax.mp3', 'munkidori.mp3', 'munna.mp3', 'murkrow.mp3', 'musharna.mp3', 'nacli.mp3', 'naclstack.mp3', 'naganadel.mp3', 'natu.mp3', 'naviathan.mp3', 'necrozma-dawnwings.mp3', 'necrozma-duskmane.mp3', 'necrozma-ultra.mp3', 'necrozma.mp3', 'necturine.mp3', 'necturna.mp3', 'nickit.mp3', 'nidoking.mp3', 'nidoqueen.mp3', 'nidoranf.mp3', 'nidoranm.mp3', 'nidorina.mp3', 'nidorino.mp3', 'nihilego.mp3', 'nincada.mp3', 'ninetales.mp3', 'ninjask.mp3', 'noctowl.mp3', 'nohface.mp3', 'noibat.mp3', 'noivern.mp3', 'nosepass.mp3', 'numel.mp3', 'nuzleaf.mp3', 'nymble.mp3', 'obstagoon.mp3', 'octillery.mp3', 'oddish.mp3', 'ogerpon.mp3', 'oinkologne-f.mp3', 'oinkologne.mp3', 'okidogi.mp3', 'omanyte.mp3', 'omastar.mp3', 'onix.mp3', 'oranguru.mp3', 'orbeetle.mp3', 'oricorio-pau.mp3', 'oricorio-pompom.mp3', 'oricorio-sensu.mp3', 'oricorio.mp3', 'orthworm.mp3', 'oshawott.mp3', 'overqwil.mp3', 'pachirisu.mp3', 'pajantom.mp3', 'palafin-hero.mp3', 'palafin.mp3', 'palkia.mp3', 'palossand.mp3', 'palpitoad.mp3', 'pancham.mp3', 'pangoro.mp3', 'panpour.mp3', 'pansage.mp3', 'pansear.mp3', 'paras.mp3', 'parasect.mp3', 'passimian.mp3', 'patrat.mp3', 'pawmi.mp3', 'pawmo.mp3', 'pawmot.mp3', 'pawniard.mp3', 'pecharunt.mp3', 'pelipper.mp3', 'perrserker.mp3', 'persian.mp3', 'petilil.mp3', 'phanpy.mp3', 'phantump.mp3', 'pheromosa.mp3', 'phione.mp3', 'pichu.mp3', 'pidgeot-mega.mp3', 'pidgeot.mp3', 'pidgeotto.mp3', 'pidgey.mp3', 'pidove.mp3', 'pignite.mp3', 'pikachu-starter.mp3', 'pikachu.mp3', 'pikipek.mp3', 'piloswine.mp3', 'pincurchin.mp3', 'pineco.mp3', 'pinsir-mega.mp3', 'pinsir.mp3', 'piplup.mp3', 'plasmanta.mp3', 'pluffle.mp3', 'plusle.mp3', 'poipole.mp3', 'politoed.mp3', 'poliwag.mp3', 'poliwhirl.mp3', 'poliwrath.mp3', 'poltchageist.mp3', 'polteageist.mp3', 'ponyta.mp3', 'poochyena.mp3', 'popplio.mp3', 'porygon.mp3', 'porygon2.mp3', 'porygonz.mp3', 'primarina.mp3', 'primeape.mp3', 'prinplup.mp3', 'privatyke.mp3', 'probopass.mp3', 'protowatt.mp3', 'psyduck.mp3', 'pumpkaboo-super.mp3', 'pumpkaboo.mp3', 'pupitar.mp3', 'purrloin.mp3', 'purugly.mp3', 'pyroak.mp3', 'pyroar.mp3', 'pyukumuku.mp3', 'quagsire.mp3', 'quaquaval.mp3', 'quaxly.mp3', 'quaxwell.mp3', 'quilava.mp3', 'quilladin.mp3', 'qwilfish.mp3', 'raboot.mp3', 'rabsca.mp3', 'ragingbolt.mp3', 'raichu.mp3', 'raikou.mp3', 'ralts.mp3', 'rampardos.mp3', 'rapidash.mp3', 'raticate.mp3', 'rattata.mp3', 'rayquaza-mega.mp3', 'rayquaza.mp3', 'rebble.mp3', 'regice.mp3', 'regidrago.mp3', 'regieleki.mp3', 'regigigas.mp3', 'regirock.mp3', 'registeel.mp3', 'relicanth.mp3', 'rellor.mp3', 'remoraid.mp3', 'reshiram.mp3', 'reuniclus.mp3', 'revavroom.mp3', 'revenankh.mp3', 'rhydon.mp3', 'rhyhorn.mp3', 'rhyperior.mp3', 'ribombee.mp3', 'rillaboom.mp3', 'riolu.mp3', 'roaringmoon.mp3', 'rockruff.mp3', 'roggenrola.mp3', 'rolycoly.mp3', 'rookidee.mp3', 'roselia.mp3', 'roserade.mp3', 'rotom.mp3', 'rowlet.mp3', 'rufflet.mp3', 'runerigus.mp3', 'sableye-mega.mp3', 'sableye.mp3', 'saharaja.mp3', 'saharascal.mp3', 'salamence-mega.mp3', 'salamence.mp3', 'salandit.mp3', 'salazzle.mp3', 'samurott.mp3', 'sandaconda.mp3', 'sandile.mp3', 'sandshrew.mp3', 'sandslash.mp3', 'sandygast.mp3', 'sandyshocks.mp3', 'sawk.mp3', 'sawsbuck.mp3', 'scatterbug.mp3', 'scattervein.mp3', 'sceptile-mega.mp3', 'sceptile.mp3', 'scizor-mega.mp3', 'scizor.mp3', 'scolipede.mp3', 'scorbunny.mp3', 'scovillain.mp3', 'scrafty.mp3', 'scraggy.mp3', 'scratchet.mp3', 'screamtail.mp3', 'scyther.mp3', 'seadra.mp3', 'seaking.mp3', 'sealeo.mp3', 'seedot.mp3', 'seel.mp3', 'seismitoad.mp3', 'sentret.mp3', 'serperior.mp3', 'servine.mp3', 'seviper.mp3', 'sewaddle.mp3', 'sharpedo-mega.mp3', 'sharpedo.mp3', 'shaymin-sky.mp3', 'shaymin.mp3', 'shedinja.mp3', 'shelgon.mp3', 'shellder.mp3', 'shellos.mp3', 'shelmet.mp3', 'shieldon.mp3', 'shiftry.mp3', 'shiinotic.mp3', 'shinx.mp3', 'shroodle.mp3', 'shroomish.mp3', 'shuckle.mp3', 'shuppet.mp3', 'sigilyph.mp3', 'silcoon.mp3', 'silicobra.mp3', 'silvally.mp3', 'simipour.mp3', 'simisage.mp3', 'simisear.mp3', 'sinistcha.mp3', 'sinistea.mp3', 'sirfetchd.mp3', 'sizzlipede.mp3', 'skarmory.mp3', 'skeledirge.mp3', 'skiddo.mp3', 'skiploom.mp3', 'skitty.mp3', 'skorupi.mp3', 'skrelp.mp3', 'skuntank.mp3', 'skwovet.mp3', 'slaking.mp3', 'slakoth.mp3', 'sliggoo.mp3', 'slitherwing.mp3', 'slowbro-mega.mp3', 'slowbro.mp3', 'slowking.mp3', 'slowpoke-galar.mp3', 'slowpoke.mp3', 'slugma.mp3', 'slurpuff.mp3', 'smeargle.mp3', 'smogecko.mp3', 'smoguana.mp3', 'smokomodo.mp3', 'smoliv.mp3', 'smoochum.mp3', 'snaelstrom.mp3', 'sneasel.mp3', 'sneasler.mp3', 'snivy.mp3', 'snom.mp3', 'snorlax.mp3', 'snorunt.mp3', 'snover.mp3', 'snubbull.mp3', 'snugglow.mp3', 'sobble.mp3', 'solgaleo.mp3', 'solosis.mp3', 'solotl.mp3', 'solrock.mp3', 'spearow.mp3', 'spectrier.mp3', 'spewpa.mp3', 'spheal.mp3', 'spidops.mp3', 'spinarak.mp3', 'spinda.mp3', 'spiritomb.mp3', 'spoink.mp3', 'sprigatito.mp3', 'spritzee.mp3', 'squawkabilly.mp3', 'squirtle.mp3', 'stakataka.mp3', 'stantler.mp3', 'staraptor.mp3', 'staravia.mp3', 'starly.mp3', 'starmie.mp3', 'staryu.mp3', 'steelix-mega.mp3', 'steelix.mp3', 'steenee.mp3', 'stonjourner.mp3', 'stoutland.mp3', 'stratagem.mp3', 'stufful.mp3', 'stunfisk.mp3', 'stunky.mp3', 'sudowoodo.mp3', 'suicune.mp3', 'sunflora.mp3', 'sunkern.mp3', 'surskit.mp3', 'swablu.mp3', 'swadloon.mp3', 'swalot.mp3', 'swampert-mega.mp3', 'swampert.mp3', 'swanna.mp3', 'swellow.mp3', 'swinub.mp3', 'swirlix.mp3', 'swirlpool.mp3', 'swoobat.mp3', 'syclant.mp3', 'syclar.mp3', 'sylveon.mp3', 'tactite.mp3', 'tadbulb.mp3', 'taillow.mp3', 'talonflame.mp3', 'tandemaus.mp3', 'tangela.mp3', 'tangrowth.mp3', 'tapubulu.mp3', 'tapufini.mp3', 'tapukoko.mp3', 'tapulele.mp3', 'tarountula.mp3', 'tatsugiri-droopy.mp3', 'tatsugiri-stretchy.mp3', 'tatsugiri.mp3', 'tauros.mp3', 'teddiursa.mp3', 'tentacool.mp3', 'tentacruel.mp3', 'tepig.mp3', 'terapagos.mp3', 'terrakion.mp3', 'thievul.mp3', 'throh.mp3', 'thundurus-therian.mp3', 'thundurus.mp3', 'thwackey.mp3', 'timburr.mp3', 'tinglu.mp3', 'tinkatink.mp3', 'tinkaton.mp3', 'tinkatuff.mp3', 'tirtouga.mp3', 'toedscool.mp3', 'toedscruel.mp3', 'togedemaru.mp3', 'togekiss.mp3', 'togepi.mp3', 'togetic.mp3', 'tomohawk.mp3', 'torchic.mp3', 'torkoal.mp3', 'tornadus-therian.mp3', 'tornadus.mp3', 'torracat.mp3', 'torterra.mp3', 'totodile.mp3', 'toucannon.mp3', 'toxapex.mp3', 'toxel.mp3', 'toxicroak.mp3', 'toxtricity-lowkey.mp3', 'toxtricity.mp3', 'tranquill.mp3', 'trapinch.mp3', 'treecko.mp3', 'trevenant.mp3', 'tropius.mp3', 'trubbish.mp3', 'trumbeak.mp3', 'tsareena.mp3', 'turtonator.mp3', 'turtwig.mp3', 'tympole.mp3', 'tynamo.mp3', 'typenull.mp3', 'typhlosion.mp3', 'tyranitar-mega.mp3', 'tyranitar.mp3', 'tyrantrum.mp3', 'tyrogue.mp3', 'tyrunt.mp3', 'umbreon.mp3', 'unfezant.mp3', 'unown.mp3', 'ursaluna.mp3', 'ursaring.mp3', 'urshifu-rapidstrike.mp3', 'urshifu.mp3', 'uxie.mp3', 'vanillish.mp3', 'vanillite.mp3', 'vanilluxe.mp3', 'vaporeon.mp3', 'varoom.mp3', 'veluza.mp3', 'venipede.mp3', 'venomicon.mp3', 'venomoth.mp3', 'venonat.mp3', 'venusaur-mega.mp3', 'venusaur.mp3', 'vespiquen.mp3', 'vibrava.mp3', 'victini.mp3', 'victreebel.mp3', 'vigoroth.mp3', 'vikavolt.mp3', 'vileplume.mp3', 'virizion.mp3', 'vivillon.mp3', 'volbeat.mp3', 'volcanion.mp3', 'volcarona.mp3', 'volkraken.mp3', 'volkritter.mp3', 'voltorb.mp3', 'voodoll.mp3', 'voodoom.mp3', 'vullaby.mp3', 'vulpix.mp3', 'wailmer.mp3', 'wailord.mp3', 'walkingwake.mp3', 'walrein.mp3', 'wartortle.mp3', 'watchog.mp3', 'wattrel.mp3', 'weavile.mp3', 'weedle.mp3', 'weepinbell.mp3', 'weezing.mp3', 'whimsicott.mp3', 'whirlipede.mp3', 'whiscash.mp3', 'whismur.mp3', 'wigglytuff.mp3', 'wiglett.mp3', 'wimpod.mp3', 'wingull.mp3', 'wishiwashi-school.mp3', 'wishiwashi.mp3', 'wobbuffet.mp3', 'wochien.mp3', 'woobat.mp3', 'wooloo.mp3', 'wooper.mp3', 'wormadam.mp3', 'wugtrio.mp3', 'wurmple.mp3', 'wynaut.mp3', 'wyrdeer.mp3', 'xatu.mp3', 'xerneas.mp3', 'xurkitree.mp3', 'yamask.mp3', 'yamper.mp3', 'yanma.mp3', 'yanmega.mp3', 'yungoos.mp3', 'yveltal.mp3', 'zacian-crowned.mp3', 'zacian.mp3', 'zamazenta-crowned.mp3', 'zamazenta.mp3', 'zangoose.mp3', 'zapdos.mp3', 'zarude.mp3', 'zebstrika.mp3', 'zekrom.mp3', 'zeraora.mp3', 'zigzagoon.mp3', 'zoroark.mp3', 'zorua.mp3', 'zubat.mp3', 'zweilous.mp3', 'zygarde-10.mp3', 'zygarde-complete.mp3', 'zygarde.mp3']

# Function to play the sound
def play_sound():
    global timer
    pass
    if sounds is True:
        global name
        # Check if the sound should play
        file_name = f"{name.lower()}.mp3"
        audio_path = addon_dir / "pokemon_sprites" / "sounds" / file_name
        if not audio_path.is_file():
            showWarning(f"Audio file not found: {audio_path}")
            return

        audio_path = str(audio_path)

        if av_player:
            av_player.play_file(filename=audio_path)
        elif legacy_play:
            legacy_play(audio_path)
        else:
            showWarning("No suitable audio player found in Anki.")
                
        # Disconnect the timer's timeout signal to prevent further plays
        try:
            timer.timeout.disconnect(play_sound)
        except TypeError:
            pass  # Do nothing if the signal was not connected

if sounds == True:    
    # Create a QTimer
    timer = QTimer()

    # Connect the timer's timeout signal to the play_sound function
    timer.timeout.connect(play_sound)

    #def play_pokemon_cry():
        #play_sound()

    #gui_hooks.reviewer_will_end.append(play_pokemon_cry)

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
            showInfo(f"{id_num}")
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

#count index - count 10 cards - easy = 20, good = 10, hard = 5, again = 0
# if index = 40 - 100 => normal ; multiply with damage
# if index < 40 => attack misses

#Badges needed for achievements:
badges = {
  "1": "100 Cards in one Session",
  "2": "200 Cards in one Session",
  "3": "300 Cards in one Session",
  "4": "500 Cards in one Session",
  "5": "Leveled a Pokemon !",
  "6": "Received the first Item !",
  "7": "First Pokemon Caught !",
  "8": "Caught first Ultra Pokemon",
  "9": "Caught first Baby Pokemon",
  "10": "Caught first Mythical Pokemon",
  "11": "First Leech Card unleeched",
  "12": "1000 Cards in one Session",
  "13": "2000 Cards in one Session",
  "14": "Received a Pokemon Egg",
  "15": "Hatched a Pokemon Egg",
  "16": "Evolved a Pokemon !",
  "17": "Caught first Normal Pokemon",
  "18": "Caught first Baby Pokemon",
  "19": "changed",
  "20": "changed",
  "21": "changed",
  "22": "changed",
  "23": "changed",
  "24": "changed",
  "25": "changed",
  "26": "changed",
  "27": "changed",
  "28": "changed",
  "29": "changed",
  "30": "changed",
  "31": "changed",
  "32": "changed",
  "33": "changed",
  "34": "changed",
  "35": "changed",
  "36": "changed",
  "37": "changed",
  "38": "changed",
  "39": "changed",
  "40": "changed",
  "41": "changed",
  "42": "changed",
  "43": "changed",
  "44": "changed",
  "45": "changed",
  "46": "changed",
  "47": "changed",
  "48": "changed",
  "49": "changed",
  "50": "changed",
  "51": "changed",
  "52": "changed",
  "53": "changed",
  "54": "changed",
  "55": "changed",
  "56": "changed",
  "57": "changed",
  "58": "changed",
  "59": "Add",
  "60": "Add",
  "61": "Add",
  "62": "Add",
  "63": "Add",
  "64": "Add",
  "65": "Add",
  "66": "Add",
  "67": "Add"
}

achievements = {
  "1": False,
  "2": False,
  "3": False,
  "4": False,
  "5": False,
  "6": False,
  "7": False,
  "8": False,
  "9": False,
  "10": False,
  "11": False,
  "12": False,
  "13": False,
  "14": False,
  "15": False,
  "16": False,
  "17": False,
  "18": False,
  "19": False,
  "20": False,
  "21": False,
  "22": False,
  "23": False,
  "24": False,
  "25": False,
  "26": False,
  "27": False,
  "28": False,
  "29": False,
  "30": False,
  "31": False,
  "32": False,
  "33": False,
  "34": False,
  "35": False,
  "36": False,
  "37": False,
  "38": False,
  "39": False,
  "40": False,
  "41": False,
  "42": False,
  "43": False,
  "44": False,
  "45": False,
  "46": False,
  "47": False,
  "48": False,
  "49": False,
  "50": False,
  "51": False,
  "52": False,
  "53": False,
  "54": False,
  "55": False,
  "56": False,
  "57": False,
  "58": False,
  "59": False,
  "60": False,
  "61": False,
  "62": False,
  "63": False,
  "64": False,
  "65": False,
  "66": False,
  "67": False,
  "68": False
}

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

pokedex_to_poke_api_db = {
  "mr-mime": "mrmime",
  "mr-rime": "mrrime",
  "deoxys": "deosyx-normal",
  "wormadam-plant": "wormadam",
  "mimejr": "mime-jr",
  "giratina": "giratina-altered",
  "shaymin-land": "shaymin-land",
  "basculin": "basculin-red-striped",
  "darmanitan": "darmanitan-standard",
  "tornadus": "tornadus-incarnate",
  "thundurus": "thundurus-incarnate",
  "landorus": "landorus-incarnate",
  "keldeo": "keldeo-ordinary",
  "meloetta": "meloetta-aria",
  "meowstic": "meowstic-male",
  "meowsticf": "meowstic-male",
  "aegislash-shield": "aegislash",
  "aegislashblade": "aegislash",
  "pumpkaboo": "pumpkaboo-average",
  "gourgeist": "gourgeist-average",
  "zygarde": "zygarde-50",
  "oricorio": "oricorio-baile",
  "lycanroc": "lycanroc-midday",
  "wishiwashi": "wishiwashi-solo",
  "typenull": "type-null",
  "minior": "minior-red-meteor",
  "mimikyu": "mimikyu-disguised",
  "tapukoko": "tapu-koko",
  "tapulele": "tapu-lele",
  "tapubulu": "tapu-bulu",
  "tapufini": "tapu-fini",
  "toxtricity": "toxtricity-amped",
  "eiscue": "eiscue-ice",
  "indeedee": "indeedee-male",
  "morpeko": "morpeko-full-belly",
  "urshifu": "urshifu-single-strike"
}

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
    
    def get_all_pokemon_moves(pokemon_name, level):
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
    class CustomLabel(QLabel):
        def mousePressEvent(self, evt):
            evt.accept()
            self.hide()

    # Assuming closeTooltip() and customCloseTooltip() are defined elsewhere
    closeTooltip()
    aw = parent or QApplication.activeWindow()
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
        global hp, gender, name
        global mainpokemon_level
        global pokemon_species
        global cards_per_round
        pokemon_encounter = 0
        pokemon_species = None
        #generation_file = ("pokeapi_db.json")
        try:
            id, pokemon_species = choose_random_pkmn_from_tier()
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
                except:
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
                enemy_attacks = get_random_moves_for_pokemon(name, level)
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
        elif card_counter < (60*cards_per_round):
            possible_tiers.extend(["Baby", "Normal", "Normal", "Normal", "Normal"])
        elif card_counter < (80*cards_per_round):
            possible_tiers.extend(["Baby", "Baby", "Normal", "Normal", "Normal", "Normal", "Ultra"])
        elif card_counter < (100*cards_per_round):
            possible_tiers.extend(["Baby", "Legendary", "Normal", "Normal", "Normal", "Normal", "Ultra", "Ultra"])
        else:
            possible_tiers.extend(["Baby", "Legendary","Mythical", "Normal", "Normal", "Normal", "Normal", "Ultra", "Ultra"])
        tier = random.choice(possible_tiers)
        id, pokemon_species = get_pokemon_id_by_tier(tier)
        return id, pokemon_species
    except:
        showWarning(f" An error occured with generating following Pkmn Info: {id}{pokemon_species} \n Please post this error message over the Report Bug Issue")

def get_pokemon_id_by_tier(tier):
    #showInfo(f"{tier}")
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
        showInfo(f"{msg}")
        mainpokemon_xp = 0
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
                            # showInfo(f"{attacks}")
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
        msg = ""
        msg += f"Your {mainpokemon_name} has gained {exp} XP.\n {experience} exp is needed for next level \n Your pokemon currently has {mainpokemon_xp}"
        color = "#6A4DAC" #pokemon leveling info color for tooltip
        try:
            tooltipWithColour(msg, color)
        except:
            pass
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
                            #pokemon["gender"] = pick_random_gender(evoName.lower()) dont replace gender
                            pokemon["growth_rate"] = search_pokeapi_db(evoName.lower(), "growth_rate")
                            pokemon["base_experience"] = search_pokeapi_db(evoName.lower(), "base_experience")
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
        name = name.capitalize()
        if nickname is None or not nickname:  # Wenn None oder leer
            save_caught_pokemon(nickname)
        else:
            save_caught_pokemon(name)
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
    return None  # Return None if no match is found

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

def search_pokeapi_db(pokemon_name,variable):
    global addon_dir
    pokemon_name = special_pokemon_names_for_pokedex_to_poke_api_db(pokemon_name)
    pokeapi_db_path = addon_dir / "pokeapi_db.json"
    with open(str(pokeapi_db_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            for pokemon_data in pokedex_data:
                name = pokemon_data["name"]
                if pokemon_data["name"] == pokemon_name:
                    var = pokemon_data.get(variable, None)
                    return var
            else:
                return None

def search_pokeapi_db_by_id(pkmn_id,variable):
    global addon_dir
    pokeapi_db_path = addon_dir / "pokeapi_db.json"
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
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        #merged_pixmap.fill(Qt.transparent)
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
            widget = QWidget()
            vbox = QVBoxLayout(widget)

            label = QLabel(widget)
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
    #window.exec()

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

reviewed_cards_count = -1
general_card_count_for_battle = 0
cry_counter = 0
# Hook into Anki's card review event
def on_review_card():
    try:
        global reviewed_cards_count, card_ratings_count, card_counter, general_card_count_for_battle, cry_counter, battle_sounds
        global hp, stats, type, battle_status, name, battle_stats
        global pokemon_encounter
        global mainpokemon_xp, mainpokemon_current_hp, mainpokemon_attacks, mainpokemon_level, mainpokemon_stats, mainpokemon_type, mainpokemon_name, mainpokemon_battle_stats
        global attack_counter
        global pkmn_window
        global achievements
        # Increment the counter when a card is reviewed
        reviewed_cards_count += 1
        card_counter += 1
        cry_counter += 1
        general_card_count_for_battle += 1
        if battle_sounds == True:
            if general_card_count_for_battle == 1:
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
                    kill_pokemon()
                    general_card_count_for_battle = 0
            # Reset the counter
            reviewed_cards_count = 0
        if cry_counter == 10:
            cry_counter = 0
            play_sound()
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
                        capitalized_name = f"{get_pokemon_diff_lang_name(int(pokemon_id)).capitalize()} ({pokemon_gender})"
                    else:
                        capitalized_name = f"{pokemon_nickname.capitalize()} ({pokemon_gender})"
                    # Create level text
                    lvl = (f" Level: {pokemon_level}")
                    type_txt = "Type: "
                    for type in pokemon_type:
                        type_txt += f" {type.capitalize()}"
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
                    name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align to the left
                    name_label.setFont(font)

                    # Create a QLabel for the level
                    level_label = QLabel(lvl)
                    level_label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align to the left
                    level_label.setFont(fontpkmnspec)

                    # Create a QLabel for the type
                    type_label = QLabel(type_txt)
                    type_label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align to the left
                    type_label.setFont(fontpkmnspec)

                    # Create a QLabel for the ability
                    ability_label = QLabel(ability_txt)
                    ability_label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align to the left
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
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    ability_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
                window.exec()
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
            capitalized_name = f"{lang_name.capitalize()}"
        else:
            capitalized_name = f"{nickname} ({lang_name.capitalize()})"
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
        wpkmn_details.exec()
    except Exception as e:
        showWarning(f"Error occured in Pokemon Details Button: {e}")

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
    label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align the label's content to the top
    label.setScaledContents(True)  # Enable scaling of the pixmap

    layout.addWidget(label)
    window.setLayout(layout)
    window.exec()

def remember_attack_details_window(id, attack_set, all_attacks):
    window = QDialog()
    layout = QHBoxLayout()
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
    layout.addWidget(label)
    layout.addWidget(attack_layout_widget)
    window.setLayout(layout)
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
    new_pokemon() #new pokemon if you change your pokemon

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
        stat_item2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bar_item2.setAlignment(Qt.AlignmentFlag.AlignCenter)
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
    window.exec()

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
        pokemon_list = [p for p in pokemon_list if p['name'] != name]

        # Write the updated data back to the file
        with open(mypokemon_path, 'w') as file:
            json.dump(pokemon_list, file, indent=2)
        showInfo(f"{name.capitalize()} has been let free.")
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
    elif group_growth_rate == "fast-then-very-slow":
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

    def __init__(self, addon_dir, parent=None):
        super().__init__(parent)
        self.addon_dir = Path(addon_dir)
        self.pokedex = []

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

    def download_pokemon_data(self):
        try:
            urls = [
                "https://play.pokemonshowdown.com/data/learnsets.json",
                "https://play.pokemonshowdown.com/data/pokedex.json",
                "https://play.pokemonshowdown.com/data/moves.json",
                "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/item_names.csv",
                "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/pokemon_species_flavor_text.csv"
                "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/pokemon_species_names.csv",
                "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/item_flavor_text.csv",
                "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/move_flavor_text.csv",
                "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/item_flag_map.csv",
                "POKEAPI"
            ]
            num_files = len(urls)
            for i, url in enumerate(urls, start=1):
                if url != "POKEAPI":
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        file_path = self.addon_dir / "user_files" / f"{url.split('/')[-1]}"
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
                    self.save_to_json(self.pokedex, self.addon_dir / "pokeapi_db.json")
            self.download_complete.emit()
        except Exception as e:
            showWarning(f"An error occurred: {e}")  # Replace with a signal if needed

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
        self.start_download(addon_dir)

    def start_download(self, addon_dir):
        self.thread = QThread()
        self.downloader = Downloader(addon_dir)
        self.downloader.moveToThread(self.thread)
        self.thread.started.connect(self.downloader.download_pokemon_data)
        self.downloader.progress_updated.connect(self.progress.setValue)
        self.downloader.download_complete.connect(self.on_download_complete)
        self.downloader.download_complete.connect(self.thread.quit)
        self.downloader.download_complete.connect(self.downloader.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_download_complete(self):
        self.label.setText("Download complete! You can now close this window.")

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

def count_images_in_folder(folder_path):
    #Counts the number of images in the specified folder.
    return len([name for name in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, name))])

def show_agreement_and_downloadsprites():
    # Show the agreement dialog
    dialog = AgreementDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
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
    try:
        global addon_dir
        # (Your existing setup code)
        sprites_path = str(addon_dir / "pokemon_sprites")
        id_to = 898 #pokeapi free to uses
        total_images_expected = id_to * 2
        max_id = 898 #latest backdefaults
        max_total_images_expected = id_to * 2
        def show_loading_window():
            try:
                window = QDialog()
                window.setWindowTitle("Loading Images")
                window.label = QLabel("Loading Images... \n This may take several minutes", window)
                window.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                window.progress = QProgressBar(window)
                window.progress.setRange(0, total_images_expected)
                layout = QVBoxLayout()
                layout.addWidget(window.label)
                layout.addWidget(window.progress)
                window.setLayout(layout)

                def update_progress(value):
                    window.progress.setValue(value)

                def on_download_complete():
                    window.label.setText("All Images have been downloaded. \n Please close this window now and once all needed files have been installed \n => Restart Anki.")

                sprite_downloader = SpriteDownloader(sprites_path, id_to)
                sprite_downloader.progress_updated.connect(update_progress)
                sprite_downloader.download_complete.connect(on_download_complete)
                sprite_downloader.start()
                window.exec()
            except Exception as e:
                showWarning(f"An error occured in download window: {e}")
        
        show_loading_window()
    except Exception as e:
        showWarning(f"An error occured in the download process of the sprites: {e}")

def show_agreement_and_downloadspritespokeshowdown():
    # Show the agreement dialog
    dialog = AgreementDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        #pyqt6.6.1 difference
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
        window.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        window.progress = QProgressBar(window)
        window.progress.setRange(0, total_images_expected)
        layout = QVBoxLayout()
        layout.addWidget(window.label)
        layout.addWidget(window.progress)
        window.setLayout(layout)

        def update_progress(value):
            window.progress.setValue(value)

        def on_download_complete():
            window.label.setText("All Images have been downloaded. \n Please close this window now and once all needed files have been installed \n => Restart Anki.")

        sprite_downloader = SpriteGifDownloader(sprites_path, id_to)
        sprite_downloader.progress_updated.connect(update_progress)
        sprite_downloader.download_complete.connect(on_download_complete)
        sprite_downloader.start()

        window.exec()

    show_loading_window()

class ItemSpriteDownloader(QThread):
    progress_updated = pyqtSignal(int)
    download_complete = pyqtSignal()  # Signal to indicate download completion
    downloading_sounds_txt = pyqtSignal()
    downloading_item_sprites_txt = pyqtSignal()
    downloading_badges_sprites_txt = pyqtSignal()  # Signal to indicate download completion

    def __init__(self, destination_to):
        super().__init__()
        global addon_dir
        self.items_destination_to = addon_dir / "pokemon_sprites" / "items"
        self.badges_destination_to = addon_dir / "pokemon_sprites" / "badges"
        self.sounds_destination_to = addon_dir / "pokemon_sprites" / "sounds"
        self.badges_base_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/badges/"
        self.item_base_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/dream-world/"
        self.sounds_base_url = "https://play.pokemonshowdown.com/audio/cries/"
        self.sound_names = ['ababo.mp3', 'abomasnow-mega.mp3', 'abomasnow.mp3', 'abra.mp3', 'absol-mega.mp3', 'absol.mp3', 'accelgor.mp3', 'aegislash.mp3', 'aerodactyl-mega.mp3', 'aerodactyl.mp3', 'aggron-mega.mp3', 'aggron.mp3', 'aipom.mp3', 'alakazam-mega.mp3', 'alakazam.mp3', 'alcremie.mp3', 'alomomola.mp3', 'altaria-mega.mp3', 'altaria.mp3', 'amaura.mp3', 'ambipom.mp3', 'amoonguss.mp3', 'ampharos-mega.mp3', 'ampharos.mp3', 'annihilape.mp3', 'anorith.mp3', 'appletun.mp3', 'applin.mp3', 'araquanid.mp3', 'arbok.mp3', 'arboliva.mp3', 'arcanine.mp3', 'arceus.mp3', 'archaludon.mp3', 'archen.mp3', 'archeops.mp3', 'arctibax.mp3', 'arctovish.mp3', 'arctozolt.mp3', 'argalis.mp3', 'arghonaut.mp3', 'ariados.mp3', 'armaldo.mp3', 'armarouge.mp3', 'aromatisse.mp3', 'aron.mp3', 'arrokuda.mp3', 'articuno.mp3', 'astrolotl.mp3', 'audino-mega.mp3', 'audino.mp3', 'aurorus.mp3', 'aurumoth.mp3', 'avalugg.mp3', 'axew.mp3', 'azelf.mp3', 'azumarill.mp3', 'azurill.mp3', 'bagon.mp3', 'baltoy.mp3', 'banette-mega.mp3', 'banette.mp3', 'barbaracle.mp3', 'barboach.mp3', 'barraskewda.mp3', 'basculegion.mp3', 'basculin.mp3', 'bastiodon.mp3', 'baxcalibur.mp3', 'bayleef.mp3', 'beartic.mp3', 'beautifly.mp3', 'beedrill-mega.mp3', 'beedrill.mp3', 'beheeyem.mp3', 'beldum.mp3', 'bellibolt.mp3', 'bellossom.mp3', 'bellsprout.mp3', 'bergmite.mp3', 'bewear.mp3', 'bibarel.mp3', 'bidoof.mp3', 'binacle.mp3', 'bisharp.mp3', 'blacephalon.mp3', 'blastoise-mega.mp3', 'blastoise.mp3', 'blaziken-mega.mp3', 'blaziken.mp3', 'blipbug.mp3', 'blissey.mp3', 'blitzle.mp3', 'boldore.mp3', 'boltund.mp3', 'bombirdier.mp3', 'bonsly.mp3', 'bouffalant.mp3', 'bounsweet.mp3', 'braixen.mp3', 'brambleghast.mp3', 'bramblin.mp3', 'brattler.mp3', 'braviary.mp3', 'breezi.mp3', 'breloom.mp3', 'brionne.mp3', 'bronzong.mp3', 'bronzor.mp3', 'brutebonnet.mp3', 'bruxish.mp3', 'budew.mp3', 'buizel.mp3', 'bulbasaur.mp3', 'buneary.mp3', 'bunnelby.mp3', 'burmy.mp3', 'butterfree.mp3', 'buzzwole.mp3', 'cacnea.mp3', 'cacturne.mp3', 'caimanoe.mp3', 'calyrex-ice.mp3', 'calyrex-shadow.mp3', 'calyrex.mp3', 'camerupt-mega.mp3', 'camerupt.mp3', 'capsakid.mp3', 'carbink.mp3', 'caribolt.mp3', 'carkol.mp3', 'carnivine.mp3', 'carracosta.mp3', 'carvanha.mp3', 'cascoon.mp3', 'castform.mp3', 'caterpie.mp3', 'cawdet.mp3', 'cawmodore.mp3', 'celebi.mp3', 'celesteela.mp3', 'centiskorch.mp3', 'ceruledge.mp3', 'cetitan.mp3', 'cetoddle.mp3', 'chandelure.mp3', 'chansey.mp3', 'charcadet.mp3', 'charizard-megax.mp3', 'charizard-megay.mp3', 'charizard.mp3', 'charjabug.mp3', 'charmander.mp3', 'charmeleon.mp3', 'chatot.mp3', 'cherrim.mp3', 'cherubi.mp3', 'chesnaught.mp3', 'chespin.mp3', 'chewtle.mp3', 'chienpao.mp3', 'chikorita.mp3', 'chimchar.mp3', 'chimecho.mp3', 'chinchou.mp3', 'chingling.mp3', 'chiyu.mp3', 'chromera.mp3', 'cinccino.mp3', 'cinderace.mp3', 'clamperl.mp3', 'clauncher.mp3', 'clawitzer.mp3', 'claydol.mp3', 'clefable.mp3', 'clefairy.mp3', 'cleffa.mp3', 'clobbopus.mp3', 'clodsire.mp3', 'cloyster.mp3', 'coalossal.mp3', 'cobalion.mp3', 'cofagrigus.mp3', 'colossoil.mp3', 'combee.mp3', 'combusken.mp3', 'comfey.mp3', 'conkeldurr.mp3', 'copperajah.mp3', 'coribalis.mp3', 'corphish.mp3', 'corsola.mp3', 'corviknight.mp3', 'corvisquire.mp3', 'cosmoem.mp3', 'cosmog.mp3', 'cottonee.mp3', 'crabominable.mp3', 'crabrawler.mp3', 'cradily.mp3', 'cramorant-gorging.mp3', 'cramorant-gulping.mp3', 'cramorant.mp3', 'cranidos.mp3', 'crawdaunt.mp3', 'cresselia.mp3', 'croagunk.mp3', 'crobat.mp3', 'crocalor.mp3', 'croconaw.mp3', 'crucibelle-mega.mp3', 'crucibelle.mp3', 'crustle.mp3', 'cryogonal.mp3', 'cubchoo.mp3', 'cubone.mp3', 'cufant.mp3', 'cupra.mp3', 'cursola.mp3', 'cutiefly.mp3', 'cyclizar.mp3', 'cyclohm.mp3', 'cyndaquil.mp3', 'dachsbun.mp3', 'darkrai.mp3', 'darmanitan.mp3', 'dartrix.mp3', 'darumaka.mp3', 'decidueye.mp3', 'dedenne.mp3', 'deerling.mp3', 'deino.mp3', 'delcatty.mp3', 'delibird.mp3', 'delphox.mp3', 'deoxys.mp3', 'dewgong.mp3', 'dewott.mp3', 'dewpider.mp3', 'dhelmise.mp3', 'dialga.mp3', 'diancie-mega.mp3', 'diancie.mp3', 'diggersby.mp3', 'diglett.mp3', 'dipplin.mp3', 'ditto.mp3', 'dodrio.mp3', 'doduo.mp3', 'dolliv.mp3', 'dondozo.mp3', 'donphan.mp3', 'dorsoil.mp3', 'dottler.mp3', 'doublade.mp3', 'dracovish.mp3', 'dracozolt.mp3', 'dragalge.mp3', 'dragapult.mp3', 'dragonair.mp3', 'dragonite.mp3', 'drakloak.mp3', 'drampa.mp3', 'drapion.mp3', 'dratini.mp3', 'drednaw.mp3', 'dreepy.mp3', 'drifblim.mp3', 'drifloon.mp3', 'drilbur.mp3', 'drizzile.mp3', 'drowzee.mp3', 'druddigon.mp3', 'dubwool.mp3', 'ducklett.mp3', 'dudunsparce.mp3', 'dugtrio.mp3', 'dunsparce.mp3', 'duohm.mp3', 'duosion.mp3', 'duraludon.mp3', 'durant.mp3', 'dusclops.mp3', 'dusknoir.mp3', 'duskull.mp3', 'dustox.mp3', 'dwebble.mp3', 'eelektrik.mp3', 'eelektross.mp3', 'eevee-starter.mp3', 'eevee.mp3', 'eiscue-noice.mp3', 'eiscue.mp3', 'ekans.mp3', 'eldegoss.mp3', 'electabuzz.mp3', 'electivire.mp3', 'electrelk.mp3', 'electrike.mp3', 'electrode.mp3', 'elekid.mp3', 'elgyem.mp3', 'embirch.mp3', 'emboar.mp3', 'emolga.mp3', 'empoleon.mp3', 'enamorus-therian.mp3', 'enamorus.mp3', 'entei.mp3', 'equilibra.mp3', 'escavalier.mp3', 'espathra.mp3', 'espeon.mp3', 'espurr.mp3', 'eternatus-eternamax.mp3', 'eternatus.mp3', 'excadrill.mp3', 'exeggcute.mp3', 'exeggutor.mp3', 'exploud.mp3', 'falinks.mp3', 'farfetchd.mp3', 'farigiraf.mp3', 'fawnifer.mp3', 'fearow.mp3', 'feebas.mp3', 'fennekin.mp3', 'feraligatr.mp3', 'ferroseed.mp3', 'ferrothorn.mp3', 'fezandipiti.mp3', 'fidgit.mp3', 'fidough.mp3', 'finizen.mp3', 'finneon.mp3', 'flaaffy.mp3', 'flabebe.mp3', 'flamigo.mp3', 'flapple.mp3', 'flarelm.mp3', 'flareon.mp3', 'fletchinder.mp3', 'fletchling.mp3', 'flittle.mp3', 'floatoy.mp3', 'floatzel.mp3', 'floette-eternal.mp3', 'floette.mp3', 'floragato.mp3', 'florges.mp3', 'fluttermane.mp3', 'flygon.mp3', 'fomantis.mp3', 'foongus.mp3', 'forretress.mp3', 'fraxure.mp3', 'frigibax.mp3', 'frillish.mp3', 'froakie.mp3', 'frogadier.mp3', 'froslass.mp3', 'frosmoth.mp3', 'fuecoco.mp3', 'furfrou.mp3', 'furret.mp3', 'gabite.mp3', 'gallade-mega.mp3', 'gallade.mp3', 'galvantula.mp3', 'garbodor.mp3', 'garchomp-mega.mp3', 'garchomp.mp3', 'gardevoir-mega.mp3', 'gardevoir.mp3', 'garganacl.mp3', 'gastly.mp3', 'gastrodon.mp3', 'genesect.mp3', 'gengar-mega.mp3', 'gengar.mp3', 'geodude.mp3', 'gholdengo.mp3', 'gible.mp3', 'gigalith.mp3', 'gimmighoul-roaming.mp3', 'gimmighoul.mp3', 'girafarig.mp3', 'giratina.mp3', 'glaceon.mp3', 'glalie-mega.mp3', 'glalie.mp3', 'glameow.mp3', 'glastrier.mp3', 'gligar.mp3', 'glimmet.mp3', 'glimmora.mp3', 'gliscor.mp3', 'gloom.mp3', 'gogoat.mp3', 'golbat.mp3', 'goldeen.mp3', 'golduck.mp3', 'golem.mp3', 'golett.mp3', 'golisopod.mp3', 'golurk.mp3', 'goodra.mp3', 'goomy.mp3', 'gorebyss.mp3', 'gossifleur.mp3', 'gothita.mp3', 'gothitelle.mp3', 'gothorita.mp3', 'gougingfire.mp3', 'gourgeist-super.mp3', 'gourgeist.mp3', 'grafaiai.mp3', 'granbull.mp3', 'grapploct.mp3', 'graveler.mp3', 'greattusk.mp3', 'greavard.mp3', 'greedent.mp3', 'greninja.mp3', 'grimer.mp3', 'grimmsnarl.mp3', 'grookey.mp3', 'grotle.mp3', 'groudon-primal.mp3', 'groudon.mp3', 'grovyle.mp3', 'growlithe.mp3', 'grubbin.mp3', 'grumpig.mp3', 'gulpin.mp3', 'gumshoos.mp3', 'gurdurr.mp3', 'guzzlord.mp3', 'gyarados-mega.mp3', 'gyarados.mp3', 'hakamoo.mp3', 'happiny.mp3', 'hariyama.mp3', 'hatenna.mp3', 'hatterene.mp3', 'hattrem.mp3', 'haunter.mp3', 'hawlucha.mp3', 'haxorus.mp3', 'heatmor.mp3', 'heatran.mp3', 'heliolisk.mp3', 'helioptile.mp3', 'hemogoblin.mp3', 'heracross-mega.mp3', 'heracross.mp3', 'herdier.mp3', 'hippopotas.mp3', 'hippowdon.mp3', 'hitmonchan.mp3', 'hitmonlee.mp3', 'hitmontop.mp3', 'honchkrow.mp3', 'honedge.mp3', 'hooh.mp3', 'hoopa-unbound.mp3', 'hoopa.mp3', 'hoothoot.mp3', 'hoppip.mp3', 'horsea.mp3', 'houndoom-mega.mp3', 'houndoom.mp3', 'houndour.mp3', 'houndstone.mp3', 'huntail.mp3', 'hydrapple.mp3', 'hydreigon.mp3', 'hypno.mp3', 'igglybuff.mp3', 'illumise.mp3', 'impidimp.mp3', 'incineroar.mp3', 'indeedee-f.mp3', 'indeedee.mp3', 'infernape.mp3', 'inkay.mp3', 'inteleon.mp3', 'ironboulder.mp3', 'ironbundle.mp3', 'ironcrown.mp3', 'ironhands.mp3', 'ironjugulis.mp3', 'ironleaves.mp3', 'ironmoth.mp3', 'ironthorns.mp3', 'irontreads.mp3', 'ironvaliant.mp3', 'ivysaur.mp3', 'jangmoo.mp3', 'jellicent.mp3', 'jigglypuff.mp3', 'jirachi.mp3', 'jolteon.mp3', 'joltik.mp3', 'jumbao.mp3', 'jumpluff.mp3', 'justyke.mp3', 'jynx.mp3', 'kabuto.mp3', 'kabutops.mp3', 'kadabra.mp3', 'kakuna.mp3', 'kangaskhan-mega.mp3', 'kangaskhan.mp3', 'karrablast.mp3', 'kartana.mp3', 'kecleon.mp3', 'keldeo.mp3', 'kerfluffle.mp3', 'kilowattrel.mp3', 'kingambit.mp3', 'kingdra.mp3', 'kingler.mp3', 'kirlia.mp3', 'kitsunoh.mp3', 'klang.mp3', 'klawf.mp3', 'kleavor.mp3', 'klefki.mp3', 'klink.mp3', 'klinklang.mp3', 'koffing.mp3', 'komala.mp3', 'kommoo.mp3', 'koraidon.mp3', 'krabby.mp3', 'kricketot.mp3', 'kricketune.mp3', 'krilowatt.mp3', 'krokorok.mp3', 'krookodile.mp3', 'kubfu.mp3', 'kyogre-primal.mp3', 'kyogre.mp3', 'kyurem-black.mp3', 'kyurem-white.mp3', 'kyurem.mp3', 'lairon.mp3', 'lampent.mp3', 'landorus-therian.mp3', 'landorus.mp3', 'lanturn.mp3', 'lapras.mp3', 'larvesta.mp3', 'larvitar.mp3', 'latias-mega.mp3', 'latias.mp3', 'latios-mega.mp3', 'latios.mp3', 'leafeon.mp3', 'leavanny.mp3', 'lechonk.mp3', 'ledian.mp3', 'ledyba.mp3', 'lickilicky.mp3', 'lickitung.mp3', 'liepard.mp3', 'lileep.mp3', 'lilligant.mp3', 'lillipup.mp3', 'linoone.mp3', 'litleo.mp3', 'litten.mp3', 'litwick.mp3', 'lokix.mp3', 'lombre.mp3', 'lopunny-mega.mp3', 'lopunny.mp3', 'lotad.mp3', 'loudred.mp3', 'lucario-mega.mp3', 'lucario.mp3', 'ludicolo.mp3', 'lugia.mp3', 'lumineon.mp3', 'lunala.mp3', 'lunatone.mp3', 'lurantis.mp3', 'luvdisc.mp3', 'luxio.mp3', 'luxray.mp3', 'lycanroc-dusk.mp3', 'lycanroc-midnight.mp3', 'lycanroc.mp3', 'mabosstiff.mp3', 'machamp.mp3', 'machoke.mp3', 'machop.mp3', 'magby.mp3', 'magcargo.mp3', 'magearna.mp3', 'magikarp.mp3', 'magmar.mp3', 'magmortar.mp3', 'magnemite.mp3', 'magneton.mp3', 'magnezone.mp3', 'makuhita.mp3', 'malaconda.mp3', 'malamar.mp3', 'mamoswine.mp3', 'manaphy.mp3', 'mandibuzz.mp3', 'manectric-mega.mp3', 'manectric.mp3', 'mankey.mp3', 'mantine.mp3', 'mantyke.mp3', 'maractus.mp3', 'mareanie.mp3', 'mareep.mp3', 'marill.mp3', 'marowak.mp3', 'marshadow.mp3', 'marshtomp.mp3', 'maschiff.mp3', 'masquerain.mp3', 'maushold-four.mp3', 'maushold.mp3', 'mawile-mega.mp3', 'mawile.mp3', 'medicham-mega.mp3', 'medicham.mp3', 'meditite.mp3', 'meganium.mp3', 'melmetal.mp3', 'meloetta.mp3', 'meltan.mp3', 'meowscarada.mp3', 'meowstic.mp3', 'meowth.mp3', 'mesprit.mp3', 'metagross-mega.mp3', 'metagross.mp3', 'metang.mp3', 'metapod.mp3', 'mew.mp3', 'mewtwo-megax.mp3', 'mewtwo-megay.mp3', 'mewtwo.mp3', 'miasmaw.mp3', 'miasmite.mp3', 'mienfoo.mp3', 'mienshao.mp3', 'mightyena.mp3', 'milcery.mp3', 'milotic.mp3', 'miltank.mp3', 'mimejr.mp3', 'mimikyu.mp3', 'minccino.mp3', 'minior.mp3', 'minun.mp3', 'miraidon.mp3', 'misdreavus.mp3', 'mismagius.mp3', 'mollux.mp3', 'moltres.mp3', 'monferno.mp3', 'monohm.mp3', 'morelull.mp3', 'morgrem.mp3', 'morpeko-hangry.mp3', 'morpeko.mp3', 'mothim.mp3', 'mrmime.mp3', 'mrrime.mp3', 'mudbray.mp3', 'mudkip.mp3', 'mudsdale.mp3', 'muk.mp3', 'mumbao.mp3', 'munchlax.mp3', 'munkidori.mp3', 'munna.mp3', 'murkrow.mp3', 'musharna.mp3', 'nacli.mp3', 'naclstack.mp3', 'naganadel.mp3', 'natu.mp3', 'naviathan.mp3', 'necrozma-dawnwings.mp3', 'necrozma-duskmane.mp3', 'necrozma-ultra.mp3', 'necrozma.mp3', 'necturine.mp3', 'necturna.mp3', 'nickit.mp3', 'nidoking.mp3', 'nidoqueen.mp3', 'nidoranf.mp3', 'nidoranm.mp3', 'nidorina.mp3', 'nidorino.mp3', 'nihilego.mp3', 'nincada.mp3', 'ninetales.mp3', 'ninjask.mp3', 'noctowl.mp3', 'nohface.mp3', 'noibat.mp3', 'noivern.mp3', 'nosepass.mp3', 'numel.mp3', 'nuzleaf.mp3', 'nymble.mp3', 'obstagoon.mp3', 'octillery.mp3', 'oddish.mp3', 'ogerpon.mp3', 'oinkologne-f.mp3', 'oinkologne.mp3', 'okidogi.mp3', 'omanyte.mp3', 'omastar.mp3', 'onix.mp3', 'oranguru.mp3', 'orbeetle.mp3', 'oricorio-pau.mp3', 'oricorio-pompom.mp3', 'oricorio-sensu.mp3', 'oricorio.mp3', 'orthworm.mp3', 'oshawott.mp3', 'overqwil.mp3', 'pachirisu.mp3', 'pajantom.mp3', 'palafin-hero.mp3', 'palafin.mp3', 'palkia.mp3', 'palossand.mp3', 'palpitoad.mp3', 'pancham.mp3', 'pangoro.mp3', 'panpour.mp3', 'pansage.mp3', 'pansear.mp3', 'paras.mp3', 'parasect.mp3', 'passimian.mp3', 'patrat.mp3', 'pawmi.mp3', 'pawmo.mp3', 'pawmot.mp3', 'pawniard.mp3', 'pecharunt.mp3', 'pelipper.mp3', 'perrserker.mp3', 'persian.mp3', 'petilil.mp3', 'phanpy.mp3', 'phantump.mp3', 'pheromosa.mp3', 'phione.mp3', 'pichu.mp3', 'pidgeot-mega.mp3', 'pidgeot.mp3', 'pidgeotto.mp3', 'pidgey.mp3', 'pidove.mp3', 'pignite.mp3', 'pikachu-starter.mp3', 'pikachu.mp3', 'pikipek.mp3', 'piloswine.mp3', 'pincurchin.mp3', 'pineco.mp3', 'pinsir-mega.mp3', 'pinsir.mp3', 'piplup.mp3', 'plasmanta.mp3', 'pluffle.mp3', 'plusle.mp3', 'poipole.mp3', 'politoed.mp3', 'poliwag.mp3', 'poliwhirl.mp3', 'poliwrath.mp3', 'poltchageist.mp3', 'polteageist.mp3', 'ponyta.mp3', 'poochyena.mp3', 'popplio.mp3', 'porygon.mp3', 'porygon2.mp3', 'porygonz.mp3', 'primarina.mp3', 'primeape.mp3', 'prinplup.mp3', 'privatyke.mp3', 'probopass.mp3', 'protowatt.mp3', 'psyduck.mp3', 'pumpkaboo-super.mp3', 'pumpkaboo.mp3', 'pupitar.mp3', 'purrloin.mp3', 'purugly.mp3', 'pyroak.mp3', 'pyroar.mp3', 'pyukumuku.mp3', 'quagsire.mp3', 'quaquaval.mp3', 'quaxly.mp3', 'quaxwell.mp3', 'quilava.mp3', 'quilladin.mp3', 'qwilfish.mp3', 'raboot.mp3', 'rabsca.mp3', 'ragingbolt.mp3', 'raichu.mp3', 'raikou.mp3', 'ralts.mp3', 'rampardos.mp3', 'rapidash.mp3', 'raticate.mp3', 'rattata.mp3', 'rayquaza-mega.mp3', 'rayquaza.mp3', 'rebble.mp3', 'regice.mp3', 'regidrago.mp3', 'regieleki.mp3', 'regigigas.mp3', 'regirock.mp3', 'registeel.mp3', 'relicanth.mp3', 'rellor.mp3', 'remoraid.mp3', 'reshiram.mp3', 'reuniclus.mp3', 'revavroom.mp3', 'revenankh.mp3', 'rhydon.mp3', 'rhyhorn.mp3', 'rhyperior.mp3', 'ribombee.mp3', 'rillaboom.mp3', 'riolu.mp3', 'roaringmoon.mp3', 'rockruff.mp3', 'roggenrola.mp3', 'rolycoly.mp3', 'rookidee.mp3', 'roselia.mp3', 'roserade.mp3', 'rotom.mp3', 'rowlet.mp3', 'rufflet.mp3', 'runerigus.mp3', 'sableye-mega.mp3', 'sableye.mp3', 'saharaja.mp3', 'saharascal.mp3', 'salamence-mega.mp3', 'salamence.mp3', 'salandit.mp3', 'salazzle.mp3', 'samurott.mp3', 'sandaconda.mp3', 'sandile.mp3', 'sandshrew.mp3', 'sandslash.mp3', 'sandygast.mp3', 'sandyshocks.mp3', 'sawk.mp3', 'sawsbuck.mp3', 'scatterbug.mp3', 'scattervein.mp3', 'sceptile-mega.mp3', 'sceptile.mp3', 'scizor-mega.mp3', 'scizor.mp3', 'scolipede.mp3', 'scorbunny.mp3', 'scovillain.mp3', 'scrafty.mp3', 'scraggy.mp3', 'scratchet.mp3', 'screamtail.mp3', 'scyther.mp3', 'seadra.mp3', 'seaking.mp3', 'sealeo.mp3', 'seedot.mp3', 'seel.mp3', 'seismitoad.mp3', 'sentret.mp3', 'serperior.mp3', 'servine.mp3', 'seviper.mp3', 'sewaddle.mp3', 'sharpedo-mega.mp3', 'sharpedo.mp3', 'shaymin-sky.mp3', 'shaymin.mp3', 'shedinja.mp3', 'shelgon.mp3', 'shellder.mp3', 'shellos.mp3', 'shelmet.mp3', 'shieldon.mp3', 'shiftry.mp3', 'shiinotic.mp3', 'shinx.mp3', 'shroodle.mp3', 'shroomish.mp3', 'shuckle.mp3', 'shuppet.mp3', 'sigilyph.mp3', 'silcoon.mp3', 'silicobra.mp3', 'silvally.mp3', 'simipour.mp3', 'simisage.mp3', 'simisear.mp3', 'sinistcha.mp3', 'sinistea.mp3', 'sirfetchd.mp3', 'sizzlipede.mp3', 'skarmory.mp3', 'skeledirge.mp3', 'skiddo.mp3', 'skiploom.mp3', 'skitty.mp3', 'skorupi.mp3', 'skrelp.mp3', 'skuntank.mp3', 'skwovet.mp3', 'slaking.mp3', 'slakoth.mp3', 'sliggoo.mp3', 'slitherwing.mp3', 'slowbro-mega.mp3', 'slowbro.mp3', 'slowking.mp3', 'slowpoke-galar.mp3', 'slowpoke.mp3', 'slugma.mp3', 'slurpuff.mp3', 'smeargle.mp3', 'smogecko.mp3', 'smoguana.mp3', 'smokomodo.mp3', 'smoliv.mp3', 'smoochum.mp3', 'snaelstrom.mp3', 'sneasel.mp3', 'sneasler.mp3', 'snivy.mp3', 'snom.mp3', 'snorlax.mp3', 'snorunt.mp3', 'snover.mp3', 'snubbull.mp3', 'snugglow.mp3', 'sobble.mp3', 'solgaleo.mp3', 'solosis.mp3', 'solotl.mp3', 'solrock.mp3', 'spearow.mp3', 'spectrier.mp3', 'spewpa.mp3', 'spheal.mp3', 'spidops.mp3', 'spinarak.mp3', 'spinda.mp3', 'spiritomb.mp3', 'spoink.mp3', 'sprigatito.mp3', 'spritzee.mp3', 'squawkabilly.mp3', 'squirtle.mp3', 'stakataka.mp3', 'stantler.mp3', 'staraptor.mp3', 'staravia.mp3', 'starly.mp3', 'starmie.mp3', 'staryu.mp3', 'steelix-mega.mp3', 'steelix.mp3', 'steenee.mp3', 'stonjourner.mp3', 'stoutland.mp3', 'stratagem.mp3', 'stufful.mp3', 'stunfisk.mp3', 'stunky.mp3', 'sudowoodo.mp3', 'suicune.mp3', 'sunflora.mp3', 'sunkern.mp3', 'surskit.mp3', 'swablu.mp3', 'swadloon.mp3', 'swalot.mp3', 'swampert-mega.mp3', 'swampert.mp3', 'swanna.mp3', 'swellow.mp3', 'swinub.mp3', 'swirlix.mp3', 'swirlpool.mp3', 'swoobat.mp3', 'syclant.mp3', 'syclar.mp3', 'sylveon.mp3', 'tactite.mp3', 'tadbulb.mp3', 'taillow.mp3', 'talonflame.mp3', 'tandemaus.mp3', 'tangela.mp3', 'tangrowth.mp3', 'tapubulu.mp3', 'tapufini.mp3', 'tapukoko.mp3', 'tapulele.mp3', 'tarountula.mp3', 'tatsugiri-droopy.mp3', 'tatsugiri-stretchy.mp3', 'tatsugiri.mp3', 'tauros.mp3', 'teddiursa.mp3', 'tentacool.mp3', 'tentacruel.mp3', 'tepig.mp3', 'terapagos.mp3', 'terrakion.mp3', 'thievul.mp3', 'throh.mp3', 'thundurus-therian.mp3', 'thundurus.mp3', 'thwackey.mp3', 'timburr.mp3', 'tinglu.mp3', 'tinkatink.mp3', 'tinkaton.mp3', 'tinkatuff.mp3', 'tirtouga.mp3', 'toedscool.mp3', 'toedscruel.mp3', 'togedemaru.mp3', 'togekiss.mp3', 'togepi.mp3', 'togetic.mp3', 'tomohawk.mp3', 'torchic.mp3', 'torkoal.mp3', 'tornadus-therian.mp3', 'tornadus.mp3', 'torracat.mp3', 'torterra.mp3', 'totodile.mp3', 'toucannon.mp3', 'toxapex.mp3', 'toxel.mp3', 'toxicroak.mp3', 'toxtricity-lowkey.mp3', 'toxtricity.mp3', 'tranquill.mp3', 'trapinch.mp3', 'treecko.mp3', 'trevenant.mp3', 'tropius.mp3', 'trubbish.mp3', 'trumbeak.mp3', 'tsareena.mp3', 'turtonator.mp3', 'turtwig.mp3', 'tympole.mp3', 'tynamo.mp3', 'typenull.mp3', 'typhlosion.mp3', 'tyranitar-mega.mp3', 'tyranitar.mp3', 'tyrantrum.mp3', 'tyrogue.mp3', 'tyrunt.mp3', 'umbreon.mp3', 'unfezant.mp3', 'unown.mp3', 'ursaluna.mp3', 'ursaring.mp3', 'urshifu-rapidstrike.mp3', 'urshifu.mp3', 'uxie.mp3', 'vanillish.mp3', 'vanillite.mp3', 'vanilluxe.mp3', 'vaporeon.mp3', 'varoom.mp3', 'veluza.mp3', 'venipede.mp3', 'venomicon.mp3', 'venomoth.mp3', 'venonat.mp3', 'venusaur-mega.mp3', 'venusaur.mp3', 'vespiquen.mp3', 'vibrava.mp3', 'victini.mp3', 'victreebel.mp3', 'vigoroth.mp3', 'vikavolt.mp3', 'vileplume.mp3', 'virizion.mp3', 'vivillon.mp3', 'volbeat.mp3', 'volcanion.mp3', 'volcarona.mp3', 'volkraken.mp3', 'volkritter.mp3', 'voltorb.mp3', 'voodoll.mp3', 'voodoom.mp3', 'vullaby.mp3', 'vulpix.mp3', 'wailmer.mp3', 'wailord.mp3', 'walkingwake.mp3', 'walrein.mp3', 'wartortle.mp3', 'watchog.mp3', 'wattrel.mp3', 'weavile.mp3', 'weedle.mp3', 'weepinbell.mp3', 'weezing.mp3', 'whimsicott.mp3', 'whirlipede.mp3', 'whiscash.mp3', 'whismur.mp3', 'wigglytuff.mp3', 'wiglett.mp3', 'wimpod.mp3', 'wingull.mp3', 'wishiwashi-school.mp3', 'wishiwashi.mp3', 'wobbuffet.mp3', 'wochien.mp3', 'woobat.mp3', 'wooloo.mp3', 'wooper.mp3', 'wormadam.mp3', 'wugtrio.mp3', 'wurmple.mp3', 'wynaut.mp3', 'wyrdeer.mp3', 'xatu.mp3', 'xerneas.mp3', 'xurkitree.mp3', 'yamask.mp3', 'yamper.mp3', 'yanma.mp3', 'yanmega.mp3', 'yungoos.mp3', 'yveltal.mp3', 'zacian-crowned.mp3', 'zacian.mp3', 'zamazenta-crowned.mp3', 'zamazenta.mp3', 'zangoose.mp3', 'zapdos.mp3', 'zarude.mp3', 'zebstrika.mp3', 'zekrom.mp3', 'zeraora.mp3', 'zigzagoon.mp3', 'zoroark.mp3', 'zorua.mp3', 'zubat.mp3', 'zweilous.mp3', 'zygarde-10.mp3', 'zygarde-complete.mp3', 'zygarde.mp3']
        self.item_names = [ "absorb-bulb.png",  "aguav-berry.png",  "air-balloon.png", "amulet-coin.png", "antidote.png", "apicot-berry.png", "armor-fossil.png",
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
        "up-grade.png", "wacan-berry.png", "water-gem.png", "water-stone.png", "watmel-berry.png", "wave-incense.png", "wepear-berry.png", "white-flute.png", "white-herb.png", "wide-lens.png", "wiki-berry.png", "wise-glasses.png", "x-accuracy.png", "x-attack.png", "x-defense.png", "x-sp-atk.png", "x-sp-def.png", "x-speed.png", "yache-berry.png", "yellow-flute.png", "yellow-scarf.png", "yellow-shard.png", "zap-plate.png", "zinc.png", "zoom-lens.png"
        ]
        if not os.path.exists(self.items_destination_to):
            os.makedirs(self.items_destination_to)
        if not os.path.exists(self.badges_destination_to):
            os.makedirs(self.badges_destination_to)
        if not os.path.exists(self.sounds_destination_to):
            os.makedirs(self.sounds_destination_to)
    def run(self):
        total_downloaded = 0
        self.downloading_item_sprites_txt.emit()
        for item_name in self.item_names:
            item_url = self.item_base_url + item_name
            response = requests.get(item_url)
            if response.status_code == 200:
                with open(os.path.join(self.items_destination_to, item_name), 'wb') as file:
                    file.write(response.content)
            total_downloaded += 1
            self.progress_updated.emit(total_downloaded)
        # Emit the download_complete signal at the end of the download process
        max_badges = 68
        self.downloading_badges_sprites_txt.emit()
        for badge_num in range(1,68):
            badge_file = f"{badge_num}.png"
            badge_url = self.badges_base_url + badge_file
            response = requests.get(badge_url)
            if response.status_code == 200:
                with open(os.path.join(self.badges_destination_to, badge_file), 'wb') as file:
                    file.write(response.content)
            total_downloaded += 1
            self.progress_updated.emit(total_downloaded)
        self.downloading_sounds_txt.emit()
        for sound in self.sound_names:
            sounds_url = self.sounds_base_url + sound
            response = requests.get(sounds_url)
            if response.status_code == 200:
                with open(os.path.join(self.sounds_destination_to, sound), 'wb') as file:
                    file.write(response.content)
            total_downloaded += 1
            self.progress_updated.emit(total_downloaded)
        total_downloaded += 1
        self.progress_updated.emit(total_downloaded)
        self.download_complete.emit()



def download_item_sprites():
    total_images_expected = int(336 + 68 + 1190)
    global addon_dir
    destination_to = addon_dir / "pokemon_sprites" / "items"

    def show_loading_window():
        window = QDialog()
        window.setWindowTitle("Downloading Item Sprites")
        window.label = QLabel("Downloading... \n This may take several minutes", window)
        window.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        window.progress = QProgressBar(window)
        window.progress.setRange(0, total_images_expected)
        layout = QVBoxLayout()
        layout.addWidget(window.label)
        layout.addWidget(window.progress)
        window.setLayout(layout)

        def update_progress(value):
            window.progress.setValue(value)

        def on_download_complete():
            window.label.setText("All Images have been downloaded. \n Please close this window now and once all needed files have been installed \n => Restart Anki.")
        
        def downloading_sounds_txt():
            window.label.setText("Now Downloading Sound Files")
        
        def downloading_item_sprites_txt():
            window.label.setText("Now Downloading Item Sprites...")

        def downloading_badges_sprites_txt():
            window.label.setText("Now Downloading Badges...")

        sprite_downloader = ItemSpriteDownloader(destination_to)
        sprite_downloader.progress_updated.connect(update_progress)
        sprite_downloader.downloading_sounds_txt.connect(downloading_sounds_txt)
        sprite_downloader.downloading_item_sprites_txt.connect(downloading_item_sprites_txt)
        sprite_downloader.downloading_badges_sprites_txt.connect(downloading_badges_sprites_txt)
        sprite_downloader.download_complete.connect(on_download_complete)
        sprite_downloader.start()

        window.exec()

    show_loading_window()

def show_agreement_and_download():
    # Show the agreement dialog
    dialog = AgreementDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
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
            mw_x = mw.x()
            mw_y = mw.y()
            width = mw.width()
            height = mw.height()
            self.setGeometry(mw_x, mw_y + height/4, 256, 256 )
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
        lang_name = get_pokemon_diff_lang_name(int(id))
        name = name.capitalize()
        # calculate wild pokemon max hp
        max_hp = calculate_hp(stats["hp"], level, ev, iv)
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
            mainpokemon_lang_name = get_pokemon_diff_lang_name(int(mainpokemon_id))
            # Draw the text on top of the image
            # Adjust the font size as needed
            painter.setFont(custom_font)
            painter.setPen(QColor(31, 31, 39))  # Text color
            painter.drawText(48, 67, f"{lang_name} ({gender})")
            painter.drawText(326, 200, mainpokemon_lang_name)
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
        custom_font = load_custom_font(font_file, 28)
        msg_font = load_custom_font(font_file, 32)

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

    def pokemon_display_badge(self, badge_number):
        global pokemon_encounter
        global addon_dir
        global badges_path
        global frontdefault
        global badges
        bckgimage_path = addon_dir / "pokemon_sprites" / "starter_screen" / "bg.png"
        badge_path = badges_path / f"{badge_number}.png"

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
        custom_font = load_custom_font(font_file, 20)
        message_box_text = f"You have received a badge for:"
        message_box_text2 = f"{badges[str(badge_number)]}!"
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(120, 270, message_box_text)
        painter.drawText(140, 290, message_box_text2)
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
        lang_name = get_pokemon_diff_lang_name(int(id))
        window_title = (f"Would you want let the  wild {lang_name} free or catch the wild {lang_name} ?")
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
        battle_widget.setScaledContents(True) #scalable ankimon window
        layout.addWidget(battle_widget)
        self.setStyleSheet("background-color: rgb(44,44,44);")
        self.setLayout(layout)
        self.setMinimumWidth(556)
        self.setMinimumHeight(300)

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
        global test, pokemon_encounter, pokedex_image_path
        # Close the main window when the spacebar is pressed
        if event.key() == Qt.Key.Key_N and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.close()
        if event.key() == Qt.Key.Key_R and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            new_pokemon()
            self.display_first_encounter()

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
        #merged_pixmap.fill(Qt.transparent)
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
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
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        #merged_pixmap.fill(Qt.transparent)
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
        if obj is mw and event.type() == QEvent.Type.KeyPress:
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
        self.read_item_file()
        # Clear the existing widgets from the layout
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        row, col = 0, 0
        max_items_per_row = 2
        max_rows = 4
        if self.itembag_list is None or not self.itembag_list:  # Wenn None oder leer
            empty_label = QLabel("You dont own any items yet.")
            self.layout.addWidget(empty_label, 1, 1)
        else:
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


class AchievementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.read_item_file()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Achievements")
        global addon_dir
        self.layout = QGridLayout()
        self.setLayout(self.layout)

    def renewWidgets(self):
        self.read_item_file()
        # Clear the existing widgets from the layout
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        row, col = 0, 0
        max_items_per_row = 2
        max_rows = 4
        if self.badge_list is None or not self.badge_list:  # Wenn None oder leer
            empty_label = QLabel("You dont own any badges yet.")
            self.layout.addWidget(empty_label, 1, 1)
        else:
            for badge_num in self.badge_list:
                if row >= max_rows:
                    break
                item_widget = self.BadgesLabel(badge_num)
                self.layout.addWidget(item_widget, row, col)
                col += 1
                if col >= max_items_per_row:
                    row += 1
                    col = 0

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
        self.show()

def report_bug():
    # Specify the URL of the Pokémon Showdown Team Builder
    bug_url = "https://github.com/Unlucky-Life/ankimon/issues"

    # Open the Team Builder in the default web browser
    QDesktopServices.openUrl(QUrl(bug_url))

achievement_bag = AchievementWindow()

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

test_action11 = QAction("Check Effectiveness Chart", mw)
test_action11.triggered.connect(eff_chart.show_eff_chart)
mw.pokemenu.addAction(test_action11)

test_action12 = QAction("Check Generations and Pokemon Chart", mw)
test_action12.triggered.connect(gen_id_chart.show_gen_chart)
mw.pokemenu.addAction(test_action12)

test_action3 = QAction("Download Database Files", mw)
qconnect(test_action3.triggered, show_agreement_and_download_database)
mw.pokemenu.addAction(test_action3)
test_action4 = QAction("Download Sprite Files", mw)
qconnect(test_action4.triggered, show_agreement_and_downloadsprites)
mw.pokemenu.addAction(test_action4)
test_action4 = QAction("Download PokemonShowDownSprites", mw)
qconnect(test_action4.triggered, show_agreement_and_downloadspritespokeshowdown)
mw.pokemenu.addAction(test_action4)
itemspritesdow = QAction("Download Sounds, Badges and Item Sprites", mw)
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

    #https://goo.gl/uhAxsg
    #https://www.reddit.com/r/PokemonROMhacks/comments/9xgl7j/pokemon_sound_effects_collection_over_3200_sfx/
    #https://archive.org/details/pokemon-dp-sound-library-disc-2_202205

"""
Future Code Notes

       mw_x = mw.x()
        mw_y = mw.y()
        width = mw.width()
        height = mw.height()
        akw_height = self.height()
        akw_width = self.width()

        amw_center = True
        if amw_center is True:
            if height > akw_height:
                y = int(mw_y + ((height/2) - (akw_height/2)))
            else:
                y = int(mw_y + ((akw_height/2) - (height/2)))
        amw_left = True
        amw_right = False
        if amw_right is True:
            x = int(mw_x + width)
        elif amw_left is True:
            x = int(mw_x-(akw_width))"""
