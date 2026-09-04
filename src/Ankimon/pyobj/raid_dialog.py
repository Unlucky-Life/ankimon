from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QListWidget, QProgressBar, QTabWidget, QWidget, QMessageBox,
)
from PyQt6.QtCore import Qt
from aqt import mw

from ..functions import raid_functions
from ..functions.raid_functions import RaidClientError


class RaidDialog(QDialog):
    def __init__(self, raid_session, parent=mw):
        super().__init__(parent)
        self.raid_session = raid_session

        self.setWindowTitle("Ankimon Raid")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(self._build_create_tab(), "Available raids")
        self.tabs.addTab(self._build_join_tab(), "Join")

        self.status_group = QWidget()
        status_layout = QVBoxLayout(self.status_group)
        self.status_label = QLabel("Not currently in a raid.")
        self.hp_bar = QProgressBar()
        self.hp_bar.setRange(0, 1)
        self.hp_bar.setValue(0)
        self.participants_list = QListWidget()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.hp_bar)
        status_layout.addWidget(QLabel("Participants:"))
        status_layout.addWidget(self.participants_list)

        refresh_row = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_status)
        self.leave_button = QPushButton("Leave raid")
        self.leave_button.clicked.connect(self.leave_raid)
        refresh_row.addWidget(self.refresh_button)
        refresh_row.addWidget(self.leave_button)
        status_layout.addLayout(refresh_row)

        layout.addWidget(self.status_group)

        self.refresh_available_raids()
        self.refresh_status()

    def _build_create_tab(self):
        tab = QWidget()
        form = QVBoxLayout(tab)
        form.addWidget(QLabel("Raids are created automatically by the server."))
        self.available_raids = QListWidget()
        form.addWidget(self.available_raids)
        self.available_raids.itemDoubleClicked.connect(self.join_available_room)
        refresh_button = QPushButton("Refresh available raids")
        refresh_button.clicked.connect(self.refresh_available_raids)
        form.addWidget(refresh_button)
        return tab

    def _build_join_tab(self):
        tab = QWidget()
        form = QVBoxLayout(tab)

        self.raid_id_input = QLineEdit()
        self.raid_id_input.setPlaceholderText("Raid ID (shared by whoever created it)")

        join_button = QPushButton("Join raid")
        join_button.clicked.connect(self.join_raid)

        form.addWidget(QLabel("Raid ID"))
        form.addWidget(self.raid_id_input)
        form.addWidget(join_button)
        return tab

    def refresh_available_raids(self):
        try:
            rooms = raid_functions.list_active_raids()
        except RaidClientError as e:
            QMessageBox.warning(self, "Ankimon Raid", str(e))
            return
        self.available_raids.clear()
        for room in rooms:
            item = QListWidgetItem(
                f"{room['boss_name']} Lv. {room['boss_level']} — "
                f"{room['party_size']}/{room.get('capacity', 5)} trainers"
            )
            item.setData(Qt.ItemDataRole.UserRole, room["code"])
            self.available_raids.addItem(item)

    def join_available_room(self, item):
        self.join_room(item.data(Qt.ItemDataRole.UserRole))

    def join_room(self, raid_id):
        try:
            raid_state = raid_functions.join_raid(raid_id)
            self.raid_session.start(raid_state)
            self.refresh_status()
        except RaidClientError as e:
            QMessageBox.warning(self, "Ankimon Raid", str(e))

    def join_raid(self):
        raid_id = self.raid_id_input.text().strip()
        if not raid_id:
            QMessageBox.warning(self, "Ankimon Raid", "Enter a raid ID first.")
            return
        try:
            raid_state = raid_functions.join_raid(raid_id)
            self.raid_session.start(raid_state)
            self.refresh_status()
        except RaidClientError as e:
            QMessageBox.warning(self, "Ankimon Raid", str(e))

    def leave_raid(self):
        if self.raid_session.raid_id:
            try:
                raid_functions.leave_raid(self.raid_session.raid_id)
            except RaidClientError as e:
                QMessageBox.warning(self, "Ankimon Raid", str(e))
        self.raid_session.stop()
        self.refresh_status()

    def refresh_status(self):
        if not self.raid_session.active or not self.raid_session.raid_id:
            self.status_label.setText("Not currently in a raid.")
            self.hp_bar.setRange(0, 1)
            self.hp_bar.setValue(0)
            self.participants_list.clear()
            return

        try:
            raid_state = raid_functions.poll_raid_state(self.raid_session.raid_id)
            self.raid_session.apply_state(raid_state)
            raid_functions.announce_completion(self.raid_session)
            self.raid_session.note_polled()
        except RaidClientError as e:
            self.status_label.setText(f"Couldn't refresh raid state: {e}")
            return

        defeated = self.raid_session.hp is not None and self.raid_session.hp <= 0
        state_text = "Defeated!" if defeated else "In progress"
        self.status_label.setText(
            f"{self.raid_session.boss_name} (Lv. {self.raid_session.boss_level}) "
            f"- {self.raid_session.hp}/{self.raid_session.max_hp} HP - {state_text}\n"
            f"Raid ID: {self.raid_session.raid_id}"
        )
        self.hp_bar.setRange(0, self.raid_session.max_hp or 1)
        self.hp_bar.setValue(max(0, self.raid_session.hp or 0))

        self.participants_list.clear()
        for participant in self.raid_session.participants.values():
            self.participants_list.addItem(
                f"{participant['username']}: {participant['damage_dealt']} damage dealt"
            )
