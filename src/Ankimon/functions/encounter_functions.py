import json
import random
import math
from typing import Union
from datetime import datetime
import uuid

from aqt import mw
from aqt.utils import showWarning

from ..pyobj.ankimon_tracker import AnkimonTracker
from ..pyobj.pokemon_obj import PokemonObject
from ..pyobj.reviewer_obj import Reviewer_Manager
from ..pyobj.test_window import TestWindow
from ..pyobj.trainer_card import TrainerCard
from ..pyobj.InfoLogger import ShowInfoLogger
from ..pyobj.evolution_window import EvoWindow
from ..functions.pokemon_functions import pick_random_gender, shiny_chance
from ..functions.pokedex_functions import get_all_pokemon_moves, search_pokeapi_db_by_id, search_pokedex, search_pokedex_by_id
from ..functions.trainer_functions import xp_share_gain_exp
from ..functions.badges_functions import check_for_badge, receive_badge
from ..functions.drawing_utils import tooltipWithColour
from ..business import calc_experience
from ..const import gen_ids
from ..singletons import (
    main_pokemon,
    ankimon_tracker_obj,
    trainer_card,
    settings_obj,
    translator,
)
from ..resources import (
    pokemon_species_baby_path,
    pokemon_species_legendary_path,
    pokemon_species_mythical_path,
    pokemon_species_normal_path,
    pokemon_species_ultra_path,
    mypokemon_path,
)

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
    # this function gets called maybe 10 times per battle round, which is concerning. 
    # it could be rewritten to run ONLY when the change in review ratio is detected.
    return percentages

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

def get_tier(total_reviews, player_level=1, event_modifier=None):
    """_summary_
    Randomly picks the tier for a new enemy Pokemon to be generated from, based on weighted probabilities based on number of reviews and player level.

    Args:
        total_reviews (int): Number of reviews done in that Anki session.
        player_level (int, optional): Trainer XP level. Defaults to 1.
        event_modifier (?, optional): Unused argument. Defaults to None.

    Returns:
        choice[0]: The first choice of TIER picked randomly (by a random.choices function) 
    """
    daily_average = int(settings_obj.get('battle.daily_average', 100))
    percentages = modify_percentages(total_reviews, daily_average, player_level)
    
    tiers = list(percentages.keys())
    probabilities = list(percentages.values())
    
    choice = random.choices(tiers, probabilities, k=1)
    return choice[0]

def choose_random_pkmn_from_tier():
    """
    Runs a tier-selection and a subsequent ID-selection function to pick a random Pokemon from a given randomly picked Tier.
    The tier is a weighted probability selection, based on total_reviews and trainer_level.
    Pokemon ID is picked randomly from within that tier. 

    Returns:
        id (int): Pokedex ID for generated Pokemon
        tier (string): Rarity tier for generated Pokemon (normal/ultra/legendary etc.)
    """
    total_reviews = ankimon_tracker_obj.total_reviews
    trainer_level = trainer_card.level
    try:
        tier = get_tier(total_reviews, trainer_level)
        id = get_pokemon_id_by_tier(tier)
        return id, tier
    except Exception as e:
        showWarning(translator.translate("error_occured", error="choose_random_pkmn_from_tier"))

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

def check_id_ok(id_num: Union[int, list[int]]):
    if isinstance(id_num, list):
        if len(id_num) > 0:
            id_num = id_num[0]
        else:
            return False
    
    if not isinstance(id_num, int):
        return False

    if id_num >= 898:
        return False

    generation = 0
    for gen, max_id in gen_ids.items():
        if id_num <= max_id:
            generation = int(gen.split('_')[1])
            config = mw.addonManager.getConfig(__name__)
            gen_config = [config[f"misc.gen{i}"] for i in range(1, 10)]
            return gen_config[generation - 1]

    return False
    
