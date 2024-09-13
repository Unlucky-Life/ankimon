import os
import requests
import json
import markdown
import random

from .resources import battlescene_path, berries_path, items_path, itembag_path

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
        
        #dont show all mainpokemon and mypokemon information in config
        if "pokemon_collection" in config:
            del config["pokemon_collection"]
        if "mainpokemon" in config:
            del config["mainpokemon"]
        
        # Convert back to JSON string
        modified_text = json.dumps(config, indent=4)
        return modified_text
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
    with open(itembag_path, 'r') as json_file:
        itembag_list = json.load(json_file)
        itembag_list.append(item_name)
    with open(itembag_path, 'w') as json_file:
        json.dump(itembag_list, json_file)
    return item_name

def random_fossil():
    fossil_names = []
    # Iterate over each file in the directory
    for file in os.listdir(items_path):
        # Check if the file is a .png file
        if file.endswith("-fossil.png"):
            # Append the file name without the .png extension to the list
            fossil_names.append(file[:-4])
    fossil_name = random.choice(fossil_names)
    with open(itembag_path, 'r') as json_file:
        itembag_list = json.load(json_file)
        itembag_list.append(fossil_name)
    with open(itembag_path, 'w') as json_file:
        json.dump(itembag_list, json_file, indent=2)
    return fossil_name