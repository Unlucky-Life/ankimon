import sys
import json
from ..resources import user_path
import os
import uuid
import datetime

new_values = {
    "everstone": False,
    "shiny": False,
    "mega": False,
    "special-form": None,
    "friendship": 0,
    "pokemon_defeated": 0,
    "ability": "No Ability",
    "individual_id": uuid.uuid4(),
    "nickname": "",
    "base_experience": 50,
    "current_hp": 50,
    "growth_rate": "medium-slow",
    "gender": "N",
    "type": ["Normal"],
    "attacks": ["tackle", "growl"],
    "evos": [],
    "id": 132,
    "captured_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}

class DataHandler:
    def __init__(self):
        self.new_values = new_values
        self.path = user_path  # Store the provided path
        self.data = {}         # Store any potential errors or file read issues
        self.read_files()

    def read_files(self):
        # Specify the files to read
        files = ['mypokemon.json', 'mainpokemon.json', 'items.json', 'team.json', 'data.json', 'badges.json']
        
        # Loop through each file and attempt to read it from the specified path
        for file in files:
            file_path = os.path.join(self.path, file)  # Construct full file path
            attr_name = os.path.splitext(file)[0]      # Use the filename without extension as the attribute name

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    if file.endswith('.json'):
                        setattr(self, attr_name, json.load(f))  # Set the file data as an attribute
                    elif file.endswith('.py'):
                        setattr(self, attr_name, f.read())      # Store raw text content if Python file
            except Exception as e:
                self.data[file] = f"Error reading {file}: {e}"  # Store error messages in self.data

    def assign_unique_ids(self, pokemon_list):
        """
        Adds a unique 'individual_id' field to each Pokémon in the provided list,
        but only if an 'individual_id' is not already set.
        Ensures no duplicate IDs are assigned.
        """
        unique_ids = set(pokemon.get("individual_id") for pokemon in pokemon_list if "individual_id" in pokemon)

        for pokemon in pokemon_list:
            # Skip Pokémon that already have an individual_id
            if "individual_id" in pokemon and pokemon["individual_id"]:
                unique_ids.add(pokemon["individual_id"])  # Ensure existing IDs are tracked
                continue

            # Assign a new unique ID
            while True:
                new_id = str(uuid.uuid4())
                if new_id not in unique_ids:
                    pokemon["individual_id"] = new_id
                    unique_ids.add(new_id)
                    break
    
    def assign_new_variables(self, pokemon_list):
        """
        Adds new fields to each Pokémon in the provided list.
        Sets their default values only if they're not already set.
        The new_values parameter should be a dictionary where the keys are the field names
        and the values are the default values.
        """
        for pokemon in pokemon_list:
            for field, default_value in self.new_values.items():
                if field not in pokemon:  # Check if the field is not already set
                    pokemon[field] = default_value
 
    def save_file(self, attr_name):
        """
        Save the updated content back to its respective JSON file.
        """
        if hasattr(self, attr_name):
            file_path = os.path.join(self.path, f"{attr_name}.json")
            try:
                with open(file_path, 'w') as f:
                    json.dump(getattr(self, attr_name), f, indent=2)
            except Exception as e:
                self.data[file_path] = f"Error saving {file_path}: {e}"
