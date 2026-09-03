from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout, QWidget
from aqt import mw

from ..functions import multiplayer_functions
from ..functions.raid_functions import show_bot_battle_result
from ..resources import trainer_sprites_path


class TrainerBotDialog(QDialog):
    """Roster view and challenge entry point for practice trainers."""

    def __init__(self, parent=mw):
        super().__init__(parent)
        self.setWindowTitle("Ankimon Trainer Battles")
        self.setMinimumSize(560, 520)
        self._seen_finished_matches = set()
        self._state = {}

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Practice against a named trainer. Each trainer fields a different Pokémon and style."))
        self.attack_status = QLabel("Banked attacks: 0 / 3")
        layout.addWidget(self.attack_status)
        self.roster = QListWidget()
        layout.addWidget(self.roster)
        refresh = QPushButton("Refresh trainers")
        refresh.clicked.connect(self.refresh)
        layout.addWidget(refresh)
        self.refresh()

    def refresh(self):
        try:
            state = multiplayer_functions.get_state()
        except multiplayer_functions.MultiplayerClientError as exc:
            QMessageBox.warning(self, "Trainer Battles", str(exc))
            return
        self._state = state
        pvp_state = state.get("pvp", {})
        self.attack_status.setText(
            f"Banked attacks: {pvp_state.get('banked_attacks', 0)} / "
            f"{pvp_state.get('max_banked_attacks', 3)}"
        )

        self.roster.clear()
        for bot in state.get("bots", []):
            item = QListWidgetItem()
            self.roster.addItem(item)
            match = next(
                (candidate for candidate in state.get("pvp", {}).get("matches", [])
                 if candidate.get("opponent") == bot.get("username") and
                 candidate.get("opponent_is_bot")),
                None,
            )
            self.roster.setItemWidget(item, self._bot_widget(bot, match, pvp_state))

        for match in state.get("pvp", {}).get("matches", []):
            if match.get("opponent_is_bot") and match.get("status") == "finished":
                match_id = match.get("id")
                if match_id and match_id not in self._seen_finished_matches:
                    self._seen_finished_matches.add(match_id)
                    won = match.get("winner") != match.get("opponent")
                    show_bot_battle_result(match.get("opponent", "trainer"), won)

    def _bot_widget(self, bot, match=None, pvp_state=None):
        widget = QWidget()
        row = QHBoxLayout(widget)
        sprite = QLabel()
        sprite_path = trainer_sprites_path / f"{bot.get('trainer_sprite', '')}.png"
        if sprite_path.exists():
            sprite.setPixmap(QPixmap(str(sprite_path)).scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            sprite.setText("Trainer")
        row.addWidget(sprite)
        battle_text = ""
        if match and match.get("status") == "active":
            battle_text = (
                f"<br><b>Battle:</b> You {match.get('your_hp', '?')} HP · "
                f"{match.get('opponent', 'Trainer')} {match.get('opponent_hp', '?')} HP"
            )
        elif match and match.get("status") == "finished":
            won = match.get("winner") != match.get("opponent")
            battle_text = f"<br><b>{'Victory' if won else 'Defeat'}</b>"
        text = QLabel(
            f"<b>{bot.get('trainer_name', bot.get('username', 'Trainer'))}</b>"
            f" &mdash; {bot.get('trainer_rank', 'Trainer')}<br>"
            f"{bot.get('motto', '')}<br>"
            f"Pokémon: {bot.get('pokemon', '?')} · Lv. {bot.get('level', '?')}"
            f"{battle_text}"
        )
        text.setTextFormat(Qt.TextFormat.RichText)
        row.addWidget(text, 1)
        challenge = QPushButton("Challenge")
        challenge.setEnabled(not bot.get("in_match", False))
        challenge.clicked.connect(lambda: self.challenge(bot))
        row.addWidget(challenge)
        if match and match.get("status") == "active":
            attack = QPushButton("Attack")
            attack.setEnabled((pvp_state or {}).get("banked_attacks", 0) > 0)
            attack.clicked.connect(lambda: self.attack(match["id"]))
            row.addWidget(attack)
        return widget

    def challenge(self, bot):
        try:
            multiplayer_functions.challenge_bot(bot["challenge_value"])
        except multiplayer_functions.MultiplayerClientError as exc:
            QMessageBox.warning(self, "Trainer Battle", str(exc))
            return
        QMessageBox.information(self, "Trainer Battle", f"{bot.get('trainer_name', bot.get('username', 'Trainer'))} accepts your challenge!\nAnswer a card to make your first move.")
        self.refresh()

    def attack(self, match_id):
        try:
            state = multiplayer_functions.submit_turn(match_id)
        except multiplayer_functions.MultiplayerClientError as exc:
            QMessageBox.warning(self, "Trainer Battle", str(exc))
            return
        self.refresh()
