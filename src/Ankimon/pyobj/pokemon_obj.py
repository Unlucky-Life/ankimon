import uuid
import json
from ..resources import pkmnimgfolder
import os

class PokemonObject:
    def __init__(
        self,
        name="Ditto",
        shiny=False,
        id=None,
        level=3,
        ability=None,
        type=None,
        stats=None,
        attacks=None,
        base_experience=0,
        growth_rate="medium",
        hp=None,
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

        if not ability or str(ability).strip().lower() in ("none", "no ability", ""):
            self.ability = "Run Away"
        else:
            self.ability = ability

        # Stats
        self.stats = {k: int(v) for k, v in (stats or {"hp": 1, "atk": 1, "def": 1, "spa": 1, "spd": 1, "spe": 1, "xp": 0}).items()}
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
        self.item = kwargs.get('item', None)

        # HP calculation
        self.max_hp = self.calculate_max_hp()
        self.current_hp = int(kwargs.get('current_hp', self.max_hp))
        self.hp = self.current_hp

    def calculate_max_hp(self):
        # Robust HP calculation with fallbacks
        base = self.stats.get("hp", 1)
        iv = self.iv.get("hp", 0)
        ev = self.ev.get("hp", 0)
        try:
            return int((((2 * base + iv + (ev // 4)) * self.level) // 100) + self.level + 10)
        except Exception:
            return 20  # Fallback minimum

    def to_dict(self):
        return {
            "name": self.name,
            "nickname": self.nickname,
            "level": self.level,
            "gender": self.gender,
            "id": self.id,
            "ability": self.ability,
            "type": self.type,
            "stats": self.stats,
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
            "evos": self.evos
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
        ev_value = self.ev["hp"] / 4
        iv_value = self.iv["hp"]
        #hp = int(((iv + 2 * (base_stat_hp + ev) + 100) * level) / 100 + 10)
        hp = int((((((self.stats["hp"] + iv_value) * 2 ) + ev_value) * self.level) / 100) + self.level + 10)
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
            'hp': self.current_hp,
            'maxhp': self.max_hp,
            'ability': normalize_name(self.ability[0]) if self.ability else 'none',
            'item': None,
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
            'status': normalize_name(self.battle_status) if self.battle_status != "fighting" else None,
            'volatile_status': set(normalize_name(vs) for vs in self.volatile_status),
            'moves': [{'id': normalize_name(move)} for move in self.attacks]
        }

    @classmethod
    def from_engine_format(cls, engine_data):
        """Create PokemonObject from poke-engine data"""
        return cls(
            name=engine_data['identifier'].capitalize(),
            level=engine_data['level'],
            current_hp=engine_data['hp'],
            stats={
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
            item=engine_data.get('item', '')
        )

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