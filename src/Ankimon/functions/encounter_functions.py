import json
import random
from typing import Union

from aqt import mw
from aqt.utils import showWarning

from ..pyobj.ankimon_tracker import AnkimonTracker
from ..functions.pokemon_functions import check_min_generate_level, pick_random_gender, shiny_chance
from ..functions.pokedex_functions import get_all_pokemon_moves, search_pokeapi_db_by_id, search_pokedex, search_pokedex_by_id
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