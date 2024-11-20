from ..resources import pokedex_path
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