"""Client-side state for an active raid, mirroring the shape of AnkimonTracker.

Owns nothing about HTTP - functions/raid_functions.py does the actual
server calls. This just tracks "am I in a raid, and what did the server
last tell me about it" so the reviewer hook and any raid UI can share it.
"""


class RaidSession:
    def __init__(self):
        self.active = False
        self.raid_id = None
        self.boss_name = None
        self.boss_level = None
        self.max_hp = None
        self.hp = None
        self.participants = {}
        self.cards_since_last_poll = 0
        self.poll_every_n_cards = 5

    def start(self, raid_state):
        """Begin tracking a raid from a raid-server state dict (as returned
        by create_raid/join_raid/poll_raid_state)."""
        self.active = True
        self.apply_state(raid_state)

    def stop(self):
        self.active = False
        self.raid_id = None
        self.boss_name = None
        self.boss_level = None
        self.max_hp = None
        self.hp = None
        self.participants = {}
        self.cards_since_last_poll = 0

    def apply_state(self, raid_state):
        """Update local tracking from a raid-server state dict."""
        self.raid_id = raid_state.get("id", self.raid_id)
        self.boss_name = raid_state.get("boss_name", self.boss_name)
        self.boss_level = raid_state.get("boss_level", self.boss_level)
        self.max_hp = raid_state.get("max_hp", self.max_hp)
        self.hp = raid_state.get("hp", self.hp)
        self.participants = raid_state.get("participants", self.participants)
        if self.hp is not None and self.hp <= 0:
            self.active = False

    def should_poll(self):
        """Whether enough cards have been reviewed since the last poll to
        justify refreshing raid state from the server."""
        return self.active and self.cards_since_last_poll >= self.poll_every_n_cards

    def note_card_reviewed(self):
        self.cards_since_last_poll += 1

    def note_polled(self):
        self.cards_since_last_poll = 0
