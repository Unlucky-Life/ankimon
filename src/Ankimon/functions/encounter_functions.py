import json
import random

from aqt.utils import showWarning

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