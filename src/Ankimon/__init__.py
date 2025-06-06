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

import json
import random
import math
import copy
from pathlib import Path
import traceback

import aqt
from anki.hooks import addHook, wrap
from aqt import gui_hooks, mw, utils
from aqt.qt import (
    QDialog,
    QLabel,
    Qt,
    QVBoxLayout,
    )
from aqt.reviewer import Reviewer
from aqt.utils import downArrow, showWarning, tr, tooltip
from aqt.utils import *
from aqt.qt import *
from PyQt6 import *
from PyQt6.QtCore import QPoint, QTimer, QUrl
from PyQt6.QtGui import QColor, QPalette, QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QFrame,
    )
from aqt.gui_hooks import webview_will_set_content
from aqt.webview import WebContent

from . import audios
from .config_var import (
    reviewer_text_message_box,
    dmg_in_reviewer,
    no_more_news,
    remove_levelcap,
    ssh,
    defeat_shortcut,
    catch_shortcut,
    reviewer_buttons,
    battle_sounds
)
from .resources import (
    addon_dir,
    pkmnimgfolder,
    mypokemon_path,
    mainpokemon_path,
    pokemon_names_file_path,
    move_names_file_path,
    itembag_path,
    badgebag_path,
    sound_list_path,
    badges_list_path,
    items_list_path,
    rate_path
)
from .menu_buttons import create_menu_actions
from .hooks import setupHooks
from .texts import (
    _bottomHTML_template,
    button_style,
    rate_addon_text_label,
    thankyou_message_text,
    dont_show_this_button_text
)
from .const import gen_ids
from .business import (
    calc_experience,
    get_multiplier_stats,
)
from .utils import (
    check_folders_exist,
    test_online_connectivity,
    read_local_file,
    read_github_file,
    compare_files,
    write_local_file,
    count_items_and_rewrite,
    give_item,
    format_pokemon_name,
    format_move_name,
    play_effect_sound,
)
from .functions.battle_functions import calculate_hp, status_effect
from .functions.reviewer_iframe import create_iframe_html, create_head_code
from .functions.url_functions import open_team_builder, rate_addon_url, report_bug, join_discord_url, open_leaderboard_url
from .functions.trainer_functions import xp_share_gain_exp
from .functions.badges_functions import check_badges, check_for_badge, receive_badge, handle_achievements, check_and_award_badges
from .functions.encounter_functions import choose_random_pkmn_from_tier
from .functions.pokemon_showdown_functions import export_to_pkmn_showdown, export_all_pkmn_showdown, flex_pokemon_collection
from .functions.drawing_utils import tooltipWithColour
from .functions.discord_function import DiscordPresence
from .functions.encounter_functions import generate_random_pokemon, new_pokemon, catch_pokemon
from .functions.pokedex_functions import (
    search_pokedex,
    search_pokedex_by_id,
    search_pokeapi_db_by_id,
    get_all_pokemon_moves,
    find_details_move,
    check_evolution_for_pokemon,
    return_name_for_id
)
from .functions.pokemon_functions import (
    pick_random_gender,
    find_experience_for_level,
    shiny_chance,
    create_caught_pokemon,
    get_levelup_move_for_pokemon,
)
from .gui_entities import UpdateNotificationWindow, HelpWindow, CheckFiles
from .pyobj.sync_pokemon_data import CheckPokemonData
from .pyobj.attack_dialog import AttackDialog
from .pyobj.backup_files import run_backup
from .pyobj.ankimon_tracker import AnkimonTracker
from .classes.choose_move_dialog import MoveSelectionDialog
from .poke_engine.ankimon_hooks_to_poke_engine import simulate_battle_with_poke_engine
from .poke_engine import constants
from .singletons import (
    logger,
    settings_obj,
    settings_window,
    translator,
    main_pokemon,
    enemy_pokemon,
    trainer_card,
    ankimon_tracker_obj,
    test_window,
    achievement_bag,
    data_handler_obj,
    data_handler_window,
    shop_manager,
    ankimon_tracker_window,
    pokedex_window,
    reviewer_obj,
    eff_chart,
    gen_id_chart,
    license,
    credits,
    evo_window,
    starter_window,
    item_window,
    version_dialog,
    pokecollection_win,
)

