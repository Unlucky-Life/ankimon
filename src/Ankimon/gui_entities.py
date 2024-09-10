from PyQt6.QtGui import QMovie, QIcon
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QTextEdit
from aqt.qt import QDialog
from PyQt6.QtCore import Qt

from .resources import icon_path


class MovieSplashLabel(QLabel):
    def __init__(self, gif_path, parent=None):
        super().__init__(parent)
        self.movie = QMovie(gif_path)
        self.movie.jumpToFrame(0)
        self.setMovie(self.movie)
        self.movie.frameChanged.connect(self.repaint)

    def showEvent(self, event):
        self.movie.start()

    def hideEvent(self, event):
        self.movie.stop()

class UpdateNotificationWindow(QDialog):
    """Custom Dialog class"""
    def __init__(self, content):
        super().__init__()
        self.setWindowTitle("Ankimon Notifications")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # For horizontal scrollbar, if you want it off
        self.text_edit.setHtml(content)
        layout.addWidget(self.text_edit)
        self.setWindowIcon(QIcon(str(icon_path)))

        self.setLayout(layout)