import logging
from PyQt6.QtWidgets import QMessageBox, QTextEdit, QVBoxLayout, QDialog, QPushButton, QApplication
from PyQt6.QtCore import Qt
import os

class ShowInfoLogger:
    def __init__(self, name="ShowInfoLogger", log_filename="app.log"):
        # Determine the path of the current script and set log file path
        script_directory = os.path.dirname(os.path.abspath(__file__))
        self.log_file = os.path.join(script_directory, log_filename)

        # Check if log file exists, and create it if it doesn't
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                f.write('')  # Create an empty file

        # Set up logging
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')  # Explicit UTF-8 encoding
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Create a separate handler for the game log messages
        self.game_logger = logging.getLogger("GameLogger")
        game_file_handler = logging.FileHandler(self.log_file,encoding="utf-8")
        game_file_handler.setLevel(logging.DEBUG)
        game_formatter = logging.Formatter('%(asctime)s - GAME - %(message)s')  # Custom format for game messages
        game_file_handler.setFormatter(game_formatter)
        self.game_logger.addHandler(game_file_handler)

        # Track the log viewer dialog
        self.log_dialog = None

        # Track the log viewer dialog
        self.log_dialog = None

    def log_and_showinfo(self, level, message):
        # Log the message
        if level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'game':
            self.game_log(message)  # Use the game-specific logging

        if level in ['info', 'warning', 'error']:
            # Show the message in a QMessageBox dialog
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Log Message")
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()

    def log(self, level, message):
        # Log the message
        if level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'game':
            self.game_log(message)  # Use the game-specific logging

    def game_log(self, message):
        # Log a game-specific message with the GAME- prefix
        self.game_logger.info(message)

    def toggle_log_window(self):
        if self.log_dialog and self.log_dialog.isVisible():
            # Close the dialog if it's open and currently focused
            self.log_dialog.close()
            self.log_dialog = None
        else:
            # Create and show the dialog if it's not open
            self.log_dialog = QDialog()
            self.log_dialog.setWindowTitle("Log Viewer")
            self.log_dialog.resize(400, 300)

            # Set dialog as a tool window to prevent it from taking focus from the main window
            self.log_dialog.setWindowFlag(Qt.WindowType.Tool)

            # Text edit widget for displaying log content with scroll functionality
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)

            # Load and display the log file contents
            with open(self.log_file, "r", encoding="utf-8") as f:
                log_content = f.read()
                text_edit.setPlainText(log_content)

            # Add a refresh button to reload the log content
            refresh_button = QPushButton("Refresh")
            refresh_button.clicked.connect(lambda: text_edit.setPlainText(open(self.log_file).read()))

            # Add a clear button to clear the log file content
            clear_button = QPushButton("Clear")
            clear_button.clicked.connect(self.clear_log_file)

            # Layout setup
            layout = QVBoxLayout()
            layout.addWidget(text_edit)
            layout.addWidget(refresh_button)
            layout.addWidget(clear_button)  # Add the Clear button
            self.log_dialog.setLayout(layout)

            # Show the dialog without taking focus away from other windows
            self.log_dialog.show()

    def clear_log_file(self):
        # Clear the log file
        with open(self.log_file, 'w') as f:
            f.write('')  # Empty the log file

        # Update the log viewer with the cleared content
        if self.log_dialog:
            text_edit = self.log_dialog.findChild(QTextEdit)
            if text_edit:
                text_edit.setPlainText('')  # Clear the displayed content in the viewer
