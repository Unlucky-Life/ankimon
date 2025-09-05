from ..resources import pokedex_path, pokedesc_lang_path, pokeapi_db_path, pokenames_lang_path, mypokemon_path, learnset_path, moves_file_path, poke_evo_path, poke_species_path, csv_file_items_cost, pokemon_csv
from aqt.utils import showWarning
from aqt import mw
import json
import random
import csv
from ..pyobj.error_handler import show_warning_with_traceback

def special_pokemon_names_for_min_level(name):
    if name == "flabébé":
        return "flabebe"
    elif name == "sirfetch'd":
        return "sirfetchd"
    elif name == "farfetch'd":
        return "farfetchd"
    elif name == "porygon-z":
        return "porygonz"
    elif name == "kommo-o":
        return "kommoo"
    elif name == "hakamo-o":
        return "hakamoo"
    elif name == "jangmo-o":
        return "jangmoo"
    elif name == "mr. rime":
        return "mrrime"
    elif name == "mr. mime":
        return "mrmime"
    elif name == "mime jr.":
        return "mimejr"
    elif name == "nidoran♂":
        return "nidoranm"
    elif name == "nidoran":
        return "nidoranf"
    elif name == "keldeo[e]":
        return "keldeo"
    elif name == "mew[e]":
        return "mew"
    elif name == "deoxys[e]":
        return "deoxys"
    elif name == "jirachi[e]":
        return "jirachi"
    elif name == "arceus[e]":
        return "arceus"
    elif name == "shaymin[e]":
        return "shaymin-land"
    elif name == "darkrai [e]":
        return "darkrai"
    elif name == "manaphy[e]":
        return "manaphy"
    elif name == "phione[e]":
        return "phione"
    elif name == "celebi[e]":
        return "celebi"
    elif name == "magearna[e]":
        return "magearna"
    elif name == "type: null":
        return "typenull"
    else:
        return name

def search_pokedex(pokemon_name, variable):
    try:
        pokemon_name = special_pokemon_names_for_min_level(pokemon_name)
        with open(str(pokedex_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)

        # Create a copy of the name to modify
        current_name = pokemon_name

        while True:
            # 1. Try to find a match with the current name
            if current_name in pokedex_data:
                pokemon_info = pokedex_data[current_name]
                var = pokemon_info.get(variable)
                if var is not None:
                    return var

            # 2. If no match, find the last hyphen
            last_hyphen_index = current_name.rfind('-')

            # 3. If no hyphen is found, we can't shorten the name anymore.
            if last_hyphen_index == -1:
                break

            # 4. Remove the suffix and try again in the next iteration
            current_name = current_name[:last_hyphen_index]

        # 5. If no match was ever found, return an empty list
        return []

    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message=f"Error searching for pokemon '{pokemon_name}'")
        return []

