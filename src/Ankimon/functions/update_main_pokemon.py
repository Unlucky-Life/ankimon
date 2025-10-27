import json
from typing import Optional

from ..functions.pokedex_functions import search_pokedex, search_pokedex_by_id
from ..resources import mainpokemon_path
from ..pyobj.pokemon_obj import PokemonObject

# default values to fall back in case of load error
MAIN_POKEMON_DEFAULT = {
    "name": "RESTART ANKI",
    "gender": None,
    "level": 5,
    "id": None,
    "ability": None,
    "type": None,
    "base_stats": None,
    "xp": None,
    "ev": None,
    "iv": None,
    "attacks": None,
    "base_experience": None,
    "hp": 100,
    "growth_rate": None,
    "evos": None,
    "individual_id": None,
    "tier": None,
    "shiny": None,
    "captured_date": None
}


def update_main_pokemon(main_pokemon: Optional[PokemonObject] = None):
    """
    Updates or initializes the main Pokémon object using data from a JSON file.

    This function attempts to read the main Pokémon's stats from a JSON file
    located at `mainpokemon_path`. If the file exists and contains valid data,
    the given `main_pokemon` object is updated with those stats. If the file is
    missing, empty, or contains invalid JSON, a new `PokemonObject` is created
    using default values.

    Args:
        main_pokemon (Optional[PokemonObject]): An optional existing Pokémon object
            to update. If None, a new object is created using `MAIN_POKEMON_DEFAULT`.

    Returns:
        tuple:
            PokemonObject: The updated or newly created Pokémon object.
            bool: True if the file was empty or invalid (i.e., default was used),
                  False if the object was successfully updated with file data.
    """

    if main_pokemon is None:
        main_pokemon = PokemonObject(**MAIN_POKEMON_DEFAULT)

    mainpokemon_empty = True
    if mainpokemon_path.is_file():
        with open(mainpokemon_path, "r", encoding="utf-8") as mainpokemon_json:
            try:
                main_pokemon_data = json.load(mainpokemon_json)
                # if main pokemon is successfully loaded make empty false
                if main_pokemon_data:
                    mainpokemon_empty = False
                    pokemon_name = search_pokedex_by_id(main_pokemon_data[0]["id"])
                    main_pokemon_data[0]["base_stats"] = search_pokedex(pokemon_name, "baseStats")
                    del main_pokemon_data[0]["stats"]  # For legacy code, i.e. for when "stats" in the JSON actually meant "base_stat"
                    main_pokemon.update_stats(**main_pokemon_data[0])
                    save_main_pokemon(main_pokemon) # Save the updated main Pokémon data
                # if file does load or is empty use default value
                else:
                    main_pokemon = PokemonObject(**MAIN_POKEMON_DEFAULT)
                max_hp = main_pokemon.calculate_max_hp()
                main_pokemon.max_hp = max_hp
                if main_pokemon_data[0].get("current_hp", max_hp) > max_hp:
                    main_pokemon_data[0]["current_hp"] = max_hp
                if main_pokemon_data:
                    main_pokemon.hp = main_pokemon_data[0].get("current_hp", max_hp)
                return main_pokemon, mainpokemon_empty


            except Exception as e:
                main_pokemon = PokemonObject(**MAIN_POKEMON_DEFAULT)
                return main_pokemon, mainpokemon_empty
    else:
        return PokemonObject(**MAIN_POKEMON_DEFAULT), mainpokemon_empty

def save_main_pokemon(main_pokemon: PokemonObject):
    """
    Saves the main Pokémon object to the mainpokemon.json file.
    Args:
        main_pokemon (PokemonObject): The Pokémon object to save.
    """
    # If the object has a to_dict method, use it; otherwise, use __dict__
    if hasattr(main_pokemon, 'to_dict'):
        data = main_pokemon.to_dict()
    else:
        data = main_pokemon.__dict__
    # Write as a single-element list for compatibility
    with open(mainpokemon_path, "w", encoding="utf-8") as f:
        json.dump([data], f, indent=4)


