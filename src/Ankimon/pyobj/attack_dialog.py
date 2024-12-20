from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea
from PyQt6.QtCore import Qt

class AttackDialog(QDialog):
    def __init__(self, attacks, new_attack):
        super().__init__()
        self.attacks = attacks
        self.new_attack = new_attack
        self.selected_attack = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"Select which Attack to Replace with {self.new_attack}")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Select which Attack to Replace with {self.new_attack}"))
        for attack in self.attacks:
            button = QPushButton(attack)
            button.clicked.connect(self.attackSelected)
            layout.addWidget(button)
        reject_button = QPushButton("Reject Attack")
        reject_button.clicked.connect(self.attackNoneSelected)
        layout.addWidget(reject_button)
        self.setLayout(layout)

    def attackSelected(self):
        sender = self.sender()
        self.selected_attack = sender.text()
        self.accept()

    def attackNoneSelected(self):
        sender = self.sender()
        self.selected_attack = sender.text()
        self.reject()