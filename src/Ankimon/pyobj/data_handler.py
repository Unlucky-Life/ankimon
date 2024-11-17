import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTextEdit
from ..resources import user_path
import os

class DataHandler:
    def __init__(self):
        self.path = user_path  # Store the provided path
        self.data = {}         # Store any potential errors or file read issues
        self.read_files()

    def read_files(self):
        # Specify the files to read
        files = ['mypokemon.json', 'mainpokemon.json', 'items.json', 'team.json', 'data.json', 'badges.json']
        
        # Loop through each file and attempt to read it from the specified path
        for file in files:
            file_path = os.path.join(self.path, file)  # Construct full file path
            attr_name = os.path.splitext(file)[0]      # Use the filename without extension as the attribute name

            try:
                with open(file_path, 'r') as f:
                    if file.endswith('.json'):
                        setattr(self, attr_name, json.load(f))  # Set the file data as an attribute
                    elif file.endswith('.py'):
                        setattr(self, attr_name, f.read())      # Store raw text content if Python file
            except Exception as e:
                self.data[file] = f"Error reading {file}: {e}"  # Store error messages in self.data