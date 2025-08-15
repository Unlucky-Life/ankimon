from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QSpacerItem, QSizePolicy, QGroupBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from aqt import mw

class AnkimonTrackerWindow:
    def __init__(self, tracker):
        self.tracker = tracker
        self.mw = mw
        self.window = None
        self.layout = None
        self.stats_labels = {}
        self.title_label = None  # To store the title label for dynamic updates
        self.previous_stats = {}  # Dictionary to store previous stats for comparison

    def get_text_color(self):
        """Returns the appropriate text color based on Anki's theme."""
        return "white" if self.mw.pm.night_mode() else "black"

    def create_gui(self):
        """Creates and sets up the GUI layout for the tracker stats."""
        if not self.window:  # Only create window once
            self.window = QWidget(self.mw)  # Use Anki's main window as the parent
            self.layout = QVBoxLayout()

            # Set up a horizontal layout to split the window
            main_layout = QHBoxLayout()

            # Left column: general stats
            left_layout = QVBoxLayout()

            # Title label
            self.title_label = QLabel("Ankimon Tracker Stats")  # Store the title label
            self.title_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.title_label.setStyleSheet(f"color: {self.get_text_color()}; padding: 2px;")
            left_layout.addWidget(self.title_label)

            # Create a label for each stat (non-Pokémon stats)
            stats = self.tracker.get_stats()
            for key, value in stats.items():
                if key not in ['main_pokemon', 'enemy_pokemon']:
                    # Add the label to both the layout and self.stats_labels for easy updating
                    label = QLabel(f"{key.capitalize()}: {value}")
                    label.setFont(QFont("Arial", 12))
                    label.setStyleSheet(f"color: {self.get_text_color()}; padding: 2px;")
                    left_layout.addWidget(label)
                    self.stats_labels[key] = label  # Store label in self.stats_labels

            # Add the left layout to the main layout
            main_layout.addLayout(left_layout)

            # Right column for Pokémon stats
            right_layout = QVBoxLayout()

            # Main Pokémon stats
            main_pokemon_stats = self.tracker.get_main_pokemon_stats()
            if main_pokemon_stats:
                stats_box = QGroupBox(f"Main Pokémon: {self.tracker.main_pokemon.name}")
                stats_box.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                stats_box.setStyleSheet(f"color: {self.get_text_color()}; padding: 2px; QGroupBox::title {{ color: {self.get_text_color()}; }}")
                stats_layout = QGridLayout()
                row, col = 0, 0
                for key, value in main_pokemon_stats.items():
                    label = QLabel(f"{key.capitalize()}: {value if value is not None else 'N/A'}")
                    label.setStyleSheet(f"color: {self.get_text_color()}; padding: 2px;")
                    stats_layout.addWidget(label, row, col)
                    self.stats_labels[f"main_pokemon_{key}"] = label
                    col += 1
                    if col == 3:
                        col = 0
                        row += 1
                stats_box.setLayout(stats_layout)
                right_layout.addWidget(stats_box)

            # Enemy Pokémon stats
            enemy_pokemon_stats = self.tracker.get_enemy_pokemon_stats()
            if enemy_pokemon_stats:
                stats_box_enemy = QGroupBox(f"Enemy Pokémon: {self.tracker.enemy_pokemon.name}")
                stats_box_enemy.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                stats_box_enemy.setStyleSheet(f"color: {self.get_text_color()}; padding: 3px; QGroupBox::title {{ color: {self.get_text_color()}; }}")
                enemy_stats_layout = QGridLayout()
                row, col = 0, 0
                for key, value in enemy_pokemon_stats.items():
                    label = QLabel(f"{key.capitalize()}: {value if value is not None else 'N/A'}")
                    label.setStyleSheet(f"color: {self.get_text_color()}; padding: 2px;")
                    enemy_stats_layout.addWidget(label, row, col)
                    self.stats_labels[f"enemy_pokemon_{key}"] = label
                    col += 1
                    if col == 3:
                        col = 0
                        row += 1
                stats_box_enemy.setLayout(enemy_stats_layout)
                right_layout.addWidget(stats_box_enemy)

            main_layout.addLayout(right_layout)
            self.layout.addLayout(main_layout)

            # Add spacing
            self.layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            self.window.setLayout(self.layout)
            self.window.setWindowTitle("Ankimon Tracker Stats")
            self.window.show()

    def update_stats(self):
        """Forcefully updates all displayed stats, regardless of change."""
        # Update the title label color
        if self.title_label:
            self.title_label.setStyleSheet(f"color: {self.get_text_color()}; padding: 2px;")

        stats = self.tracker.get_stats()
        main_pokemon_stats = self.tracker.get_main_pokemon_stats()
        enemy_pokemon_stats = self.tracker.get_enemy_pokemon_stats()

        # Combine all stats into a single dictionary
        current_stats = {
            **{f"{k}": v for k, v in stats.items() if k not in ['main_pokemon', 'enemy_pokemon']},
            **{f"main_pokemon_{k}": v for k, v in (main_pokemon_stats or {}).items()},
            **{f"enemy_pokemon_{k}": v for k, v in (enemy_pokemon_stats or {}).items()},
        }

        # Force update all labels
        for key, current_value in current_stats.items():
            if key in self.stats_labels:
                # Update the label for this stat unconditionally
                if key.startswith("main_pokemon_") or key.startswith("enemy_pokemon_"):
                    # For Pokémon stats, split on "_" and capitalize the last part
                    stat_name = key.split("_", 2)[-1].capitalize()
                    self.stats_labels[key].setText(f"{stat_name}: {current_value}")
                    self.stats_labels[key].setStyleSheet(f"color: {self.get_text_color()}; padding: 2px;")
                else:
                    # For other stats, use the key as is
                    self.stats_labels[key].setText(f"{key.capitalize()}: {current_value}")
                    self.stats_labels[key].setStyleSheet(f"color: {self.get_text_color()}; padding: 2px;")
            else:
                # If label doesn't exist, create and add it to stats_labels
                if key.startswith("main_pokemon_") or key.startswith("enemy_pokemon_"):
                    # For Pokémon stats, split on "_" and capitalize the last part
                    stat_name = key.split("_", 2)[-1].capitalize()
                    label = QLabel(f"{stat_name}: {current_value}")
                else:
                    # For other stats, use the key as is
                    label = QLabel(f"{key.capitalize()}: {current_value}")

                label.setFont(QFont("Arial", 12))
                label.setStyleSheet(f"color: {self.get_text_color()}; padding: 2px;")
                self.stats_labels[key] = label  # Store label for future updates
                self.layout.addWidget(label)  # Add it to layout

    def start_real_time_updates(self):
        """Starts real-time updates for stats using a timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Check for updates every second

    def toggle_window(self):
        """Toggles the visibility of the main window."""
        if self.window and self.window.isVisible():
            # Close the main window if it's open
            self.window.close()
        else:
            if not self.window:
                # Create and show the main window if it's not already created
                self.create_gui()  # Ensure your GUI setup method is called
                self.start_real_time_updates()  # Set up the real-time updates for the app

                # Make the main window behave like a tool window
                self.window.setWindowFlag(Qt.WindowType.Tool)  # Apply the tool window flag to the window

            # Show the window without starting a new event loop
            self.window.show()
