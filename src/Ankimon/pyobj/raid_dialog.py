from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QListWidget, QProgressBar, QTabWidget, QWidget, QMessageBox,
)
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

        self.tabs.addTab(self._build_create_tab(), "Create")
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

        self.refresh_status()

    def _build_create_tab(self):
        tab = QWidget()
        form = QVBoxLayout(tab)

        self.boss_name_input = QLineEdit()
        self.boss_name_input.setPlaceholderText("Boss name (e.g. Rayquaza)")

        self.boss_level_input = QSpinBox()
        self.boss_level_input.setRange(1, 100)
        self.boss_level_input.setValue(50)

        self.boss_hp_input = QSpinBox()
        self.boss_hp_input.setRange(1, 100000)
        self.boss_hp_input.setValue(500)

        create_button = QPushButton("Create raid")
        create_button.clicked.connect(self.create_raid)

        form.addWidget(QLabel("Boss name"))
        form.addWidget(self.boss_name_input)
        form.addWidget(QLabel("Boss level"))
        form.addWidget(self.boss_level_input)
        form.addWidget(QLabel("Boss max HP"))
        form.addWidget(self.boss_hp_input)
        form.addWidget(create_button)
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

    def create_raid(self):
        boss_name = self.boss_name_input.text().strip()
        if not boss_name:
            QMessageBox.warning(self, "Ankimon Raid", "Enter a boss name first.")
            return
        try:
            raid_state = raid_functions.create_raid(
                boss_name, self.boss_level_input.value(), self.boss_hp_input.value()
            )
            raid_functions.join_raid(raid_state["id"])
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