def generate_random_pokemon(main_pokemon_level: int, ankimon_tracker_obj: AnkimonTracker):
    """
    Generates a random wild Pokémon with attributes scaled to the level of the player's main Pokémon.

    This function resets the encounter and battle round state in the provided `AnkimonTracker` object.
    It then selects a valid Pokémon that can appear at the current level range, computes its stats, 
    determines its moves, ability, and other combat-relevant characteristics, and returns all necessary 
    data required for a battle.

    Args:
        main_pokemon_level (int): The level of the player's main Pokémon. Determines the level range of 
            the generated wild Pokémon.
        ankimon_tracker_obj (AnkimonTracker): An object used to track battle state, such as the number 
            of Pokémon encountered and cards used in the battle.

    Returns:
        tuple: A tuple containing the following elements:
            - name (str): Name of the wild Pokémon.
            - pokemon_id (int): Unique ID of the Pokémon.
            - wild_pokemon_lvl (int): The level of the generated Pokémon.
            - ability (str): The selected ability of the Pokémon.
            - pokemon_type (list[str]): List of type(s) the Pokémon belongs to.
            - base_stats (dict): Dictionary of the Pokémon's base stats.
            - moves (list[str]): List of up to 4 moves the Pokémon can use in battle.
            - base_experience (int): Experience points awarded for defeating the Pokémon.
            - growth_rate (str): Growth rate category of the Pokémon (e.g., "slow", "fast").
            - ev (dict): Effort values (EVs) for each stat, initialized to 0.
            - iv (dict): Randomly generated individual values (IVs) for each stat.
            - gender (str): Randomly assigned gender.
            - battle_status (str): Current status of the Pokémon in battle, defaulted to "fighting".
            - final_stats (dict): Final computed stats of the Pokémon.
            - tier (str): Tier from which the Pokémon was selected (e.g., common, rare).
            - ev_yield (dict): Effort values (EVs) awarded upon defeating the Pokémon.
            - is_shiny (bool): Indicates whether the Pokémon is shiny.

    Raises:
        ValueError: If no valid Pokémon can be generated (highly unlikely under normal conditions).
    """
    lvl_variation = 3
    lvl_range = max(1, main_pokemon_level - lvl_variation), max(1, main_pokemon_level + lvl_variation)
    wild_pokemon_lvl = random.randint(*lvl_range)
    wild_pokemon_lvl = max(1, wild_pokemon_lvl)  # Ensures that the wild pokemon's level is at least 1
    if main_pokemon_level == 100:
        wild_pokemon_lvl = 100

    # First, we draw a random, valid pokemon id.
    pokemon_id, tier = choose_random_pkmn_from_tier()
    name = search_pokedex_by_id(pokemon_id)
    min_allowed_pokemon_lvl = check_min_generate_level(str(name.lower()))  # Gets the minimum allowed level for that pokemon given its stage of evolution
    while (not check_id_ok(pokemon_id)) or (wild_pokemon_lvl < min_allowed_pokemon_lvl):  # We keep drawing a random pokemon until we find a valid one
        pokemon_id, tier = choose_random_pkmn_from_tier()
        name = search_pokedex_by_id(pokemon_id)
        min_allowed_pokemon_lvl = check_min_generate_level(str(name.lower()))  # Gets the minimum allowed level for that pokemon given its stage of evolution

    # Now we get all necessary information about the chosen pokemon.
    pokemon_type = search_pokedex(name, "types")
    base_experience = search_pokeapi_db_by_id(pokemon_id, "base_experience")  # Experience that the wild pokemon will give once beaten
    growth_rate = search_pokeapi_db_by_id(pokemon_id, "growth_rate")
    ev_yield = search_pokeapi_db_by_id(pokemon_id, "effort_values")
    gender = pick_random_gender(name)
    is_shiny = shiny_chance()
    battle_status = "fighting"
    base_stats = search_pokedex(name, "baseStats")

    all_possible_moves = get_all_pokemon_moves(name, wild_pokemon_lvl)
    if len(all_possible_moves) <= 4:
        moves = all_possible_moves
    else:
        moves = random.sample(all_possible_moves, 4)

    ability = "no_ability"  # Default value for ability
    possible_abilities = search_pokedex(name, "abilities")
    if possible_abilities:
        numeric_abilities = {k: v for k, v in possible_abilities.items() if k.isdigit()}
        if numeric_abilities:
            ability = random.choice(list(numeric_abilities.values()))
    
    stat_names = ["hp", "atk", "def", "spa", "spd", "spe"]
    ev = {stat: 0 for stat in stat_names}
    iv = {stat: random.randint(1, 32) for stat in stat_names}
    final_stats = base_stats

    ankimon_tracker_obj.pokemon_encounter = 0  # 0: Start of Battle: 1: Current Battle
    ankimon_tracker_obj.cards_battle_round = 0  # Amount of cards in this current battle

    return (
        name,
        pokemon_id,
        wild_pokemon_lvl,
        ability,
        pokemon_type,
        base_stats,
        moves,
        base_experience,
        growth_rate,
        ev,
        iv,
        gender,
        battle_status,
        final_stats,
        tier,
        ev_yield,
        is_shiny
    )