# Load move and pokemon name mapping at startup
with open(pokemon_names_file_path, "r", encoding="utf-8") as f:
    POKEMON_NAME_LOOKUP = json.load(f)

with open(move_names_file_path, "r", encoding="utf-8") as f:
    MOVE_NAME_LOOKUP = json.load(f)

collected_pokemon_ids = set()
_collection_loaded = False

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

# Initialize mutator and mutator_full_reset
global new_state
global mutator_full_reset 
global user_hp_after 
global opponent_hp_after 
global dmg_from_enemy_move 
global dmg_from_user_move

# Initialize collected IDs cache
def load_collected_pokemon_ids():
    global collected_pokemon_ids, _collection_loaded
    if _collection_loaded:
        return  # Already loaded, do nothing
    if mypokemon_path.is_file():
        try:
            with open(mypokemon_path, "r", encoding="utf-8") as f:
                collection = json.load(f)
                collected_pokemon_ids = {pkmn["id"] for pkmn in collection}
            _collection_loaded = True
        except Exception as e:
            logger.log("error", f"Error loading collection cache: {str(e)}")
            collected_pokemon_ids = set()
            _collection_loaded = True  # Prevent repeated attempts if file is bad

# Call this during addon initialization
load_collected_pokemon_ids()

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


# Set up web exports for static files
# mw.addonManager.setWebExports(__name__, r"user_files/.*\.(css|js|jpg|gif|html|ttf|png|mp3)")

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

caught_pokemon = {} #pokemon not caught

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
            new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon
    except Exception as e:
        showWarning(f"Error occured in killing enemy pokemon: {e}")

# def save_caught_pokemon(nickname):
#     # Create a dictionary to store the Pokémon's data
#     # add all new values like hp as max_hp, evolution_data, description and growth rate
#     global achievements
#     if enemy_pokemon.tier != None:
#         if enemy_pokemon.tier == "Normal":
#             check = check_for_badge(achievements,17)
#             if check is False:
#                 achievements = receive_badge(17,achievements)
#         elif enemy_pokemon.tier == "Baby":
#             check = check_for_badge(achievements,18)
#             if check is False:
#                 achievements = receive_badge(18,achievements)
#         elif enemy_pokemon.tier == "Ultra":
#             check = check_for_badge(achievements,8)
#             if check is False:
#                 achievements = receive_badge(8,achievements)
#         elif enemy_pokemon.tier == "Legendary":
#             check = check_for_badge(achievements,9)
#             if check is False:
#                 achievements = receive_badge(9,achievements)
#         elif enemy_pokemon.tier == "Mythical":
#             check = check_for_badge(achievements,10)
#             if check is False:
#                 achievements = receive_badge(10,achievements)

#     caught_pokemon = create_caught_pokemon(enemy_pokemon, nickname)
#     # Load existing Pokémon data if it exists
#     if mypokemon_path.is_file():
#         with open(mypokemon_path, "r", encoding="utf-8") as json_file:
#             caught_pokemon_data = json.load(json_file)
#     else:
#         caught_pokemon_data = []

#     # Append the caught Pokémon's data to the list
#     caught_pokemon_data.append(caught_pokemon)

#     # Save the caught Pokémon's data to a JSON file
#     with open(str(mypokemon_path), "w") as json_file:
#         json.dump(caught_pokemon_data, json_file, indent=2)

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
        
