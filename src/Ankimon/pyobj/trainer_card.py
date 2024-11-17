from ..resources import trainer_sprites_path

class TrainerCard:
    def __init__(self, trainer_name, badge_count, favorite_pokemon, trainer_id, level=1, xp=0, achievements=None, team="", image_path=trainer_sprites_path, highest_level=0, league="unranked", cash="0"):
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
    
    def gain_xp(self, points):
        """Method to add experience points and level up if necessary"""
        self.xp += points
        self.level_up()

    def level_up(self):
        """Method to level up the trainer based on XP"""
        while self.xp >= 100:
            self.xp -= 100
            self.level += 1

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
            'achievements': self.achievements
        }
