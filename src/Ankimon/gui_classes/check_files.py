import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QTextEdit, QWidget, QDialog
)
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QTextEdit, QWidget
)
from  ..resources import addon_dir, json_file_structure
from aqt import mw
from aqt.utils import showWarning

def check_files_in_json(json_file=json_file_structure, root_directory=addon_dir):
    """
    Checks if the files listed in the JSON file exist in the root directory.

    Args:
        json_file (str): Path to the JSON file.
        root_directory (str): The root directory to verify files against.

    Returns:
        list: A list of missing files.
    """
    def verify_files(folder_dict, current_path, missing_files):
        for child in folder_dict.get('children', []):
            if child['type'] == 'file':
                file_path = os.path.join(current_path, child['name'])
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            elif child['type'] == 'folder':
                folder_path = os.path.join(current_path, child['name'])
                if os.path.exists(folder_path):
                    verify_files(child, folder_path, missing_files)
                else:
                    missing_files.append(folder_path)

    # Load the JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        folder_structure = json.load(f)

    missing_files = []
    verify_files(folder_structure, root_directory, missing_files)

    return missing_files

class FileCheckerApp(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Checker")
        self.setGeometry(100, 100, 600, 400)
        self.json_file = json_file_structure
        self.directory = addon_dir

        # Main layout
        self.layout = QVBoxLayout(self)

        # Check Files Button
        self.check_button = QPushButton("Check Files")
        self.check_button.clicked.connect(self.check_files)
        self.layout.addWidget(self.check_button)

        # Output Display
        self.output_label = QLabel("Output:")
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.layout.addWidget(self.output_label)
        self.layout.addWidget(self.output_display)

        # Show the dialog
        self.show()

    def check_files(self):
        json_file = self.json_file
        root_directory = self.directory

        if not json_file or not root_directory:
            self.output_display.setText("Please select both a JSON file and a root directory.")
            return

        if not os.path.exists(json_file):
            self.output_display.setText(f"JSON file '{json_file}' does not exist.")
            return

        if not os.path.exists(root_directory):
            self.output_display.setText(f"Root directory '{root_directory}' does not exist.")
            return

        try:
            missing_files = check_files_in_json(json_file, root_directory)
            if missing_files:
                self.output_display.setText("Missing files/folders:\n" + "\n".join(missing_files))
            else:
                self.output_display.setText("All files and folders are present.")
        except Exception as e:
            self.output_display.setText(f"An error occurred: {str(e)}")
