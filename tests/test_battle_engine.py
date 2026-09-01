import random

from Ankimon.functions import battle_engine
from Ankimon.business import bP_none_moves


class TestResolveDamageMove:
    def test_zero_base_power_uses_flat_damage(self):
        move = {"basePower": 0, "target": "normal", "damage": 20, "type": "normal"}
        dmg = battle_engine.resolve_damage_move(
            move, level=10, multiplier=1, atk_stat=50, def_stat=50,
            attacker_type=["Normal"], defender_type=["Normal"],
        )
        assert dmg == 20

    def test_zero_base_power_non_normal_target_is_zero_not_crash(self):
        # Regression test: bP_none_moves used to return None for any target
        # other than "normal", which crashed `enemy_pokemon.hp -= dmg`.
        move = {"basePower": 0, "target": "self", "type": "normal"}
        dmg = battle_engine.resolve_damage_move(
            move, level=10, multiplier=1, atk_stat=50, def_stat=50,
            attacker_type=["Normal"], defender_type=["Normal"],
        )
        assert dmg == 0

    def test_positive_base_power_deals_damage(self):
        random.seed(0)
        move = {"basePower": 40, "target": "normal", "type": "grass"}
        dmg = battle_engine.resolve_damage_move(
            move, level=10, multiplier=1, atk_stat=50, def_stat=50,
            attacker_type=["Grass"], defender_type=["Water"], critRatio=1,
        )
        assert dmg > 0


class TestApplySecondaryStatus:
    def test_no_secondary_is_noop(self):
        move = {"target": "normal"}
        battle_status, slp_counter = battle_engine.apply_secondary_status(move, "fighting", 0)
        assert battle_status == "fighting"
        assert slp_counter == 0

    def test_guaranteed_secondary_status_applies(self):
        move = {"target": "normal", "secondary": {"status": "par", "chance": 100}}
        battle_status, slp_counter = battle_engine.apply_secondary_status(move, "fighting", 0)
        assert battle_status == "par"

    def test_self_target_never_inflicts_status(self):
        move = {"target": "self", "secondary": {"status": "par", "chance": 100}}
        battle_status, slp_counter = battle_engine.apply_secondary_status(move, "fighting", 0)
        assert battle_status == "fighting"

    def test_sleep_status_sets_a_counter(self):
        move = {"target": "normal", "secondary": {"status": "slp", "chance": 100}}
        random.seed(0)
        battle_status, slp_counter = battle_engine.apply_secondary_status(move, "fighting", 0)
        assert battle_status == "slp"
        assert 1 <= slp_counter <= 3


class TestResolveStatusMove:
    def test_self_boost_mutates_actor_stats_only(self):
        actor_stats = {"atk": 50}
        target_stats = {"atk": 50}
        # "swordsdance" is a classic +2 Attack self-boost move present in the
        # addon's real moves.json data file.
        msg, battle_status, slp_counter = battle_engine.resolve_status_move(
            "swordsdance", actor_stats, target_stats, "Machop", "Geodude", "", "fighting", 0,
        )
        assert actor_stats["atk"] > 50
        assert target_stats["atk"] == 50
        assert "Machop" in msg

    def test_target_debuff_mutates_target_stats_only(self):
        actor_stats = {"atk": 50, "def": 50}
        target_stats = {"atk": 50, "def": 50}
        # "growl" lowers the target's Attack.
        msg, battle_status, slp_counter = battle_engine.resolve_status_move(
            "growl", actor_stats, target_stats, "Machop", "Geodude", "", "fighting", 0,
        )
        assert target_stats["atk"] < 50
        assert actor_stats["atk"] == 50
        assert "Geodude" in msg
