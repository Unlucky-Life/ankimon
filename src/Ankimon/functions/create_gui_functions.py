from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from ..const import status_colors_label, status_colors_html

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

def create_status_html(status_name, settings_obj):
    xp_bar_spacer = settings_obj.compute_special_variable('xp_bar_spacer')
    hp_bar_thickness = settings_obj.get("battle.hp_bar_thickness", 2) * 4	
    show_mainpkmn_in_reviewer = int(settings_obj.get("battle.show_mainpkmn_in_reviewer", 1))
    # Get the colors for the given status name
    colors = status_colors_html.get(status_name.lower())

    # If the status name is valid, create the HTML with inline CSS
    if colors:
        if show_mainpkmn_in_reviewer == 2:
            html = f"""
            <div id=pokestatus class="Ankimon" style="
                position: fixed;
                bottom: {140 + xp_bar_spacer + hp_bar_thickness}px; /* Adjust as needed */
                right: 1%;
                z-index: 9999;
                background-color: {colors['background']};
                border: 2px solid {colors['outline']};
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 8px;
                font-weight: bold;
                display: inline-block;
                color: {colors.get('text_color', '#000000')};
                text-transform: uppercase;
                text-align: center;
                margin: 4px;
            ">{colors['name']}</div>
            """
        elif show_mainpkmn_in_reviewer == 1:
            html = f"""
            <div id=pokestatus class="Ankimon" style="
                position: fixed;
                bottom: {40 + hp_bar_thickness + xp_bar_spacer}px; /* Adjust as needed */
                right: 15%;
                z-index: 9999;
                background-color: {colors['background']};
                border: 2px solid {colors['outline']};
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 8px;
                font-weight: bold;
                display: inline-block;
                color: {colors.get('text_color', '#000000')};
                text-transform: uppercase;
                text-align: center;
                margin: 4px;
            ">{colors['name']}</div>
            """
        elif show_mainpkmn_in_reviewer == 0:
            html = f"""
            <div id=pokestatus class="Ankimon" style="
                position: fixed;
                bottom: {40 + hp_bar_thickness}px; /* Adjust as needed */
                left: 160px;
                z-index: 9999;
                background-color: {colors['background']};
                border: 2px solid {colors['outline']};
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 8px;
                font-weight: bold;
                display: inline-block;
                color: {colors.get('text_color', '#000000')};
                text-transform: uppercase;
                text-align: center;
                margin: 4px;
            ">{colors['name']}</div>
            """
    else:
        html = "<div>Unknown Status</div>"

    return html