import random
from collections import defaultdict
import copy
import traceback
from typing import Union

from .battle import Move
from .objects import Pokemon, State, StateMutator, Side
from .helpers import normalize_name
from .find_state_instructions import get_all_state_instructions
from ..pyobj.InfoLogger import ShowInfoLogger
from ..pyobj.error_handler import show_warning_with_traceback
from ..pyobj.InfoLogger import ShowInfoLogger

logger = ShowInfoLogger()

def reset_stat_boosts(pokemon: Pokemon) -> Pokemon:
    """
    Resets all stat boosts of a given Pokemon to zero.

    Args:
        pokemon (Pokemon): The Pokemon whose stat boosts will be reset.

    Returns:
        Pokemon: The same Pokemon object with all stat boosts reset to zero.
    """
    pokemon.attack_boost = 0
    pokemon.defense_boost = 0
    pokemon.special_attack_boost = 0
    pokemon.special_defense_boost = 0
    pokemon.speed_boost = 0
    pokemon.accuracy_boost = 0
    pokemon.evasion_boost = 0
    return pokemon

def reset_side(pokemon: Pokemon, side_conditions: Union[dict, None]=None) -> Side:
    """
    Resets and returns a new Side object for the given Pokemon with default or provided side conditions.

    If no side conditions are provided, a default set with all conditions initialized to zero is used.

    Args:
        pokemon (Pokemon): The active Pokemon for the side.
        side_conditions (Union[dict, None], optional): A dictionary of side conditions to apply.
            If None, defaults to all conditions set to zero.

    Returns:
        Side: A new Side object with the specified active Pokemon, an empty reserve,
              default wish and future sight settings, and the given or default side conditions.
    """
    if side_conditions is None:
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
    side = Side(
        active=pokemon,
        reserve={},
        wish=(0, 0),
        side_conditions=side_conditions,
        future_sight=(0, 0),
    )
    return side