def process_battle_data(battle_data: dict) -> str:
    """Convert raw battle instructions into human-readable format."""
    # Error handling and input validation
    

    if not isinstance(battle_data, dict) or 'battle_header' not in battle_data:
        error_msg = mw.translator.translate("invalid_battle_data")
        return f"Error: {error_msg}"
    
    try:
        # Extract battle header information
        header = battle_data['battle_header']
        user_name = format_pokemon_name(header['user']['name'])
        opponent_name = format_pokemon_name(header['opponent']['name'])
        user_move = format_move_name(header['user']['move'])
        opponent_move = format_move_name(header['opponent']['move'])
        
        # Initialize output with battle context
        output = [
            mw.translator.translate(
                "battle_header",
                user_name=user_name,
                user_level=header['user']['level'],
                opponent_name=opponent_name,
                opponent_level=header['opponent']['level']
            ),
            mw.translator.translate("user_move", user_name=user_name, move=user_move),
            mw.translator.translate("opponent_move", opponent_name=opponent_name, move=opponent_move),
            "\n=== " + mw.translator.translate("battle_effects") + " ==="
        ]

        # Helper functions for common patterns
        def format_stat(raw_stat: str) -> str:
            """Convert engine stat names to display names."""
            stat_map = {
                'atk': 'attack',
                'def': 'defense',
                'spa': 'special-attack',
                'spd': 'special-defense',
                'spe': 'speed',
                'accuracy': 'accuracy',
                'evasion': 'evasion'
            }
            return stat_map.get(raw_stat, raw_stat.replace('-', ' ').title())

        def get_pokemon_name(side: str) -> str:
            """Get formatted Pokémon name based on battle side."""
            return user_name if side == 'user' else opponent_name

        # Process each instruction
        for instr in battle_data.get('instructions', []):
            if not instr:
                continue

            action = instr[0]
            target_side = instr[1] if len(instr) > 1 else None
            pokemon_name = get_pokemon_name(target_side) if target_side else None

            try:
                if action == constants.MUTATOR_DAMAGE:
                    damage = instr[2]
                    output.append(mw.translator.translate(
                        "damage_taken",
                        pokemon_name=pokemon_name,
                        damage=damage
                    ))
                
                elif action == constants.MUTATOR_HEAL:
                    amount = instr[2]
                    output.append(mw.translator.translate(
                        "heal_effect",
                        pokemon_name=pokemon_name,
                        amount=amount
                    ))
                
                elif action == constants.MUTATOR_APPLY_STATUS:
                    status = format_move_name(instr[2])
                    output.append(mw.translator.translate(
                        "status_apply",
                        pokemon_name=pokemon_name,
                        status=status
                    ))
                
                elif action == constants.MUTATOR_BOOST:
                    stat = format_stat(instr[2])
                    amount = instr[3]
                    direction = mw.translator.translate("rose") if amount > 0 else mw.translator.translate("fell")
                    output.append(mw.translator.translate(
                        "stat_change",
                        pokemon_name=pokemon_name,
                        stat=stat,
                        direction=direction,
                        amount=abs(amount)
                    ))
                
                elif action == constants.MUTATOR_SIDE_START:
                    condition = format_move_name(instr[2])
                    side = mw.translator.translate("your_side") if target_side == 'user' else mw.translator.translate("opponent_side")
                    output.append(mw.translator.translate(
                        "side_effect",
                        side=side,
                        condition=condition
                    ))
                
                elif action == constants.MUTATOR_WEATHER_START:
                    weather = format_move_name(instr[1])
                    output.append(mw.translator.translate(
                        "weather_change",
                        weather=weather
                    ))
                              
                elif action == constants.MUTATOR_FAIL:
                    reason = instr[2] if len(instr) > 2 else "unknown"
                    output.append(mw.translator.translate(
                        "move_failed",
                        reason=reason
                    ))

                elif action == constants.MUTATOR_APPLY_VOLATILE_STATUS:
                    status = format_move_name(instr[2])
                    output.append(mw.translator.translate(
                        "volatile_status_apply",
                        pokemon_name=pokemon_name,
                        status=status.capitalize()
                    ))

                else:
                    output.append(f"Unhandled action: {action}")

            except Exception as e:
                logger.log("error", f"Error processing instruction {instr}: {str(e)}")
                continue

        # Add missed move information
        if battle_data.get('user_missed', False):
            output.append(mw.translator.translate("user_move_missed"))
        
        if battle_data.get('opponent_missed', False):
            output.append(mw.translator.translate("opponent_move_missed"))

        return "\n".join(output)

    except KeyError as e:
        error_msg = mw.translator.translate("missing_key_in_data", key=str(e))
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = mw.translator.translate("unexpected_error", error=str(e))
        return f"Error: {error_msg}"
            
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
    #name, id, level, ability, type, stats, enemy_attacks, base_experience, growth_rate, ev, iv, gender, battle_status, battle_stats, tier, ev_yield, shiny = generate_random_pokemon()
    name, id, level, ability, type, stats, enemy_attacks, base_experience, growth_rate, ev, iv, gender, battle_status, battle_stats, tier, ev_yield, shiny = generate_random_pokemon(main_pokemon.level, ankimon_tracker_obj)
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

# some of the functions that are being called within the on_review_card function are below
# for sake of tidiness ! 

