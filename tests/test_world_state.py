from pathlib import Path

from Ankimon.functions.world_state import WorldState


def test_reviews_spawn_route_encounters_and_towns_are_safe():
    world = WorldState()
    assert [world.record_review() for _ in range(3)] == [None, None, None]
    assert world.move("route_1") is True
    assert world.record_review() is None
    assert world.record_review() is None
    assert world.record_review() in {"rattata", "pidgey", "caterpie"}


def test_gym_reward_unlocks_progression_and_persists():
    world = WorldState(location="route_1")
    result = world.defeat_trainer("route_1_bug_catcher")
    assert result["money"] == 120
    assert world.money == 120
    assert world.move("ember_gym") is True
    world.defeat_trainer("ember_leader")
    assert world.badges == ["Cinder Badge"]
    assert world.money == 1520

    path = Path(".test-world-state.json")
    try:
        world.save(path)
        restored = WorldState.load(path)
        assert restored.to_dict() == world.to_dict()
    finally:
        path.unlink(missing_ok=True)


def test_unknown_or_locked_moves_are_rejected():
    world = WorldState()
    assert world.move("ember_gym") is False
    assert world.move("nowhere") is False
