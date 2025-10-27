import json
import hashlib
import requests
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor
from PyQt6.QtCore import QSize, Qt
from aqt.utils import showWarning, showInfo
from aqt import mw, utils
from ..resources import mainpokemon_path, mypokemon_path, pokeapi_db_path, moves_file_path, pokedex_path, rate_path
from ..functions.sprite_functions import get_sprite_path
from datetime import datetime
import uuid
from ..functions.pokedex_functions import search_pokeapi_db_by_id
from .error_handler import show_warning_with_traceback

# --- Module-level functions for Monthly Challenges ---

def create_monthly_challenge_pokemon(pokemon_data, make_shiny=False):
    """Creates a Pokémon dictionary from monthly challenge data."""
    base_stats = pokemon_data.get("stats", {})
    return {
        "name": pokemon_data["name"],
        "nickname": pokemon_data.get("nickname", ""),
        "id": pokemon_data["id"],
        "level": pokemon_data.get("level", 1),
        "ability": pokemon_data.get("ability", "No Ability"),
        "type": pokemon_data.get("type", ["Normal"]),
        "stats": base_stats,
        "ev": pokemon_data.get("ev", {"hp": 0, "atk": 0, "def": 0, "spa": 0, "spd": 0, "spe": 0}),
        "iv": pokemon_data.get("iv", {"hp": 15, "atk": 15, "def": 15, "spa": 15, "spd": 15, "spe": 15}),
        "attacks": pokemon_data.get("attacks", ["Tackle"]),
        "growth_rate": pokemon_data.get("growth_rate", "medium"),
        "base_experience": pokemon_data.get("base_experience", 64),
        "gender": pokemon_data.get("gender", "N"),
        "shiny": pokemon_data.get("shiny", False) or make_shiny,
        "xp": pokemon_data.get("xp", 0),
        "current_hp": pokemon_data.get("current_hp", base_stats.get("hp")),
        "friendship": pokemon_data.get("friendship", 0),
        "pokemon_defeated": pokemon_data.get("pokemon_defeated", 0),
        "everstone": pokemon_data.get("everstone", False),
        "mega": pokemon_data.get("mega", False),
        "special-form": pokemon_data.get("special-form", None),
        "tier": pokemon_data.get("tier", "Normal"),
        "captured_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "individual_id": pokemon_data["individual_id"],
        "is_favorite": pokemon_data.get("is_favorite", False),
        "held_item": pokemon_data.get("held_item", None)
    }

def add_pokemon_to_collection(new_pokemon, refresh_callback=None, parent_window=None):
    """Adds a Pokémon to the user's collection file."""
    try:
        with open(mypokemon_path, "r", encoding="utf-8") as file:
            pokemon_list = json.load(file)
        pokemon_list.append(new_pokemon)
        with open(mypokemon_path, "w", encoding="utf-8") as file:
            json.dump(pokemon_list, file, indent=2)
        if refresh_callback:
            refresh_callback()
    except Exception as e:
        show_warning_with_traceback(parent=parent_window, exception=e, message="Error adding Pokemon to collection")