def handle_enemy_faint(enemy_pokemon, collected_pokemon_ids, settings_obj):
    """
    Handles what automatically happens when the enemy Pokémon faints, based on auto-battle settings.
    """
    try:
        auto_battle_setting = int(settings_obj.get("battle.automatic_battle", 0))
        if not (0 <= auto_battle_setting <= 3):
            auto_battle_setting = 0  # fallback
    except ValueError:
        auto_battle_setting = 0  # fallback

    if auto_battle_setting == 3:  # Catch if uncollected
        enemy_id = enemy_pokemon.id
        # Check cache instead of file
        if enemy_id not in collected_pokemon_ids or enemy_pokemon.shiny:
            catch_pokemon(enemy_pokemon, ankimon_tracker_obj, logger, "", collected_pokemon_ids, achievements)
        else:
            kill_pokemon()
        new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon
    elif auto_battle_setting == 1:  # Existing auto-catch
        catch_pokemon(enemy_pokemon, ankimon_tracker_obj, logger, "", collected_pokemon_ids, achievements)
        new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon
    elif auto_battle_setting == 2:  # Existing auto-defeat
        kill_pokemon()
        new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon

    ankimon_tracker_obj.general_card_count_for_battle = 0

def handle_main_pokemon_faint(main_pokemon, enemy_pokemon, msg, translator, play_effect_sound, new_pokemon, tooltipWithColour):
    """
    Handles what happens when the main Pokémon faints.
    """
    msg += "\n " + translator.translate("pokemon_fainted", enemy_pokemon_name=main_pokemon.name.capitalize())
    play_effect_sound("Fainted")
    new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon
    main_pokemon.hp = main_pokemon.max_hp
    main_pokemon.current_hp = main_pokemon.max_hp
    main_pokemon.stat_stages = {'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'accuracy': 0, 'evasion': 0}
    tooltipWithColour(msg, "#E12939")

# Hook into Anki's card review event
def on_review_card(*args):
    try:
        battle_status = enemy_pokemon.battle_status
        multiplier = ankimon_tracker_obj.multiplier
        mainpokemon_type = main_pokemon.type
        mainpokemon_name = main_pokemon.name
        user_attack = random.choice(main_pokemon.attacks)
        enemy_attack = random.choice(enemy_pokemon.attacks)
        
        global mutator_full_reset

        global battle_sounds
        global achievements
        global new_state
        global user_hp_after
        global opponent_hp_after
        global dmg_from_enemy_move
        global dmg_from_user_move
        
        # Increment the counter when a card is reviewed
        attack_counter = ankimon_tracker_obj.attack_counter
        ankimon_tracker_obj.cards_battle_round += 1
        ankimon_tracker_obj.cry_counter += 1
        cry_counter = ankimon_tracker_obj.cry_counter
        card_counter = ankimon_tracker_obj.card_counter
        reviewer_obj.seconds = 0
        reviewer_obj.myseconds = 0
        ankimon_tracker_obj.general_card_count_for_battle += 1

        achievements = handle_achievements(card_counter, achievements)
        achievements = check_and_award_badges(card_counter, achievements, ankimon_tracker_obj, test_window)

        try:
             mutator_full_reset
        except:
            mutator_full_reset = 1

        if battle_sounds == True and ankimon_tracker_obj.general_card_count_for_battle == 1:
            play_sound()

        if ankimon_tracker_obj.cards_battle_round >= int(settings_obj.get("battle.cards_per_round", 2)):
            ankimon_tracker_obj.cards_battle_round = 0
            ankimon_tracker_obj.attack_counter = 0
            slp_counter = 0
            ankimon_tracker_obj.pokemon_encouter += 1
            multiplier = int(ankimon_tracker_obj.multiplier)

            user_attack = random.choice(main_pokemon.attacks)

            if ankimon_tracker_obj.pokemon_encouter > 0 and enemy_pokemon.hp > 0 and dmg_in_reviewer is True and multiplier < 1:               
               
                enemy_attack = random.choice(enemy_pokemon.attacks) # triggered IF enemy will attack                                  
                enemy_move = find_details_move(enemy_attack)
                enemy_move_category = enemy_move.get("category")
             
                if enemy_move_category == "Status":
                    color = "#F7DC6F"
                elif enemy_move_category == "Physical":
                    color = "#F0B27A"
                elif enemy_move_category == "Special":
                    color = "#D2B4DE"

            else:
                enemy_attack = "splash" # if enemy will NOT attack, it uses SPLASH
            
            try:
                enemy_move
            except:
                enemy_move = find_details_move(enemy_attack)
                enemy_move_category = enemy_move.get("category")

            move = find_details_move(user_attack)
            category = move.get("category")
            
            if ankimon_tracker_obj.pokemon_encouter > 0 and main_pokemon.hp > 0 and enemy_pokemon.hp > 0:
                
                if settings_obj.get("controls.allow_to_choose_moves", False) == True:
                    dialog = MoveSelectionDialog(main_pokemon.attacks)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        if dialog.selected_move:
                            user_attack = dialog.selected_move    
                            
                if category == "Status":
                    color = "#F7DC6F"

                if category == "Physical":
                    color = "#F0B27A"

                elif category == "Special":
                    color = "#D2B4DE"

            msg = ""
            # msg += f"{multiplier}x {translator.translate('multiplier')}"
            # DISABLED for now - multiplier has to be implemented properly into new system
            #failed card = enemy attack

            try:
                new_state
                mutator_full_reset

                user_hp_after
                opponent_hp_after
                dmg_from_enemy_move
                dmg_from_user_move
            except:
                new_state = []
                mutator_full_reset = 1
                user_hp_after = 0 
                opponent_hp_after = 0 
                dmg_from_enemy_move = 0 
                dmg_from_user_move = 0

            '''
            To the devs, 
            below is the MOST IMPORTANT function for the new engine.
            This runs our current Pokemon stats through the SirSkaro Poke-Engine.
            The "results" can then be used to access battle outcomes.
            '''

            #results = simulate_battle_with_poke_engine(main_pokemon, enemy_pokemon, user_attack, enemy_attack, new_state, mutator_full_reset)
            results = simulate_battle_with_poke_engine(
                main_pokemon,
                enemy_pokemon,
                user_attack,
                enemy_attack,
                new_state,
                mutator_full_reset,
                )
          
            '''
            It is important that any changes to pokemon stats are accurately represented
            in the main_pokemon and enemy_pokemon objects, in order to let them
            be arguments in the engine function.

            Next, we need an unpacker to ensure that it goes from tuple values under results, to actual variables!
            '''
            battle_info = results[0]
            new_state = copy.deepcopy(results[1])
            dmg_from_enemy_move = results[2]
            dmg_from_user_move = results[3]
            user_hp_after = new_state.user.active.hp
            opponent_hp_after = new_state.opponent.active.hp
            mutator_full_reset = results[4]

            # Unpacked and ready to go ! This info gives us pretty much ANYTHING we need to know about the battle (other than detailed logging)            

            process_battle_data(battle_info)

            # For the variables below, calculating early > individually calling multiple times later

            # Handling enemy attack on main pokemon, when multiplier < 1
            if ankimon_tracker_obj.pokemon_encouter > 0 and enemy_pokemon.hp > 0 and dmg_in_reviewer is True and multiplier < 1:               
                
                main_pokemon.hp = user_hp_after
                main_pokemon.current_hp = user_hp_after

                try:
                    msg += translator.translate("pokemon_chose_attack", pokemon_name=enemy_pokemon.name.capitalize(), pokemon_attack=enemy_attack.capitalize())

                    if dmg_from_enemy_move > 0:
                        reviewer_obj.myseconds = settings_obj.compute_special_variable("animate_time")
                        msg += translator.translate("dmg_dealt", dmg=dmg_from_enemy_move, pokemon_name=main_pokemon.name.capitalize())
                        msg += "\n"
                        if multiplier < 1:
                            play_effect_sound("HurtNormal")
                        else:
                            reviewer_obj.myseconds = 0
                                                             
                    '''elif dmg_from_enemy_move == 0:
                        if results.get('opponent_missed', False):
                            msg += "\n" + translator.translate("move_has_missed")'''
                    
                except Exception as e:
                    showWarning(f"Error rendering enemy attack: {str(e)}")

            # if enemy pokemon hp > 0, attack enemy pokemon
            if ankimon_tracker_obj.pokemon_encouter > 0 and main_pokemon.hp > 0 and enemy_pokemon.hp > 0:
                
                enemy_pokemon.hp = opponent_hp_after
                enemy_pokemon.current_hp = opponent_hp_after
                                
                msg += translator.translate("pokemon_chose_attack", pokemon_name=main_pokemon.name.capitalize(), pokemon_attack=user_attack.capitalize())
                
                if battle_status != "fighting": # dealing with SPECIAL EFFECTS on Pokemon
                    msg, acc, battle_status, enemy_pokemon.stats = status_effect(enemy_pokemon, move, slp_counter, msg, acc)
               
                else:
                    if category == "Status":
                        msg = effect_status_moves(user_attack, main_pokemon.stats, enemy_pokemon.stats, msg, enemy_pokemon.name, main_pokemon.name)                        

                        '''if dmg_from_user_move == 0:
                            if results.get('user_missed', False):
                                msg += "\n" + translator.translate("move_has_missed")'''
                            
                    else:
                        msg += translator.translate("dmg_dealt", dmg=dmg_from_user_move, pokemon_name=enemy_pokemon.name.capitalize())

                        if enemy_pokemon.hp < 0:
                            enemy_pokemon.hp = 0
                            msg += translator.translate("pokemon_fainted", enemy_pokemon_name=enemy_pokemon.name.capitalize())
                            
                    tooltipWithColour(msg, color)
                    
                    if dmg_from_user_move > 0:
                        reviewer_obj.seconds = int(settings_obj.compute_special_variable("animate_time"))
                        if multiplier == 1:
                            play_effect_sound("HurtNormal")
                        elif multiplier < 1:
                            play_effect_sound("HurtNotEffective")
                        elif multiplier > 1:
                            play_effect_sound("HurtSuper")
                    else:
                        reviewer_obj.seconds = 0

            # if enemy pokemon faints, this handles AUTOMATIC BATTLE
            if enemy_pokemon.hp < 1:
                enemy_pokemon.hp = 0
                handle_enemy_faint(enemy_pokemon, collected_pokemon_ids, settings_obj)

                mutator_full_reset = 2 # reset opponent state

        if cry_counter == 10 and battle_sounds is True:
            cry_counter = 0
            play_sound()

        # user pokemon faints
        if main_pokemon.hp < 1:
            handle_main_pokemon_faint(main_pokemon, enemy_pokemon, msg, translator, play_effect_sound, new_pokemon, tooltipWithColour)
            mutator_full_reset = 1 # fully reset battle state 

        class Container(object):
            pass

        reviewer = Container()
        reviewer.web = mw.reviewer.web
        reviewer_obj.update_life_bar(reviewer, 0, 0)
        if test_window is not None:
            test_window.display_battle()
    except Exception as e:
        showWarning(f"An error occurred in reviewer: {str(e)}")
        traceback.print_exc()

# Connect the hook to Anki's review event
gui_hooks.reviewer_did_answer_card.append(on_review_card)

life_bar_injected = False
video = False
first_start = False

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

achievements = check_badges(achievements)

if database_complete:
    if mypokemon_path.is_file() is False:
        starter_window.display_starter_pokemon()
    else:
        with open(mypokemon_path, "r", encoding="utf-8") as file:
            pokemon_list = json.load(file)
            if not pokemon_list :
                starter_window.display_starter_pokemon()

count_items_and_rewrite(itembag_path)

UserRole = 1000  # Define custom role

#buttonlayout

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
    settings_obj,
    addon_dir,          
    data_handler_obj    
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
        catch_pokemon(enemy_pokemon, ankimon_tracker_obj, logger, "", collected_pokemon_ids, achievements)
        new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon
    for hook in catch_pokemon_hooks:
        hook()

# Custom function that triggers the defeat_pokemon hook
def DefeatPokemonHook():
    if enemy_pokemon.hp < 1:
        kill_pokemon()
        new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon
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
    if enemy_pokemon.hp >= 1:
        tooltip("You only catch a pokemon once it's fainted !")
    else:
        catch_pokemon(enemy_pokemon, ankimon_tracker_obj, logger, "", collected_pokemon_ids, achievements)
        new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon

def defeat_shortcut_function():
    if enemy_pokemon.hp > 1:
        tooltip("Wild pokemon has to be fainted to defeat it !")
    else:
        kill_pokemon()
        new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon

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
