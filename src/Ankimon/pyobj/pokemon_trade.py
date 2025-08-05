import json
import hashlib
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QFrame
from PyQt6.QtGui import QPixmap, QFont, QIcon, QColor
from PyQt6.QtCore import QSize, Qt
from aqt.utils import showWarning
from aqt import mw
from ..resources import mainpokemon_path, mypokemon_path, pokeapi_db_path, moves_file_path, pokedex_path
from ..functions.sprite_functions import get_sprite_path
from datetime import datetime
import uuid
from ..functions.pokedex_functions import search_pokeapi_db_by_id


class PokemonTrade:
    TRADE_VERSION = "01"

    def __init__(self, name, id, level, ability, iv, ev, gender, attacks, individual_id, logger, refresh_callback, parent_window=None):
        self.name = name
        self.id = id
        self.level = level
        self.ability = ability
        self.iv = iv
        self.ev = ev
        self.gender = gender
        self.attacks = attacks
        self.individual_id = individual_id
        self.refresh_callback = refresh_callback
        self.logger = logger
        self.parent_window = parent_window  # The collection window or None

        # File paths
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
        except FileNotFoundError:
            self.logger.log_and_showinfo("warning", "Main Pokémon file not found!")
            return []

    def check_and_trade(self):
        pokemon_data = self.load_pokemon_data()
        for pokemon in pokemon_data:
            if self._match_main_pokemon(pokemon):
                self.logger.log_and_showinfo("warning", "You can't trade your Main Pokémon! \nPlease pick a different Main Pokémon.")
                return
        self.open_trade_window()

    def _match_main_pokemon(self, pokemon):
        return (
                pokemon["name"] == self.name
                and pokemon["id"] == self.id
                and pokemon["level"] == self.level
                and pokemon["ability"] == self.ability
                and pokemon["iv"] == self.iv
                and pokemon["ev"] == self.ev
                and pokemon["gender"] == self.gender
                and pokemon["attacks"] == self.attacks
                and pokemon["shiny"] == self.shiny
        )


    def open_trade_window(self):
        # Always use the collection window as parent if provided, else mw
        parent = self.parent_window if self.parent_window is not None else mw
        window = QDialog(parent)
        window.setWindowTitle(f"Trade Pokémon: {self.name}")
        window.setWindowModality(Qt.WindowModality.ApplicationModal)
        window.setMinimumSize(350, 450)

        main_layout = QVBoxLayout(window)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title
        title_label = QLabel(f"Trading Away: {self.name}")
        title_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Pokémon Sprites Layout
        sprites_layout = QHBoxLayout()
        sprites_layout.setSpacing(20)

        # Your Pokémon
        your_pokemon_layout = QVBoxLayout()
        your_pokemon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        from PyQt6.QtGui import QMovie, QImage, QPixmap
        your_pokemon_sprite_label = QLabel()
        sprite_size = QSize(64, 64)
        your_pokemon_sprite_label.setMaximumSize(sprite_size)
        your_pokemon_sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        your_pokemon_gif_path = get_sprite_path(
            side="front",
            sprite_type="gif",
            id=self.id,
            shiny=getattr(self, "shiny", False),
            gender=self.gender
        )
        # Load the GIF and convert to grayscale for black-and-white effect
        your_pokemon_movie = QMovie(your_pokemon_gif_path)
        # Do not use setScaledSize; instead, scale the frame for aspect ratio
        def set_bw_frame():
            frame = your_pokemon_movie.currentImage()
            if not frame.isNull():
                # Convert to grayscale while preserving alpha
                gray = QImage(frame.size(), QImage.Format.Format_ARGB32)
                for y in range(frame.height()):
                    for x in range(frame.width()):
                        color = frame.pixelColor(x, y)
                        alpha = color.alpha()
                        # Compute grayscale value using luminosity method
                        gray_value = int(0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue())
                        gray.setPixelColor(x, y, QColor(gray_value, gray_value, gray_value, alpha))
                # Scale with aspect ratio
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

        # Trade Icon
        trade_icon_label = QLabel()
        trade_icon = QIcon.fromTheme("go-next")  # Using a system theme icon
        if trade_icon.isNull():
            trade_icon_label.setText("->")  # Fallback text
        else:
            trade_icon_label.setPixmap(trade_icon.pixmap(QSize(64, 64)))
        trade_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sprites_layout.addWidget(trade_icon_label)

        # Other Pokémon (placeholder)
        other_pokemon_layout = QVBoxLayout()
        other_pokemon_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.other_pokemon_sprite_label = QLabel()
        self.other_pokemon_sprite_label.setMaximumSize(sprite_size)
        self.other_pokemon_sprite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.other_pokemon_sprite_label.setPixmap(
            QPixmap(":/icons/pokeball.png").scaled(sprite_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.other_pokemon_name_label = QLabel("")  # Will be set dynamically
        self.other_pokemon_name_label.setFont(QFont("Arial", 12))
        other_pokemon_layout.addWidget(self.other_pokemon_sprite_label)
        other_pokemon_layout.addWidget(self.other_pokemon_name_label)
        sprites_layout.addLayout(other_pokemon_layout)

        main_layout.addLayout(sprites_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)

        # --- Trade Code Interface ---
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
        self.trade_code_input.setPlaceholderText("Paste the code from the other person here")
        self.trade_code_input.textChanged.connect(self.update_other_pokemon_sprite)
        main_layout.addWidget(self.trade_code_input)

        # Trade Button
        self.trade_button = QPushButton("Generate Trade Password")
        self.trade_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.trade_button.setStyleSheet("padding: 10px;")
        self.trade_button.clicked.connect(lambda: self.generate_and_show_passwords(window))
        main_layout.addWidget(self.trade_button)

        window.exec()

    def generate_and_show_passwords(self, window):
        # Validate codes before switching
        code1 = self.trade_code_display.text().strip()
        code2 = self.trade_code_input.text().strip()
        if not code1 or not code2 or len(code2) < 15:
            showWarning("Please enter a valid trade code from the other user.")
            return

        # Hide code entry widgets
        self.your_code_label.hide()
        self.trade_code_display.hide()
        self.copy_button.hide()
        self.their_code_label.hide()
        self.trade_code_input.hide()
        self.trade_button.hide()

        # Generate and display passwords
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

        # --- Password Interface ---
        self.password_interface = QFrame()
        self.password_layout = QVBoxLayout(self.password_interface)
        self.password_layout.setSpacing(5)

        # Your password part
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

        # Their password part
        their_password_label = QLabel("Enter Trade Partner's Password:")
        their_password_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.password_layout.addWidget(their_password_label)

        self.other_password_input = QLineEdit()
        self.other_password_input.setPlaceholderText("Enter the other person's password part")
        self.password_layout.addWidget(self.other_password_input)

        # Password Button
        self.password_button = QPushButton("Perform Trade")
        self.password_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.password_button.setStyleSheet("padding: 10px;")
        self.password_button.clicked.connect(lambda: self.handle_trade_with_password(window))
        self.password_layout.addWidget(self.password_button)

        # Add to main layout
        window.layout().addWidget(self.password_interface)

    def handle_trade_with_password(self, parent_window):
        """
        Require the other user's password part to complete the trade.
        """
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
            # Prevent trading for a Pokémon of the same species (ID)
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
            return

    def copy_to_clipboard(self, text):
        clipboard = mw.app.clipboard()
        clipboard.setText(text)
        showWarning("Trade code copied to clipboard!")

    def update_other_pokemon_sprite(self, code):
        from PyQt6.QtGui import QMovie
        try:
            sprite_size = QSize(64, 64)
            parts = code.split(',')
            if len(parts) > 0 and parts[0].isdigit():
                pokemon_id = int(parts[0])
                # Default values
                other_gender = "M"
                other_shiny = False
                # Parse gender if present (3rd value in code)
                if len(parts) > 2:
                    gender_map = {"0": "M", "1": "F", "2": "N"}
                    other_gender = gender_map.get(parts[2], "M")
                # If you add shiny info to the code, parse it here (e.g., as 4th or last value)
                # For now, default to False
                sprite_path = get_sprite_path(
                    side="front",
                    sprite_type="gif",
                    id=pokemon_id,
                    shiny=other_shiny,
                    gender=other_gender
                )
                other_pokemon_movie = QMovie(sprite_path)
                # Do not use setScaledSize; instead, scale the frame for aspect ratio
                def set_other_frame():
                    frame = other_pokemon_movie.currentImage()
                    if not frame.isNull():
                        scaled = QPixmap.fromImage(frame).scaled(sprite_size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        self.other_pokemon_sprite_label.setPixmap(scaled)
                other_pokemon_movie.frameChanged.connect(lambda _: set_other_frame())
                self.other_pokemon_sprite_label.setMovie(other_pokemon_movie)
                other_pokemon_movie.start()
                set_other_frame()
                # Set the Pokémon name label
                name = self.get_pokemon_name_by_id(pokemon_id)
                self.other_pokemon_name_label.setText(name if name else "Unknown Pokémon")
            else:
                self.other_pokemon_name_label.setText("")
        except Exception:
            # In case of invalid format, reset to placeholder
            self.other_pokemon_sprite_label.setPixmap(
                QPixmap(":/icons/pokeball.png").scaled(QSize(64, 64), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.other_pokemon_name_label.setText("")

    def get_pokemon_name_by_id(self, pokemon_id):
        try:
            with open(self.pokedex_path, 'r', encoding='utf-8') as file:
                pokedex = json.load(file)
                for details in pokedex.values():
                    if details.get('num') == pokemon_id:
                        return details.get('name', str(pokemon_id))
        except Exception:
            pass
        return str(pokemon_id)

    def confirm_trade(self, parent_window):
        """
        Show a confirmation dialog before finalizing the trade.
        """
        from PyQt6.QtWidgets import QMessageBox
        code = self.trade_code_input.text()
        # Try to get the Pokémon name from the code
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

    def format_gender(self):
        gender_map = {"M": 0, "F": 1, "N": 2}
        return gender_map.get(self.gender, 3)

    def ev_string(self):
        return ','.join(str(value) for value in self.ev.values())

    def iv_string(self):
        return ','.join(str(value) for value in self.iv.values())

    def attack_ids(self):
        return ','.join([str(self.find_move_by_name(attack)) for attack in self.attacks])

    def trade_pokemon_in(self, number_code):
        try:
            numbers = [int(num) for num in number_code.split(',')]
            if len(numbers) < 15:
                showWarning("Code is incomplete.")
                return
            # Prevent trading with a Pokémon of the same ID (not individual_id)
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
        pokemon_id, level, gender_id = numbers[0], numbers[1], numbers[2]
        ev_stats = dict(zip(['hp', 'atk', 'def', 'spa', 'spd', 'spe'], numbers[3:9]))
        iv_stats = dict(zip(['hp', 'atk', 'def', 'spa', 'spd', 'spe'], numbers[9:15]))
        attacks = [self.find_move_by_num(attack_id)['name'] for attack_id in numbers[15:]]

        details = self.find_pokemon_by_id(pokemon_id)
        if not details:
            return

        base_experience = search_pokeapi_db_by_id(pokemon_id, "base_experience")

        # --- Ability generation logic (like encounter_functions) ---
        ability = "No Ability"
        possible_abilities = search_pokedex(details["name"], "abilities")
        if possible_abilities:
            numeric_abilities = {k: v for k, v in possible_abilities.items() if k.isdigit()}
            if numeric_abilities:
                ability = random.choice(list(numeric_abilities.values()))

        # --- Move generation logic (like encounter_functions) ---
        # If no valid moves are provided, generate them as in wild encounters
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
                return move['num']  # Return the move ID
            else:
                return int(33)  # Return a default message if not found

    def find_pokemon_by_id(self, pokemon_id):
        with open(self.pokedex_path, 'r', encoding='utf-8') as file:
            pokedex = json.load(file)
            for details in pokedex.values():
                if details.get('num') == pokemon_id:
                    return details
        self.logger.log_and_showinfo("warning",f"No Pokémon found with ID: {pokemon_id}")
        return None

    def gender_from_id(self, gender_id):
        return {0: "M", 1: "F", 2: "N"}.get(gender_id, "N/A")

    def get_growth_rate(self, pokemon_id):
        with open(self.pokeapi_db_path, "r", encoding="utf-8") as file:
            pokemon_data = json.load(file)
            return next((p["growth_rate"] for p in pokemon_data if p["id"] == pokemon_id), None)

    def replace_pokemon(self, new_pokemon):
        try:
            with open(self.mypokemon_path, 'r+') as file:
                pokemon_list = json.load(file)
                
                # Find and replace the Pokémon by individual ID
                for idx, pokemon in enumerate(pokemon_list):
                    if pokemon.get("individual_id") == self.individual_id:  # Match individual_id
                        pokemon_list[idx] = new_pokemon
                        break
                else:
                    self.logger.log_and_showinfo("warning","Could not find the Pokémon with the specified Individual ID.")
                    return

                # Write updated Pokémon list back to the file
                file.seek(0)
                file.truncate()
                json.dump(pokemon_list, file, indent=2)
            
            self.logger.log_and_showinfo("warning",f"Successfully traded for {new_pokemon['name']}!")
            self.refresh_callback()

        except (FileNotFoundError, json.JSONDecodeError):
            self.logger.log_and_showinfo("warning","Error updating Pokémon data.")