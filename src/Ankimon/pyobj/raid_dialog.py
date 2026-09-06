from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QProgressBar, QPushButton, QScrollArea, QVBoxLayout,
    QMessageBox, QWidget,
)
from aqt import mw

from ..functions import raid_functions
from ..functions.raid_functions import RaidClientError


class RaidDialog(QDialog):
    """Server-managed raid lobby using the multiplayer raid-boss view."""

    def __init__(self, raid_session, parent=mw):
        super().__init__(parent)
        self.raid_session = raid_session
        self.setWindowTitle("Ankimon Multiplayer - Raid Boss")
        self.setMinimumSize(420, 420)

        body = QWidget()
        layout = QVBoxLayout(body)
        layout.addWidget(self._build_active_raid_group())
        layout.addWidget(self._build_rooms_group(), stretch=1)

        scroll = QScrollArea()
        scroll.setWidget(body)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        self.refresh_available_raids()
        self.refresh_status()

    def _build_active_raid_group(self):
        group = QGroupBox("Active raid")
        layout = QVBoxLayout(group)
        self.status_label = QLabel("No active raid")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.status_label)
        self.hp_bar = QProgressBar()
        self.hp_bar.setRange(0, 100)
        self.hp_bar.setFormat("Boss HP: %p%")
        layout.addWidget(self.hp_bar)
        self.raid_info = QLabel("Join an open room below to battle together.")
        self.raid_info.setWordWrap(True)
        layout.addWidget(self.raid_info)
        layout.addWidget(QLabel("Party contributions:"))
        self.participants_list = QListWidget()
        self.participants_list.setMaximumHeight(130)
        layout.addWidget(self.participants_list)
        controls = QHBoxLayout()
        refresh_status = QPushButton("Refresh raid")
        refresh_status.clicked.connect(self.refresh_status)
        controls.addWidget(refresh_status)
        self.leave_button = QPushButton("Leave raid")
        self.leave_button.clicked.connect(self.leave_raid)
        controls.addWidget(self.leave_button)
        layout.addLayout(controls)
        return group

    def _build_rooms_group(self):
        group = QGroupBox("Raid rooms")
        layout = QVBoxLayout(group)
        layout.addWidget(QLabel("Open raid rooms are created and replenished by the server:"))
        self.available_raids = QListWidget()
        self.available_raids.itemDoubleClicked.connect(self.join_available_room)
        layout.addWidget(self.available_raids, stretch=1)

        room_controls = QHBoxLayout()
        join_selected = QPushButton("Join selected room")
        join_selected.clicked.connect(self.join_selected_room)
        room_controls.addWidget(join_selected)
        refresh = QPushButton("Refresh rooms")
        refresh.clicked.connect(self.refresh_available_raids)
        room_controls.addWidget(refresh)
        layout.addLayout(room_controls)

        code_row = QHBoxLayout()
        self.raid_id_input = QLineEdit()
        self.raid_id_input.setPlaceholderText("Raid code from a friend")
        self.raid_id_input.returnPressed.connect(self.join_raid)
        code_row.addWidget(self.raid_id_input)
        join_code = QPushButton("Join by code")
        join_code.clicked.connect(self.join_raid)
        code_row.addWidget(join_code)
        layout.addLayout(code_row)
        return group

    def refresh_available_raids(self):
        try:
            rooms = raid_functions.list_active_raids()
        except RaidClientError as exc:
            self.available_raids.clear()
            self.available_raids.addItem("Unable to load raid rooms")
            QMessageBox.warning(self, "Ankimon Raid", str(exc))
            return

        self.available_raids.clear()
        for room in rooms:
            boss = room.get("boss_name", "Raid boss")
            level = room.get("boss_level", "?")
            hp = room.get("boss_hp", 0)
            max_hp = room.get("boss_max_hp", 0)
            hp_pct = int(100 * hp / max_hp) if max_hp else 0
            capacity = room.get("capacity", 5)
            party = f"{room.get('party_size', 0)}/{capacity} trainers"
            status = "full" if room.get("party_size", 0) >= capacity else "open"
            item = QListWidgetItem(
                f"{boss} Lv. {level} - {hp_pct}% HP - {party} - {status}"
            )
            item.setData(Qt.ItemDataRole.UserRole, room.get("code"))
            self.available_raids.addItem(item)
        if not rooms:
            self.available_raids.addItem("No open raid rooms right now.")

    def join_available_room(self, item):
        raid_id = item.data(Qt.ItemDataRole.UserRole)
        if raid_id:
            self.join_room(raid_id)

    def join_selected_room(self):
        item = self.available_raids.currentItem()
        if item is None:
            QMessageBox.information(self, "Ankimon Raid", "Select an open raid room first.")
            return
        self.join_available_room(item)

    def join_room(self, raid_id):
        try:
            raid_state = raid_functions.join_raid(raid_id)
            self.raid_session.start(raid_state)
            self.refresh_status()
            self.refresh_available_raids()
        except RaidClientError as exc:
            QMessageBox.warning(self, "Ankimon Raid", str(exc))

    def join_raid(self):
        raid_id = self.raid_id_input.text().strip()
        if not raid_id:
            QMessageBox.warning(self, "Ankimon Raid", "Enter a raid code first.")
            return
        self.join_room(raid_id)

    def leave_raid(self):
        if self.raid_session.raid_id:
            try:
                raid_functions.leave_raid(self.raid_session.raid_id)
            except RaidClientError as exc:
                QMessageBox.warning(self, "Ankimon Raid", str(exc))
        self.raid_session.stop()
        self.refresh_status()
        self.refresh_available_raids()

    def refresh_status(self):
        if not self.raid_session.active or not self.raid_session.raid_id:
            self.status_label.setText("No active raid")
            self.raid_info.setText("Join an open room below to battle together.")
            self.hp_bar.setValue(0)
            self.participants_list.clear()
            self.leave_button.setEnabled(False)
            return

        try:
            raid_state = raid_functions.poll_raid_state(self.raid_session.raid_id)
            self.raid_session.apply_state(raid_state)
            raid_functions.announce_completion(self.raid_session)
            self.raid_session.note_polled()
        except RaidClientError as exc:
            self.raid_info.setText(f"Couldn't refresh raid state: {exc}")
            return

        defeated = self.raid_session.hp is not None and self.raid_session.hp <= 0
        self.status_label.setText(
            f"{self.raid_session.boss_name} (Lv. {self.raid_session.boss_level})"
        )
        max_hp = self.raid_session.max_hp or 1
        hp = self.raid_session.hp or 0
        self.hp_bar.setValue(max(0, min(100, int(100 * hp / max_hp))))
        state_text = "Defeated!" if defeated else "In progress"
        self.raid_info.setText(
            f"{hp}/{max_hp} HP - {state_text}<br>Raid code: {self.raid_session.raid_id}"
        )
        self.participants_list.clear()
        for participant in self.raid_session.participants.values():
            self.participants_list.addItem(
                f"{participant['username']} - {participant['damage_dealt']} damage"
            )
        self.leave_button.setEnabled(True)
