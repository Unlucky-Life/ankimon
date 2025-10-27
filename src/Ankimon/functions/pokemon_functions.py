import csv
import json
import random
import uuid
from datetime import datetime

from aqt.utils import showWarning

from .pokedex_functions import search_pokeapi_db_by_id, search_pokedex, search_pokedex_by_id, get_all_pokemon_moves
from .battle_functions import calculate_hp
from ..resources import (
    pokedex_path,
    next_lvl_file_path,
    mypokemon_path,
    learnset_path,
)

def pick_random_gender(pokemon_name):
    """
    Randomly pick a gender for a given Pokémon based on its gender ratios.

    Args:
        pokemon_name (str): The name of the Pokémon.
        pokedex_data (dict): Pokémon data loaded from the pokedex JSON file.

    Returns:
        str: "M" for male, "F" for female, or "Genderless" for genderless Pokémon.
    """
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
        return "M" if random_number < gender_ratio["M"] else "F"

    genders = pokemon.get("gender")
    if genders:
        return genders

    genders = ["M", "F"]
    #genders = ["M", "♀"]
    gender = random.choice(genders)
    return gender
    # Randomly choose between "M" and "F"

def calculate_max_hp_wildpokemon(enemy_pokemon):
    wild_pk_max_hp = enemy_pokemon.calculate_max_hp()
    return wild_pk_max_hp

def find_experience_for_level(group_growth_rate, level, remove_levelcap=True):
    """
    Find experience required to reach a certain level for a Pokémon with a given growth rate.
    Check for levelcap being uncaped in settings => then set diffrent experiences and if level is above 100, if so, set level to 100.
    """
    if level > 100 and remove_levelcap is False:
        level = 100
    if group_growth_rate == "medium":
        group_growth_rate = "medium-fast"
    elif group_growth_rate == "slow-then-very-fast":
        group_growth_rate = "fluctuating"
    elif group_growth_rate == "fast-then-very-slow":
        group_growth_rate = "fluctuating"
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
            if level + 1 < 50: # +1 was added to prevent -ve amounts of xp to come up (even though it wouldn't since the loop only takes in levels above 99)
                experience = ((((level+1) ** 3) * (100 - (level+1))) // 50 - ((level ** 3) * (100 - level) // 50))
            elif 50 <= level < 68:
                experience = (((level+1) ** 3) * (150 - (level+1)) // 100) - ((level ** 3) * (150 - level) // 100)
            elif 68 <= level:
                experience = (((level+1) ** 3) * (1911 - 10 * (level+1)) // 500) - ((level ** 3) * (1911 - 10 * level) // 500)
            else:
                experience = (((level+1) ** 3) * (160 - (level+1)) // 100) - ((level ** 3) * (160 - level) // 100)
        elif group_growth_rate == "fluctuating":
            if level < 15:
                experience = (((level+1) ** 3) * ((level+1) // 3 + 24) // 50) - ((level ** 3) * (level // 3 + 24) // 50)
            elif 15 <= level < 36:
                experience = (((level+1) ** 3) * ((level+1) + 14) // 50) - ((level ** 3) * (level + 14) // 50)
            elif 36 <= level:
                experience = (((level+1) ** 3) * ((level+1) // 2 + 32) // 50) - ((level ** 3) * (level // 2 + 32) // 50)
        elif group_growth_rate == "fast":
            experience = ((4 * ((level+1) ** 3)) // 5) - ((4 * (level ** 3)) // 5)
        elif group_growth_rate == "medium-fast":
            experience = ((level+1) ** 3) - (level ** 3)
        elif group_growth_rate == "medium":
            experience = ((level+1) ** 3) - (level ** 3)
        elif group_growth_rate == "medium-slow":
            experience = ((6 * ((level+1) ** 3)) // 5 - 15 * ((level+1) ** 2) + 100 * (level+1) - 140) - ((6 * (level ** 3)) // 5 - 15 * (level ** 2) + 100 * level - 140)
        elif group_growth_rate == "slow":
            experience = ((5 * ((level+1) ** 3)) // 4) - ((5 * (level ** 3)) // 4)
        return experience

def shiny_chance():
    # Shiny Pokémon probability (1 in 4096 chance)
    SHINY_PROBABILITY = 4096
    shiny = random.randint(1, SHINY_PROBABILITY) == 1
    return shiny

# unused, archived
# must fix missing fields if used
#def create_caught_pokemon(enemy_pokemon, nickname):
#    enemy_pokemon.stats["xp"] = 0
#    ev = {
#        "hp": 0,
#        "atk": 0,
#        "def": 0,
#        "spa": 0,
#        "spd": 0,
#        "spe": 0
#    }
#    caught_pokemon = {
#        "name": enemy_pokemon.name.capitalize(),
#        "nickname": nickname,
#        "level": enemy_pokemon.level,
#        "gender": enemy_pokemon.gender,
#        "id": enemy_pokemon.id,
#        "ability": enemy_pokemon.ability,
#        "type": enemy_pokemon.type,
#        "stats": enemy_pokemon.stats,
#        "ev": {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
#        "iv": enemy_pokemon.iv,
#        "attacks": enemy_pokemon.attacks,
#        "base_experience": enemy_pokemon.base_experience,
#        "current_hp": enemy_pokemon.calculate_max_hp(),
#        "growth_rate": enemy_pokemon.growth_rate,
#        "friendship": 0,
#        "pokemon_defeated": 0,
#        "everstone": False,
#        "shiny": enemy_pokemon.shiny,
#        "captured_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#        "individual_id": str(uuid.uuid4()),
#        "mega": False,
#        "special_form": None,
#    }
#    return caught_pokemon

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

def save_fossil_pokemon(pokemon_id):
    # Create a dictionary to store the Pokémon's data
    # add all new values like hp as max_hp, evolution_data, description and growth rate
    name = search_pokedex_by_id(pokemon_id)
    id = pokemon_id
    stats = search_pokedex(name, "baseStats")
    abilities = search_pokedex(name, "abilities")
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
    #stats["xp"] = 0
    ev = {
        "hp": 0,
        "atk": 0,
        "def": 0,
        "spa": 0,
        "spd": 0,
        "spe": 0
    }
    iv = {
        "hp": random.randint(1, 32),
        "atk": random.randint(1, 32),
        "def": random.randint(1, 32),
        "spa": random.randint(1, 32),
        "spd": random.randint(1, 32),
        "spe": random.randint(1, 32)
    }
    stats["xp"] = 0
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
        "friendship": 0,
        "pokemon_defeated": 0,
        "everstone": False,
        "shiny": shiny_chance(),
        "captured_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "individual_id": str(uuid.uuid4()),
        "mega": False,
        "special_form": None,
        "tier": "Fossil",
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