def simulate_battle_with_poke_engine(
    main_pokemon: Pokemon,
    enemy_pokemon: Pokemon,
    main_move: str,
    enemy_move: str,
    mutator_full_reset: int,
    state: Union[State, None]=None,
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
        main_move = "Splash"
    if not enemy_move:
        enemy_move = "Splash"


    if (state is not None) and (state.user.active.id != main_pokemon.name.lower()):
        mutator_full_reset = 1 # reset AFTER Pokemon is changed !
    if mutator_full_reset not in (0, 1):
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

        # Create Pokemon objects
        main_pokemon_poke_engine = main_pokemon.to_poke_engine_Pokemon()
        enemy_pokemon_poke_engine = enemy_pokemon.to_poke_engine_Pokemon()

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

        if state is None:
            state = State(
                user=reset_side(main_pokemon_poke_engine),
                opponent=reset_side(enemy_pokemon_poke_engine),
                weather=None,
                field=None,
                trick_room=False,
                )
        else:
            if mutator_full_reset == 0:  # Combat is ongoing
                pass
            elif mutator_full_reset == 1:  # Reset both sides of the fight
                state.user.active = reset_stat_boosts(state.user.active)
                state.user = reset_side(main_pokemon_poke_engine)
                state.opponent = reset_side(enemy_pokemon_poke_engine)

                # Reset battle_status and volatile_status for both engine state Pokémon
                if hasattr(state.user.active, 'battle_status'):
                    state.user.active.battle_status = 'fighting'
                if hasattr(state.user.active, 'volatile_status'):
                    state.user.active.volatile_status = set()
                if hasattr(state.opponent.active, 'battle_status'):
                    state.opponent.active.battle_status = 'fighting'
                if hasattr(state.opponent.active, 'volatile_status'):
                    state.opponent.active.volatile_status = set()
                # Clear Future Sight state on reset - NEW
                if hasattr(state.user, 'future_sight'):
                    state.user.future_sight = (0, 0)
                if hasattr(state.opponent, 'future_sight'):
                    state.opponent.future_sight = (0, 0)

                # Also reset the main_pokemon and enemy_pokemon Python objects
                main_pokemon.battle_status = 'fighting'
                main_pokemon.volatile_status = set()
                enemy_pokemon.battle_status = 'fighting'
                enemy_pokemon.volatile_status = set()

                state.weather = None # Reset weather to None
                state.field = None # Reset field to None
                state.trick_room = False # Reset trick room to None

            else:
                raise ValueError(f"Wrong mutator_full_reset encountered : {mutator_full_reset}")

        mutator = StateMutator(state)

        if state.opponent.active.hp == 0:
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

        # --- Debugging: State changes BEFORE applying instructions
        state_before = copy.deepcopy(mutator.state)
        mutator.apply(instrs)
        state_after = mutator.state
        battle_info_changes = diff_states(state_before, state_after)
        print_state_changes(battle_info_changes)
        # --- End Debugging

        # Save changes from State to Pokemon objects (enhanced for volatile status)
        main_pokemon.hp = state.user.active.hp
        main_pokemon.current_hp = state.user.active.hp
        enemy_pokemon.hp = state.opponent.active.hp
        enemy_pokemon.current_hp = state.opponent.active.hp

        main_pokemon.stat_stages = {
            'atk': state.user.active.attack_boost,
            'def': state.user.active.defense_boost,
            'spa': state.user.active.special_attack_boost,
            'spd': state.user.active.special_defense_boost,
            'spe': state.user.active.speed_boost,
            'accuracy': state.user.active.accuracy_boost,
            'evasion': state.user.active.evasion_boost
        }

        # Save volatile status from poke-engine state to Pokemon object - NEW
        if hasattr(state.user.active, 'volatile_status'):
            main_pokemon.volatile_status = state.user.active.volatile_status.copy()
        elif not hasattr(main_pokemon, 'volatile_status'):
            main_pokemon.volatile_status = set()


        # Same for enemy Pokemon
        enemy_pokemon.stat_stages = {
            'atk': state.opponent.active.attack_boost,
            'def': state.opponent.active.defense_boost,
            'spa': state.opponent.active.special_attack_boost,
            'spd': state.opponent.active.special_defense_boost,
            'spe': state.opponent.active.speed_boost,
            'accuracy': state.opponent.active.accuracy_boost,
            'evasion': state.opponent.active.evasion_boost
        }

        # Save volatile status for enemy - NEW
        if hasattr(state.opponent.active, 'volatile_status'):
            enemy_pokemon.volatile_status = state.opponent.active.volatile_status.copy()
        elif not hasattr(enemy_pokemon, 'volatile_status'):
            enemy_pokemon.volatile_status = set()

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

        battle_effects = []
        for instr in chosen_outcome.instructions:
            battle_effects.append(list(instr))  # Convert tuples to lists

        battle_info = {
            'battle_header': battle_header,
            'instructions': battle_effects,
            'state': new_state
            }

        print(f"{unlucky_life * 100}% chance: {battle_effects}")
        return battle_info, new_state, dmg_from_enemy_move, dmg_from_user_move, mutator_full_reset, battle_info_changes

    except Exception as e:
        show_warning_with_traceback(exception=e, message="Error simulating battle:")

def diff_states(state_before, state_after, path="", changes=None):
    """
    Recursively compare two state objects and return a list of changed attributes.
    Returns changes in format: {'key': path, 'before': value_before, 'after': value_after}
    """
    if changes is None:
        changes = []

    # Handle None cases
    if state_before is None and state_after is None:
        return changes
    if state_before is None or state_after is None:
        changes.append({
            'key': path or 'root',
            'before': state_before,
            'after': state_after
        })
        return changes

    # Handle primitive types (int, float, str, bool)
    if isinstance(state_before, (int, float, str, bool)) or isinstance(state_after, (int, float, str, bool)):
        if state_before != state_after:
            changes.append({
                'key': path or 'root',
                'before': state_before,
                'after': state_after
            })
        return changes

    # Handle sets
    if isinstance(state_before, set) or isinstance(state_after, set):
        if state_before != state_after:
            changes.append({
                'key': path or 'root',
                'before': state_before,
                'after': state_after
            })
        return changes

    # Handle tuples
    if isinstance(state_before, tuple) or isinstance(state_after, tuple):
        if state_before != state_after:
            changes.append({
                'key': path or 'root',
                'before': state_before,
                'after': state_after
            })
        return changes

    # Handle lists
    if isinstance(state_before, list) and isinstance(state_after, list):
        # Compare list lengths and elements
        if len(state_before) != len(state_after):
            changes.append({
                'key': f"{path}.length" if path else 'length',
                'before': len(state_before),
                'after': len(state_after)
            })

        # Compare elements up to the shorter length
        min_len = min(len(state_before), len(state_after))
        for i in range(min_len):
            new_path = f"{path}[{i}]" if path else f"[{i}]"
            diff_states(state_before[i], state_after[i], new_path, changes)

        # Handle extra elements in longer list
        if len(state_before) > min_len:
            for i in range(min_len, len(state_before)):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                changes.append({
                    'key': new_path,
                    'before': state_before[i],
                    'after': None
                })
        elif len(state_after) > min_len:
            for i in range(min_len, len(state_after)):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                changes.append({
                    'key': new_path,
                    'before': None,
                    'after': state_after[i]
                })
        return changes

    # Handle dictionaries
    if isinstance(state_before, dict) and isinstance(state_after, dict):
        all_keys = set(state_before.keys()) | set(state_after.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else str(key)
            before_val = state_before.get(key, None)
            after_val = state_after.get(key, None)
            diff_states(before_val, after_val, new_path, changes)
        return changes

    # Handle custom objects - check if they're the same type
    if type(state_before) != type(state_after):
        changes.append({
            'key': path or 'root',
            'before': state_before,
            'after': state_after
        })
        return changes

    # Custom class: recurse into attributes (__dict__ and __slots__ on the class)
    attrs = set()
    for obj in (state_before, state_after):
        # __dict__ attributes
        if hasattr(obj, "__dict__"):
            attrs.update(vars(obj).keys())
        # __slots__ attributes (check on the class)
        if hasattr(obj.__class__, "__slots__"):
            for slot in obj.__class__.__slots__:
                attrs.add(slot)

    if attrs:
        for attr in attrs:
            before_val = getattr(state_before, attr, None)
            after_val = getattr(state_after, attr, None)
            new_path = f"{path}.{attr}" if path else attr
            diff_states(before_val, after_val, new_path, changes)

    return changes


def print_state_changes(changes):
    """
    Print state changes in a clean format: key: before -> after
    """
    if not changes:
        return

    for change in changes:
        key = change['key']
        before = change['before']
        after = change['after']
        print(f"{key}: {before} -> {after}")

