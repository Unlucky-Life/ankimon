from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
from aqt import mw
from ..utils import get_all_sprites
from ..resources import trainer_sprites_path

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

        # Dropdown (ComboBox)
        self.dropdown = QComboBox()
        self.dropdown.addItems(self.trainer_sprites)
        layout.addWidget(self.dropdown)

        # OK Button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.on_ok)
        layout.addWidget(ok_button)

        # Set layout
        self.setLayout(layout)

    def on_ok(self):
        selected_sprite = self.dropdown.currentText()
        self.settings.set("trainer.sprite", selected_sprite)
        print(f"You chose: {selected_sprite}")
        self.accept()  # Close the dialog