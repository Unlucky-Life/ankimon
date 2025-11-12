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

import aqt
from anki.hooks import addHook, wrap
from aqt import gui_hooks, mw, utils
from aqt.qt import QDialog
from aqt.operations import QueryOp
from aqt.reviewer import Reviewer
from aqt.utils import downArrow, showWarning, tr, tooltip
from PyQt6.QtWidgets import QDialog
from aqt.gui_hooks import webview_will_set_content
from aqt.webview import WebContent
import markdown

from .resources import generate_startup_files, user_path, IS_EXPERIMENTAL_BUILD, addon_ver, addon_dir
generate_startup_files(addon_dir, user_path)

from .singletons import settings_obj
no_more_news = settings_obj.get("misc.YouShallNotPass_Ankimon_News")
ssh = settings_obj.get("misc.ssh")
defeat_shortcut = settings_obj.get("controls.defeat_key") #default: 5; ; Else if not 5 => controll + Key for capture
catch_shortcut = settings_obj.get("controls.catch_key") #default: 6; Else if not 6 => controll + Key for capture
reviewer_buttons = settings_obj.get("controls.pokemon_buttons") #default: true; false = no pokemon buttons in reviewer

from .resources import (
    addon_dir,
    pkmnimgfolder,
    mypokemon_path,
    itembag_path,
    badgebag_path,
    sound_list_path,
    badges_list_path,
)
from .menu_buttons import create_menu_actions
from .hooks import setupHooks
from .texts import _bottomHTML_template, button_style
from .utils import (
    check_folders_exist,
    safe_get_random_move,
    test_online_connectivity,
    read_local_file,
    read_github_file,
    compare_files,
    write_local_file,
    count_items_and_rewrite,
    play_effect_sound,
    get_main_pokemon_data,
    play_sound,
    load_collected_pokemon_ids,
)
from .functions.url_functions import open_team_builder, rate_addon_url, report_bug, join_discord_url, open_leaderboard_url
from .functions.badges_functions import handle_review_count_achievement, check_for_badge, receive_badge
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
from .gui_entities import UpdateNotificationWindow, CheckFiles
from .pyobj.download_sprites import show_agreement_and_download_dialog
from .pyobj.help_window import HelpWindow
from .pyobj.backup_files import run_backup
from .pyobj.backup_manager import BackupManager
from .pyobj.ankimon_sync import setup_ankimon_sync_hooks, check_and_sync_pokemon_data
from .pyobj.tip_of_the_day import show_tip_of_the_day
from .classes.choose_move_dialog import MoveSelectionDialog
from .poke_engine.ankimon_hooks_to_poke_engine import simulate_battle_with_poke_engine
from .singletons import (
    reviewer_obj,
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
    eff_chart,
    gen_id_chart,
    license,
    credits,
    evo_window,
    starter_window,
    item_window,
    version_dialog,
    achievements,
    pokemon_pc
)

from .pyobj.pokemon_trade import check_and_award_monthly_pokemon

from .functions.battle_functions import (
    update_pokemon_battle_status,
    validate_pokemon_status,
    process_battle_data,
)

from .pyobj.error_handler import show_warning_with_traceback

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

backup_manager = BackupManager(logger, settings_obj)

if settings_obj.get("misc.developer_mode"):
    backup_manager.create_backup(manual=False)

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



with open(sound_list_path, "r", encoding="utf-8") as json_file:
    sound_list = json.load(json_file)

ankimon_tracker_obj.pokemon_encouter = 0

"""
get web exports ready for special reviewer look
"""


# Set up web exports for static files
mw.addonManager.setWebExports(__name__, r"user_files/.*\.(css|js|jpg|gif|html|ttf|png|mp3)")

def on_webview_will_set_content(web_content: WebContent, context) -> None:
    if not isinstance(context, aqt.reviewer.Reviewer):
        return
    ankimon_package = mw.addonManager.addonFromModule(__name__)
    web_content.js.append(f"/_addons/{ankimon_package}/user_files/web/ankimon_hud_portal.js")



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
    show_agreement_and_download_dialog(force_download=True)
    dialog = CheckFiles()
    dialog.show()

sync_dialog = None

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

def on_reviewer_did_show_question(card):
    reviewer_obj.update_life_bar(mw.reviewer, None, None)

gui_hooks.reviewer_did_show_question.append(on_show_question)
gui_hooks.reviewer_did_show_answer.append(on_show_answer)
gui_hooks.reviewer_did_show_question.append(on_reviewer_did_show_question)

setupHooks(None, ankimon_tracker_obj)

online_connectivity = test_online_connectivity()

