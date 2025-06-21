import os
from pathlib import Path
from typing import Union
import requests
import json
import markdown
import random
import csv
from collections import Counter

from aqt.utils import showWarning, showInfo
from PyQt6.QtGui import QFontDatabase, QFont

from . import audios
from .pyobj.settings import Settings
from .pyobj.InfoLogger import ShowInfoLogger
from .functions.battle_functions import calculate_hp
from .functions.pokedex_functions import find_details_move, search_pokedex
from .resources import (
    battlescene_path,
    berries_path,
    items_path,
    itembag_path,
    csv_file_items_cost,
    csv_file_descriptions,
    font_path,
    pokemon_names_file_path,
    move_names_file_path,
    hurt_normal_sound_path,
    hurt_noteff_sound_path,
    hurt_supereff_sound_path,
    hpheal_sound_path,
    ownhplow_sound_path,
    fainted_sound_path,
    mypokemon_path,
    mainpokemon_path,
    addon_dir,
)

# Load move and pokemon name mapping at startup
with open(pokemon_names_file_path, "r", encoding="utf-8") as f:
    POKEMON_NAME_LOOKUP = json.load(f)
with open(move_names_file_path, "r", encoding="utf-8") as f:
    MOVE_NAME_LOOKUP = json.load(f)


def format_pokemon_name(name: str) -> str:
    """
    Look up the official Pokémon name using the normalized key.
    Falls back to capitalizing if not found.
    """
    key = name.replace(" ", "").replace("-", "").replace("_", "").lower()
    return POKEMON_NAME_LOOKUP.get(key, name.capitalize())

def format_move_name(move: str) -> str:
    """
    Look up the official move name using the normalized key.
    Falls back to title-casing with spaces if not found.
    """
    key = move.replace(" ", "").replace("-", "").replace("_", "").lower()
    return MOVE_NAME_LOOKUP.get(key, " ".join(word.capitalize() for word in move.replace("_", " ").split()))
    
def check_folders_exist(parent_directory, folder):
    folder_path = os.path.join(parent_directory, folder)
    return os.path.isdir(folder_path)

def check_file_exists(folder, filename):
    file_path = os.path.join(folder, filename)
    return os.path.isfile(file_path)

def test_online_connectivity(url='https://raw.githubusercontent.com/Unlucky-Life/ankimon/main/update_txt.md', timeout=5):
    try:
        # Attempt to get the URL
        response = requests.get(url, timeout=timeout)

        # Check if the response status code is 200 (OK)
        if response.status_code == 200:
            return True
    except:
        # Connection error means no internet connectivity
        return False
    

# Define the hook function
def addon_config_editor_will_display_json(text: str) -> str:
    """
    This function modifies the JSON configuration text before displaying it to the user.
    It replaces the values for the keys "pokemon_collection" and "mainpokemon".
    
    Args:
        text (str): The JSON configuration text.
    
    Returns:
        str: The modified JSON configuration text.
    """
    try:
        # Parse the JSON text
        config = json.loads(text)
        if "mainpokemon" in config:
            #showInfo(f"{config}")
            showInfo("This Configuration is old and wont be used anymore. \n Please use the Settings Window in the Ankimon Menu => Settings")
            #mw.settings_ankimon.show_window()
            #dont show all mainpokemon and mypokemon information in config
            if "pokemon_collection" in config:
                del config["pokemon_collection"]
            if "mainpokemon" in config:
                del config["mainpokemon"]
            if "trainer.cash" in config:
                del config["trainer.cash"]
        
        
            # Convert back to JSON string
            modified_text = json.dumps(config, indent=4)
            return modified_text
        return text
    except json.JSONDecodeError:
        # Handle JSON parsing error
        return text
    
# Function to read the content of the local file
def read_local_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return None
    
# Function to check if the file exists on GitHub and read its content
def read_github_file(url):
    response = requests.get(url)
        
    if response.status_code == 200:
        # File exists, parse the Markdown content
        content = response.text
        html_content = markdown.markdown(content)
        return content, html_content
    else:
        return None, None

# Function to check if the content of the two files is the same
def compare_files(local_content, github_content):
    return local_content == github_content

