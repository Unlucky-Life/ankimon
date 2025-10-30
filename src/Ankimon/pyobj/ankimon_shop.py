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
    QMessageBox,
    QSizePolicy,
    QFont,
    QFontDatabase,
    QToolTip
)
from aqt.theme import theme_manager

from ..functions.pokedex_functions import find_details_move

from ..utils import give_item, daily_item_list, get_item_price, get_item_description
from ..resources import items_path, user_path, pokemon_tm_learnset_path

# Daily Rotating Items Pool
DAILY_ITEMS_POOL = daily_item_list()

# Standard Items
"""STANDARD_ITEMS = [
    {"name": "poke-ball"},
    {"name": "potion"},
    {"name": "rare-candy"},
]"""

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

        # Retro Pokemon styling dimensions
        self.frame_h = 120
        self.frame_w = 340

        self.tm_price = 1000

        # Load Early GameBoy font
        self.early_gameboy_font = self._load_early_gameboy_font()

    def _load_early_gameboy_font(self):
        """Load the Early GameBoy font for retro styling exclusively."""
        font = QFont("Early GameBoy", 14)
        return font

    def _is_night_mode(self):
        """Check if Anki is in night mode."""
        return theme_manager.night_mode

    def _get_theme_colors(self):
        """Get color scheme based on current theme using Anki's actual theme colors."""
        # Use Anki's built-in color variables that work with both themes
        if self._is_night_mode():
            return {
                'background': 'var(--window-bg)',
                'border': 'var(--border)',
                'text_primary': 'var(--text)',
                'text_secondary': 'var(--text-fg)',
                'accent_red': '#FD4F49',  # Red for Daily Items
                'accent_teal': "#1A99DD",  # Blue for Daily TMs
                'accent_yellow': '#84D437',  # Gray for Standard Items
                'button_bg': 'var(--button-bg)',
                'button_hover': 'var(--button-hover-bg)',
                'frame_bg': 'var(--frame-bg)',
                'frame_hover': 'var(--button-hover-bg)',
                'success': '#66BB6A',
                'warning': '#FF7043'
            }
        else:
            return {
                'background': 'var(--window-bg)',
                'border': 'var(--border)',
                'text_primary': 'var(--text)',
                'text_secondary': 'var(--text-fg)',
                'accent_red': '#FD4F49',  # Red for Daily Items
                'accent_teal': '#1A99DD',  # Blue for Daily TMs
                'accent_yellow': '#84D437',  # Gray for Standard Items
                'button_bg': 'var(--button-bg)',
                'button_hover': 'var(--button-hover-bg)',
                'frame_bg': 'var(--frame-bg)',
                'frame_hover': 'var(--button-hover-bg)',
                'success': '#4CAF50',
                'warning': '#FF6B6B'
            }

    def toggle_window(self):
        """Toggles the visibility of the Pokemon shop window."""
        if self.window and self.window.isVisible():
            self.window.close()
        else:
            if not self.window or not self.window.isVisible():
                self.create_gui()
            self.window.show()

    def create_gui(self):
        """Create the retro Pokemon-style shop GUI with theme support."""
        self.window = QDialog(parent=mw)
        self.window.setWindowTitle("Ankimon Mart")
        self.window.setGeometry(100, 100, 750, 450)

        colors = self._get_theme_colors()

        # Apply Anki's theme class to inherit theme colors
        self.window.setProperty("class", "ankimon-shop")

        # Theme-aware background using Anki's CSS variables
        self.window.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['background']};
                border: 4px solid {colors['border']};
            }}
        """)

        self.window.setWindowFlag(Qt.WindowType.Tool)

        # Main layout with Pokemon-style spacing
        main_layout = QVBoxLayout(self.window)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Header section with theme-aware styling
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)

        # Shop sections layout
        shop_layout = QHBoxLayout()
        shop_layout.setSpacing(15)

        # Create the two shop sections with theme colors
        daily_section = self._create_shop_section("Daily Items", self.get_daily_items(), colors['accent_red'])
        tm_section = self._create_shop_section("Daily TMs", self.get_daily_tms(), colors['accent_teal'], is_tm=True)
        #standard_section = self._create_shop_section("Standard Items", STANDARD_ITEMS, colors['accent_yellow'])

        shop_layout.addWidget(daily_section)
        shop_layout.addWidget(tm_section)
        #shop_layout.addWidget(standard_section)

        main_layout.addLayout(shop_layout)

    def _create_header(self):
        """Create the theme-aware Ankimon Mart header in a single horizontal line."""
        colors = self._get_theme_colors()
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)

        # Ankimon Mart title
        title_label = QLabel("ANKIMON MART")
        title_font = QFont(self.early_gameboy_font)
        title_font.setPointSize(18)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {colors['text_primary']};
                background-color: {colors['border']};
                border: 3px solid {colors['text_primary']};
                border-radius: 8px;
                padding: 8px 16px;
                margin: 4px;
            }}
        """)

        # Money display
        self.currency_qlabel = QLabel(f"MONEY: ${self.settings_obj.get('trainer.cash', 0)}")
        money_font = QFont(self.early_gameboy_font)
        money_font.setPointSize(12)
        self.currency_qlabel.setFont(money_font)
        self.currency_qlabel.setStyleSheet(f"""
            QLabel {{
                color: {colors['text_primary']};
                background-color: {colors['button_bg']};
                border: 2px solid {colors['text_primary']};
                border-radius: 6px;
                padding: 6px 12px;
            }}
        """)

        # Create the reroll button with the desired text
        reroll_button = QPushButton(f"REROLL SHOP\n${self.daily_items_reroll_cost}")

        button_font = QFont(self.early_gameboy_font)
        button_font.setPointSize(10)
        reroll_button.setFont(button_font)

        reroll_button.setFixedWidth(reroll_button.sizeHint().width())

        reroll_button.setMinimumHeight(50)

        reroll_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['accent_red']};
                color: {colors['text_primary']};
                border: 3px solid {colors['text_primary']};
                border-radius: 8px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors['button_hover']};
                border: 3px solid {colors['accent_yellow']};
            }}
            QPushButton:pressed {{
                background-color: {colors['border']};
            }}
        """)
        reroll_button.clicked.connect(lambda: self.reroll_daily_items(cost=self.daily_items_reroll_cost))

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.currency_qlabel)
        header_layout.addWidget(reroll_button)

        return header_layout

    def _create_shop_section(self, title, items, color, is_tm=False):
        """Create a theme-aware shop section without boundaries."""
        colors = self._get_theme_colors()
        section_frame = QFrame()
        section_frame.setFixedWidth(340)
        # Removed border styles to remove boundaries
        section_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['frame_bg']};
                border-radius: 12px;
                margin: 4px;
            }}
        """)

        section_layout = QVBoxLayout(section_frame)
        section_layout.setContentsMargins(8, 8, 8, 8)
        section_layout.setSpacing(8)

        # Section title with Early GameBoy font
        title_label = QLabel(title.upper())
        title_label.setFont(self.early_gameboy_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {colors['text_primary']};
                background-color: {color};
                border-radius: 6px;
                padding: 6px;
                font-weight: bold;
            }}
        """)
        section_layout.addWidget(title_label)

        # Items grid
        items_layout = QVBoxLayout()
        items_layout.setSpacing(6)

        # Get items based on type
        if title == "Daily Items" and not self.todays_daily_items:
            self.todays_daily_items = items
        elif title == "Daily TMs" and not self.todays_daily_tms:
            self.todays_daily_tms = items

        for item in items:
            item_frame = self._create_retro_item_frame(item, color, is_tm)
            items_layout.addWidget(item_frame)

        section_layout.addLayout(items_layout)
        section_layout.addStretch()

        return section_frame

    def _create_retro_item_frame(self, item, section_color, is_tm=False):
        """Create a theme-aware retro-styled item frame with tooltip for description."""
        colors = self._get_theme_colors()

        if is_tm:
            item['UI_NAME'] = item["name"].replace('-', ' ').title()
            item['price'] = self.tm_price
            # Description for TMs: fixed string
            description_text = f"Allows a Pokémon to be taught the move {item['UI_NAME']} (if able)"
        else:
            item['UI_NAME'] = item["name"].replace('-', ' ').title()
            item['price'] = get_item_price(item["name"])
            # Description for regular items: use get_item_description with language from settings
            description_text = get_item_description(item['name'], self.settings_obj.get('misc.language', '9'))
            if not description_text:
                description_text = f"A useful item: {item['UI_NAME']}"

        frame = QFrame()
        frame.setFixedHeight(90)
        # Tooltip with item description for hover popup
        frame.setToolTip(description_text)

        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['frame_bg']};
                border-radius: 8px;
                margin: 2px;
            }}
            QFrame:hover {{
                background-color: {colors['frame_hover']};
            }}
        """)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        # Item image
        image_label = QLabel()
        if is_tm:
            image_path = items_path / f"Bag_TM_{find_details_move(item["name"])["type"].lower()}_SV_Sprite.png"
        else:
            image_path = f"{items_path}/{item["name"]}.png"

        pixmap = QPixmap(str(image_path))
        image_label.setPixmap(pixmap.scaled(56, 56, Qt.AspectRatioMode.KeepAspectRatio))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(image_label)

        # Item info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        # Item name
        name_label = QLabel(item['UI_NAME'])
        name_font = QFont(self.early_gameboy_font)
        name_font.setPointSize(10)
        name_label.setFont(name_font)
        name_label.setStyleSheet(f"QLabel {{ color: {colors['text_secondary']}; font-weight: bold; }}")
        info_layout.addWidget(name_label)

        # Price
        price_label = QLabel(f"${item.get('price', 1000)}")
        price_font = QFont(self.early_gameboy_font)
        price_font.setPointSize(9)
        price_label.setFont(price_font)
        price_label.setStyleSheet(f"QLabel {{ color: {colors['success']}; font-weight: bold; }}")
        info_layout.addWidget(price_label)

        layout.addLayout(info_layout)
        layout.addStretch()

        # Buy button with theme-aware styling
        buy_button = QPushButton("BUY")
        buy_font = QFont(self.early_gameboy_font)
        buy_font.setPointSize(8)
        buy_button.setFont(buy_font)
        buy_button.setFixedHeight(35)
        buy_button.setFixedWidth(buy_button.sizeHint().width())

        buy_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {section_color};
                color: {colors['text_primary']};
                border: 2px solid {colors['text_primary']};
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors['button_hover']};
                color: {section_color};
                border: 2px solid {section_color};
            }}
            QPushButton:pressed {{
                background-color: {colors['border']};
            }}
        """)

        if is_tm:
            buy_button.clicked.connect(lambda checked, item=item: self.buy_item(item, item.get("item_type")))
        else:
            buy_button.clicked.connect(lambda checked, item=item: self.buy_item(item))

        layout.addWidget(buy_button)

        return frame

    def get_daily_items(self):
        """Generate daily items based on the current date."""
        if os.path.isfile(self.shop_save_file):
            with open(self.shop_save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("items") and data.get("date") == datetime.now().strftime("%Y-%m-%d"):
                    return data.get("items")

        seed = datetime.now().strftime("%Y-%m-%d")
        random.seed(seed)
        return random.sample(DAILY_ITEMS_POOL, self.number_of_daily_items)

    def get_daily_tms(self):
        """Works like get_daily_items, but for TMs"""
        if os.path.isfile(self.shop_save_file):
            with open(self.shop_save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("technical_machines") and data.get("date") == datetime.now().strftime("%Y-%m-%d"):
                    return data.get("technical_machines")

        tm_pool = self.get_tm_pool()
        seed = datetime.now().strftime("%Y-%m-%d")
        random.seed(seed)
        return random.sample(tm_pool, self.number_of_daily_items)

    def get_tm_pool(self) -> list[str]:
        with open(pokemon_tm_learnset_path, "r") as f:
            pokemon_tm_learnset = json.load(f)

        def flatten(xss):
            return [x for xs in xss for x in xs]
        all_tms = flatten(list(pokemon_tm_learnset.values()))
        all_tms = list(set(all_tms))
        all_tms = [
            {
            "name": tm,
            "description": f"Allows a Pokemon to be taught the move {tm} (if able).",
            "price": self.tm_price,
            "item_type": "TM",
            } for tm in all_tms]
        return list(all_tms)

    def buy_item(self, item, item_type: Union[str, None]=None):
        """Handle item purchase with theme-aware retro-style messages."""
        colors = self._get_theme_colors()

        try:
            if self.settings_obj.get('trainer.cash', 0) < item['price']:
                msg = QMessageBox(mw)
                msg.setWindowTitle("Ankimon Mart")
                msg.setText("You don't have enough money!")
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setStyleSheet(f"""
                    QMessageBox {{
                        background-color: {colors['background']};
                        color: {colors['text_primary']};
                    }}
                    QMessageBox QPushButton {{
                        background-color: {colors['warning']};
                        color: {colors['text_primary']};
                        border: 2px solid {colors['text_primary']};
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-weight: bold;
                    }}
                """)
                msg.exec()
                return

            self.set_callback('trainer.cash', int(self.get_callback('trainer.cash', 0) - item['price']))
            self.currency_qlabel.setText(f"MONEY: ${self.settings_obj.get('trainer.cash', 0)}")

            msg = QMessageBox(mw)
            msg.setWindowTitle("Ankimon Mart")
            msg.setText(f"Thank you!\nYou bought {item.get('UI_NAME', 'Unknown')} for ${item['price']}!")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {colors['background']};
                    color: {colors['text_primary']};
                }}
                QMessageBox QPushButton {{
                    background-color: {colors['success']};
                    color: {colors['text_primary']};
                    border: 2px solid {colors['text_primary']};
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-weight: bold;
                }}
            """)
            msg.exec()

            give_item(item['name'], item_type)
        except Exception as e:
            self.logger.log_and_showinfo("error", f"Failed to purchase item: {e}")

    def reroll_daily_items(self, cost: int = 0) -> None:
        """Rerolls the daily items in the shop with theme-aware messaging"""
        colors = self._get_theme_colors()

        if self.settings_obj.get('trainer.cash', 0) < cost:
            msg = QMessageBox(mw)
            msg.setWindowTitle("Ankimon Mart")
            msg.setText("You don't have enough money to reroll!")
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {colors['background']};
                    color: {colors['text_primary']};
                }}
                QMessageBox QPushButton {{
                    background-color: {colors['warning']};
                    color: {colors['text_primary']};
                    border: 2px solid {colors['text_primary']};
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-weight: bold;
                }}
            """)
            msg.exec()
            return

        self.set_callback('trainer.cash', int(self.get_callback('trainer.cash', 0) - cost))
        self.currency_qlabel.setText(f"MONEY: ${self.settings_obj.get('trainer.cash', 0)}")

        # Generate new random items
        random.seed()  # Use current time for truly random reroll
        self.todays_daily_items = random.sample(DAILY_ITEMS_POOL, self.number_of_daily_items)
        self.todays_daily_tms = random.sample(self.get_tm_pool(), self.number_of_daily_items)

        # SAVE IMMEDIATELY - before GUI refresh
        with open(self.shop_save_file, 'w', encoding='utf-8') as f:
            data = {
                "items": self.todays_daily_items,
                "technical_machines": self.todays_daily_tms,
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
            json.dump(data, f, ensure_ascii=False, indent=4)

        # Now refresh the window - it will load from the updated JSON file
        self.toggle_window()
        self.toggle_window()
