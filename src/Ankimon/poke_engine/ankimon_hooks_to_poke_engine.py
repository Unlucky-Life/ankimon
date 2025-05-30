import random
from collections import defaultdict
import copy

from .battle import Move
from .objects import Pokemon, State, StateMutator, Side
from .helpers import normalize_name
from .find_state_instructions import get_all_state_instructions
from ..pyobj.InfoLogger import ShowInfoLogger

#logger = ShowInfoLogger()

def reset_pokemon(
    state: State,
    mutator_full_reset: int,
    main_pokemon_obj: Pokemon,
    enemy_pokemon_obj: Pokemon,
    side_conditions: dict,
    ):
    """
    Resets the battle state for both the user's and opponent's Pokémon based on the value of 
    `mutator_full_reset`. The function creates new `Side` objects for both the user and the opponent, 
    adjusting their active Pokémon, reserves, wishes, side conditions, and future sight. 
    It also updates the weather, field, and trick room conditions if necessary.

    Args:
        state (State): The current battle state, including user and opponent sides, and battle conditions.
        mutator_full_reset (int): A flag that determines how the battle state is reset:
            - 0: Keep both user and opponent sides unchanged.
            - 1: Reset both user and opponent sides.
            - 2: Keep the user side unchanged, reset the opponent side.
        main_pokemon_obj (Pokemon): The user's active Pokémon object used in the reset.
        enemy_pokemon_obj (Pokemon): The opponent's active Pokémon object used in the reset.
        side_conditions (dict): A dictionary containing any active side conditions (e.g., Stealth Rock, Spikes).

    Returns:
        State: A new `State` object with the updated user and opponent sides, weather, field, and trick room conditions.

    Notes:
        - The `mutator_full_reset` value determines whether the user, the opponent, or both sides are reset.
        - If `mutator_full_reset` is set to 1, both the user and opponent sides will be reset.
        - If `mutator_full_reset` is set to 2, the user side will remain unchanged, but the opponent side will be reset.
        - The weather, field, and trick room conditions are reset to `None` if `mutator_full_reset` is 1.
    """

    # mutator_full_reset == 0 : Keep the USER side, keep the enemy side
    # mutator_full_reset == 1 : reset both sides
    # mutator_full_reset == 2 : Keep the USER side, reset the enemy side

    user_side = Side(
        active=main_pokemon_obj if mutator_full_reset == 1 else state.user.active,
        reserve={} if mutator_full_reset == 1 else state.user.reserve,
        wish=(0, 0) if mutator_full_reset == 1 else state.user.wish,
        side_conditions=side_conditions.copy() if mutator_full_reset == 1 else state.user.side_conditions,
        future_sight=(0, 0) if mutator_full_reset == 1 else state.user.future_sight,
    )

    opponent_side = Side(
        active=enemy_pokemon_obj if mutator_full_reset in (1, 2) else state.opponent.active,
        reserve={} if mutator_full_reset in (1, 2) else state.opponent.reserve,
        wish=(0, 0) if mutator_full_reset in (1, 2) else state.opponent.wish,
        side_conditions=side_conditions.copy() if mutator_full_reset in (1, 2) else state.opponent.side_conditions,
        future_sight=(0, 0) if mutator_full_reset in (1, 2) else state.opponent.future_sight,
    )

    weather = None if mutator_full_reset == 1 else state.weather,
    field = None if mutator_full_reset == 1 else state.field,
    trick_room = None if mutator_full_reset == 1 else state.trick_room

    new_state = State(
        user=user_side,
        opponent=opponent_side,
        weather =weather,
        field=field,
        trick_room=trick_room
    )

    return new_state

