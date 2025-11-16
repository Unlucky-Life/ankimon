from ..resources import trainer_sprites_path, mypokemon_path
from ..functions.trainer_functions import find_trainer_rank
from aqt.utils import showWarning, showInfo
import math
import json
from .ankimon_leaderboard import sync_data_to_leaderboard, get_unique_pokemon, get_total_pokemon, get_shinies


# Constants for leveling
BASE_XP = 50  # Base XP required for level 1
EXPONENTIAL_FACTOR = 1.5  # Scaling factor for exponential XP curve

# Tier-based XP rewards (can be extended)
POKEMON_TIERS = {
    "normal": 10,
    "baby": 16,
    "ultra": 30,
    "legendary": 120,
    "mythical": 160,
}

class TrainerCard:
    def __init__(self, logger, main_pokemon, settings_obj, trainer_name, badge_count, trainer_id, level=1, xp=0, achievements=None, team="", image_path=trainer_sprites_path, league="unranked"):
        self.logger = logger
        self.main_pokemon = main_pokemon
        self.settings_obj = settings_obj
        self.trainer_name = trainer_name      # Name of the trainer
        self.badge_count = badge_count        # Number of badges the trainer has earned
        self.favorite_pokemon = main_pokemon.name  # Trainer's favorite Pokémon
        self.trainer_id = trainer_id          # Unique ID for the trainer
        self.level = int(settings_obj.get("trainer.level"))                    # Trainer's level
        self.xp = xp                          # Experience points
        self.achievements = achievements if achievements else []  # List of achievements (if any)
        self.team = team   # Team as a simple string
        highest_level = self.get_highest_level_pokemon()
        self.highest_level = highest_level  # Highest level Pokémon
        highest_pokemon_level = int(self.highest_pokemon_level())
        self.image_path = f"{trainer_sprites_path}" + "/" + settings_obj.get("trainer.sprite") + ".png"
        league = find_trainer_rank(int(self.highest_pokemon_level()), int(self.level))  # Trainer's rank in the Pokémon world
        self.league = league
        cash = int(settings_obj.get("trainer.cash"))
        self.cash = cash

        #Sync Data to ankimon leaderboard
        data = {
            'trainerRank': f"{league}",  # Example rank
            'trainerName': trainer_name,  # Example trainer name
            'level': max(1, int(settings_obj.get("trainer.level"))),
            'pokedex': get_unique_pokemon(),  # Example Pokedex
            'caughtPokemon': get_total_pokemon(),  # Example Pokedex
            'highestLevel': highest_pokemon_level,  # Example highest level
            'shinies': f"{get_shinies()}",  # Example shinies
            'cash': cash,  # Example cash,
            'trainerSprite': f'{settings_obj.get("trainer.sprite") + ".png"}'
        }
        try:
            sync_data_to_leaderboard(data)
        except Exception as e :
            self.logger.log_and_showinfo("error", f"Error in syncing data to leaderboard {e}")


    def get_highest_level_pokemon(self):
        """Method to find the name of the highest-level Pokémon from the mypokemon_path."""
        try:
            # Read the Pokémon data from the file
            with open(mypokemon_path, "r", encoding="utf-8") as file:
                pokemon_data = json.load(file)

            if not pokemon_data:
                return None  # Return None if the data is empty

            # Find the Pokémon with the highest level and return its name
            highest_pokemon = max(pokemon_data, key=lambda p: p.get("level", 0))
            return f"{highest_pokemon.get('name', 'None')} (Level {highest_pokemon.get('level', 0)})"
        except FileNotFoundError:
            showInfo(f"File not found: {mypokemon_path}")
            return "None"
        except json.JSONDecodeError:
            showInfo(f"Error decoding JSON from file: {mypokemon_path}")
            return "None"

    def highest_pokemon_level(self):
        """Method to find the name of the highest-level Pokémon from the mypokemon_path."""
        try:
            # Read the Pokémon data from the file
            with open(mypokemon_path, "r", encoding="utf-8") as file:
                pokemon_data = json.load(file)

            if not pokemon_data:
                return int(0)  # Return None if the data is empty

            # Find the Pokémon with the highest level and return its name
            highest_pokemon = max(pokemon_data, key=lambda p: p.get("level", 0))
            return int(highest_pokemon.get('level', 0))
        except FileNotFoundError:
            showInfo(f"File not found: {mypokemon_path}")
            return int(0)
        except json.JSONDecodeError:
            showInfo(f"Error decoding JSON from file: {mypokemon_path}")
            return int(0)

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
            'favorite_pokemon': self.main_pokemon.name,
            'highest_level_pokemon': self.get_highest_level_pokemon(),
            'team': self.team,
            'achievements': self.achievements,
            'xp_for_next_level': self.xp_for_next_level,
            'league': self.league,
        }

    def xp_for_next_level(self):
        """Calculate XP required for the next level."""
        return int(BASE_XP * math.pow(self.level, EXPONENTIAL_FACTOR))

    def on_level_up(self):
        """Triggered when leveling up."""
        self.logger.log_and_showinfo("game", f"Congratulations! You reached Level {self.level}!")

    def gain_xp(self, tier, allow_to_choose_move=False):
        """Add XP based on defeated Pokémon's tier."""
        xp_gained = POKEMON_TIERS.get(tier.lower(), 0)
        if allow_to_choose_move is True:
            xp_gained = xp_gained * 0.5
        self.xp += xp_gained
        print(f"Gained {xp_gained} XP from defeating a {tier} Pokémon!")
        self.check_level_up()

    def check_level_up(self):
        """Update level based on XP."""
        while self.xp >= self.xp_for_next_level():
            self.level += 1
            self.settings_obj.set("trainer.level", self.level)
            self.on_level_up()
