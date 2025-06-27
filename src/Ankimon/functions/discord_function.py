import threading
import random
import time
from ..addon_files.lib.pypresence import Presence
from aqt.utils import showWarning, tooltip
from aqt import mw

class DiscordPresence:
    def __init__(self, client_id, large_image_url, ankimon_tracker, logger, settings_obj, parent=mw):
        try:
            self.RPC = Presence(client_id)
            self.RPC.connect()
            self.large_image_url = large_image_url
            self.ankimon_tracker = ankimon_tracker
            self.logger_obj = mw.logger
            self.settings = settings_obj
            self.loop = True
            self.start_time = time.time()
            self.thread = None
            self.quotes = [
                "Study hard, your Ankimon is watching!",
                "Ankimon, I choose you—let’s master this deck!",
                "Your knowledge is super effective!",
                "Critical hit! You mastered that concept.",
                "Never give up! Every review gets you closer to evolution.",
                "Your brain gained 50 XP! Keep going!",
                "It’s dangerous to go alone—take your Ankimon deck!",
                "A wild Flashcard appeared! What will you do?",
                "Evolve your knowledge—level up with every session!",
                "Gotta review ‘em all, Ankimon style!"
            ]
            self.special_quotes = [
                f"In battle with {self.ankimon_tracker.main_pokemon.name.capitalize()} Lvl {self.ankimon_tracker.main_pokemon.level}",
                f"Currently battling {self.ankimon_tracker.enemy_pokemon.name.capitalize()} Lvl {self.ankimon_tracker.enemy_pokemon.level}",
                f"{self.ankimon_tracker.main_pokemon.name.capitalize()} is fired up and ready to fight!",
                f"The opponent {self.ankimon_tracker.enemy_pokemon.name.capitalize()} seems tough—stay sharp!",
                f"{self.ankimon_tracker.main_pokemon.name.capitalize()} is waiting for your next move!",
                f"Level up and take down {self.ankimon_tracker.enemy_pokemon.name.capitalize()}!",
                f"Victory is within reach for {self.ankimon_tracker.main_pokemon.nickname or self.ankimon_tracker.main_pokemon.name.capitalize()}!",
                f"{self.ankimon_tracker.main_pokemon.name.capitalize()} is determined to show its strength!",
                f"Keep your guard up! {self.ankimon_tracker.enemy_pokemon.name.capitalize()} is no pushover.",
                f"The battle is intense, but {self.ankimon_tracker.main_pokemon.name.capitalize()} won't back down!",
                f"Strategy is key! Plan your moves wisely against {self.ankimon_tracker.enemy_pokemon.name.capitalize()}!",
                f"The stakes are high! {self.ankimon_tracker.main_pokemon.name.capitalize()} needs your help to win this fight!",
                f"Total reviews completed: {self.ankimon_tracker.total_reviews}",
                f"{self.ankimon_tracker.good_count} good reviews so far—keep it up!",
                f"You've marked {self.ankimon_tracker.again_count} cards as 'Again'—let's focus and improve!",
                f"Great job! {self.ankimon_tracker.easy_count} cards rated 'Easy'!",
                f"{self.ankimon_tracker.hard_count} cards rated 'Hard'—you're tackling the tough ones!",
            ]
            self.state = random.choice(self.quotes)
        except Exception as e:
            mw.logger.log("info",f"Error with Discord setup: {e}")

    def update_presence(self):
        """
        Update the Discord Rich Presence with a new state message.
        """
        try:
            while self.loop:
                self.RPC.update(
                    state = random.choice(self.quotes) if int(self.settings.get("misc.discord_rich_presence_text", 1)) == 1 else random.choice(self.special_quotes),
                    large_image=self.large_image_url,
                    start=self.start_time
                )
                time.sleep(30)  # Sleep for 30 seconds before updating again
        except Exception as e:
            mw.logger.log("error",f"Error updating Discord Rich Presence: {e}")

    def start(self):
        """
        Start updating the Discord Rich Presence in a separate thread.
        """
        try:
            if not hasattr(self, 'thread') or self.thread is None or not self.thread.is_alive():
                self.loop = True
                self.thread = threading.Thread(target=self.update_presence, daemon=True)
                self.thread.start()
        except Exception as e:
            mw.logger.log("error",f"Error starting Discord Rich Presence: {e}")

    def stop(self):
        """
        Stop updating the Discord Rich Presence.
        """
        try:
            self.loop = False
            if hasattr(self, 'thread') and self.thread and self.thread.is_alive():
                self.thread.join() # Wait for the thread to finish
                self.thread = None  # Reset the thread
            self.RPC.clear()
        except Exception as e:
            mw.logger.log("error",f"Error clearing Discord Rich Presence: {e}")

    def stop_presence(self):
        """
        Update the Discord Rich Presence to indicate a break when stopping.
        """
        try:
            self.loop = False
            if not self.loop:
                self.RPC.update(
                    state="Break time! You’ve earned it.",
                    large_image=self.large_image_url
                )
        except Exception as e:
            mw.logger.log("error",f"Error updating presence to break state: {e}")
