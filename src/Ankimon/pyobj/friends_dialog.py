from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QInputDialog, QLabel, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout, QWidget
from aqt import mw

from ..functions import multiplayer_functions


class FriendsDialog(QDialog):
    """Small, explicit presence view for friends and incoming requests."""

    def __init__(self, parent=mw):
        super().__init__(parent)
        self.setWindowTitle("Ankimon Friends")
        self.setMinimumSize(560, 460)
        self._friends = {}
        layout = QVBoxLayout(self)
        self.summary = QLabel("Loading friends...")
        layout.addWidget(self.summary)
        self.friend_list = QListWidget()
        layout.addWidget(self.friend_list)
        controls = QHBoxLayout()
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        controls.addWidget(refresh)
        add = QPushButton("Add friend")
        add.clicked.connect(self.add_friend)
        controls.addWidget(add)
        remove = QPushButton("Remove selected")
        remove.clicked.connect(self.remove_selected)
        controls.addWidget(remove)
        layout.addLayout(controls)
        self.refresh()

    def refresh(self):
        try:
            state = multiplayer_functions.get_state()
        except multiplayer_functions.MultiplayerClientError as exc:
            self.summary.setText(f"Unable to load friends: {exc}")
            return
        friends = state.get("friends", [])
        self._friends = {str(friend.get("username")): friend for friend in friends}
        self.friend_list.clear()
        online = reviewing = 0
        for friend in friends:
            if friend.get("online"):
                online += 1
            if friend.get("reviewing_now"):
                reviewing += 1
            status = self._status_text(friend)
            item = QListWidgetItem(
                f"{friend.get('username', 'friend')}  ·  {status}"
            )
            item.setData(Qt.ItemDataRole.UserRole, friend.get("username"))
            self.friend_list.addItem(item)
        self.summary.setText(
            f"Friends: {len(friends)}  ·  Online: {online}  ·  Reviewing: {reviewing}"
        )
        self._show_requests(state.get("friend_requests") or {})

    @staticmethod
    def _status_text(friend):
        if friend.get("in_match"):
            return "in trainer battle"
        if friend.get("in_raid"):
            return "in raid"
        if friend.get("reviewing_now"):
            return "reviewing now"
        if friend.get("online"):
            return "online"
        return "offline"

    def _show_requests(self, requests):
        incoming = requests.get("incoming", [])
        if not incoming:
            return
        for request in incoming:
            username = request.get("username")
            answer = QMessageBox.question(
                self,
                "Friend request",
                f"Accept friend request from {username}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            try:
                multiplayer_functions.respond_friend(
                    username, answer == QMessageBox.StandardButton.Yes
                )
            except multiplayer_functions.MultiplayerClientError as exc:
                QMessageBox.warning(self, "Friends", str(exc))
        if incoming:
            self.refresh()

    def add_friend(self):
        username, accepted = QInputDialog.getText(self, "Add friend", "Username:")
        if not accepted or not username.strip():
            return
        try:
            multiplayer_functions.add_friend(username.strip())
        except multiplayer_functions.MultiplayerClientError as exc:
            QMessageBox.warning(self, "Friends", str(exc))
            return
        self.refresh()

    def remove_selected(self):
        item = self.friend_list.currentItem()
        username = item.data(Qt.ItemDataRole.UserRole) if item else None
        if not username:
            return
        try:
            multiplayer_functions.remove_friend(username)
        except multiplayer_functions.MultiplayerClientError as exc:
            QMessageBox.warning(self, "Friends", str(exc))
            return
        self.refresh()