def simulate_battle_with_poke_engine(
    main_pokemon: Pokemon,
    enemy_pokemon: Pokemon,
    main_move: str,
    enemy_move: str,
    new_state: State,
    mutator_full_reset: int,
    traceback: "module"
    ):
    """
    Simulates a battle between two Pokémon using the poke-engine if available. 
    The function selects the Pokémon moves (either provided or random), handles state changes, 
    and applies battle instructions based on the current battle state. The function then 
    computes and returns the battle results, including damage dealt, missed moves, 
    and the updated battle state.

    Args:
        main_pokemon (Pokemon): The user's active Pokémon.
        enemy_pokemon (Pokemon): The opponent's active Pokémon.
        main_move (str or None): The move chosen by the user's Pokémon. If None, a random move will be selected.
        enemy_move (str or None): The move chosen by the opponent's Pokémon. If None, a random move will be selected.
        new_state (State): The current battle state, including the Pokémon's stats, field conditions, etc.
        mutator_full_reset (int): A flag controlling whether the battle state should be reset.
        traceback (module): The traceback module used to handle exceptions during battle simulation.

    Returns:
        tuple: A tuple containing:
            - battle_info (dict): A dictionary with the battle header and instructions for each Pokémon move.
            - new_state (State): The updated battle state after the battle simulation.
            - dmg_from_enemy_move (int): The damage dealt to the user's Pokémon by the enemy.
            - dmg_from_user_move (int): The damage dealt to the enemy's Pokémon by the user.
            - mutator_full_reset (int): The flag indicating if the battle state was reset.

    Raises:
        Exception: If any unexpected error occurs during the simulation, the traceback will be printed.

    Notes:
        - If no moves are provided for the Pokémon, a random move is selected.
        - The outcome of the battle is determined based on probability, with weights reflecting typical battle mechanics.
        - The function prints a summary of the battle result, including damage dealt and whether any moves missed.
        - The state mutator is applied to update the battle state after the moves are resolved.
    """

    # If no move is provided, use a random move
    if main_move is None and main_pokemon.attacks:
        main_move = random.choice(main_pokemon.attacks)
    if enemy_move is None and enemy_pokemon.attacks:
        enemy_move = random.choice(enemy_pokemon.attacks)
    if not main_move:
        main_move = "Struggle"
    if not enemy_move:
        enemy_move = "Struggle"
    
    try:
        if main_pokemon.name.lower() != new_state.user.active.id:
            mutator_full_reset = 1 # reset AFTER Pokemon is changed !
        new_state.weather,
        new_state.field,
        new_state.trick_room
    except:
        mutator_full_reset = 1

    try:
        main_move_normalized = normalize_name(main_move)
        enemy_move_normalized = normalize_name(enemy_move)

                
        # Store only the chosen outcome
        battle_header = {
            'user': {
                'name': main_pokemon.name,
                'level': main_pokemon.level,
                'move': main_move
            },
            'opponent': {
                'name': enemy_pokemon.name,
                'level': enemy_pokemon.level,
                'move': enemy_move
            }
        }

        main_pokemon_dict = main_pokemon.to_engine_format()
        enemy_pokemon_dict = enemy_pokemon.to_engine_format()

        # Create Pokemon objects (positional args as required)
        main_pokemon_obj = Pokemon(
            identifier=main_pokemon_dict['identifier'],
            level=main_pokemon_dict['level'],
            types=main_pokemon_dict['types'],
            hp=main_pokemon_dict['hp'],
            maxhp=main_pokemon_dict['maxhp'],
            ability=main_pokemon_dict['ability'],
            item=main_pokemon_dict['item'],
            attack=main_pokemon_dict['attack'],
            defense=main_pokemon_dict['defense'],
            special_attack=main_pokemon_dict['special_attack'],
            special_defense=main_pokemon_dict['special_defense'],
            speed=main_pokemon_dict['speed'],
            nature=main_pokemon_dict.get('nature', 'serious'),
            evs=main_pokemon_dict.get('evs', (85,) * 6),
            attack_boost=main_pokemon_dict.get('attack_boost', 0),
            defense_boost=main_pokemon_dict.get('defense_boost', 0),
            special_attack_boost=main_pokemon_dict.get('special_attack_boost', 0),
            special_defense_boost=main_pokemon_dict.get('special_defense_boost', 0),
            speed_boost=main_pokemon_dict.get('speed_boost', 0),
            accuracy_boost=main_pokemon_dict.get('accuracy_boost', 0), 
            evasion_boost=main_pokemon_dict.get('evasion_boost', 0),
            status=main_pokemon_dict.get('status', None),
            terastallized=main_pokemon_dict.get('terastallized', False),
            volatile_status=main_pokemon_dict.get('volatile_status', set()),
            moves=main_pokemon_dict.get('moves', [])
        )

        enemy_pokemon_obj = Pokemon(
            identifier=enemy_pokemon_dict['identifier'],
            level=enemy_pokemon_dict['level'],
            types=enemy_pokemon_dict['types'],
            hp=enemy_pokemon_dict['hp'],
            maxhp=enemy_pokemon_dict['maxhp'],
            ability=enemy_pokemon_dict['ability'],
            item=enemy_pokemon_dict['item'],
            attack=enemy_pokemon_dict['attack'],
            defense=enemy_pokemon_dict['defense'],
            special_attack=enemy_pokemon_dict['special_attack'],
            special_defense=enemy_pokemon_dict['special_defense'],
            speed=enemy_pokemon_dict['speed'],
            nature=enemy_pokemon_dict.get('nature', 'serious'),
            evs=enemy_pokemon_dict.get('evs', (85,) * 6),
            attack_boost=main_pokemon_dict.get('attack_boost', 0),
            defense_boost=main_pokemon_dict.get('defense_boost', 0),
            special_attack_boost=main_pokemon_dict.get('special_attack_boost', 0),
            special_defense_boost=main_pokemon_dict.get('special_defense_boost', 0),
            speed_boost=main_pokemon_dict.get('speed_boost', 0),
            accuracy_boost=main_pokemon_dict.get('accuracy_boost', 0), 
            evasion_boost=main_pokemon_dict.get('evasion_boost', 0),
            status=enemy_pokemon_dict.get('status', None),
            terastallized=enemy_pokemon_dict.get('terastallized', False),
            volatile_status=enemy_pokemon_dict.get('volatile_status', set()),
            moves=enemy_pokemon_dict.get('moves', [])
        )
        
        # Default side_conditions with all needed keys
        side_conditions = defaultdict(int, {
            'stealthrock': 0,
            'spikes': 0,
            'toxicspikes': 0,
            'tailwind': 0,
            'reflect': 0,
            'lightscreen': 0,
            'auroraveil': 0,
            'protect': 0,
        })

        try:
            if mutator_full_reset not in (0, 1, 2):
                mutator_full_reset = 1
        except:
            mutator_full_reset = 1

        state = reset_pokemon(new_state,mutator_full_reset,main_pokemon_obj,enemy_pokemon_obj,side_conditions)
        
        mutator = StateMutator(state)

        try:
            if state.opponent.active.hp == 0:
                main_move = "Splash"
                enemy_move = "Splash"
        except:
            main_move = "Splash"
            enemy_move = "Splash"

        # Get all possible outcomes
        transpose_instructions = get_all_state_instructions(
            mutator, main_move_normalized, enemy_move_normalized
        )

        # Randomly select ONE outcome from possible outcomes, using probability weights for the outcomes in actual Pokemon battles
        # e.g. if P(outcome 1):P(outcome 2) = 20% : 80%, then 20% chance to pick outcome 1 (picks randomly)
        weights = [outcome.percentage for outcome in transpose_instructions]
        chosen_outcome = random.choices(transpose_instructions, weights=weights, k=1)[0]
        
        instrs = chosen_outcome.instructions

        user_hp_before = int(state.user.active.hp)
        opponent_hp_before = int(state.opponent.active.hp)

        mutator.apply(instrs)

        main_pokemon.stat_stages = {
            'atk': state.user.active.attack_boost,
            'def': state.user.active.defense_boost,
            'spa': state.user.active.special_attack_boost,
            'spd': state.user.active.special_defense_boost,
            'spe': state.user.active.speed_boost,
            'accuracy': state.user.active.accuracy_boost, 
            'evasion': state.user.active.evasion_boost
        }
        enemy_pokemon.stat_stages = {
            'atk': state.opponent.active.attack_boost,
            'def': state.opponent.active.defense_boost,
            'spa': state.opponent.active.special_attack_boost,
            'spd': state.opponent.active.special_defense_boost,
            'spe': state.opponent.active.speed_boost,
            'accuracy': state.opponent.active.accuracy_boost, 
            'evasion': state.opponent.active.evasion_boost
        }

        new_state = copy.deepcopy(state)

        mutator_full_reset = int(0) # preserve battle state - until something else changes this value

        user_hp_after = int(new_state.user.active.hp)
        opponent_hp_after = int(new_state.opponent.active.hp)

        dmg_from_user_move = int(opponent_hp_before - opponent_hp_after)
        dmg_from_enemy_move = int(user_hp_before - user_hp_after)

        # Reference to the founder and creator of Ankimon, Unlucky-life.
        # Unlucky, we are very proud of you for your work. You are a legend. 
        # It's been a pleasure being part of this journey. -- h0tp (and friends)

        if int(chosen_outcome.percentage) == 0:
            unlucky_life = int(1)
        else:
            unlucky_life = int(chosen_outcome.percentage)
        
        # On a serious note, the function above is the CHANCE that the chosen_outcome was picked out of ALL
        # the choices in transpose_instructions, based on factors like accuracy rate, the chance to
        # inflict a certain status (like sleep or paralyze), etc.  

        # Did the chosen outcome deal damage?
        user_did_damage = any(i[0] == 'damage' and i[1] == 'opponent' and i[2] > 0 for i in instrs)
        opponent_did_damage = any(i[0] == 'damage' and i[1] == 'user' and i[2] > 0 for i in instrs)

        # Could the move have dealt damage in any possible outcome?
        user_move_can_hit = any(
            any(i[0] == 'damage' and i[1] == 'opponent' and i[2] > 0 for i in outcome.instructions)
            for outcome in transpose_instructions
        )
        opponent_move_can_hit = any(
            any(i[0] == 'damage' and i[1] == 'user' and i[2] > 0 for i in outcome.instructions)
            for outcome in transpose_instructions
        )

        # Final miss detection: missed if this outcome did not deal damage, but another could have
        user_missed = user_move_can_hit and not user_did_damage
        opponent_missed = opponent_move_can_hit and not opponent_did_damage

        battle_effects = []
        for instr in chosen_outcome.instructions:
            battle_effects.append(list(instr))  # Convert tuples to lists

        print(f"{unlucky_life * 100}% chance: {battle_effects}")

        battle_info = {'battle_header': battle_header,
                'instructions': battle_effects,
                'user_missed': user_missed,
                'opponent_missed': opponent_missed}

        return (battle_info, copy.deepcopy(new_state), dmg_from_enemy_move, dmg_from_user_move, mutator_full_reset)
    
    except Exception as e:
        
        traceback.print_exc()