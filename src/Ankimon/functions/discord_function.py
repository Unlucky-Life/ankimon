import threading
import random
import time
from ..addon_files.lib.pypresence import Presence
from aqt.utils import showWarning

class DiscordPresence:
    def __init__(self, client_id, large_image_url):
        self.RPC = Presence(client_id)
        self.RPC.connect()
        self.large_image_url = large_image_url
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
        self.state=random.choice(self.quotes)

    def update_presence(self):
        """
        Update the Discord Rich Presence with a new state message.
        """
        try:
            while self.loop:
                self.RPC.update(
                    state=self.state,
                    large_image=self.large_image_url,
                    start=self.start_time
                )
                time.sleep(5)  # Sleep for 5 seconds before updating again
        except Exception as e:
            showWarning(f"Error updating Discord Rich Presence: {e}")

    def start(self):
        """
        Start updating the Discord Rich Presence in a separate thread.
        """
        if not self.thread:
            self.thread = threading.Thread(target=self.update_presence)
            self.thread.start()

    def stop(self):
        """
        Stop updating the Discord Rich Presence.
        """
        self.loop = False
        if self.thread:
            self.thread.join()  # Wait for the thread to finish

    def stop_presence(self):
        """
        Update the Discord Rich Presence to indicate a break when stopping.
        """
        if not self.loop:
            self.RPC.update(
                state="Break time! You’ve earned it.",
                large_image=self.large_image_url
            )