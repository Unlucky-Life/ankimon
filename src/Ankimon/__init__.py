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

try:
    from .debug_console import show_ankimon_dev_console
except ModuleNotFoundError:
    # Debug console should not be available to non devs, so it's fine if this import doesn't succeed
    pass

import json
import random
import copy
from pathlib import Path
import traceback

import aqt
from anki.hooks import addHook, wrap
from aqt import gui_hooks, mw, utils
from aqt.qt import QDialog
from aqt.reviewer import Reviewer
from aqt.utils import downArrow, showWarning, tr, tooltip
from PyQt6.QtWidgets import QDialog
from aqt.gui_hooks import webview_will_set_content
from aqt.webview import WebContent

from .resources import generate_startup_files, user_path, IS_EXPERIMENTAL_BUILD, addon_ver

generate_startup_files(user_path)

from .config_var import (
    dmg_in_reviewer,
    no_more_news,
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
)
from .menu_buttons import create_menu_actions
from .hooks import setupHooks
from .texts import _bottomHTML_template, button_style
from .business import (
    get_multiplier_stats,
)
from .utils import (
    check_folders_exist,
    safe_get_random_move,
    test_online_connectivity,
    read_local_file,
    read_github_file,
    compare_files,
    write_local_file,
    count_items_and_rewrite,
    format_pokemon_name,
    format_move_name,
    play_effect_sound,
    get_main_pokemon_data,
    play_sound,
    load_collected_pokemon_ids,
)
from .functions.reviewer_iframe import create_iframe_html, create_head_code
from .functions.url_functions import open_team_builder, rate_addon_url, report_bug, join_discord_url, open_leaderboard_url
from .functions.badges_functions import check_badges, handle_achievements, check_and_award_badges
from .functions.pokemon_showdown_functions import export_to_pkmn_showdown, export_all_pkmn_showdown, flex_pokemon_collection
from .functions.drawing_utils import tooltipWithColour
from .functions.discord_function import DiscordPresence
from .functions.rate_addon_functions import rate_this_addon
from .functions.encounter_functions import (
    generate_random_pokemon,
    new_pokemon,
    catch_pokemon,
    kill_pokemon,
    handle_enemy_faint,
    handle_main_pokemon_faint
)
from .functions.pokedex_functions import find_details_move
from .gui_entities import UpdateNotificationWindow, CheckFiles
from .pyobj.help_window import HelpWindow
from .pyobj.sync_pokemon_data import CheckPokemonData
from .pyobj.backup_files import run_backup
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
    achievements,
    pokemon_pc
)

from .pyobj.error_handler import show_warning_with_traceback
from .functions.drawing_utils import draw_gender_symbols, draw_stat_boosts

# Load move and pokemon name mapping at startup
with open(pokemon_names_file_path, "r", encoding="utf-8") as f:
    POKEMON_NAME_LOOKUP = json.load(f)

with open(move_names_file_path, "r", encoding="utf-8") as f:
    MOVE_NAME_LOOKUP = json.load(f)

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
except Exception as e:
    show_warning_with_traceback(parent=mw, exception=e, message="Backup error:")

# Initialize mutator and mutator_full_reset
global new_state
global mutator_full_reset 
global user_hp_after 
global opponent_hp_after 
global dmg_from_enemy_move 
global dmg_from_user_move

# Initialize collected IDs cache
# Call this during addon initialization
collected_pokemon_ids = set()
_collection_loaded = False
if not _collection_loaded: # If the collection hasn't already been loaded
    collected_pokemon_ids = load_collected_pokemon_ids()
    _collection_loaded = True

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
        
        if IS_EXPERIMENTAL_BUILD == True:
            github_url = "https://raw.githubusercontent.com/h0tp-ftw/ankimon/refs/heads/main/assets/changelogs/{addon_ver}.md"
        
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
        show_warning_with_traceback(parent=mw, exception=e, message="Error connecting to GitHub:")

def open_help_window(online_connectivity):
    try:
        # TODO: online_connectivity must be a function?
        # TODO: HelpWindow constructor must be empty?
        help_dialog = HelpWindow(online_connectivity)
        help_dialog.exec()
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message="Error in opening Help Guide:")

gen_config = []
for i in range(1,10):
    gen_config.append(config[f"misc.gen{i}"])

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
                show_warning_with_traceback(parent=mw, exception=e, message="Error processing instruction:")
                continue

        # Add missed move information
        if battle_data.get('user_missed', False):
            output.append(mw.translator.translate("user_move_missed"))
        
        if battle_data.get('opponent_missed', False):
            output.append(mw.translator.translate("opponent_move_missed"))

        return "\n".join(output)

    except KeyError as e:
        show_warning_with_traceback(parent=mw, exception=e, message="Missing key in data:")
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message="Unexpected error:")
            
