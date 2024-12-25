from aqt import mw
from aqt.qt import *
import random
from datetime import datetime
from ..utils import give_item, daily_item_list, get_item_price, get_item_description
from ..resources import items_path
# Daily Rotating Items Pool
DAILY_ITEMS_POOL = daily_item_list()

# Standard Items
STANDARD_ITEMS = [
    {"name": "poke-ball"},
    {"name": "potion"},
    {"name": "rare-candy"},
]


class PokemonShopManager:
    def __init__(self, logger, settings_obj, set_callback, get_callback):
        self.window = None
        self.logger = logger
        self.settings_obj = settings_obj
        self.set_callback = set_callback
        self.get_callback = get_callback

    def toggle_window(self):
        """Toggles the visibility of the Pokémon shop window."""
        if self.window and self.window.isVisible():
            # Close the window if it is visible
            self.window.close()
        else:
            # Always recreate the window if it's closed
            if not self.window or not self.window.isVisible():
                self.create_gui()

            # Show the window
            self.window.show()

    
    def create_gui(self):
        """Create and configure the Ankimon shop GUI."""
        # Create the dialog window with the Anki main window as its parent
        self.window = QDialog(parent=mw)
        self.window.setWindowTitle("Ankimon Shop")
        self.window.setGeometry(100, 100, 1000, 400)  # Adjust window size as needed

        # Make the window behave like a tool window (not modal)
        self.window.setWindowFlag(Qt.WindowType.Tool)

        # Set up the main horizontal layout for the window
        main_layout = QHBoxLayout()

        # --- Left Side for Daily Items ---
        daily_layout = QVBoxLayout()  # Vertical layout for daily items
        daily_label = QLabel("<h1>Daily Items</h1>")
        daily_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        daily_layout.addWidget(daily_label)

        # Create a grid layout for displaying daily items
        daily_grid = QGridLayout()

        daily_items = self.get_daily_items()
        for row, item in enumerate(daily_items):
            item['UI_NAME'] = item.get('name', 'poke-ball').replace('-', ' ').capitalize()
            item['price'] = get_item_price(item.get('name', 'poke-ball'))

            # Create a QFrame to wrap the row content
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #FFFFFF;
                    padding: 5px;
                }
            """)

            # Create a layout inside the frame for the row content
            frame_layout = QHBoxLayout(frame)

            # Image
            image_path = f"{items_path}/{item.get('name', 'poke-ball')}.png"
            pixmap = QPixmap(image_path)
            image_label = QLabel()
            image_label.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Name
            name_label = QLabel(f"<h3>{item.get('UI_NAME', 'poke-ball')}</h3>")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Description
            description_text = get_item_description(item['name'], self.settings_obj.get('misc.language', '9'))
            description_label = QLabel(f"<em>{description_text}</em>")
            description_label.setWordWrap(True)
            description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            description_label.setToolTip(description_text)

            # Price
            price_label = QLabel(f"<b>${item.get('price', 1000)}</b>")
            price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Buy button
            buy_button = QPushButton("Buy")
            buy_button.clicked.connect(lambda checked, item=item: self.buy_item(item))

            # Add widgets to the frame layout
            frame_layout.addWidget(image_label)  # Add Image label
            frame_layout.addWidget(name_label)  # Add Name label
            frame_layout.addWidget(description_label)  # Add Description label
            frame_layout.addWidget(price_label)  # Add Price label
            frame_layout.addWidget(buy_button)  # Add Buy button

            # Add the frame to the grid layout
            daily_grid.addWidget(frame, row, 0, 1, 4)

        daily_layout.addLayout(daily_grid)

        # --- Right Side for Standard Items ---
        standard_layout = QVBoxLayout()  # Vertical layout for standard items
        standard_label = QLabel("<h1>Standard Items</h1>")
        standard_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        standard_layout.addWidget(standard_label)

        # Create a grid layout for displaying standard items
        standard_grid = QGridLayout()

        for row, item in enumerate(STANDARD_ITEMS):
            item['UI_NAME'] = item.get('name', 'poke-ball').replace('-', ' ').capitalize()
            item['price'] = get_item_price(item.get('name', 'poke-ball'))

            # Create a QFrame to wrap the row content
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #FFFFFF;
                    padding: 5px;
                }
            """)

            # Create a layout inside the frame for the row content
            frame_layout = QHBoxLayout(frame)

            # Image
            image_path = f"{items_path}/{item.get('name', 'poke-ball')}.png"
            pixmap = QPixmap(image_path)
            image_label = QLabel()
            image_label.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Name
            name_label = QLabel(f"<h3>{item.get('UI_NAME', 'poke-ball')}</h3>")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Description
            description_text = get_item_description(item['name'], self.settings_obj.get('misc.language', '9'))
            description_label = QLabel(f"<em>{description_text}</em>")
            description_label.setWordWrap(True)
            description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            description_label.setToolTip(description_text)

            # Price
            price_label = QLabel(f"<b>${item.get('price', 1000)}</b>")
            price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Buy button
            buy_button = QPushButton("Buy")
            buy_button.clicked.connect(lambda checked, item=item: self.buy_item(item))

            # Add widgets to the frame layout
            frame_layout.addWidget(image_label)  # Add Image label
            frame_layout.addWidget(name_label)  # Add Name label
            frame_layout.addWidget(description_label)  # Add Description label
            frame_layout.addWidget(price_label)  # Add Price label
            frame_layout.addWidget(buy_button)  # Add Buy button

            # Add the frame to the grid layout
            standard_grid.addWidget(frame, row, 0, 1, 4)

        standard_layout.addLayout(standard_grid)

        # Add both layouts to the main horizontal layout
        main_layout.addLayout(daily_layout, stretch=1)  # Left side
        main_layout.addLayout(standard_layout, stretch=1)  # Right side

        top_layout = QVBoxLayout()
        self.currency_qlabel = QLabel(f"<h2>Current Cash: ${self.settings_obj.get('trainer.cash', 0)}</h2>")
        top_layout.addWidget(self.currency_qlabel)

        # Create a vertical layout for the complete window
        complete_layout = QVBoxLayout(self.window)
        complete_layout.addLayout(top_layout)
        complete_layout.addLayout(main_layout)
        # Apply the main layout to the window
        self.window.setLayout(complete_layout)

    def get_daily_items(self):
        """Generate daily items based on the current date."""
        seed = datetime.now().strftime("%Y-%m-%d")
        random.seed(seed)
        return random.sample(DAILY_ITEMS_POOL, 3)

    def buy_item(self, item):
        try:
            """Handle item purchase."""
            if self.settings_obj.get('trainer.cash', 0) < item['price']:
                QMessageBox.critical(mw, "Purchase Failed", "You do not have enough cash to purchase this item.")
                return
            self.set_callback('trainer.cash', int(self.get_callback('trainer.cash', 0) - item['price']))
            self.currency_qlabel.setText(f"<h2>Current Cash: ${self.settings_obj.get('trainer.cash', 0)}</h2>")
            QMessageBox.information(mw, "Purchase Successful", f"You purchased {item.get('name', 'poke-ball').replace('-', ' ').capitalize()} for ${item['price']}! \n {self.get_callback('trainer.cash', 0)} cash remaining.")
            give_item(item['name'], self.logger)
        except Exception as e:
            self.logger.log_and_showinfo("error", f"Failed to purchase item: {e}")
            QMessageBox.critical(mw, "Purchase Failed", "An error occurred while purchasing the item.")