def new_pokemon(
        pokemon: PokemonObject,
        test_window: TestWindow,
        ankimon_tracker: AnkimonTracker,
        reviewer_obj: Reviewer_Manager
        ) -> PokemonObject:
    """
    Initializes a new wild Pokémon encounter by generating a random Pokémon,
    updating its stats, setting its HP, and preparing the battle scene.

    This function uses the player's main Pokémon level to generate an appropriately
    leveled wild Pokémon with randomized attributes. It updates the provided `pokemon`
    object with generated data, resets HP, triggers any battle scene randomization,
    and updates the reviewer interface if applicable.

    Args:
        pokemon (PokemonObject): The Pokémon object to be updated with the new wild Pokémon's data.
        test_window (TestWindow): Optional UI window to display the first encounter scene.
        ankimon_tracker (AnkimonTracker): Object tracking battle-related state and handling battle scene randomization.
        reviewer_obj (Reviewer_Manager): Manager object responsible for updating battle review elements like life bars.

    Returns:
        PokemonObject: The updated `pokemon` object representing the newly generated wild Pokémon ready for battle.
    """
    (
        name,
        pkmn_id,
        level,
        ability,
        pkmn_type,
        stats,
        enemy_attacks,
        base_experience,
        growth_rate,
        ev,
        iv,
        gender,
        battle_status,
        battle_stats,
        tier,
        ev_yield,
        is_shiny
        ) = generate_random_pokemon(main_pokemon.level, ankimon_tracker_obj)
    pokemon_data = {
        'name': name,
        'id': pkmn_id,
        'level': level,
        'ability': ability,
        'type': pkmn_type,
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
        'shiny': is_shiny
    }
    pokemon.update_stats(**pokemon_data)
    max_hp = pokemon.calculate_max_hp()
    pokemon.current_hp = max_hp
    pokemon.hp = max_hp
    pokemon.max_hp = max_hp
    
    ankimon_tracker.randomize_battle_scene()
    if test_window is not None:
        test_window.display_first_encounter()
    class Container(object):
        pass
    reviewer = Container()
    reviewer.web = mw.reviewer.web
    reviewer_obj.update_life_bar(reviewer, 0, 0)

    return pokemon

# def kill_pokemon(
#         enemy_pokemon: PokemonObject,
#         test_window: TestWindow,
#         evo_window: EvoWindow,
#         logger: ShowInfoLogger,
#         reviewer_obj: Reviewer_Manager,
#         trainer_card: Union[TrainerCard, None]=None
#         ):
#     if trainer_card is not None:
#         trainer_card.gain_xp(enemy_pokemon.tier, settings_obj.get("controls.allow_to_choose_moves", False))
    
#     # Calculate experience based on whether moves are chosen manually
#     exp = calc_experience(main_pokemon.base_experience, enemy_pokemon.level)
#     if settings_obj.get("controls.allow_to_choose_moves", False):
#         exp *= 0.5
    
#     # Ensure exp is at least 1 and round up if it's a decimal
#     exp = max(1, math.ceil(exp))
    
#     # Handle XP share logic
#     xp_share_individual_id = settings_obj.get("trainer.xp_share", None)
#     if xp_share_individual_id:
#         exp = xp_share_gain_exp(logger, settings_obj, evo_window, main_pokemon.id, exp, xp_share_individual_id)
    
#     # Save main Pokémon's progress
#     main_pokemon.level = save_main_pokemon_progress(
#         mainpokemon_path,
#         main_pokemon.level,
#         main_pokemon.name,
#         main_pokemon.base_experience,
#         main_pokemon.growth_rate,
#         exp
#     )
    
#     ankimon_tracker_obj.general_card_count_for_battle = 0
    
#     # Show a new random Pokémon if the test window is visible
#     if test_window.isVisible():
#         new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon

