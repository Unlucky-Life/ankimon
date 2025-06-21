import os
import random
from datetime import datetime
import json
from typing import Union

from aqt import mw
from aqt.qt import (
    Qt,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QGridLayout,
    QFrame,
    QPixmap,
    QMessageBox
)

from ..utils import give_item, daily_item_list, get_item_price, get_item_description
from ..resources import items_path, user_path, pokemon_tm_learnset_path

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
        self.number_of_daily_items = 3
        self.daily_items_reroll_cost = 100
        self.todays_daily_items = []
        self.todays_daily_tms = []
        self.shop_save_file = user_path / "todays_shop.json"

        # Height and width of the frames containing the displayed items
        self.frame_h = 120
        self.frame_w = 400

        self.tm_price = 1000

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

        # Daily items
        if not self.todays_daily_items:  # If the list of daily items is empty
            self.todays_daily_items = self.get_daily_items()
        for row, item in enumerate(self.todays_daily_items):
            item['UI_NAME'] = item.get('name', 'poke-ball').replace('-', ' ').capitalize()
            item['price'] = get_item_price(item.get('name', 'poke-ball'))

            # Create a QFrame to wrap the row content
            frame = QFrame()
            frame.setFixedHeight(self.frame_h)
            frame.setFixedWidth(self.frame_w)

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


        # --- Middle column for daily TMs ---
        daily_tms_layout = QVBoxLayout()  # Vertical layout for daily items
        daily_tms_label = QLabel("<h1>Daily TMs</h1>")
        daily_tms_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        daily_tms_layout.addWidget(daily_tms_label)

        daily_tms_grid = QGridLayout()

        # Daily TMs
        if not self.todays_daily_tms:  # If the list of daily items is empty
            self.todays_daily_tms = self.get_daily_tms()
        for row, item in enumerate(self.todays_daily_tms):
            item['UI_NAME'] = item.get('name', '').replace('-', ' ').capitalize()
            item['price'] = self.tm_price

            # Create a QFrame to wrap the row content
            frame = QFrame()
            frame.setFixedHeight(self.frame_h)
            frame.setFixedWidth(self.frame_w)

            # Create a layout inside the frame for the row content
            frame_layout = QHBoxLayout(frame)

            # Image
            image_path = items_path / "Bag_TM_Normal_SV_Sprite.png"
            pixmap = QPixmap(str(image_path))
            image_label = QLabel()
            image_label.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Name
            name_label = QLabel(f"<h3>{item.get('UI_NAME', 'poke-ball')}</h3>")
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Description
            #description_text = get_item_description(item['name'], self.settings_obj.get('misc.language', '9'))
            description_text = f"Allows a Pokémon to be taught the move {item['UI_NAME']} (if able)"
            description_label = QLabel(f"<em>{description_text}</em>")
            description_label.setWordWrap(True)
            description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            description_label.setToolTip(description_text)

            # Price
            price_label = QLabel(f"<b>${item.get('price')}</b>")
            price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Buy button
            buy_button = QPushButton("Buy")
            buy_button.clicked.connect(lambda checked, item=item: self.buy_item(item, item.get("item_type")))

            # Add widgets to the frame layout
            frame_layout.addWidget(image_label)  # Add Image label
            frame_layout.addWidget(name_label)  # Add Name label
            frame_layout.addWidget(description_label)  # Add Description label
            frame_layout.addWidget(price_label)  # Add Price label
            frame_layout.addWidget(buy_button)  # Add Buy button

            # Add the frame to the grid layout
            daily_tms_grid.addWidget(frame, row, 0, 1, 4)
        daily_tms_layout.addLayout(daily_tms_grid)

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
            frame.setFixedHeight(self.frame_h)
            frame.setFixedWidth(self.frame_w)

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
        main_layout.addLayout(daily_tms_layout, stretch=1)  # Middle
        main_layout.addLayout(standard_layout, stretch=1)  # Right side

        self.currency_qlabel = QLabel(f"<h2>Current Cash: ${self.settings_obj.get('trainer.cash', 0)}</h2>")
        daily_items_reroll_button = QPushButton(f"Reroll daily items  ${self.daily_items_reroll_cost}")
        daily_items_reroll_button.setFixedSize(180, 25)
        daily_items_reroll_button.clicked.connect(lambda: self.reroll_daily_items(cost=self.daily_items_reroll_cost))
        top_layout = QVBoxLayout()
        top_layout.addWidget(self.currency_qlabel)
        top_layout.addWidget(daily_items_reroll_button)

        # Create a vertical layout for the complete window
        complete_layout = QVBoxLayout(self.window)
        complete_layout.addLayout(top_layout)
        complete_layout.addLayout(main_layout)
        # Apply the main layout to the window
        self.window.setLayout(complete_layout)

    def get_daily_items(self):
        """Generate daily items based on the current date."""

        # In case the shop has been reset today, we need to load the latest reroll
        if os.path.isfile(self.shop_save_file):
            with open(self.shop_save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("items") and data.get("date") == datetime.now().strftime("%Y-%m-%d"):
                    return data.get("items")

        # If there was no reroll today (i.e. it's a new day), we generate a whole new shop
        seed = datetime.now().strftime("%Y-%m-%d")
        random.seed(seed)
        return random.sample(DAILY_ITEMS_POOL, self.number_of_daily_items)
    
    def get_daily_tms(self):
        """
        Works like get_daily_items, but for TMs
        """
        # In case the shop has been reset today, we need to load the latest reroll
        if os.path.isfile(self.shop_save_file):
            with open(self.shop_save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("technical_machines") and data.get("date") == datetime.now().strftime("%Y-%m-%d"):
                    return data.get("technical_machines")
        
        # If there was no reroll today (i.e. it's a new day), we generate a whole new shop
        tm_pool = self.get_tm_pool()
        seed = datetime.now().strftime("%Y-%m-%d")
        random.seed(seed)
        return random.sample(tm_pool, self.number_of_daily_items)
    
    def get_tm_pool(self) -> list[str]:
        with open(pokemon_tm_learnset_path, "r") as f:
            pokemon_tm_learnset = json.load(f)

        # Reminder : pokemon_tm_learnset is a dict in the format {"pokemon_name": list[str]}
        def flatten(xss):
            return [x for xs in xss for x in xs]
        all_tms = flatten(list(pokemon_tm_learnset.values()))
        all_tms = list(set(all_tms))  # getting rid of duplicates
        all_tms = [
            {
            "name": tm,
            "description": f"Allows a Pokémon to be taught the move {tm} (if able).",
            "price": self.tm_price,
            "item_type": "TM",
            } for tm in all_tms]
        return list(all_tms)

    def buy_item(self, item, item_type: Union[str, None]=None):
        try:
            """Handle item purchase."""
            if self.settings_obj.get('trainer.cash', 0) < item['price']:
                QMessageBox.critical(mw, "Purchase Failed", "You do not have enough cash to purchase this item.")
                return
            self.set_callback('trainer.cash', int(self.get_callback('trainer.cash', 0) - item['price']))
            self.currency_qlabel.setText(f"<h2>Current Cash: ${self.settings_obj.get('trainer.cash', 0)}</h2>")
            QMessageBox.information(mw, "Purchase Successful", f"You purchased {item.get('name', 'poke-ball').replace('-', ' ').capitalize()} for ${item['price']}! \n {self.get_callback('trainer.cash', 0)} cash remaining.")
            give_item(item['name'], item_type)
        except Exception as e:
            self.logger.log_and_showinfo("error", f"Failed to purchase item: {e}")
            QMessageBox.critical(mw, "Purchase Failed", "An error occurred while purchasing the item.")

    def reroll_daily_items(self, cost: int = 0) -> None:
        """
        Rerolls the daily items in the shop

        Args:
            cost (int): The cost in Pokedollars to reroll the shop. Defaults to 0.

        Returns:
            None
        """
        # First, we check if the user actually has enough money to pay for the reroll
        if self.settings_obj.get('trainer.cash', 0) < cost:
            QMessageBox.critical(mw, "Purchase Failed", "You do not have enough money to reroll the shop.")
            return
        
        # We substract the cost of the reroll to the amount of money the user has
        self.set_callback('trainer.cash', int(self.get_callback('trainer.cash', 0) - cost))
        self.currency_qlabel.setText(f"<h2>Current Cash: ${self.settings_obj.get('trainer.cash', 0)}</h2>")

        # Rerolling the list of today's items
        random.seed()
        self.todays_daily_items = random.sample(DAILY_ITEMS_POOL, self.number_of_daily_items)
        self.todays_daily_tms = random.sample(self.get_tm_pool(), self.number_of_daily_items)

        # Refreshing the window by closing and reopening it
        self.toggle_window() # Closing the window
        self.toggle_window() # Opening the window

        # After the reroll, we save the items currently present in the shop. That way, if Anki is reopened, the new items are still there
        with open(self.shop_save_file, 'w', encoding='utf-8') as f:
            data = {
                "items": self.todays_daily_items,
                "technical_machines": self.todays_daily_tms,
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
            json.dump(data, f, ensure_ascii=False, indent=4)