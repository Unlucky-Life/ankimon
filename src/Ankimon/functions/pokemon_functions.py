from ..resources import pokedex_path, next_lvl_file_path
import csv
import json
import random

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
    

import random

def shiny_chance():
    # Shiny Pokémon probability (1 in 4096 chance)
    SHINY_PROBABILITY = 4096
    shiny = random.randint(1, SHINY_PROBABILITY) == 1
    return shiny

import uuid
import json
from datetime import datetime

def create_caught_pokemon(enemy_pokemon, nickname):
    enemy_pokemon.stats["xp"] = 0
    ev = {
        "hp": 0,
        "atk": 0,
        "def": 0,
        "spa": 0,
        "spd": 0,
        "spe": 0
    }
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
    return caught_pokemon