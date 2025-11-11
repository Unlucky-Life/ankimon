import json
from aqt.utils import showWarning
from ..resources import mainpokemon_path, mypokemon_path, starters_path

def get_starter_evolution_ids(starter_id: int) -> list[int]:
    """
    Returns a list containing the starter's ID and its two direct evolution IDs.
    Assumes a linear evolution path of n, n+1, n+2.
    """
    return [starter_id, starter_id + 1, starter_id + 2]

def migrate_starter_individual_id():
    """
    Checks for and fixes a bug where a starter's individual_id in mainpokemon.json
    does not match any Pokemon in mypokemon.json.
    This migration finds the correct starter in mypokemon.json based on stats
    and updates its individual_id to match the one in mainpokemon.json.
    This function is now triggered only when the main pokemon is changed and
    is a starter or an evolution of a starter.
    """
    if not mainpokemon_path.is_file() or not mypokemon_path.is_file():
        return

    try:
        with open(mainpokemon_path, "r", encoding="utf-8") as f:
            main_pokemon_data = json.load(f)
        with open(mypokemon_path, "r", encoding="utf-8") as f:
            my_pokemon_data = json.load(f)
        with open(starters_path, "r", encoding="utf-8") as f:
            starters_data = json.load(f)
    except (json.JSONDecodeError, IOError):
        # Files might be empty or corrupted, so we can't proceed.
        return

    if not main_pokemon_data:
        return

    main_pokemon = main_pokemon_data[0]
    main_individual_id = main_pokemon.get("individual_id")
    main_pokemon_id = main_pokemon.get("id")

    if not main_individual_id:
        # No individual_id in mainpokemon, so nothing to sync.
        return

    # Check if the individual_id from mainpokemon exists in mypokemon
    if any(p.get("individual_id") == main_individual_id for p in my_pokemon_data):
        # The ID already matches, so no migration is needed.
        return

    # Get all starter and starter evolution IDs
    all_starter_evolution_ids = []
    for starter_info in starters_data.values():
        starter_id = int(starter_info["id"])
        all_starter_evolution_ids.extend(get_starter_evolution_ids(starter_id))

    if main_pokemon_id not in all_starter_evolution_ids:
        # The main Pokemon is not a starter or its evolution, so we don't apply the fix.
        return

    # Find a potential match in mypokemon.json
    potential_match = None
    for pokemon in my_pokemon_data:
        # A starter in mypokemon.json affected by the bug might not have an individual_id
        if pokemon.get("id") == main_pokemon.get("id") and \
           pokemon.get("iv") == main_pokemon.get("iv") and \
           pokemon.get("gender") == main_pokemon.get("gender") and \
           pokemon.get("ability") == main_pokemon.get("ability") and \
           pokemon.get("shiny") == main_pokemon.get("shiny"):
            potential_match = pokemon
            break # Found a match

    if potential_match:
        # We found the starter. Now, update its individual_id.
        showWarning(
            "Ankimon has detected and fixed an issue with your starter Pokémon's data. "
            "Your starter's unique ID has been synchronized. No action is needed from you."
        )
        potential_match["individual_id"] = main_individual_id

        try:
            with open(mypokemon_path, "w", encoding="utf-8") as f:
                json.dump(my_pokemon_data, f, indent=4)
        except IOError:
            showWarning(
                "Ankimon could not save the fix for your starter Pokémon. "
                "Please check file permissions for the Ankimon addon folder."
            )