#get main pokemon details:
if database_complete:
    try:
        mainpokemon_name, mainpokemon_id, mainpokemon_ability, mainpokemon_type, mainpokemon_stats, mainpokemon_attacks, mainpokemon_level, mainpokemon_base_experience, mainpokemon_xp, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate, mainpokemon_ev, mainpokemon_iv, mainpokemon_evolutions, mainpokemon_battle_stats, mainpokemon_gender, mainpokemon_nickname = get_main_pokemon_data()
        starter = True
    except Exception:
        starter = False
        mainpokemon_level = 5
    #name, id, level, ability, type, stats, enemy_attacks, base_experience, growth_rate, ev, iv, gender, battle_status, battle_stats, tier, ev_yield, shiny = generate_random_pokemon()
    name, id, level, ability, type, base_stats, enemy_attacks, base_experience, growth_rate, ev, iv, gender, battle_status, battle_stats, tier, ev_yield, shiny = generate_random_pokemon(main_pokemon.level, ankimon_tracker_obj)
    pokemon_data = {
        'name': name,
        'id': id,
        'level': level,
        'ability': ability,
        'type': type,
        'base_stats': base_stats,
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
            play_sound(enemy_pokemon.id, settings_obj)

        if ankimon_tracker_obj.cards_battle_round >= int(settings_obj.get("battle.cards_per_round", 2)):
            ankimon_tracker_obj.cards_battle_round = 0
            ankimon_tracker_obj.attack_counter = 0
            slp_counter = 0
            ankimon_tracker_obj.pokemon_encouter += 1
            multiplier = int(ankimon_tracker_obj.multiplier)

            if ankimon_tracker_obj.pokemon_encouter > 0 and enemy_pokemon.hp > 0 and dmg_in_reviewer is True and multiplier < 1:               
                enemy_move = safe_get_random_move(enemy_pokemon.attacks, logger=logger)
                enemy_move_category = enemy_move.get("category")
             
                if enemy_move_category == "Status":
                    color = "#F7DC6F"
                elif enemy_move_category == "Physical":
                    color = "#F0B27A"
                elif enemy_move_category == "Special":
                    color = "#D2B4DE"

            else:
                enemy_attack = "splash" # if enemy will NOT attack, it uses SPLASH

            move = safe_get_random_move(main_pokemon.attacks, logger=logger)
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
                new_state = None
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

            results = simulate_battle_with_poke_engine(
                main_pokemon,
                enemy_pokemon,
                user_attack,
                enemy_attack,
                mutator_full_reset,
                new_state,
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
                        tooltipWithColour(f" -{dmg_from_enemy_move} HP ", "#F06060", x=-200)
                        if multiplier < 1:
                            play_effect_sound("HurtNormal")
                        else:
                            reviewer_obj.myseconds = 0
                                                             
                    '''elif dmg_from_enemy_move == 0:
                        if results.get('opponent_missed', False):
                            msg += "\n" + translator.translate("move_has_missed")'''
                    
                except Exception as e:
                    show_warning_with_traceback(parent=mw, exception=e, message="Error rendering enemy attack:")

            # if enemy pokemon hp > 0, attack enemy pokemon
            if ankimon_tracker_obj.pokemon_encouter > 0 and main_pokemon.hp > 0 and enemy_pokemon.hp > 0:
                
                enemy_pokemon.hp = opponent_hp_after
                enemy_pokemon.current_hp = opponent_hp_after
                                
                msg += translator.translate("pokemon_chose_attack", pokemon_name=main_pokemon.name.capitalize(), pokemon_attack=user_attack.capitalize())
                
                if battle_status != "fighting": # dealing with SPECIAL EFFECTS on Pokemon
                    pass
               
                else:
                    if category == "Status":
                        pass

                        '''if dmg_from_user_move == 0:
                            if results.get('user_missed', False):
                                msg += "\n" + translator.translate("move_has_missed")'''
                            
                    else:
                        msg += translator.translate("dmg_dealt", dmg=dmg_from_user_move, pokemon_name=enemy_pokemon.name.capitalize())

                        if enemy_pokemon.hp < 1:
                            enemy_pokemon.hp = 0
                            msg += translator.translate("pokemon_fainted", enemy_pokemon_name=enemy_pokemon.name.capitalize())
                            
                    tooltipWithColour(msg, color)
                    
                    if dmg_from_user_move > 0:
                        reviewer_obj.seconds = int(settings_obj.compute_special_variable("animate_time"))
                        tooltipWithColour(f" -{dmg_from_user_move} HP ", "#F06060", x=200)
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
                handle_enemy_faint(
                    main_pokemon,
                    enemy_pokemon,
                    collected_pokemon_ids,
                    test_window,
                    evo_window,
                    reviewer_obj,
                    logger,
                    achievements
                    )

                mutator_full_reset = 2 # reset opponent state

        if cry_counter == 10 and battle_sounds is True:
            cry_counter = 0
            play_sound(enemy_pokemon.id, settings_obj)

        # user pokemon faints
        if main_pokemon.hp < 1:
            handle_main_pokemon_faint(main_pokemon, enemy_pokemon, test_window, reviewer_obj, translator)
            mutator_full_reset = 1 # fully reset battle state 

        class Container(object):
            pass

        reviewer = Container()
        reviewer.web = mw.reviewer.web
        reviewer_obj.update_life_bar(reviewer, 0, 0)
        if test_window is not None:
            test_window.display_battle()
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message="An error occurred in reviewer:")

# Connect the hook to Anki's review event
gui_hooks.reviewer_did_answer_card.append(on_review_card)

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

#buttonlayout
# Create menu actions
# Create menu actions
create_menu_actions(
    database_complete,
    online_connectivity,
    None,#pokecollection_win,
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
    data_handler_obj,
    pokemon_pc,
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
        kill_pokemon(main_pokemon, enemy_pokemon, evo_window, logger , achievements, trainer_card)
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
        kill_pokemon(main_pokemon, enemy_pokemon, evo_window, logger , achievements, trainer_card)
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
