from PyQt6.QtCore import Qt  # Add this import
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtGui import QPixmap
from aqt import mw
from ..utils import get_all_sprites
from ..resources import trainer_sprites_path
import os

class TrainerSpriteDialog(QDialog):
    def __init__(self, settings_obj, parent=mw):
        super().__init__(parent)
        self.setWindowTitle("Choose Your Trainer Sprite")
        self.settings = settings_obj
        self.trainer_sprites = get_all_sprites(trainer_sprites_path)

        # Layout
        layout = QVBoxLayout()

        # Label
        label = QLabel("Choose your trainer sprite:")
        layout.addWidget(label)

        # Image Preview (QLabel)
        self.image_preview = QLabel()
        layout.addWidget(self.image_preview)

        # Dropdown (ComboBox)
        self.dropdown = QComboBox()
        self.dropdown.addItems(self.trainer_sprites)
        self.dropdown.currentTextChanged.connect(self.update_preview)
        layout.addWidget(self.dropdown)

        # OK Button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.on_ok)
        layout.addWidget(ok_button)

        # Set layout
        self.setLayout(layout)

        # Initial preview update
        self.update_preview(self.dropdown.currentText())

    def update_preview(self, selected_sprite):
        # Construct the path to the sprite image
        sprite_path = os.path.join(trainer_sprites_path, selected_sprite + ".png")
        if os.path.exists(sprite_path):
            pixmap = QPixmap(sprite_path)
            self.image_preview.setPixmap(pixmap.scaled(150, 150))  # Resize the image to fit in the preview
            self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the image
        else:
            self.image_preview.clear()  # Clear the preview if no image found

    def on_ok(self):
        selected_sprite = self.dropdown.currentText()
        self.settings.set("trainer.sprite", selected_sprite)
        print(f"You chose: {selected_sprite}")
        self.accept()  # Close the dialog
