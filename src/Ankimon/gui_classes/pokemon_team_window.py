from Ankimon.functions.sprite_functions import get_sprite_path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QGroupBox, QFrame, QGridLayout, QComboBox, QDialogButtonBox
from PyQt6.QtGui import QPixmap
import json
import os
from aqt import mw
from aqt.utils import showInfo, showWarning
from ..resources import mypokemon_path, frontdefault, team_pokemon_path

class PokemonTeamDialog(QDialog):
    def __init__(self, settings_obj, logger, parent=mw):
        super().__init__(parent)
        self.setWindowTitle("Choose Your Pokémon Team (Max 6 Pokémon)")
        self.settings = settings_obj
        self.logger = logger

        # Set the minimum size of the dialog
        self.setMinimumSize(900, 500)  # Minimum size of 900x500 pixels

        # Load the Pokémon team data
        self.my_pokemon = self.load_my_pokemon()
        self.team_pokemon = [None] * 6  # Assuming a team can hold 6 Pokémon
        self.team_pokemon = self.load_pokemon_team()

        # Layout
        layout = QVBoxLayout()

        # Label
        label = QLabel("Choose your Pokémon team (up to 6 Pokémon):")
        layout.addWidget(label)

        # Team selection area (scrollable)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        team_widget = QGroupBox()
        team_layout = QGridLayout()  # Change this to QGridLayout for grid arrangement

        # Create a frame for each Pokémon in the team
        self.pokemon_frames = []
        for i in range(6):
            row = i // 3  # Determine the row (0 or 1)
            col = i % 3  # Determine the column (0, 1, or 2)

            frame = QFrame()
            frame.setFrameShape(QFrame.Shape.StyledPanel)
            frame.setFrameShadow(QFrame.Shadow.Raised)

            pokemon_layout = QVBoxLayout()

            # Label for Pokémon name and level
            pokemon_label = QLabel(f"Pokémon {i+1}: Not Selected")
            pokemon_layout.addWidget(pokemon_label)

            # Add Pokémon sprite preview
            sprite_label = QLabel()
            pokemon_layout.addWidget(sprite_label)

            # "Switch out Pokémon" button
            switch_button = QPushButton(f"Switch out Pokémon {i+1}")
            switch_button.clicked.connect(lambda _, i=i: self.switch_out_pokemon(i))
            pokemon_layout.addWidget(switch_button)

            # "Remove Pokémon" button
            remove_button = QPushButton(f"Remove Pokémon {i+1}")
            remove_button.clicked.connect(lambda _, i=i: self.remove_pokemon(i))
            pokemon_layout.addWidget(remove_button)

            frame.setLayout(pokemon_layout)
            team_layout.addWidget(frame, row, col)  # Add frame to grid layout at specific row and column
            self.pokemon_frames.append({'frame': frame, 'label': pokemon_label, 'sprite': sprite_label, 'switch_button': switch_button, 'remove_button': remove_button})

        team_widget.setLayout(team_layout)
        scroll_area.setWidget(team_widget)
        layout.addWidget(scroll_area)

        # XP Share dropdown
        self.xp_share_combo = QComboBox()
        self.xp_share_combo.addItem("No XP Share")
        for pokemon in self.my_pokemon:
            self.xp_share_combo.addItem(f"{pokemon['name']} (Level {pokemon['level']})", pokemon['individual_id'])

        # Set the initial XP Share Pokémon (based on settings)
        xp_share_pokemon_individual_id = self.settings.get("trainer.xp_share", None)
        if xp_share_pokemon_individual_id:
            xp_share_index = next((i for i, p in enumerate(self.my_pokemon) if p['individual_id'] == xp_share_pokemon_individual_id), 0) + 1
            self.xp_share_combo.setCurrentIndex(xp_share_index)

        layout.addWidget(QLabel("Choose Pokémon with XP Share:"))
        layout.addWidget(self.xp_share_combo)

        # OK Button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.on_ok)
        layout.addWidget(ok_button)

        # Set layout
        self.setLayout(layout)

        # Initialize team with current Pokémon data
        self.update_team_display()

        self.exec()

    def load_my_pokemon(self):
        """Load the player's Pokémon data from a JSON string (in this case, hardcoded)"""
        # Replace the following with the actual loading method if from a file:
        with open(mypokemon_path, "r", encoding="utf-8") as file:
            pokemon_data = json.load(file)
        return pokemon_data

    def load_pokemon_team(self):
        """Load the player's Pokémon Team from a JSON string (in this case, hardcoded)"""
        with open(team_pokemon_path, "r", encoding="utf-8") as file:
            team_data = json.load(file)

        # Load the player's Pokémon data (mypokemon_path)
        my_pokemon_data = self.load_my_pokemon()

        matching_pokemon = []

        # Loop through each Pokémon in the team and find corresponding Pokémon in 'mypokemon_path'
        for pokemon_in_team in team_data:
            individual_id = pokemon_in_team.get('individual_id')
            # Find Pokémon in 'mypokemon_path' with matching individual_id
            for pokemon_in_my_pokemon in my_pokemon_data:
                if pokemon_in_my_pokemon.get('individual_id', '') == individual_id:
                    matching_pokemon.append(pokemon_in_my_pokemon)

        return matching_pokemon

    def update_team_display(self):
        """Update the display with the player's current team"""
        # Ensure team_pokemon has 6 slots (pad with None if less than 6)
        max_pokemon_slots = 6
        self.team_pokemon = self.team_pokemon[:max_pokemon_slots]  # Trim to a max of 6 Pokémon
        self.team_pokemon.extend([None] * (max_pokemon_slots - len(self.team_pokemon)))  # Pad with None if less than 6

        for i, frame_data in enumerate(self.pokemon_frames):
            # Check if a Pokémon is selected for this slot (i.e., it's not None)
            if self.team_pokemon[i] is not None:
                pokemon = self.team_pokemon[i]
                pokemon_name = pokemon['name']
                pokemon_level = pokemon['level']
                sprite_path = os.path.join(frontdefault, f"{pokemon['id']}.png")

                # Update label with name and level
                frame_data['label'].setText(f"{pokemon_name} (Level {pokemon_level})")

                # Display the sprite image
                if os.path.exists(sprite_path):
                    pixmap = QPixmap(sprite_path)
                    frame_data['sprite'].setPixmap(pixmap.scaled(50, 50))  # Resize sprite for preview
                    frame_data['sprite'].setAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    frame_data['sprite'].clear()
            else:
                frame_data['label'].setText("Pokémon Not Selected")
                frame_data['sprite'].clear()  # Clear the sprite if not selected

    def switch_out_pokemon(self, slot):
        """Allow the player to switch out a Pokémon for the selected slot"""

        # Create a dialog to choose a new Pokémon for the slot
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Pokémon to Switch In")
        dialog.setMinimumSize(300, 200)

        layout = QVBoxLayout()

        label = QLabel("Choose a Pokémon to switch in:")
        layout.addWidget(label)

        # Create a dropdown to select a new Pokémon
        combo_box = QComboBox()

        # Add only those Pokémon to the combo box that are not already in the team (checked by individual_id)
        used_pokemon_ids = [pokemon['individual_id'] for pokemon in self.team_pokemon if pokemon is not None]
        # Check if there are Pokémon left to choose from (those whose individual_id is not in used_pokemon_ids)
        available_pokemon = [pokemon for pokemon in self.my_pokemon if pokemon and pokemon['individual_id'] not in used_pokemon_ids]

        if available_pokemon:
            for pokemon in available_pokemon:
                combo_box.addItem(f"{pokemon['name']} (Level {pokemon['level']})", pokemon)

                # Set a preview image as item data
                sprite_path = get_sprite_path("front", "png", pokemon['id'], pokemon["shiny"], pokemon["gender"])
                pixmap = QPixmap(sprite_path)
                combo_box.setItemData(combo_box.count() - 1, pixmap, Qt.ItemDataRole.DecorationRole)
        else:
            combo_box.addItem("No available Pokémon", None)  # Display a message if no Pokémon are available

        layout.addWidget(combo_box)

        # Label for the image preview
        preview_label = QLabel("Preview:")
        layout.addWidget(preview_label)
        image_label = QLabel()
        layout.addWidget(image_label)

        # Function to update the image preview when a new item is selected
        def update_preview(index):
            pokemon = combo_box.itemData(index)
            if pokemon:
                sprite_path = get_sprite_path("front", "png", pokemon['id'], pokemon["shiny"], pokemon["gender"])
                pixmap = QPixmap(sprite_path)
                image_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Connect the selection change to the preview update
        combo_box.currentIndexChanged.connect(lambda: update_preview(combo_box.currentIndex()))

        # Button to confirm the selection
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(lambda: self.confirm_switch(combo_box.currentIndex(), slot, dialog))
        button_box.rejected.connect(dialog.reject)

        layout.addWidget(button_box)

        dialog.setLayout(layout)
        dialog.exec()

    def confirm_switch(self, selected_index, slot, dialog):
        """Confirm the Pokémon switch and update the team"""
        # Get the selected Pokémon from combo_box.itemData()
        selected_pokemon = dialog.findChild(QComboBox).itemData(selected_index)

        if selected_pokemon:
            self.team_pokemon[slot] = selected_pokemon  # Replace the Pokémon in the team slot

            # Update the team display
            self.update_team_display()

        dialog.accept()

    def remove_pokemon(self, slot):
        """Remove the Pokémon from the team and handle XP Share if necessary"""
        # Check if there's a Pokémon in the selected slot
        if self.team_pokemon[slot] is not None:
            # Check if the Pokémon in this slot is the one with XP Share
            pokemon_individual_id = self.team_pokemon[slot]['individual_id']
            xp_share_pokemon_individual_id = self.settings.get("trainer.xp_share")

            if xp_share_pokemon_individual_id == pokemon_individual_id:
                # Remove XP Share from the Pokémon if it exists
                self.settings.set("trainer.xp_share", None)

            # Remove the Pokémon from the team slot
            self.team_pokemon[slot] = None

            # Update the display after removal
            self.update_team_display()

    def on_ok(self):
        """Store the selected Pokémon team and XP Share setting, then close the dialog"""
        #team = [frame_data['label'].text() for frame_data in self.pokemon_frames if frame_data['label'].text() != "Pokémon Not Selected"]
        team_data = []  # Initialize the list to store selected Pokémon

        # Process each Pokémon frame to construct the team
        for frame_data in self.team_pokemon:
            if frame_data:  # Ensure the Pokémon has a name
                # Restructure Pokémon data to the desired format
                pokemon_data = {
                    "individual_id": frame_data['individual_id']
                }
                team_data.append(pokemon_data)

        pokemon_names = []

        for frame_data in self.team_pokemon:
            if frame_data:
                # Restructure Pokémon data to the desired format
                pokemon_name = {
                    "name": frame_data['name']
                }
                pokemon_names.append(pokemon_name)

        # Get the selected Pokémon for XP Share
        xp_share_pokemon = self.xp_share_combo.currentText()
        if xp_share_pokemon != "No XP Share":
            # Retrieve the individual_id of the selected Pokémon
            current_index = self.xp_share_combo.currentIndex()
            xp_share_individual_id = self.xp_share_combo.itemData(current_index)
        else:
            xp_share_individual_id = None

        # Update settings with the selected team and XP Share setting
        self.settings.set("trainer.team", team_data)
        self.settings.set("trainer.xp_share", xp_share_individual_id)  # Save XP Share Pokémon

        try:
            with open(team_pokemon_path, "w") as json_file:
                json.dump(team_data, json_file, indent=4)

            self.logger.log_and_showinfo("info", f"Trainer settings saved to {team_pokemon_path}.")
            self.logger.log_and_showinfo("info", f"You chose the following team: [{', '.join([pokemon['name'] for pokemon in pokemon_names])}]\nXP Share: {xp_share_pokemon}")
        except Exception as e:
            self.logger.log_and_showinfo("error", f"Failed to save trainer settings: {e}")

        self.accept()  # Close the dialog
