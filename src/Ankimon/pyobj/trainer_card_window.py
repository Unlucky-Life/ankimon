from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel,
                           QHBoxLayout, QWidget, QGridLayout)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from ..resources import trainer_sprites_path
import os

class TrainerCardGUI(QDialog):
    def __init__(self, trainer_card, settings_obj, parent=None):
        super().__init__(parent)
        self.trainer_card = trainer_card
        self.settings = settings_obj
        self.is_open = False
        self.init_ui()
        self.show()

    def init_ui(self):
        self.setWindowTitle('Trainer Card')
        self.setFixedSize(500, 350)

        # Main layout
        main_layout = QHBoxLayout(self)

        # Left side - Image, name, username, and badges section
        left_widget = QWidget()
        left_widget.setFixedWidth(220)  # Set fixed width for left side
        left_layout = QVBoxLayout(left_widget)

        # Trainer image
        self.trainer_image = QLabel()
        self.trainer_image.setFixedSize(200, 200)
        self.trainer_image.setStyleSheet("""
            QLabel {
                border: 2px solid #4a90e2;
                border-radius: 10px;
            }
        """)

        image_path = os.path.join(trainer_sprites_path, self.settings.get("trainer.sprite") + ".png")

        # Load trainer image if it exists
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.trainer_image.setPixmap(
                pixmap.scaled(190, 190, Qt.AspectRatioMode.KeepAspectRatio)
            )
        else:
            self.trainer_image.setText("No Image Available")

        self.trainer_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Name label
        name_label = QLabel(self.settings.get("trainer.name"))
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Username label (using trainer_id as username)
        username_label = QLabel(f"@{self.trainer_card.trainer_id}")
        username_label.setFont(QFont("Arial", 10))
        username_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Badge count
        badge_label = QLabel(f"Badges: {self.trainer_card.badge_count()}")
        badge_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #level label
        self.level_label = QLabel(f"Level: {self.trainer_card.level}   " + f"XP: {self.trainer_card.xp}")
        self.level_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add widgets to left layout
        left_layout.addWidget(name_label)
        left_layout.addWidget(username_label)
        left_layout.addWidget(self.trainer_image)
        left_layout.addWidget(self.level_label)
        left_layout.addWidget(badge_label)
        left_layout.addStretch()

        # Right side - Info section
        right_widget = QWidget()
        right_widget.setFixedHeight(300)  # Set fixed width for left side
        right_layout = QVBoxLayout(right_widget)

        # Create styled labels
        def create_info_label(title, value):
            title_label = QLabel(f"{title} {value}")
            title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            title_label.setWordWrap(True)
            right_layout.addWidget(title_label)
            return title_label

        # Add trainer information (excluding name and id since they're now on the left)
        self.cash = create_info_label("Cash:", f"{self.trainer_card.cash}$")
        self.fav_pokemon_label = create_info_label("Favorite Pokémon:", self.trainer_card.favorite_pokemon)
        self.team_pokemon_label = create_info_label("Team:", self.trainer_card.team)
        self.highest_level_label = create_info_label("Highest Level:", self.trainer_card.highest_level)
        self.league_label = create_info_label("League:", self.trainer_card.league)
        self.next_lvl_label = create_info_label(f"XP Needed for Level Up:", f"{self.trainer_card.xp_for_next_level()} XP")
        # Add widgets to main layout
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

    def update_display(self):
        """Update all displayed information"""
        # Update left side
        name_label = self.findChild(QLabel, "name_label")
        if name_label:
            name_label.setText(str(self.trainer_card.trainer_name))

        username_label = self.findChild(QLabel, "username_label")
        if username_label:
            username_label.setText(f"@{self.trainer_card.trainer_id}")

        # Update right side
        self.level_label.setText(f"Level: {self.trainer_card.level} XP: {self.trainer_card.xp}")
        self.fav_pokemon_label.setText(f"Favorite Pokémon: {self.trainer_card.favorite_pokemon}")
        self.team_pokemon_label.setText(f"Team: {self.trainer_card.team}")
        self.highest_level_label.setText(f"Highest Level: {self.trainer_card.highest_level}")
        self.league_label.setText(f"League: {self.trainer_card.league}")

        # Update image if changed
        if os.path.exists(self.trainer_card.image_path):
            pixmap = QPixmap(self.trainer_card.image_path)
            self.trainer_image.setPixmap(
                pixmap.scaled(190, 190, Qt.AspectRatioMode.KeepAspectRatio)
            )

    def toggle_window(self):
            """Toggle the window between open and closed states"""
            if not self.is_open:
                self.update_display()
                self.show()
                self.is_open = True
            else:
                self.hide()
                self.is_open = False