# Function to write content to a local file
def write_local_file(file_path, content):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def read_html_file(file_path):
    """Reads an HTML file and returns its content as a string."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    
def random_battle_scene():
    # TODO: choice?
    # TODO: merge with random_berries and
    battle_scenes = {}
    for index, filename in enumerate(os.listdir(battlescene_path)):
        if filename.endswith(".png"):
            battle_scenes[index + 1] = filename
    # Get the corresponding file name
    battlescene_file = battle_scenes.get(random.randint(1, len(battle_scenes)))
    return battlescene_file

def random_berries():
    berries = {}
    for index, filename in enumerate(os.listdir(berries_path)):
        if filename.endswith(".png"):
            berries[index + 1] = filename
    # Get the corresponding file name
    berries_file = berries.get(random.randint(1, len(berries)))
    return berries_file

def filter_item_sprites(string):
    # Initialize an empty list to store the file names
    item_names = []
    # Iterate over each file in the directory
    for file in os.listdir(items_path):
        # Check if the file is a .png file
        if file.endswith(".png"):
            # Append the file name without the .png extension to the list
            item_names.append(file[:-4])
    #filter by -ball, -repel..etc
    item_names = [name for name in item_names if name.endswith(f"{string}")]
    showInfo(f"{item_names}")
    return item_names

def random_item():
    # Initialize an empty list to store the file names
    item_names = []
    # Iterate over each file in the directory
    for file in os.listdir(items_path):
        # Check if the file is a .png file
        if file.endswith(".png"):
            # Append the file name without the .png extension to the list
            item_names.append(file[:-4])
    item_names = [name for name in item_names if not name.endswith("-ball")]
    item_names = [name for name in item_names if not name.endswith("-repel")]
    item_names = [name for name in item_names if not name.endswith("-incense")]
    item_names = [name for name in item_names if not name.endswith("-fang")]
    item_names = [name for name in item_names if not name.endswith("dust")]
    item_names = [name for name in item_names if not name.endswith("-piece")]
    item_names = [name for name in item_names if not name.endswith("-nugget")]
    item_name = random.choice(item_names)
    # add item to item list
    give_item(item_name)
    return item_name

# Function to get the list of daily items
def daily_item_list():
    item_names = []
    # You may want to fetch more information, such as description and price
    for file in os.listdir(items_path):
        if file.endswith(".png"):
            item_name = file[:-4]
            if not item_name.endswith("dust") and not item_name.endswith("-piece") and not item_name.endswith("-nugget") and get_item_price(item_name) != 0:
                item_names.append({
                    "name": item_name,
                    "description": f"Item: {item_name}",
                    "price": get_item_price(item_name)  # You need to ensure this returns the correct price
                })
    return item_names

# Function to give an item to the player
def give_item(item_name, item_type: Union[str, None]=None):
    with open(itembag_path, "r", encoding="utf-8") as json_file:
        itembag_list = json.load(json_file)
        # Check if the item exists and update quantity, otherwise append
        for item in itembag_list:
            if item.get("item") == item_name:
                item["quantity"] += 1
                break
        else:
            # Add a new item if not found
            item_dict = {"item": item_name, "quantity": 1}
            if item_type is not None:
                item_dict["type"] = item_type
            itembag_list.append(item_dict)
    with open(itembag_path, 'w', encoding="utf-8") as json_file:
        json.dump(itembag_list, json_file, indent=4)
    #logger.log_and_showinfo('game', f"Player bought item {item_name.capitalize()}")

#Function to return a cost of an item
def get_item_price(item_name, file_path=csv_file_items_cost):
    """
    Returns the cost of an item from a CSV file based on its identifier (name).

    Parameters:
        file_path (str): Path to the CSV file.
        item_name (str): The identifier (name) of the item.

    Returns:
        int: The cost of the item, or None if the item is not found or has no id.
    """
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['identifier'] == item_name:
                    cost = row['cost']
                    return int(cost)
    except FileNotFoundError:
        showWarning(f"Error: File {file_path} not found.")
        return int(1000)
    except KeyError:
        showWarning("Error: CSV file does not contain the expected headers.")
        return int(1000)
    except Exception as e:
        showWarning(f"Unexpected error: {e}")
        return int(1000)

    return None

#Function to return a cost of an item
def get_item_id(item_name, file_path=csv_file_items_cost):
    """
    Returns the cost of an item from a CSV file based on its identifier (name).

    Parameters:
        file_path (str): Path to the CSV file.
        item_name (str): The identifier (name) of the item.

    Returns:
        int: The id of the item, or None if the item is not found or has no id.
    """
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['identifier'] == item_name:
                    id = row['id']
                    return int(id)
    except FileNotFoundError:
        showWarning(f"Error: File {file_path} not found.")
        return int(4)
    except KeyError:
        showWarning("Error: CSV file does not contain the expected headers.")
        return int(4)
    except Exception as e:
        showWarning(f"Unexpected error: {e}")
        return int(4)

#Function to return a random fossil
def random_fossil():
    fossil_names = []
    # Iterate over each file in the directory
    for file in os.listdir(items_path):
        # Check if the file is a .png file
        if file.endswith("-fossil.png"):
            # Append the file name without the .png extension to the list
            fossil_names.append(file[:-4])
    fossil_name = random.choice(fossil_names)
    give_item(fossil_name)
    return fossil_name

def count_items_and_rewrite(file_path):
    """
    Reads the items.json file, counts item occurrences, 
    and rewrites the file with items and their quantities in the form of dictionaries.
    
    :param file_path: Path to the items.json file.
    """
    try:
        # Read the existing file
        with open(file_path, "r", encoding="utf-8") as file:
            items = json.load(file)

        # Ensure the file contains a list
        if not isinstance(items, list):
            raise ValueError("The items.json file should contain a list of item names.")

        # Count the occurrences of each item
        item_counts = Counter(items)

        # Create a list of dictionaries with item names and their quantities
        updated_items = [{"item": item, "quantity": count} for item, count in item_counts.items()]

        # Rewrite the file with the updated list
        with open(file_path, 'w') as file:
            json.dump(updated_items, file, indent=4)

        print("items.json has been updated with item quantities!")
    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON. Ensure the file contains valid JSON data.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Assuming the data is stored in a CSV file named 'item_flavor_texts.csv'
def get_item_description(item_name, language_id):
    """
    Fetch the flavor text for an item based on its item_id, version_group_id, and language_id.
    => get item_id from item_name via items.csv
    :param item_id: The ID of the item.
    :param language_id: The language ID for the flavor text.
    :param file_path: The path to the CSV file containing the flavor texts.
    :return: The flavor text if found, otherwise None.
    """
    try:
        item_id = get_item_id(item_name)
        file_path=csv_file_descriptions
        # Open the CSV file and read the contents
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Iterate through each row in the CSV
            for row in reader:
                # Check if the current row matches the item_id, version_group_id, and language_id
                if (int(row['item_id']) == item_id and
                        int(row['language_id']) == language_id):
                    return row['flavor_text']  # Return the matching flavor text
        
        # If no match is found, return None
        return None
    
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
def load_custom_font(font_size, language):
    if language == 1:
        font_file = "pkmn_w.ttf"
        font_file_path = font_path / font_file
        font_size = int((font_size * 1) / 2)
        if font_file_path.exists():
            font_name = "PKMN Western"
        else:
            font_name = "Early GameBoy"
            font_file = "Early GameBoy.ttf"
            font_size = int((font_size * 5) / 7)
    else:
        font_name = "Early GameBoy"
        font_file = "Early GameBoy.ttf"
        font_size = int((font_size * 2) / 5)

    # Register the custom font with its file path
    QFontDatabase.addApplicationFont(str(font_path / font_file))
    custom_font = QFont(font_name)  # Use the font family name you specified in the font file
    custom_font.setPointSize(int(font_size))  # Adjust the font size as needed

    return custom_font

def get_all_sprites(directory):
    """
    Returns a list of trainer sprite names without the '.png' extension
    from the specified directory.
    
    :param directory: Path to the directory containing trainer sprite images.
    :return: List of sprite names without '.png'.
    """
    try:
        sprite_names = [
            os.path.splitext(file)[0]  # Remove the file extension
            for file in os.listdir(directory)
            if file.endswith(".png")  # Filter for .png files
        ]
        return sprite_names
    except FileNotFoundError:
        print(f"Error: The directory '{directory}' does not exist.")
        return []
    
def play_effect_sound(sound_type):
    sound_effects = Settings().get("audio.sound_effects", False)
    if sound_effects is True:
        audio_path = None
        if sound_type == "HurtNotEffective":
            audio_path = hurt_noteff_sound_path
        elif sound_type == "HurtNormal":
            audio_path = hurt_normal_sound_path
        elif sound_type == "HurtSuper":
            audio_path = hurt_supereff_sound_path
        elif sound_type == "OwnHpLow":
            audio_path = ownhplow_sound_path
        elif sound_type == "HpHeal":
            audio_path = hpheal_sound_path
        elif sound_type == "Fainted":
            audio_path = fainted_sound_path

        if not audio_path.is_file():
            return
        else:   
            audio_path = Path(audio_path)
            #threading.Thread(target=playsound.playsound, args=(audio_path,)).start()
            audios.will_use_audio_player()
            audios.audio(audio_path)
    else:
        pass

def save_error_code(error_code, logger=None):
    error_fix_msg = ""
    try:
        # Find the position of the phrase "can't be transferred from Gen"
        index = error_code.find("can't be transferred from Gen")

        # Extract the substring starting from this position
        relevant_text = error_code[index:]

        # Find the first number in the extracted text (assuming it's the generation number)
        generation_number = int(''.join(filter(str.isdigit, relevant_text)))

        # Show the generation number
        error_fix_msg += (f"\n Please use Gen {str(generation_number)[0]} or lower")

        index = error_code.find("can't be transferred from Gen")

        # Extract the substring starting from this position
        relevant_text = error_code[index:]

        # Find the first number in the extracted text (assuming it's the generation number)
        generation_number = int(''.join(filter(str.isdigit, relevant_text)))

        error_fix_msg += (f"\n Please use Gen {str(generation_number)[0]} or lower")

    except Exception as e:
        if logger is not None:
            logger.log_and_showinfo("info",f"An error occurred: {e}")

    if logger is not None:
        logger.log_and_showinfo("info",f"{error_fix_msg}")

def get_main_pokemon_data():
    with (open(str(mainpokemon_path), "r", encoding="utf-8") as json_file):
        main_pokemon_datalist = json.load(json_file)

    main_pokemon_data = []
    for main_pokemon_data in main_pokemon_datalist:
        _name = main_pokemon_data["name"]
        if not main_pokemon_data.get('nickname') or main_pokemon_data.get('nickname') is None:
            _nickname = None
        else:
            _nickname = main_pokemon_data['nickname']
        _id = main_pokemon_data["id"]
        _ability = main_pokemon_data["ability"]
        _type = main_pokemon_data["type"]
        _stats = main_pokemon_data["stats"]
        _attacks = main_pokemon_data["attacks"]
        _level = main_pokemon_data["level"]
        _hp_base_stat = main_pokemon_data["stats"]["hp"]
        _evolutions = search_pokedex(main_pokemon_data["name"], "evos")
        _xp = main_pokemon_data.get("xp") or main_pokemon_data["stats"].get("xp", 0)
        _ev = main_pokemon_data["ev"]
        _iv = main_pokemon_data["iv"]
        #mainpokemon_battle_stats = mainpokemon_stats
        _battle_stats = {}
        for d in [_stats, _iv, _ev]:
            for key, value in d.items():
                _battle_stats[key] = value
        #mainpokemon_battle_stats += mainpokemon_iv
        #mainpokemon_battle_stats += mainpokemon_ev
        _hp = calculate_hp(_hp_base_stat, _level, _ev, _iv)
        _current_hp = _hp
        _base_experience = main_pokemon_data["base_experience"]
        _growth_rate = main_pokemon_data["growth_rate"]
        _gender = main_pokemon_data["gender"]
        
        return (
            _name,
            _id,
            _ability,
            _type,
            _stats,
            _attacks,
            _level,
            _base_experience,
            _xp,
            _hp,
            _current_hp,
            _growth_rate,
            _ev,
            _iv,
            _evolutions,
            _battle_stats,
            _gender,
            _nickname
        )

def play_sound(enemy_pokemon_id: int, settings_obj: Settings):
    if settings_obj.get("audio.sounds", False):
        file_name = f"{enemy_pokemon_id}.ogg"
        audio_path = addon_dir / "user_files" / "sprites" / "sounds" / file_name
        if audio_path.is_file():
            audio_path = Path(audio_path)
            audios.will_use_audio_player()
            audios.audio(audio_path)

def load_collected_pokemon_ids() -> set:
    if not mypokemon_path.is_file():
        return set()
    
    collected_pokemon_ids = set()
    try:
        with open(mypokemon_path, "r", encoding="utf-8") as f:
            collection = json.load(f)
            collected_pokemon_ids = {pkmn["id"] for pkmn in collection}
    except Exception as e:
        ShowInfoLogger().log("error", f"Error loading collection cache: {str(e)}")
    
    return collected_pokemon_ids

def limit_ev_yield(current_pokemon_ev: dict[str, int], ev_yield: dict[str, int]) -> dict[str, int]:
    """
    Limits the EV (Effort Value) yield for a Pokémon based on current EVs and Pokémon game rules.

    Ensures that the total EVs after applying the yield do not exceed 510, and that no single
    stat exceeds 252 EVs. Adjusts the EV yield to comply with these constraints by capping individual
    stats and reducing EVs randomly if the total would exceed the maximum allowed.

    Args:
        current_pokemon_ev (dict[str, int]): Current EVs of the Pokémon, with keys as stat abbreviations 
            ("hp", "atk", "def", "spa", "spd", "spe") and values as their EV amounts.
        ev_yield (dict[str, int]): Proposed EV yields from a defeated Pokémon, with keys as full stat names 
            ("hp", "attack", "defense", "special-attack", "special-defense", "speed") and values as EV amounts.

    Raises:
        ValueError: If any key in `current_pokemon_ev` or `ev_yield` is not a recognized stat.

    Returns:
        dict[str, int]: Adjusted EV yields that do not cause the Pokémon's total EVs to exceed 510 or any
        single stat to exceed 252. The keys correspond to full stat names.
    """
    # The sum of EVs of a Pokemon can only add up to 510. With a limit of 252 EVs in a single stat.
    for stat in current_pokemon_ev.keys():
        if stat not in ("hp", "atk", "def", "spa", "spd", "spe"):
            raise ValueError(f"Unknown EV : {stat}")
        
    for stat in ev_yield.keys():
        if stat not in ("hp", "attack", "defense", "special-attack", "special-defense", "speed"):
            raise ValueError(f"Unknown EV : {stat}")
        
    zipped_keys = zip(
        ["hp", "atk", "def", "spa", "spd", "spe"],
        ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
    )
        
    new_ev_yield = {"hp": 0, "attack": 0, "defense": 0, "special-attack": 0, "special-defense": 0, "speed": 0}
    
    for key_1, key_2 in zipped_keys:
        # For each stat, we yield an amount of EVs that will not exceed the value of 252
        new_ev_yield[key_2] = min(ev_yield[key_2], 252 - current_pokemon_ev[key_1])

    # To ensure that we won't go above 510 EVs after yielding the EVs, we randomly reduce the EV yield until we drop below the 510 limit
    while (sum(current_pokemon_ev.values()) + sum(new_ev_yield.values())) > 510:
        rand_key = [key for key, val in new_ev_yield.items() if val > 0]  # We only reduce the positive EV yield values. In other words : We don't give out negative EV yields
        if len(rand_key) == 0:
            break
        rand_key = random.choice(rand_key)
        new_ev_yield[rand_key] -= 1

    # This final block here is specifically made to give out negative EV yields
    # This might be necessary if, for any reason, the user's pokemon has a total EV sum already above 510
    # In that case, we randomly give out negative EV yields to bring down the EVs of the user's pokemon below 510
    while (sum(current_pokemon_ev.values()) + sum(new_ev_yield.values())) > 510:
        rand_key = random.choice(list(new_ev_yield.keys()))  # This time, we choose any EV yields, including those that could already have a negative EV yield
        new_ev_yield[rand_key] -= 1

    return new_ev_yield

def iv_rand_gauss(mu: float=15, sigma: float=5) -> int:
    """
    Generates a random individual value (IV) using a Gaussian distribution,
    clamped to the range [0, 31].

    Args:
        mu (float, optional): The mean of the Gaussian distribution. Defaults to 15.
        sigma (float, optional): The standard deviation of the Gaussian distribution. Defaults to 5.

    Returns:
        int: An integer IV value between 0 and 31 inclusive.
    """
    rand = random.gauss(mu, sigma)
    rand = max(0, rand)  # ensures that rand >= 0
    rand = min(31, rand)  # ensures that rand <= 31
    return int(rand)

def get_ev_spread(mode: str="random") -> dict[str, int]:
    """
    Generate an EV (Effort Value) spread for Pokémon stats based on the specified mode.

    Args:
        mode (str): The mode of EV distribution. Supported modes are:
            - "random": Randomly distributes up to 510 EVs across stats using a uniform distribution,
                        with each stat capped at 252 EVs.
            - "pair": Assigns 252 EVs to two random stats and 4 EVs to a third random stat.
            - "defense": Returns a predefined defensive spread with 252 EVs in Defense and Special Defense,
                         and 4 EVs in HP.
            - "uniform": Distributes EVs evenly (84 EVs) across all stats.

    Returns:
        dict[str, int]: A dictionary mapping each stat ("hp", "atk", "def", "spa", "spd", "spe")
                        to its corresponding EV value according to the selected mode.
    """
    stat_names = ["hp", "atk", "def", "spa", "spd", "spe"]
    if mode == "random":  # Draws each EV following a uniform probability distribution
        cuts = sorted(random.sample(range(510 + 1), 6 - 1))
        parts = [a - b for a, b in zip(cuts + [510], [0] + cuts)]
        parts = [min(252, part) for part in parts]
        evs = {stat: val for stat, val in zip(stat_names, parts)}
        return evs
    elif mode == "pair":  # Draws 2 stats at 252 EVs, and a 3rd at 4 EVs
        ev = {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
        stats = random.sample(stat_names, 3)
        ev[stats[0]] = 252
        ev[stats[1]] = 252
        ev[stats[2]] = 4
        return ev
    elif mode == "defense":
        return {"hp": 4, "atk": 0, "def": 252, "spa": 0, "spd": 252, "spe": 0}
    elif mode == "uniform":
        return {"hp": 84, "atk": 84, "def": 84, "spa": 84, "spd": 84, "spe": 84}
    
    raise ValueError(f"Received unknown value for 'mode': {mode}")

def safe_get_random_move(
    pokemon_moves: list[str],
    logger: Union[ShowInfoLogger, None] = None
) -> dict:
    """
    Attempts to retrieve details of a randomly selected move from a list of Pokémon moves.

    This function shuffles the provided list of move names and tries to find the first
    move for which details can be successfully retrieved using `find_details_move`. If no
    valid move is found, it logs a warning (if a logger is provided) and defaults to
    returning the details for the move "Splash".

    Args:
        pokemon_moves (list[str]): A list of move names to select from.
        logger (Union[ShowInfoLogger, None], optional): An optional logger instance for
            logging warnings if no valid move is found. Defaults to None.

    Returns:
        dict: A dictionary containing the details of a valid move if found;
            otherwise, the details for the move "Splash".
    """
    rand_moves = pokemon_moves.copy()
    random.shuffle(rand_moves)
    # We go through the shuffled list to find the first move that gets successfully parsed
    for move in rand_moves:
        move_details = find_details_move(move) or find_details_move(
            format_move_name(move)
        )
        if move_details is not None:
            return move_details
        else:
            if logger is not None:
                logger.log(
                    "warning",
                    f"Could not parse the following move : {str(move)}",
                )

    # If we fail to successfully parse a single move, we just return Splash
    if logger is not None:
        logger.log(
            "warning",
            f"Could not parse a single move in the following moveset : {str(pokemon_moves)}",
        )
    return find_details_move(format_move_name("splash"))