def check_and_award_monthly_pokemon(logger):
    """Checks for and automatically awards the current monthly challenge Pokémon."""
    try:
        should_check = False
        if rate_path.is_file():
            with open(rate_path, "r", encoding="utf-8") as f:
                if json.load(f).get("rate_this") is True:
                    should_check = True
        
        if not should_check:
            logger.log("info", "Monthly Pokemon check skipped: user has not rated the addon.")
            return

        logger.log("info", "Checking for monthly challenge Pokemon award.")
        now = datetime.now()
        month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        current_month_str = f"{month_names[now.month - 1]} {now.year}"
        monthly_data_url = "https://raw.githubusercontent.com/h0tp-ftw/ankimon/refs/heads/main/assets/challenges/monthly_challenges.json"
        
        try:
            response = requests.get(monthly_data_url, timeout=2)
            response.raise_for_status()
            monthly_challenges = response.json()
        except requests.exceptions.RequestException as e:
            logger.log("error", f"Could not fetch monthly challenges; likely no internet connection. Details: {e}")
            return  # Exit gracefully if fetching fails

        current_challenge = next((c for c in monthly_challenges if c.get("month") == current_month_str), None)

        if not current_challenge:
            logger.log("info", f"No monthly challenge found for {current_month_str}.")
            return

        challenge_pokemon_data = current_challenge.get("pokemon")
        if not challenge_pokemon_data:
            logger.log("warning", f"Monthly challenge for {current_month_str} is missing 'pokemon' data.")
            return

        challenge_individual_id = challenge_pokemon_data.get("individual_id")
        if not challenge_individual_id:
            logger.log("warning", f"Monthly challenge for {current_month_str} is missing 'individual_id' in 'pokemon' data.")
            return

        try:
            with open(mypokemon_path, "r", encoding="utf-8") as f:
                my_pokemon = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.log("error", f"Failed to load or parse mypokemon.json: {e}")
            return

        if any(p.get("individual_id") == challenge_individual_id for p in my_pokemon):
            logger.log("info", f"User already has the Pokémon for {current_month_str} (ID: {challenge_individual_id}).")
            return

        logger.log("info", f"Awarding Pokémon for {current_month_str}: {challenge_pokemon_data.get('name')}")
        make_shiny = False
        prev_id = current_challenge.get("previous_challenge_individual_id")
        threshold = current_challenge.get("defeat_threshold")

        if prev_id and threshold:
            logger.log("info", f"Checking for shiny eligibility: prev_id={prev_id}, threshold={threshold}")
            for p in my_pokemon:
                if p.get("individual_id") == prev_id and p.get("pokemon_defeated", 0) >= threshold:
                    logger.log("info", f"Shiny criteria met for {challenge_pokemon_data.get('name')}.")
                    make_shiny = True
                    break
        
        new_pokemon = create_monthly_challenge_pokemon(challenge_pokemon_data, make_shiny=make_shiny)
        add_pokemon_to_collection(new_pokemon)

        shiny_text = " (Shiny)" if new_pokemon["shiny"] else ""
        description = current_challenge.get("description", "")
        message = f"Congratulations! You've received your monthly challenge Pokémon: {new_pokemon['name']}{shiny_text}!"
        if description:
            message += f"\n\n{description}"
        message += "\n\nFor more information on monthly challenges and to redeem higher-tier prizes for your performance, please check the Ankimon Discord!"
        
        utils.showInfo(message)
        logger.log("info", f"Successfully awarded {new_pokemon['name']}{shiny_text}.")

    except Exception as e:
        logger.log("error", f"An unexpected error occurred in check_and_award_monthly_pokemon: {e}")
        # Still failing silently on the user's end, but with more detailed logs for debugging.
        pass


