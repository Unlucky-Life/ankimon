from ..resources import pokedex_path, pokedesc_lang_path, pokeapi_db_path, pokenames_lang_path, mypokemon_path
from aqt.utils import showWarning
import json
import random
import csv

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
        #showWarning("Error in Handling Pokémon name")
        return name

def search_pokedex(pokemon_name,variable):
    pokemon_name = special_pokemon_names_for_min_level(pokemon_name)
    with open(str(pokedex_path), "r", encoding="utf-8") as json_file:
            pokedex_data = json.load(json_file)
            if pokemon_name in pokedex_data:
                pokemon_info = pokedex_data[pokemon_name]
                var = pokemon_info.get(variable, None)
                return var
            else:
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
            return descriptions
    else:
        ["Description not found."]

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
        with open(filename, 'r') as file:
            data = json.load(file)
            ids = [character['id'] for character in data]
            owned_pokemon_ids = ids
            return owned_pokemon_ids
    except Exception as e:
        showWarning(f"Error: {e} with function extract_ids_from_file")
        return []