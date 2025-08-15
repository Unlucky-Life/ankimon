import json
from .pokedex_functions import extract_ids_from_file
from ..resources import mypokemon_path, badges_list_path
from .pokemon_functions import find_experience_for_level
from .pokedex_functions import check_evolution_for_pokemon, return_name_for_id
from aqt.utils import showInfo, showWarning

def find_trainer_rank(highest_level, trainer_level):
    """
    Determines the Pokémon rank based on the player's achievements like Pokémon caught (from Pokedex),
    highest level Pokémon, trainer XP, trainer level, shiny Pokémon count, and badges.

    Args:
    highest_level (int): The highest level Pokémon the player owns.
    trainer_level (int): The level of the trainer.

    Returns:
    str: The Pokémon rank (Grand Champion, Champion, Elite, Veteran, Rookie, etc.).
    """
    try:
        # Count the amount of Pokémon caught based on the Pokedex
        caught_pokemon = len(extract_ids_from_file())

        # Count the number of shiny Pokémon
        shiny_pokemon_count = 0
        with open(mypokemon_path, 'r', encoding='utf-8') as f:
            my_pokemon = json.load(f)
            shiny_pokemon_count = sum(1 for pokemon in my_pokemon if pokemon.get('shiny', False))  # Assuming 'shiny' is a key

        # Count badges
        with open(badges_list_path, 'r', encoding='utf-8') as f:
            badges = json.load(f)
            badge_count = len(badges)

        # Determine rank based on achievements
        if caught_pokemon >= 900 and highest_level >= 99 and trainer_level >= 100 and shiny_pokemon_count >= 50:
            rank = "Legendary Trainer"
        elif caught_pokemon >= 800 and highest_level >= 95 and trainer_level >= 80 and shiny_pokemon_count >= 25:
            rank = "Grand Champion"
        elif caught_pokemon >= 700 and highest_level >= 90 and trainer_level >= 70 and shiny_pokemon_count >= 20:
            rank = "Champion"
        elif caught_pokemon >= 600 and highest_level >= 80 and trainer_level >= 60 and shiny_pokemon_count >= 10 and badge_count >= 8:
            rank = "Master Trainer"
        elif caught_pokemon >= 500 and highest_level >= 75 and trainer_level >= 50 and shiny_pokemon_count >= 5 and badge_count > 6:
            rank = "Elite"
        elif caught_pokemon >= 400 and highest_level >= 70 and trainer_level >= 45 and shiny_pokemon_count >= 3 and badge_count > 5:
            rank = "Elite Trainer"
        elif caught_pokemon >= 350 and highest_level >= 60 and trainer_level >= 40 and shiny_pokemon_count >= 2 and badge_count > 4:
            rank = "Advanced Trainer"
        elif caught_pokemon >= 300 and highest_level >= 50 and trainer_level >= 30 and shiny_pokemon_count > 0 and badge_count > 3:
            rank = "Veteran"
        elif caught_pokemon >= 250 and highest_level >= 40 and trainer_level >= 20 and shiny_pokemon_count > 0:
            rank = "Skilled Trainer"
        elif caught_pokemon >= 150 and highest_level >= 30 and trainer_level >= 10:
            rank = "Rookie"
        else:
            rank = "Novice Trainer"  # Default rank for beginners

        return rank

    except FileNotFoundError:
        print("Error: One of the files (Pokedex or MyPokemon) could not be found.")
        return "Unknown Rank"

def xp_share_gain_exp(logger, settings_obj, evo_window, main_pokemon_id, exp, xp_share_individual_id):
    # Ensure that the XP Share Pokémon is set and different from the main Pokémon
    if not xp_share_individual_id:
        return exp

    if xp_share_individual_id == main_pokemon_id:
        return exp

    original_exp = int(exp * 0.5)
    remove_level_cap = settings_obj.get("misc.remove_level_cap", False)
    exp = int(exp * 0.5)  # Convert the experience to an integer

    # Open the mypokemon_path JSON file and load the data
    with open(mypokemon_path, "r", encoding="utf-8") as json_file:
        mypokemon_data = json.load(json_file)

    msg = ""
    evolution_triggered = False

    # Iterate through the Pokémon data and find the matching individual_id
    for pokemon in mypokemon_data:
        if pokemon["individual_id"] != str(xp_share_individual_id):  # Ensure same type comparison
            continue

        # Increase the xp of the matched Pokémon
        current_level = int(pokemon['level'])  # MODIFIED: Use local variable for level
        current_xp = pokemon.get("xp") or pokemon["stats"].get("xp", 0)
        growth_rate = pokemon['growth_rate']  # MODIFIED: Use local variable for growth rate
        experience_needed = int(find_experience_for_level(growth_rate, current_level, remove_level_cap))  # MODIFIED: Pre-calculate needed XP
        evo_id = None # Initialize variable

        logger.log("info", "Running XP share function")
        if experience_needed > exp + current_xp:
            pokemon["xp"] = current_xp + exp
        else:
            while exp + current_xp > experience_needed:
                if (remove_level_cap or current_level < 100):
                    current_level += 1
                    exp = exp + current_xp - experience_needed
                    current_xp = 0
                    experience_needed = int(find_experience_for_level(growth_rate, current_level, remove_level_cap))  # MODIFIED: Recalculate needed XP
                    msg += f"XP increased for {pokemon['name']} with level {current_level} and XP {exp}\n"
                else:
                    break
            pokemon['level'] = current_level
            pokemon['xp'] = 0 if exp < 0 else exp

        # Check for evolution
        evo_id = check_evolution_for_pokemon(
            pokemon['individual_id'],
            pokemon['id'],
            pokemon['level'],
            evo_window,
            pokemon['everstone']
        )

        if evo_id is not None:
            msg += f"{pokemon['name']} is about to evolve to {return_name_for_id(evo_id).capitalize()} at level {pokemon['level']}"
            evolution_triggered = True

            # Write the XP/level changes to file BEFORE calling evolution
            with open(mypokemon_path, "w", encoding="utf-8") as json_file:
                json.dump(mypokemon_data, json_file, indent=4)

            # Now call evolution (which will read the updated file and handle the evolution)
            break  # Exit the loop since we found and processed the Pokemon

    # Only write to file if no evolution was triggered (since evolution already wrote to file)
    if not evolution_triggered:
        with open(mypokemon_path, "w", encoding="utf-8") as json_file:
            json.dump(mypokemon_data, json_file, indent=4)

    logger.log("info", f"{msg}")
    return original_exp  # Return the amount of experience added
