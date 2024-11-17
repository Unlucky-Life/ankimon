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
        eff = get_effectiveness(move_type)
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