#Connect to GitHub and Check for Notification and HelpGuideChanges
update_infos_md = addon_dir / "updateinfos.md"
def download_changelog():
    try:
        # URL of the file on GitHub
        github_url = f"https://raw.githubusercontent.com/h0tp-ftw/ankimon/refs/heads/main/assets/changelogs/{addon_ver}.md"
    
        # Read content from GitHub
        github_content = read_github_file(github_url)
    
        # If changelog content is None, try unknown.md as a fallback for all builds
        if github_content is None:
            github_url = "https://raw.githubusercontent.com/h0tp-ftw/ankimon/refs/heads/main/assets/changelogs/unknown.md"
            github_content = read_github_file(github_url)

        return github_content
    except Exception as e:
        return e

if online_connectivity and ssh:
    def done(result: Exception | str | None):
        if isinstance(result, Exception):
            show_warning_with_traceback(parent=mw, exception=result, message="Error connecting to GitHub:")
            return
        if result is None:
            showWarning("Failed to retrieve Ankimon content from GitHub.")
            return
        # Read content from the local file
        local_content = read_local_file(update_infos_md)
        # If local content is not the same as the GitHub content, open dialog
        if not compare_files(local_content, result):
            write_local_file(update_infos_md, result)
            dialog = UpdateNotificationWindow(markdown.markdown(result))
            if not no_more_news:
                dialog.exec()
    op = QueryOp(
        parent=mw,
        op=lambda _col: download_changelog(), # Background operation
        success=done, # Ran on UI thread
    ).without_collection().run_in_background()

def open_help_window(online_connectivity):
    try:
        # TODO: online_connectivity must be a function?
        # TODO: HelpWindow constructor must be empty?
        help_dialog = HelpWindow(online_connectivity)
        help_dialog.exec()
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message="Error in opening Help Guide:")

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

# How many cards need to be done before receiving an item
item_receive_value = random.randint(3, 385)

