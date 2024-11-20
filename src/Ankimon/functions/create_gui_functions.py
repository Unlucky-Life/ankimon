from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ..const import status_colors_label

def create_status_label(status_name):

    # Get the colors for the given status name
    colors = status_colors_label.get(status_name.lower())

    # If the status name is valid, create and style the QLabel
    if colors:
        label = QLabel(status_name.capitalize())
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            f"background-color: {colors['background']};"
            f"border: 2px solid {colors['outline']};"
            f"border-radius: 5px;"
            f"padding: 5px 10px;"
            f"font-weight: bold;"
            f"color: {colors.get('text_color', '#000000')};"
        )
    else:
        label = QLabel("Unknown Status")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet(
            "padding: 5px 10px;"
        )

    return label