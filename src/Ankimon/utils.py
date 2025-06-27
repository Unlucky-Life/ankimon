import os
import requests
import json
import markdown
import random
import csv
from .resources import battlescene_path, berries_path, items_path, itembag_path, csv_file_items_cost, csv_file_descriptions, items_list_path, font_path
from aqt.utils import showWarning, showInfo
from collections import Counter
from PyQt6.QtGui import QFontDatabase, QFont
from aqt import mw

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
def give_item(item_name):
    with open(itembag_path, "r", encoding="utf-8") as json_file:
        itembag_list = json.load(json_file)
        # Check if the item exists and update quantity, otherwise append
        for item in itembag_list:
            if item.get("item") == item_name:
                item["quantity"] += 1
                break
        else:
            # Add a new item if not found
            itembag_list.append({"item": item_name, "quantity": 1})
    with open(itembag_path, 'w', encoding="utf-8") as json_file:
        json.dump(itembag_list, json_file)
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

import os

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