# Hook into Anki's card review event
def on_review_card(*args):
    try:
        multiplier = ankimon_tracker_obj.multiplier
        mainpokemon_type = main_pokemon.type
        mainpokemon_name = main_pokemon.name
        if main_pokemon.attacks:
            user_attack = random.choice(main_pokemon.attacks)
        else:
            user_attack = "splash"
        if enemy_pokemon.attacks:
            enemy_attack = random.choice(enemy_pokemon.attacks)
        else:
            enemy_attack = "splash"

        global mutator_full_reset

        battle_sounds = settings_obj.get("audio.battle_sounds")
        global achievements
        global new_state
        global user_hp_after
        global opponent_hp_after
        global dmg_from_enemy_move
        global dmg_from_user_move

        global item_receive_value

        # Increment the counter when a card is reviewed
        attack_counter = ankimon_tracker_obj.attack_counter
        ankimon_tracker_obj.cards_battle_round += 1
        ankimon_tracker_obj.cry_counter += 1
        cry_counter = ankimon_tracker_obj.cry_counter
        total_reviews = ankimon_tracker_obj.total_reviews
        reviewer_obj.seconds = 0
        reviewer_obj.myseconds = 0
        ankimon_tracker_obj.general_card_count_for_battle += 1
                
        color = "#F0B27A" # Initialize with a default color

        # Handle achievements based on total reviews
        achievements = handle_review_count_achievement(total_reviews, achievements)

        item_receive_value -= 1
        if item_receive_value <= 0:
            item_receive_value = random.randint(3, 385)

            test_window.display_item()

            # Give them a badge for getting an item
            if not check_for_badge(achievements,6):
                receive_badge(6, achievements)

        if total_reviews == 10:
            settings_obj.set("trainer.cash", settings_obj.get("trainer.cash") + 200)
            trainer_card.cash = settings_obj.get("trainer.cash")

        try:
             mutator_full_reset
        except:
            mutator_full_reset = 1

        if battle_sounds == True and ankimon_tracker_obj.general_card_count_for_battle == 1:
            play_sound(enemy_pokemon.id, settings_obj)

        if ankimon_tracker_obj.cards_battle_round >= int(settings_obj.get("battle.cards_per_round")):
            ankimon_tracker_obj.cards_battle_round = 0
            ankimon_tracker_obj.attack_counter = 0
            slp_counter = 0
            ankimon_tracker_obj.pokemon_encouter += 1
            multiplier = int(ankimon_tracker_obj.multiplier)

            if ankimon_tracker_obj.pokemon_encouter > 0 and enemy_pokemon.hp > 0 and multiplier < 1:
                enemy_move = safe_get_random_move(enemy_pokemon.attacks, logger=logger)
                enemy_move_category = enemy_move.get("category")

                if enemy_move_category == "Status":
                    color = "#F7DC6F"
                elif enemy_move_category == "Special":
                    color = "#D2B4DE"
                else:
                    color = "#F0B27A"

            else:
                enemy_attack = "splash" # if enemy will NOT attack, it uses SPLASH

            move = safe_get_random_move(main_pokemon.attacks, logger=logger)
            category = move.get("category")

            if ankimon_tracker_obj.pokemon_encouter > 0 and main_pokemon.hp > 0 and enemy_pokemon.hp > 0:

                if settings_obj.get("controls.allow_to_choose_moves") == True:
                    dialog = MoveSelectionDialog(main_pokemon.attacks)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        if dialog.selected_move:
                            user_attack = dialog.selected_move

                if category == "Status":
                    color = "#F7DC6F"

                elif category == "Special":
                    color = "#D2B4DE"

                else:
                    color = "#F0B27A"

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

            # 2. Unpack results from the simulation
            battle_info = results[0]
            new_state = copy.deepcopy(results[1])
            dmg_from_enemy_move = results[2]  # NOTE : This is ACTUALLY the sum of all damages and heals that occured to the user during the turn
            dmg_from_user_move = results[3]
            mutator_full_reset = results[4]
            current_battle_info_changes = results[5]
            instructions = results[0]["instructions"]
            heals_to_user = sum([inst[2] for inst in instructions if inst[0:2] == ['heal', 'user']])
            heals_to_opponent = sum([inst[2] for inst in instructions if inst[0:2] == ['heal', 'opponent']])
            true_dmg_from_enemy_move = sum([inst[2] for inst in instructions if inst[0:2] == ['damage', 'user']])
            true_dmg_from_user_move = sum([inst[2] for inst in instructions if inst[0:2] == ['damage', 'opponent']])

            # workaround for the DAMAGE being negative in some cases
            if true_dmg_from_enemy_move < 0:
                true_dmg_from_enemy_move = 0
                heals_to_user += abs(true_dmg_from_enemy_move)  # Add the negative damage as a heal
            if true_dmg_from_user_move < 0:
                true_dmg_from_user_move = 0
                heals_to_opponent += abs(true_dmg_from_user_move)

            # 3. --- IMMEDIATE STATE SYNCHRONIZATION (THE FIX) ---
            # Update Pokémon objects with the new state from the engine BEFORE any other processing.
            # This ensures all subsequent functions have the correct HP and status.
            main_pokemon.hp = new_state.user.active.hp
            main_pokemon.current_hp = new_state.user.active.hp
            enemy_pokemon.hp = new_state.opponent.active.hp
            enemy_pokemon.current_hp = new_state.opponent.active.hp

            # Update statuses based on instructions, now that HP is correct.
            enemy_status_changed, main_status_changed = update_pokemon_battle_status(
                battle_info, enemy_pokemon, main_pokemon
            )

            # Final validation to ensure consistency
            enemy_pokemon.battle_status = validate_pokemon_status(enemy_pokemon)
            main_pokemon.battle_status = validate_pokemon_status(main_pokemon)

            # 4. Generate the battle log message using the now-correct Pokémon states
            formatted_battle_log = process_battle_data(
                battle_info=battle_info,
                multiplier=multiplier,
                main_pokemon=main_pokemon,
                enemy_pokemon=enemy_pokemon,
                user_attack=user_attack,
                enemy_attack=enemy_attack,
                dmg_from_user_move=true_dmg_from_user_move,
                dmg_from_enemy_move=true_dmg_from_enemy_move,
                user_hp_after=main_pokemon.hp, # Use the already updated HP
                opponent_hp_after=enemy_pokemon.hp, # Use the already updated HP
                battle_status=main_pokemon.battle_status,
                pokemon_encounter=ankimon_tracker_obj.pokemon_encouter,
                translator=translator,
                changes=current_battle_info_changes
            )

            # Display the complete message
            tooltipWithColour(formatted_battle_log, color)

            # Handle sound effects and animations (existing code)
            if true_dmg_from_enemy_move > 0 and multiplier < 1:
                reviewer_obj.myseconds = settings_obj.compute_special_variable("animate_time")
                tooltipWithColour(f" -{true_dmg_from_enemy_move} HP ", "#F06060", x=-200)
                play_effect_sound(settings_obj, "HurtNormal")

            if true_dmg_from_user_move > 0:
                reviewer_obj.seconds = settings_obj.compute_special_variable("animate_time")
                tooltipWithColour(f" -{true_dmg_from_user_move} HP ", "#F06060", x=200)
                if multiplier == 1:
                    play_effect_sound(settings_obj, "HurtNormal")
                elif multiplier < 1:
                    play_effect_sound(settings_obj, "HurtNotEffective")
                elif multiplier > 1:
                    play_effect_sound(settings_obj, "HurtSuper")
            else:
                reviewer_obj.seconds = 0

            if int(heals_to_user) != 0:
                # "Negative heal" can happen sometimes. That's how the Life Orb item deals its damage for instance
                heal_color = "#68FA94" if heals_to_user > 0 else "#F06060"
                sign = "+" if heals_to_user > 0 else ""
                tooltipWithColour(f" {sign}{int(heals_to_user)} HP ", heal_color, x=-250)

            if int(heals_to_opponent) != 0:
                # "Negative heal" can happen sometimes. That's how the Life Orb item deals its damage for instance
                heal_color = "#68FA94" if heals_to_opponent > 0 else "#F06060"
                sign = "+" if heals_to_opponent > 0 else ""
                tooltipWithColour(f" {sign}{int(heals_to_opponent)} HP ", heal_color, x=250)

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

                mutator_full_reset = 1 # reset opponent state

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
            if enemy_pokemon.hp > 0:
                test_window.display_battle()
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message="An error occurred in reviewer:")

