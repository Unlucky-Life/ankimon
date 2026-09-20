"""Small, persistent overworld model for the Ankimon RPG loop.

The addon is driven by Anki reviews rather than a real-time game loop.  This
module gives those reviews a Pokémon-GBA-style world to advance through without
depending on Qt or Anki globals.  UI code can call :meth:`record_review` after
an answered card and persist the returned state in the user's data directory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Route:
    name: str
    exits: tuple[str, ...]
    encounters: tuple[tuple[str, int], ...] = ()
    trainer_ids: tuple[str, ...] = ()
    required_badges: int = 0


ROUTES: dict[str, Route] = {
    "starter_town": Route("Starter Town", ("route_1",)),
    "route_1": Route(
        "Route 1",
        ("starter_town", "ember_gym"),
        encounters=(("rattata", 45), ("pidgey", 35), ("caterpie", 20)),
        trainer_ids=("route_1_bug_catcher",),
    ),
    "ember_gym": Route(
        "Ember Gym",
        ("route_1",),
        trainer_ids=("ember_leader",),
        required_badges=0,
    ),
}


TRAINERS: dict[str, dict[str, Any]] = {
    "route_1_bug_catcher": {
        "name": "Bug Catcher Kai",
        "party": (("caterpie", 4), ("weedle", 4)),
        "reward": 120,
        "rematchable": True,
    },
    "ember_leader": {
        "name": "Leader Ember",
        "party": (("slugma", 12), ("magmar", 14)),
        "reward": 1400,
        "badge": "Cinder Badge",
        "rematchable": False,
    },
}


@dataclass
class WorldState:
    """Serializable world progress for one trainer."""

    location: str = "starter_town"
    review_steps: int = 0
    badges: list[str] = field(default_factory=list)
    defeated_trainers: list[str] = field(default_factory=list)
    money: int = 0
    last_encounter: str | None = None

    def __post_init__(self) -> None:
        if self.location not in ROUTES:
            raise ValueError(f"Unknown world location: {self.location}")
        self.review_steps = max(0, int(self.review_steps))
        self.money = max(0, int(self.money))

    @property
    def route(self) -> Route:
        return ROUTES[self.location]

    def move(self, destination: str) -> bool:
        """Move to an adjacent, unlocked location."""
        if destination not in self.route.exits or destination not in ROUTES:
            return False
        target = ROUTES[destination]
        if len(self.badges) < target.required_badges:
            return False
        self.location = destination
        return True

    def record_review(self, *, correct: bool = True) -> str | None:
        """Advance the world after a reviewed card and maybe spawn an encounter.

        Every third review on a route produces one weighted wild encounter.
        Towns remain safe, matching the Pokémon Center/town expectation from a
        GBA game while keeping encounter pacing appropriate for Anki sessions.
        """
        self.review_steps += 1
        if not self.route.encounters or self.review_steps % 3:
            return None
        # Stable selection makes saves/replays predictable and avoids global RNG
        # affecting battle calculations.
        total = sum(weight for _, weight in self.route.encounters)
        cursor = (self.review_steps * (2 if correct else 1)) % total
        for species, weight in self.route.encounters:
            cursor -= weight
            if cursor < 0:
                self.last_encounter = species
                return species
        return None

    def available_trainers(self) -> list[dict[str, Any]]:
        """Return local trainers at the current location that can be challenged."""
        result = []
        for trainer_id in self.route.trainer_ids:
            trainer = TRAINERS[trainer_id]
            if trainer_id not in self.defeated_trainers or trainer.get("rematchable"):
                result.append({"id": trainer_id, **trainer})
        return result

    def defeat_trainer(self, trainer_id: str) -> dict[str, Any]:
        """Apply a trainer victory and return its reward payload."""
        if trainer_id not in self.route.trainer_ids:
            raise ValueError("Trainer is not available at the current location")
        trainer = TRAINERS.get(trainer_id)
        if trainer is None:
            raise ValueError(f"Unknown trainer: {trainer_id}")
        if trainer_id not in self.defeated_trainers:
            self.defeated_trainers.append(trainer_id)
        reward = int(trainer.get("reward", 0))
        self.money += reward
        badge = trainer.get("badge")
        if badge and badge not in self.badges:
            self.badges.append(badge)
        return {"trainer_id": trainer_id, "money": reward, "badge": badge}

    def to_dict(self) -> dict[str, Any]:
        return {
            "location": self.location,
            "review_steps": self.review_steps,
            "badges": list(self.badges),
            "defeated_trainers": list(self.defeated_trainers),
            "money": self.money,
            "last_encounter": self.last_encounter,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "WorldState":
        return cls(**(data or {}))

    def save(self, path: str | Path) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "WorldState":
        source = Path(path)
        if not source.exists():
            return cls()
        return cls.from_dict(json.loads(source.read_text(encoding="utf-8")))