def search_pokedex_by_name_for_id(pokemon_name, variable):
    pokemon_name = special_pokemon_names_for_min_level(pokemon_name)
    with open(str(pokedex_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            if pokemon_name in pokedex_data:
                pokemon_info = pokedex_data[pokemon_name]
                var = pokemon_info.get("num", None)
                return var
            else:
                return None

def search_pokedex_by_id(pokemon_id):
    with open(str(pokedex_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            for entry_name, attributes in pokedex_data.items():
                if attributes['num'] == pokemon_id:
                    return entry_name
    return 'Pokémon not found'

def get_mainpokemon_evo(pokemon_name):
    with open(str(pokedex_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            if pokemon_name not in pokedex_data:
                return []
            pokemon_info = pokedex_data[pokemon_name]
            evolutions = pokemon_info.get("evos", [])
            return evolutions

def search_pokeapi_db(pkmn_name,variable):
    with open(str(pokeapi_db_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            for pokemon_data in pokedex_data:
                name = pokemon_data["name"]
                if pokemon_data["name"] == pkmn_name:
                    var = pokemon_data.get(variable, None)
                    return var

def search_pokeapi_db_by_id(pkmn_id,variable):
    with open(str(pokeapi_db_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            for pokemon_data in pokedex_data:
                if pokemon_data["id"] == pkmn_id:
                    var = pokemon_data.get(variable, None)
                    return var

#TODO change all the functions to use language as a parameter
def get_pokemon_descriptions(species_id, language):
    descriptions = []  # Initialize an empty list to store matching descriptions
    with open(pokedesc_lang_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if int(row['species_id']) == species_id and int(row['language_id']) == language:
                # Replace control characters for readability, if necessary
                flavor_text = row['flavor_text'].replace('\x0c', ' ')
                descriptions.append(flavor_text)  # Add the matching description to the list
    if descriptions:
        if len(descriptions) > 1:
            return random.choice(descriptions)
        else:
            return descriptions[0]
    else:
        return "Description not found."

#TODO change all the functions to use language as a parameter
def get_pokemon_diff_lang_name(pokemon_id, language):
    with open(pokenames_lang_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row if there is one
        for row in reader:
            # Assuming the CSV structure is: pokemon_species_id,local_language_id,name,genus
            species_id, lang_id, name, genus = row
            if int(species_id) == pokemon_id and int(lang_id) == language:
                return name
    return "No Translation in this language"  # Return None if no match is found

def extract_ids_from_file():
    try:
        filename = mypokemon_path
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            ids = [character['id'] for character in data]
            owned_pokemon_ids = ids
            owned_pokemon_ids = sorted(list(set(owned_pokemon_ids)))
            #showWarning(f"Owned Pokémon IDs: {owned_pokemon_ids}")
            return owned_pokemon_ids
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message="Error extracting IDs from file")
        return []


def get_all_pokemon_moves(pk_name, level):
        """
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
        pk_name = pk_name.lower()

        # Retrieve the learnset for the specified Pokémon
        pokemon_learnset = learnsets.get(pk_name, {})

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

            # Pick up to 4 random moves and append them to the attacks list
            for move, highest_level in moves_and_levels_list:
                attacks.append(f"{move}")

        return attacks

def find_details_move(move_name):
    try:
        with open(moves_file_path, "r", encoding="utf-8") as json_file:
            moves_data = json.load(json_file)
            move = moves_data.get(move_name.lower())  # Use get() to access the move by name
            if move:
                return move
            move_name = move_name.replace(" ", "")
            try:
                move = moves_data.get(move_name.lower())
                return move
            except:
                #logger.log_and_showinfo("info",f"Can't find the attack {move_name} in the database.")
                move = moves_data.get("tackle")
                return move
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message=f"There is an issue in find_details_move for move: {move_name}")
        return None

def get_pokemon_evolution_data_all(pokemon_id, file_path=poke_evo_path):
    # Open the CSV file
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter='\t')  # Assuming tab-separated values
        for row in reader:
            # Check if the current row's Pokémon ID matches the requested ID
            if int(row['id']) == pokemon_id:
                # Return the data as a dictionary for the specific Pokémon ID
                evolution_data = {
                    'id': row['id'],
                    'evolved_species_id': row['evolved_species_id'],
                    'evolution_trigger_id': row['evolution_trigger_id'],
                    'trigger_item_id': row['trigger_item_id'],
                    'minimum_level': row['minimum_level'],
                    'gender_id': row['gender_id'],
                    'location_id': row['location_id'],
                    'held_item_id': row['held_item_id'],
                    'time_of_day': row['time_of_day'],
                    'known_move_id': row['known_move_id'],
                    'known_move_type_id': row['known_move_type_id'],
                    'minimum_happiness': row['minimum_happiness'],
                    'minimum_beauty': row['minimum_beauty'],
                    'minimum_affection': row['minimum_affection'],
                    'relative_physical_stats': row['relative_physical_stats'],
                    'party_species_id': row['party_species_id'],
                    'party_type_id': row['party_type_id'],
                    'trade_species_id': row['trade_species_id'],
                    'needs_overworld_rain': row['needs_overworld_rain'],
                    'turn_upside_down': row['turn_upside_down']
                }

                # Add the evolution trigger ID description
                evolution_trigger_map = {
                    1: "level-up",
                    2: "trade",
                    3: "use-item",
                    4: "shed",
                    5: "spin",
                    6: "tower-of-darkness",
                    7: "tower-of-waters",
                    8: "three-critical-hits",
                    9: "take-damage",
                    10: "other",
                    11: "agile-style-move",
                    12: "strong-style-move",
                    13: "recoil-damage"
                }

                #trigger_id = int(row['evolution_trigger_id'])
                #evolution_data['evolution_trigger_description'] = evolution_trigger_map.get(trigger_id, "Unknown Trigger ID")

                return evolution_data

        # Return None if the Pokémon ID is not found
        return None

def check_evolution_by_item(pokemon_id, item_id, file_path=poke_evo_path):
    """
    Check if a Pokémon evolves using a specific item.

    Args:
        pokemon_id (int): The ID of the Pokémon.
        item_id (int): The ID of the item.

    Returns:
        bool: True if the Pokémon evolves with the given item, False otherwise.
    """
    # Get the evolution data for the given Pokémon ID
    possible_evos = pokemon_evolves_from_id(pokemon_id)  # Ensure this returns a list of possible evolutions
    if not possible_evos:
        showWarning("No possible evos found")
        return False

    # Iterate through the possible evolutions
    for evos in possible_evos:
        evo_data = get_pokemon_evolution_data(int(evos))
        if evo_data:
            if (
                int(evo_data['evolution_trigger_id']) == 3 and
                int(evo_data['trigger_item_id']) == int(item_id)
            ):
                return int(evo_data['evolved_species_id'])  # Return True as soon as a matching evolution is found

    # If no evolution matches the criteria, return False
    return None

#get pokemon name for next evolution from csv species
#get pokemon id from name
# get from pokemon_evolutions.csv with pokemon evo id the evo trigger id and evolution min_level or item_id

def check_evolution_for_pokemon(individual_id, pokemon_id, level, evo_window, everstone=False):
    """
    Check if a Pokémon evolves using a specific item or level condition.

    Args:
        individual_id (int): The ID of the individual Pokémon.
        id (int): A unique identifier for the Pokémon instance.
        pokemon_id (int): The ID of the Pokémon species.
        level (int): The current level of the Pokémon.
        evo_window (object): The evolution window object for displaying evolution information.
        everstone (bool): Whether the Pokémon is holding an Everstone. Defaults to False.

    Returns:
        int | None: The evolution ID if an evolution is found, or None otherwise.
    """
    if not everstone:
        try:
            # Get the evolution data for the given Pokémon ID
            possible_evos = pokemon_evolves_from_id(pokemon_id)  # Ensure this returns a list of possible evolutions
            if not possible_evos:
                #showWarning("No possible evolutions found")
                return None

            # Check each possible evolution
            for evos in possible_evos:
                evo_data = get_pokemon_evolution_data(int(evos))
                # Only handle level-up evolutions (trigger_id == 1)
                if evo_data and int(evo_data.get("evolution_trigger_id", 0)) == 1:
                    min_level_str = evo_data.get("minimum_level", "")
                    # Only proceed if min_level_str represents a valid integer
                    if not min_level_str or not str(min_level_str).isdigit():
                        continue  # Skip this evolution if minimum_level is missing or not a number
                    min_level = int(min_level_str)
                    if min_level <= level:
                        evo_window.display_pokemon_evo(individual_id, pokemon_id, int(evos))
                        return int(evos)  # Return the evolution ID

            # If no evolutions fit the criteria
            #showWarning("No fitting evolution found for the given level")
            return None
        except Exception as e:
            show_warning_with_traceback(parent=mw, exception=e, message=f"Error checking evolution for Pokémon ID {pokemon_id}")
            return None
    else:
        return None

def check_if_evolution_exists(pokemon_id):
    possible_evos = pokemon_evolves_from_id(pokemon_id)  # Ensure this returns a list of possible evolutions
    if not possible_evos:
        showWarning("No possible evos found")
        return False
    else:
        return possible_evos

def pokemon_evolves_from_id(pokemon_id):
    """Get the list of Pokémon IDs that evolve into the given Pokémon ID
    from the pokemon_species.csv file.
    """
    evolves_from_ids = []  # List to hold the ids of Pokémon that evolve into the given ID
    try:
        # Open the CSV file
        with open(poke_species_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Safely check if 'evolves_from_species_id' exists and is a valid number
                evolves_from_species_id = row.get('evolves_from_species_id', None)
                if evolves_from_species_id:
                    try:
                        # Convert to integer and compare
                        if int(evolves_from_species_id) == int(pokemon_id):
                            evolves_from_ids.append(row['id'])
                    except ValueError:
                        # Handle the case where 'evolves_from_species_id' is not a valid integer
                        continue

        # Return the list of evolves_from_species_id or an empty list if no matches
        #if evolves_from_ids:
        #showWarning(f"Evolves from IDs: {evolves_from_ids}")
        #else:
        #    showWarning(f"No evolutions found for Pokémon ID '{pokemon_id}'")

        return evolves_from_ids
    except Exception as e:
        # Use a more specific error message
        show_warning_with_traceback(exception=e, message="Error in pokemon_evolves_from_id function: {e} with pokemon_id {pokemon_id}")
        return []

def get_pokemon_evolution_data(pokemon_id):
    """Returns the evolution data for a given Pokémon ID by matching evolved_species_id."""
    evolution_data = None  # Initialize variable to hold evolution data

    try:
        # Open the CSV file
        with open(poke_evo_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            # Search for the given Pokémon ID in the evolved_species_id column
            for row in reader:
                try:
                    # Compare the evolved_species_id with the given pokemon_id (as an integer)
                    if int(row['evolved_species_id']) == int(pokemon_id):
                        # If a match is found, store the evolution data
                        evolution_data = row
                        break  # No need to continue once we find a match
                except ValueError:
                    # Handle case where evolved_species_id is not a valid integer
                    continue

        # Check if evolution data was found, log a message if not
        if not evolution_data:
            showWarning(f"No evolution data found for Pokémon ID '{pokemon_id}'")
            pass
    except FileNotFoundError as e:
        show_warning_with_traceback(parent=mw, exception=e, message=f"The evolution data file was not found.")
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message=f"Error retrieving evolution data for Pokémon ID {pokemon_id}")
    return evolution_data

def check_key_in_table(column_name, value, file_path):
    """Checks if a given value exists in the specified column and returns the matching row."""
    matching_row = None  # Initialize variable to hold matching row

    try:
        # Open the CSV file
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            # Search for the value in the specified column
            for row in reader:
                # Use .get() to prevent KeyError if the column doesn't exist
                if row.get(column_name) and str(row[column_name]) == str(value):  # Compare as string for consistency
                    matching_row = row
                    break  # Exit the loop once the matching row is found

    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
    except Exception as e:
        print(f"Error: {e}")

    # Return the matching row or None if no match is found
    return matching_row

def return_name_for_id(pokemon_id):
    """
    For National Pokedex Pokémon ID, return the name (identifier).

    Parameters:
        pokemon_id (int): The ID of the Pokémon to search for.

    Returns:
        str: The name (identifier) of the Pokémon if found.
        None: If no matching Pokémon is found or an error occurs.
    """
    try:
        # Open the CSV file
        with open(pokemon_csv, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)  # Read the file as a dictionary

            # Search for the value in the "id" column
            for row in reader:
                if int(row['id']) == int(pokemon_id):  # Convert CSV id to integer for comparison
                    return row['identifier']  # Return the identifier from the CSV row

        # Log a message if the item is not found
        showWarning(f"Name for Pokemon with ID '{pokemon_id}' not found in the CSV.")
        return None
    except Exception as e:
        # Log any unexpected errors
        show_warning_with_traceback(parent=mw, exception=e, message=f"No evolution data found for Pokémon ID '{pokemon_id}'")(f"Error retrieving name for Pokémon ID '{pokemon_id}': {e}")
        return None

def return_id_for_item_name(item_name):
    """
    Returns the ID of an item based on its name (identifier) from a CSV file.

    Parameters:
        item_name (str): The name of the item to search for.

    Returns:
        str: The ID of the item if found.
        None: If no matching item is found or an error occurs.
    """
    try:
        # Open the CSV file
        with open(csv_file_items_cost, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)  # Read the file as a dictionary

            # Search for the value in the "identifier" column
            for row in reader:
                if row['identifier'] == item_name:  # Check if the identifier matches the item name
                    return row['id']  # Return the id from the CSV row

        # Log a message if the item is not found
        showWarning("warning", f"Item '{item_name}' not found in the CSV.")
        return None
    except Exception as e:
        show_warning_with_traceback(parent=mw, exception=e, message=f"Error retrieving ID for item '{item_name}'")
        return None
