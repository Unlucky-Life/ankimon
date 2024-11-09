from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer


class AnkimonTracker:
    def __init__(self):
        """
        Initializes the AnkimonTracker object with default values for tracking reviews and card responses.
        
        Attributes:
            total_reviews (int): The total number of reviews.
            good_count (int): The count of 'good' responses.
            again_count (int): The count of 'again' responses.
            hard_count (int): The count of 'hard' responses.
            easy_count (int): The count of 'easy' responses.
            current_mode (str): The current mode of the tracker, default is "idle".
            timer (QTimer): A QTimer object to handle timing events.
            time_elapsed (int): The time elapsed since the timer started.
        
        Modes:
            - "egg"
            - "battle"
            - "leveling"
        """
        self.total_reviews = 0
        self.good_count = 0
        self.again_count = 0
        self.hard_count = 0
        self.easy_count = 0
        self.current_mode = "idle"
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.time_elapsed = 0

    def review(self, answer):
        self.total_reviews += 1
        if answer == "good":
            self.good_count += 1
        elif answer == "again":
            self.again_count += 1
        elif answer == "hard":
            self.hard_count += 1
        elif answer == "easy":
            self.easy_count += 1
        else:
            raise ValueError("Invalid answer type")

    def get_stats(self):
        return {
            "total_reviews": self.total_reviews,
            "good_count": self.good_count,
            "again_count": self.again_count,
            "hard_count": self.hard_count,
            "easy_count": self.easy_count,
            "current_mode": self.current_mode,
            "time_elapsed": self.time_elapsed
        }

    def update_timer(self):
        self.time_elapsed += 1

    def start_timer(self):
        self.timer.start(1000)  # Timer updates every second

    def stop_timer(self):
        self.timer.stop()

    def reset_timer(self):
        self.time_elapsed = 0


class AnkimonTrackerGUI:
    def __init__(self, tracker):
        """
        Initializes the AnkimonTrackerGUI object, which handles the graphical display of tracker stats.
        
        Parameters:
            tracker (AnkimonTracker): An instance of the AnkimonTracker to fetch and display stats.
        """
        self.tracker = tracker
        self.app = None  # Initialize the QApplication only when needed
        self.window = None
        self.layout = None
        self.stats_labels = {}

    def create_gui(self):
        """Creates and sets up the GUI layout for the tracker stats."""
        if not self.app:
            self.app = QApplication([])

        self.window = QWidget()
        self.layout = QVBoxLayout()

        # Create a label for each stat
        stats = self.tracker.get_stats()
        for key in stats:
            label = QLabel(f"{key}: {stats[key]}")
            self.stats_labels[key] = label  # Store the label for future updates
            self.layout.addWidget(label)

        self.window.setLayout(self.layout)
        self.window.setWindowTitle("Ankimon Tracker Stats")
        self.window.show()

    def update_stats(self):
        """Updates the displayed stats in the GUI."""
        stats = self.tracker.get_stats()
        for key, label in self.stats_labels.items():
            label.setText(f"{key}: {stats[key]}")

    def start_real_time_updates(self):
        """Starts the real-time updates for stats using a timer."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Update stats every second

    def show_stats_window(self):
        """Sets up and starts the application window."""
        self.create_gui()
        self.start_real_time_updates()
        self.app.exec()