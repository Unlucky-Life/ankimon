from PyQt6.QtCore import QTimer
from .pokemon_obj import PokemonObject
from datetime import datetime, timedelta
from aqt.utils import showWarning
from .error_handler import show_warning_with_traceback
from ..functions.pokedex_functions import extract_ids_from_file
from ..utils import random_battle_scene
import random

class AnkimonTracker:
    def __init__(self, trainer_card, settings_obj):

        # Object bindings
        self.trainer_card = trainer_card
        self.settings = settings_obj

        # Existing stats
        self.total_reviews = 0
        self.good_count = 0
        self.again_count = 0
        self.hard_count = 0
        self.easy_count = 0
        self.current_mode = "idle"
        
        # Session and card timers
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.update_session_timer)
        self.card_timer = QTimer()
        self.card_timer.timeout.connect(self.update_card_timer)
        self.cards_battle_round = 0
        
        # Time tracking
        self.session_time_elapsed = 0
        self.card_time_elapsed = 0
        self.session_time = 0
        self.card_counter = -1
        
        # Tracking additional stats
        self.card_ratings_count = {"Again": 0, "Hard": 0, "Good": 0, "Easy": 0}
        self.multiplier = 1
        self.streak = 0  #Streak for follow up right cards
        self.streak_days = []  # List to track [date, streak]
        self.check_streak()
        self.main_pokemon = None
        self.enemy_pokemon = None
        self.pokemon_stats = {}

        #Item Receive Value
        self.item_receive_value = random.randint(3, 120)

        #Track Pokemon Battle Cards
        self.cry_counter = 0
        self.attack_counter = 0
        self.slp_counter = 0

        #battlescene
        self.randomize_battle_scene()

        #Check if Pokemon is already caught
        self.owned_pokemon_ids = extract_ids_from_file()
        self.pokemon_in_collection = False

        self.pokemon_encouter = 0 #mode for pokemon encounter
        self.general_card_count_for_battle = 0 #count for general card count for battle
        self.caught = 0 #check if pokemon is caught
        
        # Start the session timer when the object is initialized
        self.start_session_timer()

    def set_main_pokemon(self, pokemon):
        """Set the main Pokémon being used."""
        if isinstance(pokemon, PokemonObject):
            self.main_pokemon = pokemon
    
    def set_enemy_pokemon(self, pokemon):
        """Set the enemy Pokémon being fought against."""
        if isinstance(pokemon, PokemonObject):
            self.enemy_pokemon = pokemon

    def check_streak(self):
        """Check and update streak_days based on today's date."""
        today = datetime.today().date()

        if not self.streak_days:
            # Initialize streak if it doesn't exist
            self.streak_days = [[today, 1]]
            return

        # Retrieve the last recorded date and streak count
        last_date, current_streak = self.streak_days[0]

        if last_date == today:
            # No need to update if today is already recorded
            return

        # Calculate the difference in days between today and the last recorded date
        days_difference = (today - last_date).days

        if days_difference == 1:
            # If it's exactly 1 day ago, increase the streak
            self.streak_days[0] = [today, current_streak + 1]
        elif days_difference > 1:
            # If it's more than 1 day, reset the streak
            self.streak_days[0] = [today, 1]

    def get_main_pokemon_stats(self):
        """Retrieve the stats of the main Pokémon."""
        if self.main_pokemon:
            return self.main_pokemon.get_stats()
        return None

    def get_enemy_pokemon_stats(self):
        """Retrieve the stats of the enemy Pokémon."""
        if self.enemy_pokemon:
            return self.enemy_pokemon.get_stats()
        return None

    def add_pokemon(self, pokemon):
        """Add a PokemonObject to the tracker."""
        if isinstance(pokemon, PokemonObject):
            self.pokemon_stats[pokemon.id] = pokemon.get_stats()

    def update_pokemon_stats(self, pokemon):
        """Update stats of a given PokemonObject in the tracker."""
        if pokemon.id in self.pokemon_stats:
            self.pokemon_stats[pokemon.id] = pokemon.get_stats()

    def get_pokemon_stats(self, pokemon_id):
        """Retrieve stats of a specific Pokémon by its ID."""
        return self.pokemon_stats.get(pokemon_id)

    def review(self, answer):
        """Track review statistics based on the answer."""
        if answer == "again":
            self.again_count += 1
            self.streak = 0  # Reset streak if "again"
        elif answer in ["good", "hard", "easy"]:
            # Increment respective count and add to streak for valid answers
            count = getattr(self, f"{answer}_count")  # Get the current count
            count += 1  # Increment the count
            setattr(self, f"{answer}_count", count)  # Set the updated count back to the attribute
            self.streak += 1  # Increment streak
        else:
            raise ValueError("Invalid answer type")

        self.total_reviews += 1
        # Increase the number of cards reviewed and update session time
        self.card_counter += 1
        self.card_ratings_count[answer.capitalize()] += 1
        
        self.check_achievements(self.total_reviews)

        # Stop the card timer after answering and calculate multiplier
        self.reset_card_timer()

        # After 2 cards - set multiplier
        if self.card_counter == 2:
            self.calc_multiply_card_rating()

    def check_achievements(self, total_reviews):
        if total_reviews == 10:
            self.settings.set("trainer.cash", self.settings.get("trainer.cash") + 200)
            self.trainer_card.cash += 200

    def update_streak(self, new_day):
        """Update the streak for daily reviews (each position represents a day)."""
        if not self.streak or self.streak[-1] != new_day:
            self.streak.append(new_day)  # Add a new day to the streak array

    def get_stats(self):
        """Get all the tracked statistics."""
        return {
            "total_reviews": self.total_reviews,
            "good_count": self.good_count,
            "again_count": self.again_count,
            "hard_count": self.hard_count,
            "easy_count": self.easy_count,
            "card_counter": self.card_counter,
            "card_ratings_count": self.card_ratings_count,
            "card_time_elapsed": self.card_time_elapsed,
            "session_time": self.session_time_elapsed,  # Include session time here
            "multiplier": self.multiplier,
            "current_mode": self.current_mode,
            "streak": self.streak,
            "streak_days": self.streak_days,
            "main_pokemon": self.get_main_pokemon_stats(),
            "enemy_pokemon": self.get_enemy_pokemon_stats(),
        }

    def start_card_timer(self):
        """Start the card answer timer."""
        self.card_time_elapsed = 0  # Reset for each new card
        self.card_timer.start(1000)  # Update every second

    def stop_card_timer(self):
        """Stop the card answer timer."""
        self.card_timer.stop()

    def update_card_timer(self):
        """Update the card timer for each second spent on a card."""
        self.card_time_elapsed += 1

    def start_session_timer(self):
        """Start the session timer."""
        self.session_time_elapsed = 0  # Reset session timer on new session
        self.session_timer.start(1000)  # Session timer updates every second

    def stop_session_timer(self):
        """Stop the session timer."""
        self.session_timer.stop()

    def update_session_timer(self):
        """Increment the total session time each second."""
        self.session_time_elapsed += 1

    def calc_multiply_card_rating(self):
        """Calculate the multiplier based on card rating counts."""
        max_points = 20
        multiply_sum = (self.card_ratings_count['Easy'] * 20 +
                        self.card_ratings_count['Hard'] * 5 +
                        self.card_ratings_count['Good'] * 10)
        
        self.multiplier = multiply_sum / max_points
        # Reset card ratings count for next round
        self.card_ratings_count = {"Again": 0, "Hard": 0, "Good": 0, "Easy": 0}
        self.card_counter = 0

    def reset_timers(self):
        """Reset both the session and card timers."""
        self.session_time_elapsed = 0

    def reset_card_timer(self):
        self.card_time_elapsed = 0

    def check_pokecoll_in_list(self):
        owned_pokemon_ids = self.owned_pokemon_ids
        id = self.enemy_pokemon.id
        self.pokemon_in_collection = False
        for num in owned_pokemon_ids:
            if num == id:
                self.pokemon_in_collection = True
    
    def get_ids_in_collection(self):
        try:
            owned_pokemon_ids = []
            owned_pokemon_ids = extract_ids_from_file()
            self.owned_pokemon_ids = owned_pokemon_ids
        except Exception as e:
            show_warning_with_traceback(parent=mw, exception=e, message="Error: from AnkimonTracker with function extract_ids_from_file")
    
    def get_badges(self):
        pass

    def randomize_battle_scene(self):
        self.battlescene_file = random_battle_scene()