class PokemonTrade:
    TRADE_VERSION = "01"

    def __init__(self, name, id, level, ability, iv, ev, gender, attacks, individual_id, shiny, logger, refresh_callback, parent_window=None):
        self.name = name
        self.id = id
        self.level = level
        self.ability = ability
        self.iv = iv
        self.ev = ev
        self.gender = gender
        self.attacks = attacks
        self.individual_id = individual_id
        self.shiny = shiny
        self.refresh_callback = refresh_callback
        self.logger = logger
        self.parent_window = parent_window
        self.mainpokemon_path = mainpokemon_path
        self.mypokemon_path = mypokemon_path
        self.pokeapi_db_path = pokeapi_db_path
        self.moves_file_path = moves_file_path
        self.pokedex_path = pokedex_path
        self.check_and_trade()

    def load_pokemon_data(self):
        try:
            with open(self.mainpokemon_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError as e:
            show_warning_with_traceback(parent=self.parent_window, exception=e, message="Main Pokémon file not found!")
            return []

    def check_and_trade(self):
        pokemon_data = self.load_pokemon_data()
        for pokemon in pokemon_data:
            if self._match_main_pokemon(pokemon):
                self.logger.log_and_showinfo("warning", "You can't trade your Main Pokémon!\nPlease pick a different Main Pokémon.")
                return
        self.open_trade_window()

    def _match_main_pokemon(self, pokemon):
        return (
            pokemon["name"] == self.name and pokemon["id"] == self.id and pokemon["level"] == self.level and
            pokemon["ability"] == self.ability and pokemon["iv"] == self.iv and pokemon["ev"] == self.ev and
            pokemon["gender"] == self.gender and pokemon["attacks"] == self.attacks and pokemon["shiny"] == self.shiny
        )

    def open_trade_window(self):
        parent = self.parent_window if self.parent_window is not None else mw
        window = QDialog(parent)
        window.setWindowTitle(f"Trade Pokémon: {self.name}")
        window.setWindowModality(Qt.WindowModality.ApplicationModal)
        window.setMinimumSize(380, 450)

        main_layout = QVBoxLayout(window)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        title_label = QLabel(f"Trading Away: {self.name}")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        sprites_layout = QHBoxLayout()
        sprites_layout.setSpacing(20)

        your_pokemon_layout = QVBoxLayout()
        your_pokemon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        from PyQt6.QtGui import QMovie, QImage, QPixmap
        your_pokemon_sprite_label = QLabel()
        sprite_size = QSize(64, 64)
        your_pokemon_sprite_label.setMaximumSize(sprite_size)
        your_pokemon_sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        your_pokemon_gif_path = get_sprite_path(side="front", sprite_type="gif", id=self.id, shiny=getattr(self, "shiny", False), gender=self.gender)
        
        your_pokemon_movie = QMovie(your_pokemon_gif_path)
        def set_bw_frame():
            frame = your_pokemon_movie.currentImage()
            if not frame.isNull():
                gray = QImage(frame.size(), QImage.Format.Format_ARGB32)
                for y in range(frame.height()):
                    for x in range(frame.width()):
                        color = frame.pixelColor(x, y)
                        alpha = color.alpha()
                        gray_value = int(0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue())
                        gray.setPixelColor(x, y, QColor(gray_value, gray_value, gray_value, alpha))
                scaled = QPixmap.fromImage(gray).scaled(sprite_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                your_pokemon_sprite_label.setPixmap(scaled)
        your_pokemon_movie.frameChanged.connect(lambda _: set_bw_frame())
        your_pokemon_sprite_label.setMovie(your_pokemon_movie)
        your_pokemon_movie.start()
        set_bw_frame()
        your_pokemon_name_label = QLabel(f"{self.name}")
        your_pokemon_name_label.setFont(QFont("Arial", 12))
        your_pokemon_layout.addWidget(your_pokemon_sprite_label)
        your_pokemon_layout.addWidget(your_pokemon_name_label)
        sprites_layout.addLayout(your_pokemon_layout)

        trade_icon_label = QLabel("->")
        trade_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sprites_layout.addWidget(trade_icon_label)

        other_pokemon_layout = QVBoxLayout()
        other_pokemon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.other_pokemon_sprite_label = QLabel()
        self.other_pokemon_sprite_label.setMaximumSize(sprite_size)
        self.other_pokemon_sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.other_pokemon_sprite_label.setPixmap(QPixmap(":/icons/pokeball.png").scaled(sprite_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.other_pokemon_name_label = QLabel("")
        self.other_pokemon_name_label.setFont(QFont("Arial", 12))
        other_pokemon_layout.addWidget(self.other_pokemon_sprite_label)
        other_pokemon_layout.addWidget(self.other_pokemon_name_label)
        sprites_layout.addLayout(other_pokemon_layout)

        main_layout.addLayout(sprites_layout)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        self.trade_code_layout = QVBoxLayout()
        self.trade_code_layout.setSpacing(5)

        self.your_code_label = QLabel("Your Trade Code:")
        self.your_code_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.trade_code_layout.addWidget(self.your_code_label)

        self.code_display_layout = QHBoxLayout()
        clipboard_info = f"{self.id},{self.level},{self.format_gender()},{self.ev_string()},{self.iv_string()},{self.attack_ids()}"
        self.trade_code_display = QLineEdit(clipboard_info)
        self.trade_code_display.setReadOnly(True)
        self.trade_code_display.setFont(QFont("Courier New", 10))
        self.code_display_layout.addWidget(self.trade_code_display)

        self.copy_button = QPushButton("Copy")
        self.copy_button.setToolTip("Copy the trade code to your clipboard")
        self.copy_button.clicked.connect(lambda: self.copy_to_clipboard(clipboard_info))
        self.code_display_layout.addWidget(self.copy_button)
        self.trade_code_layout.addLayout(self.code_display_layout)

        main_layout.addLayout(self.trade_code_layout)

        self.their_code_label = QLabel("Enter Their Trade Code:")
        self.their_code_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        main_layout.addWidget(self.their_code_label)

        self.trade_code_input = QLineEdit()
        self.trade_code_input.setPlaceholderText("Paste trade code here")
        self.trade_code_input.textChanged.connect(self.update_other_pokemon_sprite)
        main_layout.addWidget(self.trade_code_input)

        self.trade_button = QPushButton("Generate Trade Password")
        self.trade_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.trade_button.setStyleSheet("padding: 10px;")
        self.trade_button.clicked.connect(lambda: self.generate_and_show_passwords(window))
        main_layout.addWidget(self.trade_button)

        window.exec()

    def generate_and_show_passwords(self, window):
        code1 = self.trade_code_display.text().strip()
        code2 = self.trade_code_input.text().strip()
        if not code1 or not code2 or len(code2) < 15:
            showWarning("Please enter a valid trade code from the other user.")
            return

        parts = code2.split(',')
        if len(parts) > 0 and parts[0].isdigit():
            incoming_id = int(parts[0])
            if incoming_id == self.id:
                showWarning("You cannot trade with a Pokémon of the same species (ID) as the one you're trading away!")
                return

        self.your_code_label.hide()
        self.trade_code_display.hide()
        self.copy_button.hide()
        self.their_code_label.hide()
        self.trade_code_input.hide()
        self.trade_button.hide()

        codes = sorted([code1, code2])
        combo = codes[0] + "|" + codes[1]
        hash_digest = hashlib.sha256(combo.encode()).hexdigest()
        part1 = hash_digest[:len(hash_digest) // 2]
        part2 = hash_digest[len(hash_digest) // 2:]

        if code1 < code2:
            my_part = part1
            self._their_password_part = part2
        else:
            my_part = part2
            self._their_password_part = part1

        my_part += self.TRADE_VERSION
        self._their_password_part += self.TRADE_VERSION

        self.password_interface = QFrame()
        self.password_layout = QVBoxLayout(self.password_interface)
        self.password_layout.setSpacing(5)

        your_password_label = QLabel("Your Password (To Send to Trade Partner):")
        your_password_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.password_layout.addWidget(your_password_label)

        your_password_display_layout = QHBoxLayout()
        your_password_display = QLineEdit(my_part)
        your_password_display.setReadOnly(True)
        your_password_display.setFont(QFont("Courier New", 10))
        your_password_display_layout.addWidget(your_password_display)

        copy_password_button = QPushButton("Copy")
        copy_password_button.setToolTip("Copy your password part to the clipboard")
        copy_password_button.clicked.connect(lambda: self.copy_to_clipboard(my_part))
        your_password_display_layout.addWidget(copy_password_button)
        self.password_layout.addLayout(your_password_display_layout)

        their_password_label = QLabel("Enter Trade Partner's Password:")
        their_password_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.password_layout.addWidget(their_password_label)

        self.other_password_input = QLineEdit()
        self.other_password_input.setPlaceholderText("Enter the other person's password part")
        self.password_layout.addWidget(self.other_password_input)

        self.password_button = QPushButton("Perform Trade")
        self.password_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.password_button.setStyleSheet("padding: 10px;")
        self.password_button.clicked.connect(lambda: self.handle_trade_with_password(window))
        self.password_layout.addWidget(self.password_button)

        window.layout().addWidget(self.password_interface)

    def handle_trade_with_password(self, parent_window):
        their_part_entered = self.other_password_input.text().strip()
        if not their_part_entered:
            showWarning("Please enter the password part from the other user.")
            return

        if len(their_part_entered) < 34:
            showWarning("Incorrect password format.")
            return

        their_version = their_part_entered[-2:]
        if their_version != self.TRADE_VERSION:
            showWarning(f"Trade incompatible due to Ankimon trade versions. \n\nYour verison: {self.TRADE_VERSION}, partner's version: {their_version}.\n\nPlease get the latest version of Ankimon for both users!")
            return

        if their_part_entered == self._their_password_part:
            code = self.trade_code_input.text().strip()
            parts = code.split(',')
            if len(parts) > 0 and parts[0].isdigit():
                incoming_id = int(parts[0])
                if incoming_id == self.id:
                    showWarning("You cannot trade with a Pokémon of the same species (ID) as the one you're trading away!")
                    return
            self.confirm_trade(parent_window)
        else:
            showWarning("Incorrect password part. Please check with the other user.")

    def copy_to_clipboard(self, text):
        clipboard = mw.app.clipboard()
        clipboard.setText(text)
        showInfo("Trade code copied to clipboard!")

    def update_other_pokemon_sprite(self, code):
        from PyQt6.QtGui import QMovie
        try:
            sprite_size = QSize(64, 64)
            parts = code.split(',')
            self.other_pokemon_sprite_label.clear()
            self.other_pokemon_sprite_label.setPixmap(QPixmap())
            self.other_pokemon_name_label.setText("")
            if len(parts) > 0 and parts[0].isdigit():
                pokemon_id = int(parts[0])
                other_gender = "M"
                other_shiny = False
                if len(parts) > 2:
                    gender_map = {"0": "M", "1": "F", "2": "N"}
                    other_gender = gender_map.get(parts[2], "M")
                
                sprite_path = get_sprite_path(side="front", sprite_type="gif", id=pokemon_id, shiny=other_shiny, gender=other_gender)
                
                if hasattr(self, '_other_pokemon_movie') and self._other_pokemon_movie is not None:
                    self._other_pokemon_movie.stop()
                    self._other_pokemon_movie.deleteLater()
                    self._other_pokemon_movie = None
                other_pokemon_movie = QMovie(sprite_path)
                self._other_pokemon_movie = other_pokemon_movie
                
                def set_other_frame():
                    frame = other_pokemon_movie.currentImage()
                    if not frame.isNull():
                        scaled = QPixmap.fromImage(frame).scaled(sprite_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        self.other_pokemon_sprite_label.setPixmap(scaled)
                other_pokemon_movie.frameChanged.connect(lambda _: set_other_frame())
                self.other_pokemon_sprite_label.setMovie(other_pokemon_movie)
                other_pokemon_movie.start()
                set_other_frame()
                name = self.get_pokemon_name_by_id(pokemon_id)
                self.other_pokemon_name_label.setText(name if name else "Unknown Pokémon")
            else:
                self.other_pokemon_sprite_label.setPixmap(QPixmap(":/icons/pokeball.png").scaled(QSize(64, 64), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                self.other_pokemon_name_label.setText("")
        except Exception:
            self.other_pokemon_sprite_label.setPixmap(QPixmap(":/icons/pokeball.png").scaled(QSize(64, 64), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.other_pokemon_name_label.setText("")

    def get_pokemon_name_by_id(self, pokemon_id):
        try:
            with open(self.pokedex_path, 'r', encoding='utf-8') as file:
                pokedex = json.load(file)
                for details in pokedex.values():
                    if details.get('num') == pokemon_id:
                        return details.get('name', str(pokemon_id))
        except Exception as e:
            show_warning_with_traceback(parent=self.parent_window, exception=e, message=f"An error occurred while getting the Pokémon name for ID {pokemon_id}.")
        return str(pokemon_id)

    def confirm_trade(self, parent_window):
        from PyQt6.QtWidgets import QMessageBox
        code = self.trade_code_input.text()
        name = "the other Pokémon"
        parts = code.split(',')
        if len(parts) > 0 and parts[0].isdigit():
            pokemon_id = int(parts[0])
            name = self.get_pokemon_name_by_id(pokemon_id)
        msg = QMessageBox(parent_window)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Confirm Trade")
        msg.setText(f"Are you sure you want to trade your {self.name} for {name}?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        result = msg.exec()
        if result == QMessageBox.StandardButton.Yes:
            self.trade_pokemon_in(code)

    def trade_pokemon_in(self, number_code):
        code = number_code.strip()
        try:
            numbers = [int(num) for num in code.split(',')]
            if len(numbers) < 15:
                showWarning("Code is incomplete.")
                return
            incoming_id = numbers[0]
            if incoming_id == self.id:
                showWarning("You cannot trade with a Pokémon of the same species (ID) as the one you're trading away!")
                return
            self.process_trade(numbers)
        except ValueError:
            showWarning("Please enter a valid Pokémon Code!")

    def process_trade(self, numbers):
        from ..functions.pokedex_functions import search_pokedex, search_pokeapi_db_by_id, get_all_pokemon_moves
        import random
        try:
            pokemon_id, level, gender_id = numbers[0], numbers[1], numbers[2]
            ev_stats = dict(zip(['hp', 'atk', 'def', 'spa', 'spd', 'spe'], numbers[3:9]))
            iv_stats = dict(zip(['hp', 'atk', 'def', 'spa', 'spd', 'spe'], numbers[9:15]))
            attacks = [self.find_move_by_num(attack_id)['name'] for attack_id in numbers[15:]]

            details = self.find_pokemon_by_id(pokemon_id)
            if not details:
                raise ValueError(f"Could not find Pokémon details for ID {pokemon_id}")

            base_experience = search_pokeapi_db_by_id(pokemon_id, "base_experience")

            ability = "No Ability"
            possible_abilities = search_pokedex(details["name"], "abilities")
            if possible_abilities:
                numeric_abilities = {k: v for k, v in possible_abilities.items() if k.isdigit()}
                if numeric_abilities:
                    ability = random.choice(list(numeric_abilities.values()))

            if not attacks or any(a == "Unknown Move" for a in attacks):
                all_possible_moves = get_all_pokemon_moves(details["name"], level)
                if len(all_possible_moves) <= 4:
                    attacks = all_possible_moves
                else:
                    attacks = random.sample(all_possible_moves, 4)

            new_pokemon = {
                "name": details["name"],
                "nickname": "",
                "ability": ability,
                "id": pokemon_id,
                "gender": self.gender_from_id(gender_id),
                "level": level,
                "type": details["types"],
                "stats": details["baseStats"],
                "ev": ev_stats,
                "iv": iv_stats,
                "attacks": attacks,
                "growth_rate": self.get_growth_rate(pokemon_id),
                "current_hp": self.calculate_max_hp(details["baseStats"]["hp"], level, ev_stats, iv_stats),
                "base_experience": base_experience,
                "friendship": 0,
                "pokemon_defeated": 0,
                "everstone": False,
                "shiny": False,
                "mega": False,
                "special-form": None,
                "capture_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "individual_id": str(uuid.uuid4())
            }
            new_pokemon["xp"] = 0
            self.replace_pokemon(new_pokemon)
        except Exception as e:
            show_warning_with_traceback(parent=self.parent_window, exception=e, message="An error occurred while processing the trade.")

    def calculate_max_hp(self, base_hp, level, ev, iv):
        ev_value = ev["hp"] / 4
        iv_value = iv["hp"]
        return int((((2 * base_hp + iv_value + ev_value) * level) / 100) + level + 10)

    def find_move_by_num(self, move_num):
        with open(self.moves_file_path, 'r', encoding='utf-8') as file:
            moves_data = json.load(file)
            return next((move for move in moves_data.values() if move.get('num') == move_num), {"name": "Unknown Move"})

    def find_move_by_name(self, move_name):
        with open(self.moves_file_path, 'r', encoding='utf-8') as file:
            moves_data = json.load(file)
            move = next((move for move in moves_data.values() if move.get('name').lower() == move_name.lower()), None)
            if move:
                return move['num']
            else:
                return int(33)

    def find_pokemon_by_id(self, pokemon_id):
        try:
            with open(self.pokedex_path, 'r', encoding='utf-8') as file:
                pokedex = json.load(file)
                for details in pokedex.values():
                    if details.get('num') == pokemon_id:
                        return details
            self.logger.log_and_showinfo("warning",f"No Pokémon found with ID: {pokemon_id}")
            return None
        except FileNotFoundError as e:
            show_warning_with_traceback(parent=self.parent_window, exception=e, message=f"Pokedex file not found.")
            return None

    def gender_from_id(self, gender_id):
        return {0: "M", 1: "F", 2: "N"}.get(gender_id, "N/A")

    def get_growth_rate(self, pokemon_id):
        try:
            with open(self.pokeapi_db_path, "r", encoding="utf-8") as file:
                pokemon_data = json.load(file)
                return next((p["growth_rate"] for p in pokemon_data if p["id"] == pokemon_id), None)
        except FileNotFoundError as e:
            show_warning_with_traceback(parent=self.parent_window, exception=e, message="PokeAPI DB file not found.")
            return None

    def replace_pokemon(self, new_pokemon):
        try:
            with open(self.mypokemon_path, 'r+') as file:
                pokemon_list = json.load(file)

                for idx, pokemon in enumerate(pokemon_list):
                    if pokemon.get("individual_id") == self.individual_id:
                        pokemon_list[idx] = new_pokemon
                        break
                else:
                    self.logger.log_and_showinfo("warning","Could not find the Pokémon with the specified Individual ID.")
                    return

                file.seek(0)
                file.truncate()
                json.dump(pokemon_list, file, indent=2)

            self.logger.log_and_showinfo("warning",f"Successfully traded for {new_pokemon['name']}!")
            self.refresh_callback()

        except (FileNotFoundError, json.JSONDecodeError) as e:
            show_warning_with_traceback(parent=self.parent_window, exception=e, message="Error updating Pokémon data.")
    
    def format_gender(self):
        gender_map = {"M": 0, "F": 1, "N": 2}
        return gender_map.get(self.gender, 3)

    def ev_string(self):
        return ','.join(str(value) for value in self.ev.values())

    def iv_string(self):
        return ','.join(str(value) for value in self.iv.values())

    def attack_ids(self):
        return ','.join([str(self.find_move_by_name(attack)) for attack in self.attacks])
