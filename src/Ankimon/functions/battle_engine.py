"""Pure, Anki-independent battle resolution logic.

Extracted from the reviewer hook in ``__init__.py`` so the damage/status
math can be unit tested without mocking Qt/Anki. No ``aqt``/``global``
state here on purpose - callers own and thread their own state
(``battle_status``, ``slp_counter``) through these functions.
"""
import random

from .battle_functions import calc_atk_dmg, get_effectiveness, status_effect
from .pokedex_functions import find_details_move
from ..business import get_multiplier_stats, bP_none_moves


def resolve_status_effect(pokemon_obj, move, slp_counter, msg, acc):
    """Apply an active battle status (par/brn/psn/tox/frz/slp) before a move resolves.

    Thin wrapper around ``battle_functions.status_effect`` - kept here so
    all battle-round logic has one entry point.
    """
    return status_effect(pokemon_obj, move, slp_counter, msg, acc)


def resolve_status_move(move_name, actor_stats, target_stats, actor_name, target_name,
                         msg, battle_status, slp_counter):
    """Apply a status move's stat boosts / inflicted status.

    Returns (msg, battle_status, slp_counter). ``actor_stats``/``target_stats``
    are mutated in place (same as the legacy behaviour), matching how the
    caller mutates ``PokemonObject.stats`` dicts today.
    """
    move = find_details_move(move_name)
    target = move.get("target")
    boosts = move.get("boosts", {}) or {}
    move_stat = move.get("status", None)
    secondary = move.get("secondary", None)

    if move_stat is not None:
        battle_status = move_stat
    if secondary is not None:
        secondary_status = secondary.get("status")
        if secondary_status is not None and random.random() < secondary.get("chance", 0) / 100:
            battle_status = secondary_status
    if battle_status == "slp":
        slp_counter = random.randint(1, 3)

    if target == "self":
        for boost, stage in boosts.items():
            multiplier = get_multiplier_stats(stage)
            actor_stats[boost] = actor_stats.get(boost, 0) * multiplier
            msg += f" {actor_name.capitalize()}'s "
            if stage < 0:
                msg += f"{boost.capitalize()} decreased."
            elif stage > 0:
                msg += f"{boost.capitalize()} increased."
    elif target in ("normal", "allAdjacentFoes"):
        for boost, stage in boosts.items():
            multiplier = get_multiplier_stats(stage)
            target_stats[boost] = target_stats.get(boost, 0) * multiplier
            msg += f" {target_name.capitalize()}'s "
            if stage < 0:
                msg += f"{boost.capitalize()} decreased."
            elif stage > 0:
                msg += f"{boost.capitalize()} increased."

    return msg, battle_status, slp_counter


def apply_secondary_status(move, battle_status, slp_counter):
    """Roll a damaging move's secondary status-inflict chance, if any.

    Returns (battle_status, slp_counter).
    """
    move_stat = move.get("status", None)
    secondary = move.get("secondary", None)
    if secondary is None:
        return battle_status, slp_counter

    target = move.get("target")
    secondary_status = secondary.get("status")
    if target in ("normal", "allAdjacentFoes"):
        if move_stat is not None:
            battle_status = move_stat
        if secondary_status is not None and random.random() < secondary.get("chance", 0) / 100:
            battle_status = secondary_status
    if battle_status == "slp":
        slp_counter = random.randint(1, 3)

    return battle_status, slp_counter


def resolve_damage_move(move, level, multiplier, atk_stat, def_stat, attacker_type, defender_type, critRatio=1):
    """Compute damage for a Physical/Special move, including the base-power-less case.

    Returns the integer damage dealt (>= 0). Callers are responsible for
    clamping a landed hit to a minimum of 1 damage, matching existing
    battle-round behaviour.
    """
    base_power = move.get("basePower", 0)
    if not base_power:
        return int(bP_none_moves(move))
    move_type = move.get("type", "Normal")
    return int(calc_atk_dmg(level, multiplier, base_power, atk_stat, def_stat,
                             attacker_type, move_type, defender_type, critRatio))