# Connect the hook to Anki's review event
gui_hooks.reviewer_did_answer_card.append(on_review_card)

if database_complete:
    with open(badgebag_path, "r", encoding="utf-8") as json_file:
        badge_list = json.load(json_file)
        if len(badge_list) > 1: # has atleast one badge
            rate_this_addon()

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
    settings_obj.get("controls.key_for_opening_closing_ankimon"),
    join_discord_url,
    open_leaderboard_url,
    settings_obj,
    addon_dir,
    data_handler_obj,
    pokemon_pc,
    backup_manager,
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

def on_profile_did_open():
    """Initialize services after profile is loaded."""
    # Show tip of the day
    try:
        show_tip_of_the_day()
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message="Error showing tip of the day:")

    # Award monthly pokemon if applicable
    try:
        if online_connectivity:
            check_and_award_monthly_pokemon(logger)
        else:
            logger.log("info", "Skipping monthly pokemon check due to no internet connectivity.")
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message="Error awarding monthly pokemon:")

    # AnkiWeb Sync
    try:
        ankiweb_sync = settings_obj.get("misc.ankiweb_sync")
        if not ankiweb_sync:
            logger.log("info", "AnkiWeb sync is disabled in settings - skipping sync system initialization")
            return

        # Set up sync hooks now that profile is available
        setup_ankimon_sync_hooks(settings_obj, logger)

        if not online_connectivity:
            logger.log("info", "No connection - AnkiWeb sync is disabled for this session")
        else: #if enabled and internet is available
            # Check for sync conflicts and show dialog if needed
            global sync_dialog
            sync_dialog = check_and_sync_pokemon_data(settings_obj, logger)
            logger.log("info", "Ankimon sync system initialized successfully")
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message="Error setting up sync system:")

# Hook to expose the function
def on_profile_loaded():
    mw.defeatpokemon = DefeatPokemonHook
    mw.catchpokemon = CatchPokemonHook
    mw.add_catch_pokemon_hook = add_catch_pokemon_hook
    mw.add_defeat_pokemon_hook = add_defeat_pokemon_hook

# Add hook to run on profile load
addHook("profileLoaded", on_profile_loaded)

gui_hooks.profile_did_open.append(on_profile_did_open)
gui_hooks.profile_will_close.append(backup_manager.on_anki_close)

def catch_shortcut_function():
    if enemy_pokemon.hp < 1:
        catch_pokemon(enemy_pokemon, ankimon_tracker_obj, logger, "", collected_pokemon_ids, achievements)
        new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon
    else:
        tooltip("You only catch a pokemon once it's fainted!")

def defeat_shortcut_function():
    if enemy_pokemon.hp < 1:
        kill_pokemon(main_pokemon, enemy_pokemon, evo_window, logger , achievements, trainer_card)
        new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon
    else:
        tooltip("Wild pokemon has to be fainted to defeat it!")

catch_shortcut = catch_shortcut.lower()
defeat_shortcut = defeat_shortcut.lower()
#// adding shortcuts to _shortcutKeys function in anki
def _shortcutKeys_wrap(self, _old):
    original = _old(self)
    original.append((catch_shortcut, lambda: catch_shortcut_function()))
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
            catch_shortcut_function()
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

if settings_obj.get("misc.discord_rich_presence") == True:
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
