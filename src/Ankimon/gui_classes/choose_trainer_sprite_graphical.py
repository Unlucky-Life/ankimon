
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
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
        self.trainer_sprites = get_all_sprites(trainer_sprites_path)
        self.setModal(True)

        # Layout
        layout = QVBoxLayout()

        # Label
        label = QLabel("Choose your trainer sprite:")
        layout.addWidget(label)

        # List Widget
        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(100, 100))
        self.list_widget.setFlow(QListWidget.Flow.LeftToRight)
        self.list_widget.setWrapping(True)
        self.list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)

        # Populate List Widget
        for sprite_name in self.trainer_sprites:
            sprite_path = os.path.join(trainer_sprites_path, sprite_name + ".png")
            if os.path.exists(sprite_path):
                item = QListWidgetItem(QIcon(sprite_path), sprite_name)
                self.list_widget.addItem(item)

        # Set layout
        self.setLayout(layout)
        self.setMinimumSize(500, 400)

    def on_item_clicked(self, item):
        selected_sprite = item.text()
        self.settings.set("trainer.sprite", selected_sprite)
        self.accept()
