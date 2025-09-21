from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, 
    QLabel, QMessageBox, QListWidgetItem, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase, QFont, QIcon
from pathlib import Path

from ..pyobj.backup_manager import BackupManager
from ..resources import addon_dir

class BackupItemWidget(QWidget):
    """Custom widget for displaying a single backup's information."""
    def __init__(self, backup_data: dict, parent=None):
        super().__init__(parent)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(15, 10, 15, 10)
        self.main_layout.setSpacing(15)

        # Date Info
        date_layout = QVBoxLayout()
        date_str, time_str = backup_data.get('date', ' ').split(' ', 1)
        date_label = QLabel(date_str)
        time_label = QLabel(time_str)
        date_label.setObjectName("DateLabel")
        time_label.setObjectName("TimeLabel")
        date_layout.addWidget(date_label)
        date_layout.addWidget(time_label)
        date_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Trainer Info
        trainer_layout = QVBoxLayout()
        trainer_name = backup_data.get('trainer_name', 'N/A')
        main_pokemon_name = backup_data.get('main_pokemon_name', 'N/A')
        main_pokemon_level = backup_data.get('main_pokemon_level', 'N/A')
        trainer_name_label = QLabel(f"{trainer_name}")
        main_pokemon_label = QLabel(f"{main_pokemon_name} (Lv. {main_pokemon_level})")
        trainer_name_label.setObjectName("TrainerName")
        trainer_layout.addWidget(trainer_name_label)
        trainer_layout.addWidget(main_pokemon_label)

        # Game Stats
        stats_layout = QVBoxLayout()
        poke_count = backup_data.get('pokemon_count', 0)
        item_count = backup_data.get('item_count', 0)
        cash = backup_data.get('trainer_cash', 0)
        poke_count_label = QLabel(f"{poke_count} Pokémon")
        item_count_label = QLabel(f"{item_count} Items")
        cash_label = QLabel(f"${cash}")
        cash_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        stats_layout.addWidget(poke_count_label)
        stats_layout.addWidget(item_count_label)

        self.main_layout.addLayout(date_layout)
        self.main_layout.addLayout(trainer_layout)
        self.main_layout.addStretch()
        self.main_layout.addLayout(stats_layout)
        self.main_layout.addWidget(cash_label)
        self.setLayout(self.main_layout)

class BackupManagerDialog(QDialog):
    def __init__(self, backup_manager: BackupManager, parent=None):
        super().__init__(parent)
        self.backup_manager = backup_manager
        self.setWindowTitle("Ankimon Backup Manager")
        self.setMinimumSize(650, 500)
        self.init_ui()
        self.apply_stylesheet()
        self.refresh_backup_list()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.backup_list_widget = QListWidget()
        self.backup_list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        main_layout.addWidget(self.backup_list_widget)

        button_layout = QHBoxLayout()
        self.restore_button = QPushButton("Restore Backup")
        self.restore_button.clicked.connect(self.restore_selected_backup)
        self.restore_button.setEnabled(False)
        self.restore_button.setObjectName("RestoreButton")
        
        self.manual_backup_button = QPushButton("Create New Backup")
        self.manual_backup_button.clicked.connect(self.create_manual_backup)
        
        self.delete_button = QPushButton("Delete Backup")
        self.delete_button.clicked.connect(self.delete_selected_backup)
        self.delete_button.setEnabled(False)
        self.delete_button.setObjectName("DeleteButton")

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)

        button_layout.addWidget(self.manual_backup_button)
        button_layout.addStretch()
        button_layout.addWidget(self.restore_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

        # Add backup path label
        backup_path_label = QLabel(f"Backups are stored in: {self.backup_manager.backups_path}")
        backup_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        backup_path_label.setObjectName("BackupPathLabel")
        main_layout.addWidget(backup_path_label)

        self.setLayout(main_layout)

    def apply_stylesheet(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #2a2a2a;
                color: #f0f0f0;
            }}
            QListWidget {{
                background-color: #3c3c3c;
                border: 2px solid #555;
                border-radius: 5px;
            }}
            QListWidget::item {{
                border-bottom: 1px solid #4a4a4a;
                color: #e0e0e0;
            }}
            QListWidget::item:selected {{
                background-color: #e33b3b;
                color: #ffffff;
                border: 1px solid #ff5c5c;
            }}
            #DateLabel {{
                font-weight: bold;
                color: #cccccc;
            }}
            #TimeLabel {{
                color: #aaaaaa;
                font-size: 0.9em;
            }}
            #TrainerName {{
                font-weight: bold;
                font-size: 1.1em;
                color: #ffffff;
            }}
            QPushButton {{
                background-color: #5a5a5a;
                border: 1px solid #777;
                padding: 8px 12px;
                border-radius: 5px;
                color: #f0f0f0;
            }}
            QPushButton:hover {{
                background-color: #6a6a6a;
                border-color: #888;
            }}
            QPushButton:disabled {{
                background-color: #4a4a4a;
                color: #888;
            }}
            #RestoreButton {{
                background-color: #c0392b;
            }}
            #RestoreButton:hover {{
                background-color: #e74c3c;
            }}
            #DeleteButton {{
                background-color: #992d22;
            }}
            #DeleteButton:hover {{
                background-color: #c0392b;
            }}
            #BackupPathLabel {{
                font-size: 0.8em;
                color: #aaaaaa;
            }}
        """)

    def refresh_backup_list(self):
        self.backup_list_widget.clear()
        backups = self.backup_manager.get_backups()
        if not backups:
            no_backup_item = QListWidgetItem("No backups found.")
            no_backup_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.backup_list_widget.addItem(no_backup_item)
            return

        for backup in backups:
            item = QListWidgetItem(self.backup_list_widget)
            item.setData(Qt.ItemDataRole.UserRole, backup)
            widget = BackupItemWidget(backup)
            item.setSizeHint(widget.sizeHint())
            self.backup_list_widget.addItem(item)
            self.backup_list_widget.setItemWidget(item, widget)

    def on_selection_changed(self):
        has_selection = len(self.backup_list_widget.selectedItems()) > 0
        self.restore_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def create_manual_backup(self):
        self.backup_manager.create_backup(manual=True)
        self.refresh_backup_list()

    def delete_selected_backup(self):
        selected_items = self.backup_list_widget.selectedItems()
        if not selected_items:
            return

        reply = QMessageBox.question(self, "Delete Backup",
                                     "Are you sure you want to permanently delete this backup?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            selected_backup = selected_items[0].data(Qt.ItemDataRole.UserRole)
            backup_path = selected_backup.get('path')
            if backup_path:
                self.backup_manager.delete_backup(backup_path)
                self.refresh_backup_list()
            else:
                QMessageBox.warning(self, "Error", "Could not find path for the selected backup.")

    def restore_selected_backup(self):
        selected_items = self.backup_list_widget.selectedItems()
        if not selected_items:
            return
        
        selected_backup = selected_items[0].data(Qt.ItemDataRole.UserRole)
        backup_path = selected_backup.get('path')
        
        if backup_path:
            self.backup_manager.restore_backup(backup_path)
        else:
            QMessageBox.warning(self, "Error", "Could not find path for the selected backup.")
