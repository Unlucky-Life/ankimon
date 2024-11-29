import json
class PokemonObject:
    def __init__(self, name="Ditto", shiny=False, id=1, level=3, ability=["None"], type=["Normal"], current_hp=15, stats=None, attacks=None, base_experience=0, 
                 growth_rate=None, hp=None, ev=None, iv=None, gender=None, battle_status="Fighting", xp=0, 
                 position=0, nickname=None, moves=None, evos=None, tier = "Normal"):
        self.name = name
        self.nickname = nickname or "" # Allow nickname to be set in the constructor
        self.shiny = shiny
        self.id = id
        self.level = level
        self.ability = ability
        self.type = type
        self.stats = stats or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}  # Default to empty dict if None
        self.attacks = attacks or []  # Default to empty list if None
        self.base_experience = base_experience
        self.growth_rate = growth_rate
        self.current_hp = current_hp or 15  # Ensure 'current_hp' is accepted here
        self.ev = ev or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}  # Default to empty dict if None
        self.iv = iv or {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}  # Default to empty dict if None
        self.hp = int((((((stats["hp"] + iv["hp"]) * 2 ) + (ev["hp"] / 4)) * level) / 100) + level + 10)
        self.max_hp = self.hp
        self.gender = gender
        self.battle_status = battle_status
        self.xp = xp
        self.position = position
        self.evos = evos or []
        self._battle_stats = {}  # Private attribute for battle stats
        self.tier = tier or "Normal"
        
        # Store battle stats for easy access
        self._update_battle_stats()

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

class PokemonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PokemonObject):
            return obj.__dict__  # Convert PokemonObject instance to dictionary
        return json.JSONEncoder.default(self, obj)
