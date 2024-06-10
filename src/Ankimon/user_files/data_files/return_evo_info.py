import csv
from pathlib import Path
file_dir = Path(__file__).parents[0]

def get_evolution_entry(evolved_species_id):
    evolved_species_id = str(evolved_species_id)
    with open(f'{file_dir}/pokemon_evolution.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == evolved_species_id:
                keys = ["id", "evolved_species_id", "evolution_trigger_id", "trigger_item_id", "minimum_level",
            "gender_id", "location_id", "held_item_id", "time_of_day", "known_move_id", "known_move_type_id",
            "minimum_happiness", "minimum_beauty", "minimum_affection", "relative_physical_stats", "party_species_id",
            "party_type_id", "trade_species_id", "needs_overworld_rain", "turn_upside_down"]
                return dict(zip(keys, row))
    return None

# evolved_species_id = input("Enter the evolved species ID: ")
# entry = get_evolution_entry(evolved_species_id)
# if entry:
#     print("Evolution entry:", entry)
# else:
#     print("No entry found for the given evolved species ID.")

# value = input("Key: ")
# info = entry.get(f"{value}", "No entry found for the given evolved species ID.")
# print(info)

def get_item_id(item_name):
    with open(f'{file_dir}/items.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == item_name:
                return row[0]
    return None

#item_name = input("Enter the item name: ")
#item_id = get_item_id(item_name)
#if item_id:
#    print("Item ID:", item_id)
#else:
    #print("Item not found.")