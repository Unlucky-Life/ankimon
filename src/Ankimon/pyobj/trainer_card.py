from ..resources import trainer_sprites_path

import math

# Constants for leveling
BASE_XP = 50  # Base XP required for level 1
EXPONENTIAL_FACTOR = 1.5  # Scaling factor for exponential XP curve

# Tier-based XP rewards (can be extended)
POKEMON_TIERS = {
    "normal": 10,
    "baby": 30,
    "ultra": 75,
    "legendary": 500,
    "mythical": 1000,
}

class TrainerCard:
    def __init__(self, trainer_name, badge_count, favorite_pokemon, trainer_id, logger, level=1, xp=0, achievements=None, team="", image_path=trainer_sprites_path, highest_level=0, league="unranked", cash="0"):
        self.trainer_name = trainer_name      # Name of the trainer
        self.badge_count = badge_count        # Number of badges the trainer has earned
        self.favorite_pokemon = favorite_pokemon  # Trainer's favorite Pokémon
        self.trainer_id = trainer_id          # Unique ID for the trainer
        self.level = level                    # Trainer's level
        self.xp = xp                          # Experience points
        self.achievements = achievements if achievements else []  # List of achievements (if any)
        self.team = team                      # Team as a simple string
        self.highest_level_pokemon = self.get_highest_level_pokemon()  # Highest level Pokémon
        self.image_path = image_path
        self.league = league
        self.highest_level = highest_level
        self.cash = cash

    def get_highest_level_pokemon(self):
        """Method to find the highest level Pokémon (from the team string)"""
        if not self.team:
            return None
        # Split the team string and extract the levels
        pokemons = self.team.split(", ")
        highest_pokemon = max(pokemons, key=lambda p: int(p.split(" (Level ")[-1].split(")")[0]))
        return highest_pokemon

    def add_achievement(self, achievement):
        """Method to add a new achievement"""
        self.achievements.append(achievement)

    def set_team(self, team_pokemons):
        """Method to set the trainer's active team (team as a string)"""
        self.team = ", ".join(team_pokemons)

    def display_card_data(self):
        """Method to return trainer card data as a dictionary"""
        return {
            'trainer_name': self.trainer_name,
            'trainer_id': self.trainer_id,
            'level': self.level,
            'xp': self.xp,
            'badges': self.badge_count,
            'favorite_pokemon': self.favorite_pokemon,
            'highest_level_pokemon': self.highest_level_pokemon,
            'team': self.team,
            'achievements': self.achievements,
            'xp_for_next_level': self.xp_for_next_level
        }

    def xp_for_next_level(self):
        """Calculate XP required for the next level."""
        return int(BASE_XP * math.pow(self.level, EXPONENTIAL_FACTOR))

    def on_level_up(self):
        """Triggered when leveling up."""
        logger.log_and_showinfo("game", f"🎉 Congratulations! You reached Level {self.level}!")

    def gain_xp(self, tier):
        """Add XP based on defeated Pokémon's tier."""
        xp_gained = POKEMON_TIERS.get(tier.lower(), 0)
        self.xp += xp_gained
        print(f"Gained {xp_gained} XP from defeating a {tier} Pokémon!")
        self.check_level_up()

    def check_level_up(self):
        """Update level based on XP."""
        while self.xp >= self.xp_for_next_level():
            self.level += 1
            self.on_level_up()