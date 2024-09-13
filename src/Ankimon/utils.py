import os
import requests
import json
import markdown

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
