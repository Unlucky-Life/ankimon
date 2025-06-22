import threading
import random
import time
from ..addon_files.lib.pypresence import Presence
from aqt.utils import showWarning, tooltip
from aqt import mw, gui_hooks

# Discord Rich Presence client ID and large image URL
client_id = '1319014423876075541'  # Replace with your actual client ID
large_image_url = "https://raw.githubusercontent.com/Unlucky-Life/ankimon/refs/heads/main/src/Ankimon/ankimon_logo.png"  # URL for the large image

def initialize_discord_presence(parent=mw):
    """
    Initialize Discord Rich Presence for Ankimon.
    Args:
        ankimon_tracker: Tracker object for Ankimon game state.
        logger: Logger object for logging.
        mw.settings_obj: Settings object for user preferences.
        parent: Parent object, defaults to mw from anki (main window).
    Returns:
        DiscordPresence instance if successful, None otherwise.
    """
    try:
        if mw.settings_obj.get("misc.discord_rich_presence",False) == True:
            mw.ankimon_presence = DiscordPresence(client_id, large_image_url)  # Establish connection and get the presence instance

            # Register the hook functions with Anki's GUI hooks
            gui_hooks.reviewer_did_answer_card.append(on_reviewer_initialized)
            gui_hooks.reviewer_will_end.append(mw.ankimon_presence.stop_presence)
            gui_hooks.sync_did_finish.append(mw.ankimon_presence.stop)
    except Exception as e:
        mw.logger.log("info",f"Error with Discord setup: {e}")
        return None

# Hook functions for Anki
def on_reviewer_initialized(rev, card, ease):
    client_id = '1319014423876075541'  # Replace with your actual client ID
    large_image_url = "https://raw.githubusercontent.com/Unlucky-Life/ankimon/refs/heads/main/src/Ankimon/ankimon_logo.png"  # URL for the large image
    # if user opens the reviewer, check if the Discord presence is already initialized
    # else 
    if mw.ankimon_presence:
        # if the presence is already initialized, start the loop if not set yet
        if mw.ankimon_presence.loop is False:
            mw.ankimon_presence.loop = True
            mw.ankimon_presence.start()
    else:
        # if the presence is not initialized, create a new instance
        mw.ankimon_presence = DiscordPresence(client_id, large_image_url)  # Establish connection and get the presence instance
        mw.ankimon_presence.loop = True
        mw.ankimon_presence.start()
            
def on_reviewer_will_end(*args):
    # if the user closes the reviewer, stop the Discord presence loop
    mw.ankimon_presence.loop = False
    mw.ankimon_presence.stop_presence()

class DiscordPresence:
    """
    Manages Discord Rich Presence integration for Ankimon.
    This class handles connecting to Discord, updating the user's Rich Presence status with motivational or context-aware messages,
    and managing the lifecycle of the presence updates in a background thread.
    Attributes:
        RPC: The Discord Rich Presence client instance.
        large_image_url (str): URL for the large image to display in the presence.
        ankimon_tracker: Object tracking Ankimon game state and statistics.
        logger_obj: Logger object for logging events and errors.
        settings: Settings object for retrieving user preferences.
        loop (bool): Controls the update loop for presence.
        start_time (float): Timestamp when presence started.
        thread (threading.Thread): Background thread for updating presence.
        quotes (list): List of general motivational quotes for presence.
        special_quotes (list): List of dynamic, context-aware quotes based on Ankimon state.
        state (str): Current state message for presence.
    Args:
        client_id (str): Discord application client ID.
        large_image_url (str): URL for the large image in presence.
        ankimon_tracker: Tracker object for Ankimon game state.
        logger: Logger object for logging.
        settings_obj: Settings object for user preferences.
        parent: Parent object, defaults to mw (main window).
    Methods:
        update_presence():
            Periodically updates Discord Rich Presence with a new state message, alternating between general and special quotes
            based on user settings.
        start():
            Starts the background thread to continuously update Discord Rich Presence.
        stop():
            Stops the background thread and clears the Discord Rich Presence.
        stop_presence():
            Updates the Discord Rich Presence to indicate a break when stopping.
    """
    def __init__(self, client_id, large_image_url, parent=mw):
        try:
            # Initialize Discord Rich Presence
            self.RPC = Presence(client_id)
            # Connect to Discord
            self.RPC.connect()
            self.large_image_url = large_image_url
            self.ankimon_tracker = mw.ankimon_tracker
            self.settings = mw.settings_obj
            self.client_id = client_id
            self.large_image_url = large_image_url
            
            #start loop to update presence
            self.loop = True

            #get the start time of study session
            self.start_time = time.time()
            self.thread = None

            # Initialize quotes and special quotes
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
            # Set random intial quote
            self.state = random.choice(self.quotes)
        except Exception as e:
            mw.logger.log("info",f"Error with Discord setup: {e}")

    def update_presence(self):
        """
        Update the Discord Rich Presence with a new state message.
        """
        try:
            # while loop is True, update the presence every 30 seconds
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
            # Stop the loop and clear the presence when loop is set to false
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
            # when user moves to deck overview set loop to False and update presence to break state
            self.loop = False
            if not self.loop:
                self.RPC.update(
                    state="Break time! You’ve earned it.",
                    large_image=self.large_image_url
                )
        except Exception as e:
            mw.logger.log("error",f"Error updating presence to break state: {e}")