def save_caught_pokemon(
        enemy_pokemon: PokemonObject,
        nickname: Union[str, None]=None,
        achievements: Union[dict, None]=None
        ):
    # Create a dictionary to store the Pokémon's data
    # add all new values like hp as max_hp, evolution_data, description and growth rate
    if enemy_pokemon.tier is not None and achievements is not None:
        if enemy_pokemon.tier == "Normal":
            check = check_for_badge(achievements, 17)
            if check is False:
                achievements = receive_badge(17,achievements)
        elif enemy_pokemon.tier == "Baby":
            check = check_for_badge(achievements, 18)
            if check is False:
                achievements = receive_badge(18, achievements)
        elif enemy_pokemon.tier == "Ultra":
            check = check_for_badge(achievements, 8)
            if check is False:
                achievements = receive_badge(8, achievements)
        elif enemy_pokemon.tier == "Legendary":
            check = check_for_badge(achievements, 9)
            if check is False:
                achievements = receive_badge(9, achievements)
        elif enemy_pokemon.tier == "Mythical":
            check = check_for_badge(achievements, 10)
            if check is False:
                achievements = receive_badge(10, achievements)

    if nickname is None:
        nickname = enemy_pokemon.name.capitalize()

    enemy_pokemon.stats["xp"] = 0
    caught_pokemon = {
        "name": enemy_pokemon.name.capitalize(),
        "nickname": nickname,
        "level": enemy_pokemon.level,
        "gender": enemy_pokemon.gender,
        "id": enemy_pokemon.id,
        "ability": enemy_pokemon.ability,
        "type": enemy_pokemon.type,
        "stats": enemy_pokemon.stats,
        "ev": enemy_pokemon.ev,
        "iv": enemy_pokemon.iv,
        "attacks": enemy_pokemon.attacks,
        "base_experience": enemy_pokemon.base_experience,
        "current_hp": enemy_pokemon.calculate_max_hp(),
        "growth_rate": enemy_pokemon.growth_rate,
        "friendship": 0,
        "pokemon_defeated": 0,
        "everstone": False,
        "shiny": enemy_pokemon.shiny,
        "captured_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "individual_id": str(uuid.uuid4()),
        "mega": False,
        "special-form": None,
    }

    # Load existing Pokémon data if it exists
    caught_pokemon_data = []
    if mypokemon_path.is_file():
        with open(mypokemon_path, "r", encoding="utf-8") as json_file:
            caught_pokemon_data = json.load(json_file)

    # Append the caught Pokémon's data to the list
    caught_pokemon_data.append(caught_pokemon)

    # Save the caught Pokémon's data to a JSON file
    with open(str(mypokemon_path), "w") as json_file:
        json.dump(caught_pokemon_data, json_file, indent=2)

def catch_pokemon(
        enemy_pokemon: PokemonObject,
        test_window: TestWindow,
        logger: ShowInfoLogger,
        reviewer_obj: Reviewer_Manager,
        ankimon_tracker_obj: AnkimonTracker,
        nickname: Union[str, None]=None,
        collected_pokemon_ids: Union[set, None]=None,
        achievements: Union[dict, None]=None,
        ):
    ankimon_tracker_obj.caught += 1
    if ankimon_tracker_obj.caught > 1:
        if settings_obj.get('gui.pop_up_dialog_message_on_defeat', True) is True:
            logger.log_and_showinfo("info",translator.translate("already_caught_pokemon")) # Display a message when the Pokémon is caught

    # If we arrive here, this means that ankimon_tracker_obj.caught == 1
    if nickname is not None or not nickname:
        nickname = enemy_pokemon.name
    if collected_pokemon_ids is not None:
        collected_pokemon_ids.add(enemy_pokemon.id)  # Update cache
    save_caught_pokemon(enemy_pokemon, nickname, achievements)
    ankimon_tracker_obj.general_card_count_for_battle = 0
    msg = translator.translate("caught_wild_pokemon", enemy_pokemon_name=enemy_pokemon.name.capitalize())
    if settings_obj.get('gui.pop_up_dialog_message_on_defeat', True) is True:
        logger.log_and_showinfo("info",f"{msg}") # Display a message when the Pokémon is caught
    color = "#6A4DAC" #pokemon leveling info color for tooltip
    try:
        tooltipWithColour(msg, color)
    except Exception as e:
        pass
    new_pokemon(enemy_pokemon, test_window, ankimon_tracker_obj, reviewer_obj)  # Show a new random Pokémon