import random
import json
from ..resources import effectiveness_chart_file_path
from .battle_text_functions import effectiveness_text

def get_effectiveness(move_type, def_type):
    move_type = move_type.capitalize()
    attacking_types = []
    attacking_types.append(move_type)
    defending_types = def_type
    attacking_types = [attacking_type.capitalize() for attacking_type in attacking_types]
    defending_types = [defending_type.capitalize() for defending_type in defending_types]
    with open(effectiveness_chart_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        # Find the effectiveness values for each attacking type
        effectiveness_values = []
        for attacking_type in attacking_types:
            if attacking_type in data:
                # Find the effectiveness values for each defending type
                eff_values = [data[attacking_type][defending_type] for defending_type in defending_types]
                effectiveness_values.extend(eff_values)  # Use extend to add values to the list
        if effectiveness_values:
            if len(effectiveness_values) > 1:
                # Multiply all values in the list
                eff_value = 1
                for value in effectiveness_values:
                    eff_value *= value
                effective_txt = effectiveness_text(eff_value)
                return eff_value
            else:
                effective_txt = effectiveness_text(effectiveness_values[0])
                return effectiveness_values[0]
    # If the combination is not found, return None or a default value
    return None

def calc_atk_dmg(level, critical, power, stat_atk, wild_stat_def, main_type, move_type, wild_type, critRatio):
        if power is None:
            # You can choose a default power or handle it according to your requirements
            power = 0
        if critRatio == 1:
            crit_chance = 0.0417
        elif critRatio == 2:
            crit_chance = 0.125
        elif critRatio == 3:
            crit_chance = 0.5
        elif critRatio > 3:
            crit_chance = 1
        random_number = random.random()  # Generate a random number between 0 and 1
        if random_number > crit_chance:
            critical = critical * 1
        else:
            critical += 2
        stab = 1.5 if move_type == main_type else 1.0
        eff = get_effectiveness(move_type, wild_type)
        # random luck
        random_number = random.randint(217, 255)
        random_factor = random_number / 255
        damage = (((((2 * level * critical) + 2) / 5) * power * stat_atk / wild_stat_def) + 2) / 50 * stab * eff * random_factor
        # if main pkmn type = move type => damage * 1,5
        # if wild pokemon type x main pokemon type => 0.5 not very eff.; 1.0 eff.; 2 very eff.
        return damage

def calculate_hp(base_stat_hp, level, ev, iv):
    ev_value = ev["hp"] / 4
    iv_value = iv["hp"]
    #hp = int(((iv + 2 * (base_stat_hp + ev) + 100) * level) / 100 + 10)
    hp = int((((((base_stat_hp + iv_value) * 2 ) + ev_value) * level) / 100) + level + 10)
    return hp

def status_effect(pokemon_obj, move, slp_counter, msg, acc):
    # Extend the existing dictionary with the "Fighting" status
    stats = pokemon_obj._battle_stats
    stat = pokemon_obj.battle_status
    hp = pokemon_obj.hp
    name = pokemon_obj.name
    if stat == "par":
        stats["spe"] = stats["spe"] * 0.5
        msg += f" {name.capitalize()}'s speed is reduced."
        missing_chance = 1/4
        random_number = random.random()
        if random_number < missing_chance:
            msg += (f"{name} is paralyzed! It can't move!")
            acc = 0
    elif stat == "brn":
        dmg = 1/16 * pokemon_obj.calculate_max_hp()
        hp -= dmg
        msg += (f"Wild {name} was hurt by burning!")
    elif stat == "psn":
        max_hp = pokemon_obj.calculate_max_hp()
        dmg = 1 / 8 * max_hp
        hp -= dmg
        msg += (f"The wild {name} was hurt by its poisoning!")
    elif stat == "tox":
        max_hp = pokemon_obj.calculate_max_hp()
        dmg = ((random.randint(1,3)) / 16 * max_hp)
        hp -= dmg
        msg += (f"The wild {name} is badly poisoned and was hurt by is poisoning!")
        stat = "psn"
    elif stat == "frz":
        free_chance = 20 / 100
        if move["type"] == "fire" and move["target"] != "self":
            free_chance = 1
        random_number = random.random()
        if random_number < free_chance:
            msg += (f"Wild {name} is frozen solid!")
            acc = 0
        else:
            stat = None
            msg += (f"Wild {name} is no longer frozen!")
    elif stat == "slp":
            if slp_counter > 1:
                slp_counter -= 1
                msg += (f"Wild {name} is asleep!")
            else:
                stat = None
                msg += (f"Wild {name} is no longer asleep!")
    return msg, acc, stat, battle_stats