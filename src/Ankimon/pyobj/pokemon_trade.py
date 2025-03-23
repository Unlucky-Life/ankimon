import json
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from aqt.utils import showWarning
from aqt import mw
from ..resources import mainpokemon_path, mypokemon_path, pokeapi_db_path, moves_file_path, pokedex_path
from datetime import datetime
import uuid
from ..functions.pokedex_functions import search_pokeapi_db_by_id

class PokemonTrade:
    def __init__(self, name, id, level, ability, iv, ev, gender, attacks, individual_id, logger, refresh_callback):
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
            self.logger.log_and_showinfo("warning","Main Pokémon file not found!")
            return []

    def check_and_trade(self):
        pokemon_data = self.load_pokemon_data()
        for pokemon in pokemon_data:
            if self._match_main_pokemon(pokemon):
                self.logger.log_and_showinfo("warning","You can't trade your Main Pokémon! \nPlease pick a different Main Pokémon.")
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
        )

    def open_trade_window(self):
        window = QDialog()
        window.setWindowTitle(f"Trade Pokémon {self.name}")

        # Trade Code Input Field
        trade_code_input = QLineEdit()
        trade_code_input.setPlaceholderText("Enter Pokémon Code you want to trade for")

        # Trade Button
        trade_button = QPushButton("Trade Pokémon")
        trade_button.clicked.connect(lambda: self.trade_pokemon_in(trade_code_input.text()))

        # Generate Clipboard Content
        clipboard_info = f"{self.id},{self.level},{self.format_gender()},{self.ev_string()},{self.iv_string()},{self.attack_ids()}"
        mw.app.clipboard().setText(clipboard_info)

        # Layout Setup
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"{self.name} Code: {clipboard_info}"))
        layout.addWidget(trade_code_input)
        layout.addWidget(trade_button)

        window.setLayout(layout)
        window.exec()

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
                raise ValueError("Code is incomplete.")
            self.process_trade(numbers)
        except ValueError:
            showWarning("Please enter a valid Pokémon Code!")

    def process_trade(self, numbers):
        pokemon_id, level, gender_id = numbers[0], numbers[1], numbers[2]
        ev_stats = dict(zip(['hp', 'atk', 'def', 'spa', 'spd', 'spe'], numbers[3:9]))
        iv_stats = dict(zip(['hp', 'atk', 'def', 'spa', 'spd', 'spe'], numbers[9:15]))
        attacks = [self.find_move_by_num(attack_id)['name'] for attack_id in numbers[15:]]

        details = self.find_pokemon_by_id(pokemon_id)
        if not details:
            return

        base_experience = search_pokeapi_db_by_id(pokemon_id, "base_experience")

        # Create new Pokémon object for incoming trade code pokemon
        new_pokemon = {
            "name": details["name"],
            "nickname": "",
            "ability": "No Ability",
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

        new_pokemon["stats"]["xp"] = 0

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
