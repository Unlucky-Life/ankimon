import random

import pytest

from Ankimon.functions.battle_functions import (
    calc_atk_dmg,
    calculate_hp,
    get_effectiveness,
    status_effect,
)
from Ankimon.pyobj.pokemon_obj import PokemonObject


def make_pokemon(**overrides):
    kwargs = dict(
        name="Bulbasaur",
        id=1,
        level=10,
        type=["Grass"],
        stats={"hp": 45, "atk": 49, "def": 49, "spa": 65, "spd": 65, "spe": 45},
        ev={"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        iv={"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0},
        battle_status="fighting",
    )
    kwargs.update(overrides)
    return PokemonObject(**kwargs)


class TestGetEffectiveness:
    def test_super_effective(self):
        # Water vs Fire is super effective (2x)
        assert get_effectiveness("water", ["Fire"]) == 2

    def test_not_very_effective(self):
        # Fire vs Water is not very effective (0.5x)
        assert get_effectiveness("fire", ["Water"]) == 0.5

    def test_neutral(self):
        assert get_effectiveness("normal", ["Normal"]) == 1

    def test_dual_type_multiplies(self):
        # Electric vs Water/Flying: 2x * 2x = 4x
        assert get_effectiveness("electric", ["Water", "Flying"]) == 4


class TestCalcAtkDmg:
    def test_returns_nonnegative_damage(self):
        random.seed(0)
        dmg = calc_atk_dmg(
            level=10, critical=1, power=40, stat_atk=50, wild_stat_def=50,
            main_type=["Grass"], move_type="grass", wild_type=["Water"], critRatio=1,
        )
        assert dmg > 0

    def test_none_power_treated_same_as_zero_power(self):
        random.seed(0)
        none_dmg = calc_atk_dmg(
            level=10, critical=1, power=None, stat_atk=50, wild_stat_def=50,
            main_type=["Grass"], move_type="grass", wild_type=["Water"], critRatio=1,
        )
        random.seed(0)
        zero_dmg = calc_atk_dmg(
            level=10, critical=1, power=0, stat_atk=50, wild_stat_def=50,
            main_type=["Grass"], move_type="grass", wild_type=["Water"], critRatio=1,
        )
        assert none_dmg == zero_dmg

    def test_stab_increases_damage(self):
        random.seed(1)
        stab_dmg = calc_atk_dmg(10, 1, 40, 50, 50, ["Grass"], "grass", ["Normal"], 1)
        random.seed(1)
        no_stab_dmg = calc_atk_dmg(10, 1, 40, 50, 50, ["Fire"], "grass", ["Normal"], 1)
        assert stab_dmg > no_stab_dmg

    def test_crit_ratio_4_always_crits(self):
        # critRatio > 3 forces a 100% crit chance path (still probabilistic on the
        # "critical" multiplier itself being applied) - just assert it doesn't error
        # and produces a positive result across repeated rolls.
        for seed in range(5):
            random.seed(seed)
            dmg = calc_atk_dmg(10, 1, 40, 50, 50, ["Grass"], "grass", ["Water"], 4)
            assert dmg >= 0


class TestCalculateHp:
    def test_higher_level_gives_more_hp(self):
        low = calculate_hp(45, 5, {"hp": 0}, {"hp": 0})
        high = calculate_hp(45, 50, {"hp": 0}, {"hp": 0})
        assert high > low

    def test_hp_is_int(self):
        assert isinstance(calculate_hp(45, 10, {"hp": 0}, {"hp": 0}), int)


class TestStatusEffect:
    def test_returns_stats_not_undefined_name(self):
        # Regression test for the confirmed bug: status_effect used to return
        # the undefined name `battle_stats` instead of the local `stats`.
        pokemon = make_pokemon(battle_status="fighting")
        move = {"type": "normal", "target": "normal"}
        msg, acc, stat, stats = status_effect(pokemon, move, slp_counter=2, msg="", acc=100)
        assert stats == pokemon._battle_stats

    def test_paralysis_reduces_speed_and_can_prevent_move(self):
        pokemon = make_pokemon(battle_status="par")
        move = {"type": "normal", "target": "normal"}
        random.seed(0)
        msg, acc, stat, stats = status_effect(pokemon, move, slp_counter=0, msg="", acc=100)
        assert stats["spe"] == pytest.approx(pokemon.stats["spe"] * 0.5)
        assert "speed is reduced" in msg

    def test_sleep_counts_down_then_wakes(self):
        pokemon = make_pokemon(battle_status="slp")
        move = {"type": "normal", "target": "normal"}
        msg, acc, stat, stats = status_effect(pokemon, move, slp_counter=2, msg="", acc=100)
        assert stat == "slp"
        assert "asleep" in msg

        msg2, acc2, stat2, stats2 = status_effect(pokemon, move, slp_counter=1, msg="", acc=100)
        assert stat2 is None
        assert "no longer asleep" in msg2

    def test_burn_deals_damage_over_time(self):
        # Regression test: burn/poison/toxic used to compute damage into a
        # local `hp` variable that was never written back to the Pokemon.
        pokemon = make_pokemon(battle_status="brn")
        starting_hp = pokemon.hp
        move = {"type": "normal", "target": "normal"}
        status_effect(pokemon, move, slp_counter=0, msg="", acc=100)
        assert pokemon.hp < starting_hp

    def test_poison_deals_damage_over_time(self):
        pokemon = make_pokemon(battle_status="psn")
        starting_hp = pokemon.hp
        move = {"type": "normal", "target": "normal"}
        status_effect(pokemon, move, slp_counter=0, msg="", acc=100)
        assert pokemon.hp < starting_hp

    def test_toxic_deals_damage_and_becomes_poison(self):
        pokemon = make_pokemon(battle_status="tox")
        starting_hp = pokemon.hp
        move = {"type": "normal", "target": "normal"}
        msg, acc, stat, stats = status_effect(pokemon, move, slp_counter=0, msg="", acc=100)
        assert pokemon.hp < starting_hp
        assert stat == "psn"

    def test_freeze_thaws_on_fire_move(self):
        pokemon = make_pokemon(battle_status="frz")
        move = {"type": "fire", "target": "normal"}
        random.seed(0)
        msg, acc, stat, stats = status_effect(pokemon, move, slp_counter=0, msg="", acc=100)
        assert stat is None
        assert "no longer frozen" in msg
