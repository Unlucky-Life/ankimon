import uuid
import json
from ..resources import pkmnimgfolder
import os

class PokemonObject:
    def __init__(self, name="Ditto", shiny=False, id=1, level=3, ability=["None"], type=["Normal"], current_hp=15, stats=None, attacks=None, base_experience=0, 
                 growth_rate=None, hp=None, ev=None, iv=None, gender=None, battle_status="Fighting", xp=0, 
                 position=0, nickname=None, moves=None, evos=None, tier = "Normal", ev_yield = {"hp": 1, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}, friendship = 0, **kwargs):
        self.name = name
        self.nickname = nickname or "" # Allow nickname to be set in the constructor
        self.shiny = shiny or False  # Default to False if None
        self.id = id
        self.level = level or 3  # Default to 3 if None
        self.ability = ability or ["None"]  # Default to ["None"] if None
        self.type = type or ["Normal"]
        self.stats = stats or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}  # Default to empty dict if None
        self.attacks = attacks or []  # Default to empty list if None
        self.base_experience = base_experience
        self.growth_rate = growth_rate
        self.current_hp = current_hp or 15  # Ensure 'current_hp' is accepted here
        self.ev = ev or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}  # Default to empty dict if None
        self.iv = iv or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}  # Default to empty dict if None
        self.ev_yield = ev_yield or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}
        self.hp = int((((((stats["hp"] + iv["hp"]) * 2 ) + (ev["hp"] / 4)) * level) / 100) + level + 10)
        self.max_hp = self.hp
        self.gender = gender
        self.battle_status = battle_status
        self.xp = xp or 0
        self.position = position
        self.evos = evos or []
        self._battle_stats = {}  # Private attribute for battle stats
        self.tier = tier or "Normal"
        self.everstone = kwargs.get('everstone', False)
        
        #individual_id for saving pokemon
        self.individual_id = kwargs.get('individual_id', str(uuid.uuid4()))

        #friendship value
        self.friendship = friendship or 0

        # Store battle stats for easy access
        self._update_battle_stats()
    
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

class PokemonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PokemonObject):
            return obj.__dict__  # Convert PokemonObject instance to dictionary
        return json.JSONEncoder.default(self, obj)