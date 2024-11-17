import json
class PokemonObject:
    def __init__(self, name, pokemon_species, shiny, id, level, ability, typ, stats=None, attacks=None, base_experience=0, 
                 growth_rate=None, hp=None, max_hp=None, ev=None, iv=None, gender=None, battle_status="Fighting", xp=0, 
                 position=(0, 0), nickname=None, evolutions=None, moves=None):
        self.name = name
        self.nickname = nickname  # Allow nickname to be set in the constructor
        self.pokemon_species = pokemon_species
        self.shiny = shiny
        self.id = id
        self.level = level
        self.ability = ability
        self.type = typ
        self.stats = stats or {}  # Default to empty dict if None
        self.attacks = attacks or []  # Default to empty list if None
        self.base_experience = base_experience
        self.growth_rate = growth_rate
        self.hp = hp or 0  # Default to 0 if None
        self.max_hp = max_hp or 0  # Default to 0 if None
        self.ev = ev or {}  # Default to empty dict if None
        self.iv = iv or {}  # Default to empty dict if None
        self.gender = gender
        self.battle_status = battle_status
        self.xp = xp
        self.position = position
        self.moves = moves or []
        self.evolutions = evolutions or []
        self._battle_stats = {}  # Private attribute for battle stats
        
        # Store battle stats for easy access
        self._update_battle_stats()

    def get_stats(self):
        """Return the stats of the Pokémon."""
        return vars(self)
    
    def update_stats(self, **kwargs):
        """Update Pokémon's stats with new values."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._update_battle_stats()

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

class PokemonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PokemonObject):
            return obj.__dict__  # Convert PokemonObject instance to dictionary
        return json.JSONEncoder.default(self, obj)
