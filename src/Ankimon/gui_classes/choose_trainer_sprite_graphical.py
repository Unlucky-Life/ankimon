from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QGridLayout, QWidget, QScrollArea, QPushButton
from PyQt6.QtGui import QIcon
from aqt import mw
from ..utils import get_all_sprites
from ..resources import trainer_sprites_path
import os

class TrainerSpriteGraphicalDialog(QDialog):
    def __init__(self, settings_obj, parent=mw):
        super().__init__(parent)
        self.setWindowTitle("Choose Your Trainer Sprite")
        self.settings = settings_obj
        self.trainer_sprites = sorted(get_all_sprites(trainer_sprites_path))
        self.setModal(True)

        # Layout
        layout = QVBoxLayout()

        # Label
        label = QLabel("Choose your trainer sprite:")
        layout.addWidget(label)

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Grid Widget
        grid_widget = QWidget()
        self.grid_layout = QGridLayout(grid_widget)
        scroll_area.setWidget(grid_widget)

        # Populate Grid
        self.populate_grid()

        # Set layout
        self.setLayout(layout)
        self.setMinimumSize(910, 600)

    def populate_grid(self):
        col = 0
        row = 0
        last_letter = ''
        for sprite_name in self.trainer_sprites:
            if sprite_name[0].lower() != last_letter:
                last_letter = sprite_name[0].lower()
                col = 0
                row += 1
            
            sprite_path = os.path.join(trainer_sprites_path, sprite_name + ".png")
            if os.path.exists(sprite_path):
                # Create a widget to hold the button and label
                item_widget = QWidget()
                item_layout = QVBoxLayout(item_widget)
                item_layout.setContentsMargins(0, 0, 0, 0)
                item_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                button = QPushButton()
                button.setIcon(QIcon(sprite_path))
                button.setIconSize(QSize(100, 100))
                button.setFixedSize(QSize(110, 110))
                button.clicked.connect(lambda _, s=sprite_name: self.on_sprite_clicked(s))
                item_layout.addWidget(button)

                formatted_name = self.format_sprite_name(sprite_name)
                name_label = QLabel(formatted_name)
                name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                item_layout.addWidget(name_label)

                self.grid_layout.addWidget(item_widget, row, col)
                col += 1
                if col >= 6:
                    col = 0
                    row += 1

    def format_sprite_name(self, name):
        return ' '.join(word.capitalize() for word in name.split('-'))

    def on_sprite_clicked(self, sprite_name):
        self.settings.set("trainer.sprite", sprite_name)
        self.accept()
