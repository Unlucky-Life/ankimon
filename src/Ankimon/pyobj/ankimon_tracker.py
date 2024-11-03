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

    def show_stats_window(self):
        app = QApplication([])
        window = QWidget()
        layout = QVBoxLayout()

        stats = self.get_stats()
        for key, value in stats.items():
            layout.addWidget(QLabel(f"{key}: {value}"))

        window.setLayout(layout)
        window.setWindowTitle("Ankimon Tracker Stats")
        window.show()
        app.exec()
        if __name__ == "__main__":
            tracker = AnkimonTracker()
            tracker.current_mode = "egg"  # Example of setting the mode
            tracker.start_timer()
            tracker.show_stats_window()