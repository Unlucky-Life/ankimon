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

def create_status_html(status_name, settings_obj, is_pokemon_owned=False, addon_package=""):
    xp_bar_spacer = settings_obj.compute_special_variable('xp_bar_spacer')
    hp_bar_thickness = settings_obj.get("gui.review_hp_bar_thickness", 2) * 4
    show_mainpkmn_in_reviewer = int(settings_obj.get("gui.show_mainpkmn_in_reviewer", 1))
    # Get the colors for the given status name
    colors = status_colors_html.get(status_name.lower())

    # If the status name is valid, create the HTML with inline CSS
    if colors:
        badge_html = ''
        if is_pokemon_owned:
            pokeball_url = f"/_addons/{addon_package}/user_files/web/images/pokeball.png"
            badge_html = f'<img id="owned-indicator-badge" src="{pokeball_url}" style="margin-right: 8px; width: 22px; height: 22px; background-color: var(--ankimon-outline); border-radius: 50%; padding: 2px; box-sizing: border-box; flex-shrink: 0;">'

        if show_mainpkmn_in_reviewer == 2:
            html = f"""
            <div id=pokestatus-container class="Ankimon" style="display: flex; align-items: center; position: fixed; bottom: {140 + xp_bar_spacer + hp_bar_thickness}px; right: 1%; z-index: 9999;">
            {badge_html}
            <div id=pokestatus class="Ankimon" style="
                background-color: {colors['background']};
                border: 2px solid {colors['outline']};
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 8px;
                font-weight: bold !important;
                display: inline-block;
                color: {colors.get('text_color', '#000000')};
                text-transform: uppercase;
                text-align: center;
                margin: 4px;
                font-family: Arial, sans-serif;
            ">{colors['name']}</div>
            </div>
            """
        elif show_mainpkmn_in_reviewer == 1:
            html = f"""
            <div id=pokestatus-container class="Ankimon" style="display: flex; align-items: center; position: fixed; bottom: {40 + hp_bar_thickness + xp_bar_spacer}px; right: 15%; z-index: 9999;">
            {badge_html}
            <div id=pokestatus class="Ankimon" style="
                background-color: {colors['background']};
                border: 2px solid {colors['outline']};
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 8px;
                font-weight: bold !important;
                display: inline-block;
                color: {colors.get('text_color', '#000000')};
                text-transform: uppercase;
                text-align: center;
                margin: 4px;
                font-family: Arial, sans-serif;
            ">{colors['name']}</div>
            </div>
            """
        elif show_mainpkmn_in_reviewer == 0:
            html = f"""
            <div id=pokestatus-container class="Ankimon" style="display: flex; align-items: center; position: fixed; bottom: {40 + hp_bar_thickness}px; left: 160px; z-index: 9999;">
            {badge_html}
            <div id=pokestatus class="Ankimon" style="
                background-color: {colors['background']};
                border: 2px solid {colors['outline']};
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 8px;
                font-weight: bold !important;
                display: inline-block;
                color: {colors.get('text_color', '#000000')};
                text-transform: uppercase;
                text-align: center;
                margin: 4px;
                font-family: Arial, sans-serif;
            ">{colors['name']}</div>
            </div>
            """
    else:
        html = "<div>Unknown Status</div>"

    return html