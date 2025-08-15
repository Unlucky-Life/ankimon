from typing import Union
import uuid
import json
import os

from ..poke_engine.objects import Pokemon
from ..resources import pkmnimgfolder, mainpokemon_path, mypokemon_path
from ..utils import substract_item_from_itembag, give_item

class PokemonObject:
    def __init__(
        self,
        name="Ditto",
        shiny=False,
        id=None,
        level=3,
        ability=None,
        type=None,
        current_hp=15,
        base_stats=None,
        attacks=None,
        base_experience=0,
        growth_rate="medium",
        hp=16,
        ev=None,
        iv=None,
        gender="N",
        battle_status="Fighting",
        xp=0,
        position=(0, 0),
        nickname="",
        moves=None,
        evos=None,
        tier="Normal",
        ev_yield=None,
        friendship=0,
        individual_id=None,
        everstone=False,
        pokemon_defeated=0,
        is_favorite=False,
        captured_date=None,
        held_item: Union[str, None]=None,
        **kwargs
    ):
        # Unique identifier
        self.individual_id = str(individual_id) if individual_id else str(uuid.uuid4())
        self.name = str(name)
        self.nickname = str(nickname) if nickname is not None else ""
        self.shiny = bool(shiny)
        self.id = int(id) if id is not None else 132
        self.level = int(level)
        self.ability = ability if ability else "None"
        self.type = list(type) if type else ["Normal"]
        self.gender = str(gender) if gender is not None else "N"
        self.tier = str(tier) if tier is not None else "Normal"
        self.everstone = bool(everstone)
        self.pokemon_defeated = int(pokemon_defeated)

        if not ability or str(ability).strip().lower() in ("none", "no ability", ""):
            self.ability = "Run Away"
        else:
            self.ability = ability

        # Stats
        self.base_stats = base_stats or {"hp": 1, "atk": 1, "def": 1, "spa": 1, "spd": 1, "spe": 1}
        self.ev = {k: int(v) for k, v in (ev or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}).items()}
        self.iv = {k: int(v) for k, v in (iv or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}).items()}
        self.ev_yield = {k: int(v) for k, v in (ev_yield or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}).items()}

        # Attacks and moves
        self.attacks = list(attacks) if attacks else ["Struggle"]
        self.moves = list(moves) if moves else []

        # Experience and growth
        self.base_experience = int(base_experience)
        self.growth_rate = str(growth_rate)
        self.xp = int(xp)
        self.friendship = int(friendship)
        self.evos = list(evos) if evos else []

        # Battle and status
        self.battle_status = str(battle_status)
        self.position = tuple(position) if isinstance(position, (list, tuple)) else (0, 0)
        self.stat_stages = kwargs.get('stat_stages', {
            'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'accuracy': 0, 'evasion': 0
        })
        self.volatile_status = set(kwargs.get('volatile_status', []))
        self.nature = kwargs.get('nature', 'serious')
        self.held_item = held_item

        # HP calculation
        self.max_hp = self.calculate_max_hp()
        self.hp = int(kwargs.get('hp', self.max_hp))
        self.current_hp = current_hp or 15

        self.is_favorite = bool(is_favorite)
        self.captured_date = captured_date or None

    @classmethod
    def calc_stat(
        cls,
        stat_name: str,
        base_stat_val: int,
        level: int,
        iv: int,
        ev: int,
        nature: str
        ) -> int:
        if stat_name == "hp":
            hp = 10 + level + int((2 * base_stat_val + iv + int(ev / 4)) * level / 100)  # Formula found on bulbapedia
            return int(hp)
        elif stat_name in ("atk", "def", "spa", "spd", "spe"):
            nature_mult = PokemonObject.get_nature_stat_mult(stat_name, nature)  # Formula found on bulbapedia
            stat = (5 + int((2 * base_stat_val + iv + int(ev / 4)) * level / 100)) * nature_mult
            return int(stat)
        raise ValueError(f"Received an unknown stat_name : {stat_name}")

    @property
    def stats(self) -> dict:
        _dict = {}
        for key, val in self.base_stats.items():
            if key not in ("hp", "atk", "def", "spa", "spd", "spe"):
                continue
            _dict[key] = PokemonObject.calc_stat(
                key, val, self.level, self.iv[key], self.ev[key], self.nature
                )
        return _dict

    @stats.setter
    def stats(self, value):
        raise AttributeError("Setting the value of the stats of a Pokemon is forbidden as they are automatically calculated using their base stats. You can instead set the base_stats of the Pokemon.")

    @classmethod
    def get_nature_stat_mult(cls, stat_name: str, nature: str) -> float:
        if stat_name == "atk":
            if nature.lower() in ("lonely", "brave", "adamant", "naughty"):
                return 1.1
            if nature.lower() in ("bold", "timid", "modest", "calm"):
                return 0.9
        elif stat_name == "def":
            if nature.lower() in ("bold", "relaxed", "impish", "lax"):
                return 1.1
            if nature.lower() in ("lonely", "hasty", "mild", "gentle"):
                return 0.9
        elif stat_name == "spa":
            if nature.lower() in ("modest", "mild", "quiet", "rash"):
                return 1.1
            if nature.lower() in ("adamant", "impish", "jolly", "careful"):
                return 0.9
        elif stat_name == "spd":
            if nature.lower() in ("calm", "gentle", "sassy", "careful"):
                return 1.1
            if nature.lower() in ("naughty", "lax", "naive", "rash"):
                return 0.9
        elif stat_name == "spe":
            if nature.lower() in ("timid", "hasty", "jolly", "naive"):
                return 1.1
            if nature.lower() in ("brave", "relaxed", "quiet", "sassy"):
                return 0.9
        return 1.0

    def to_dict(self):
        return {
            "name": self.name,
            "nickname": self.nickname,
            "level": self.level,
            "gender": self.gender,
            "id": self.id,
            "ability": self.ability,
            "type": self.type,
            "base_stats": self.base_stats,
            "stats": self.stats,  # Calculated stats
            "ev": self.ev,
            "iv": self.iv,
            "attacks": self.attacks,
            "base_experience": self.base_experience,
            "growth_rate": self.growth_rate,
            "everstone": self.everstone,
            "shiny": self.shiny,
            "captured_date": getattr(self, "captured_date", None),
            "individual_id": self.individual_id,
            "mega": getattr(self, "mega", False),
            "special-form": getattr(self, "special_form", None),
            "evos": self.evos,
            "xp": self.xp,
            "hp": self.hp,  # Current HP
            "friendship": self.friendship,
            "pokemon_defeated": self.pokemon_defeated,
            "tier": self.tier,  # Added tier
            "is_favorite": getattr(self, "is_favorite", False),  # Added with default
            # Additional fields from your example
            "current_hp": getattr(self, "current_hp", "hp"),  # For backward compatibility
            "held_item": self.held_item,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def get_stats(self):
        """Return the stats of the Pokémon."""
        return vars(self)

    def update_stats(self, **kwargs):
        """Update the attributes of the Pokémon object with keyword arguments."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self._update_battle_stats()  # Update battle stats

    def reset_stats(self):
        """Reset the stats of the Pokémon to default values."""
        self.hp = self.max_hp
        self.battle_status = "Fighting"
        self._update_battle_stats()

    def _update_battle_stats(self):
        """Update battle stats with current stats, EVs, and IVs."""
        self._battle_stats = {}
        # Only update battle stats with valid keys
        for d in [self.stats, self.iv, self.ev]:
            for key, value in d.items():
                self._battle_stats[key] = value

    def calculate_max_hp(self):
        ev, iv = self.ev["hp"], self.iv["hp"]
        hp = 10 + self.level + int((2 * self.base_stats["hp"] + iv + int(ev / 4)) * self.level / 100)
        hp = int(hp)
        return hp

    def get_sprite_path(self, side, sprite_type):
        """Return the path to the sprite of the Pokémon."""
        base_path = f"{side}_default_gif" if sprite_type == "gif" else f"{side}_default"

        shiny_path = "shiny/" if self.shiny else ""
        gender_path = "female/" if self.gender == "F" else ""

        path = f"{pkmnimgfolder}/{base_path}/{shiny_path}{gender_path}{self.id}.{sprite_type}"
        default_path = f"{pkmnimgfolder}/front_default/substitute.png"

        # Check if the file exists at the given path
        if os.path.exists(path):
            return path
        else:
            if self.gender == "F":
                gender_path = ""
                path = f"{pkmnimgfolder}/{base_path}/{shiny_path}{gender_path}{self.id}.{sprite_type}"
                return path
            elif self.shiny == "True":
                shiny_path = ""
                path = f"{pkmnimgfolder}/{base_path}/{shiny_path}{gender_path}{self.id}.{sprite_type}"
                return path
            else:
                return default_path

    def to_engine_format(self):
        from ..poke_engine.helpers import normalize_name
        return {
            'identifier': normalize_name(self.name),
            'level': self.level,
            'nature': getattr(self, 'nature', 'serious'),
            'evs': (
                self.ev.get('hp', 0),
                self.ev.get('atk', 0),
                self.ev.get('def', 0),
                self.ev.get('spa', 0),
                self.ev.get('spd', 0),
                self.ev.get('spe', 0)
            ),
            'types': [normalize_name(t) for t in self.type],
            'hp': self.hp,
            'maxhp': self.max_hp,
            'ability': normalize_name(self.ability) if self.ability else 'none',
            'item': normalize_name(self.held_item) if self.held_item else None,
            'attack': self.stats.get('atk', 0),
            'defense': self.stats.get('def', 0),
            'special_attack': self.stats.get('spa', 0),
            'special_defense': self.stats.get('spd', 0),
            'speed': self.stats.get('spe', 0),
            'ivs': (
                self.iv.get('hp', 0),
                self.iv.get('atk', 0),
                self.iv.get('def', 0),
                self.iv.get('spa', 0),
                self.iv.get('spd', 0),
                self.iv.get('spe', 0)
            ),
            'attack_boost': self.stat_stages.get('atk', 0),
            'defense_boost': self.stat_stages.get('def', 0),
            'special_attack_boost': self.stat_stages.get('spa', 0),
            'special_defense_boost': self.stat_stages.get('spd', 0),
            'speed_boost': self.stat_stages.get('spe', 0),
            'accuracy_boost': self.stat_stages.get('accuracy', 0),
            'evasion_boost': self.stat_stages.get('evasion', 0),
            'status': self.battle_status if self.battle_status != "fighting" else None,
            'volatile_status': set(normalize_name(vs) for vs in self.volatile_status),
            'moves': [{'id': normalize_name(move)} for move in self.attacks]
        }

    @classmethod
    def from_engine_format(cls, engine_data):
        """Create PokemonObject from poke-engine data"""
        return cls(
            name=engine_data['identifier'].capitalize(),
            level=engine_data['level'],
            hp=engine_data['hp'],
            base_stats={
                'hp': engine_data.get('maxhp', 0),
                'atk': engine_data['attack'],
                'def': engine_data['defense'],
                'spa': engine_data['special_attack'],
                'spd': engine_data['special_defense'],
                'spe': engine_data['speed']
            },
            ev={k: v for k, v in zip(['hp','atk','def','spa','spd','spe'], engine_data['evs'])},
            iv={k: v for k, v in zip(['hp','atk','def','spa','spd','spe'], engine_data['ivs'])},
            battlestatus=engine_data.get('status', 'fighting'),
            moves=engine_data['moves'],
            stat_stages={
                'atk': engine_data['stat_stages']['attack'],
                'def': engine_data['stat_stages']['defense'],
                'spa': engine_data['stat_stages']['special_attack'],
                'spd': engine_data['stat_stages']['special_defense'],
                'spe': engine_data['stat_stages']['speed'],
                'accuracy': engine_data['stat_stages']['accuracy'],
                'evasion': engine_data['stat_stages']['evasion']
            },
            volatile_status=set(engine_data.get('volatile_status', [])),
            nature=engine_data.get('nature', 'serious'),
            held_item=engine_data.get('item', '')
        )

    def to_poke_engine_Pokemon(self) -> Pokemon:
        _dict = self.to_engine_format()
        pokemon = Pokemon(
            identifier=_dict['identifier'],
            level=_dict['level'],
            types=_dict['types'],
            hp=_dict['hp'],
            maxhp=_dict['maxhp'],
            ability=_dict['ability'],
            item=_dict['item'],
            attack=_dict['attack'],
            defense=_dict['defense'],
            special_attack=_dict['special_attack'],
            special_defense=_dict['special_defense'],
            speed=_dict['speed'],
            nature=_dict.get('nature', 'serious'),
            evs=_dict.get('evs', (85,) * 6),
            attack_boost=_dict.get('attack_boost', 0),
            defense_boost=_dict.get('defense_boost', 0),
            special_attack_boost=_dict.get('special_attack_boost', 0),
            special_defense_boost=_dict.get('special_defense_boost', 0),
            speed_boost=_dict.get('speed_boost', 0),
            accuracy_boost=_dict.get('accuracy_boost', 0),
            evasion_boost=_dict.get('evasion_boost', 0),
            status=_dict.get('status', None),
            terastallized=_dict.get('terastallized', False),
            volatile_status=_dict.get('volatile_status', set()),
            moves=_dict.get('moves', [])
        )
        return pokemon

    def reset_bonuses(self):
        """
        This method resets various bonuses and status effects currently applied
        to the pokemon.

        This method is typically used to reset the stat boosts of the main
        Pokemon when the opponent gets KOed, preventing the user from
        steamrolling every wild pokemon once the main pokemon is setup with
        stat boosts.

        Args:
            None

        Returns:
            None
        """
        self.stat_stages = {
            'atk': 0,
            'def': 0,
            'spa': 0,
            'spd': 0,
            'spe': 0,
            'accuracy': 0,
            'evasion': 0
            }

    def give_held_item(self, held_item: str) -> None:
        """
        Assigns a held item to the Pokémon and updates relevant data files.

        If the Pokémon is already holding an item, it is removed first. The specified
        item is subtracted from the item bag, assigned as the Pokémon's held item,
        and then saved in the user's Pokémon data files.

        This method updates both `mypokemon_path` (the full Pokémon list) and
        `mainpokemon_path` (if the Pokémon is the main one) to reflect the new held item.

        Args:
            held_item (str): The name of the item to be given to the Pokémon.

        Returns:
            None

        Side Effects:
            - Modifies `mypokemon_path` JSON file to set the held item.
            - Modifies `mainpokemon_path` JSON file if the Pokémon is the main one.
            - Removes one instance of the held item from the item bag.
            - If an item is already held, it is removed first.
            - Uses `ShowInfoLogger` for logging in case of errors via `substract_item_from_itembag`.
        """
        # If the pokemon already holds an object, we remove it to make room for the new one.
        if self.held_item:
            self.remove_held_item()

        substract_item_from_itembag(held_item, quantity=1)
        self.held_item = held_item

        # Then, We save that information in the user data
        # First, we save the info in mypokemon_path
        with open(mypokemon_path, "r", encoding="utf-8") as f:
            pokemon_list_data = json.load(f)

        for i in range(len(pokemon_list_data)):
            if pokemon_list_data[i]["individual_id"] == self.individual_id:
                pokemon_list_data[i]["held_item"] = held_item
                break

        with open(str(mypokemon_path), "w") as f:
            json.dump(pokemon_list_data, f, indent=2)

        # Secondly, we save the info in mainpokemon_path, if the pokemon happens to be our main pokemon
        with open(mainpokemon_path, "r", encoding="utf-8") as f:
            main_pokemon_data = json.load(f)

        if main_pokemon_data[0]["individual_id"] == self.individual_id:
            main_pokemon_data[0]["held_item"] = held_item
            with open(str(mainpokemon_path), "w") as f:
                json.dump(main_pokemon_data, f, indent=2)

    def remove_held_item(self) -> None:
        """
        Removes the held item from the Pokémon and updates relevant data files.

        If the Pokémon is currently holding an item, the item is returned to the item bag
        via `give_item`, the `held_item` attribute is cleared, and the change is saved
        in both `mypokemon_path` (the user's Pokémon list) and `mainpokemon_path` (if the
        Pokémon is the main one).

        Returns:
            None

        Side Effects:
            - Adds the held item back to the item bag using `give_item`.
            - Updates the `mypokemon_path` JSON file to set `held_item` to `None`.
            - If the Pokémon is the main Pokémon, updates the `mainpokemon_path` file as well.
        """
        if self.held_item is None:
            return

        give_item(self.held_item)  # We put the item back in the item bag
        self.held_item = None

        # Then, We save that information in the user data
        # First, we save the info in mypokemon_path
        with open(mypokemon_path, "r", encoding="utf-8") as f:
            pokemon_list_data = json.load(f)

        for i in range(len(pokemon_list_data)):
            if pokemon_list_data[i]["individual_id"] == self.individual_id:
                pokemon_list_data[i]["held_item"] = None
                break

        with open(str(mypokemon_path), "w") as f:
            json.dump(pokemon_list_data, f, indent=2)

        # Secondly, we save the info in mainpokemon_path, if the pokemon happens to be our main pokemon
        with open(mainpokemon_path, "r", encoding="utf-8") as f:
            main_pokemon_data = json.load(f)

        if main_pokemon_data[0]["individual_id"] == self.individual_id:
            main_pokemon_data[0]["held_item"] = None
            with open(str(mainpokemon_path), "w") as f:
                json.dump(main_pokemon_data, f, indent=2)


class PokemonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PokemonObject):
            data = obj.__dict__.copy()
            # Convert complex types to serializable formats
            data['volatile_status'] = list(data['volatile_status'])
            data['stat_stages'] = data.get('stat_stages', {})
            data['moves'] = data.get('attacks', [])
            return data
        return super().default(obj)
