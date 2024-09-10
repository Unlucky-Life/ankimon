import markdown

from PyQt6.QtGui import QMovie, QIcon
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QTextEdit, QCheckBox, QPushButton, QMessageBox
from aqt.qt import QDialog
from PyQt6.QtCore import Qt

from .resources import icon_path, addon_dir
from .texts import terms_text
from .utils import read_local_file


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


class AgreementDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Setup the dialog layout
        layout = QVBoxLayout()
        # Add a label with the warning message
        title = QLabel("""Please agree to the terms before downloading the information:""")
        subtitle = QLabel("""Terms and Conditions Clause""")
        terms = QLabel(terms_text)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(terms)
         # Ensure the terms QLabel is readable and scrolls if necessary
        terms.setWordWrap(True)
        terms.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Add a checkbox for the user to agree to the terms
        self.checkbox = QCheckBox("I agree to the above named terms.")
        layout.addWidget(self.checkbox)

        # Add a button to proceed
        proceed_button = QPushButton("Proceed")
        proceed_button.clicked.connect(self.on_proceed_clicked)
        layout.addWidget(proceed_button)

        self.setLayout(layout)

    def on_proceed_clicked(self):
        if self.checkbox.isChecked():
            self.accept()  # Close the dialog and return success
        else:
            QMessageBox.warning(self, "Agreement Required", "You must agree to the terms to proceed.")

class Version_Dialog(QDialog):
    """Custom Dialog class"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ankimon Notifications")
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # For horizontal scrollbar, if you want it off
        self.local_file_path = addon_dir / "update_notes.md"
        self.local_content = read_local_file(self.local_file_path)
        self.html_content = markdown.markdown(self.local_content)
        self.text_edit.setHtml(self.html_content)
        layout.addWidget(self.text_edit)
        self.setWindowIcon(QIcon(str(icon_path)))
        self.setLayout(layout)
    
    def open(self):
        self.exec()