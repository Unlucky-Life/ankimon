import json

from aqt import mw
from aqt.qt import QDialog, QLabel,Qt, QVBoxLayout
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QLineEdit

from ..functions.pokedex_functions import search_pokedex
from ..functions.url_functions import open_browser_window
from ..utils import save_error_code
from ..resources import mypokemon_path
from ..singletons import main_pokemon, logger
from ..pyobj.error_handler import show_warning_with_traceback

def export_to_pkmn_showdown():
    # Create a main window
    window = QDialog(mw)
    window.setWindowTitle("Export Pokemon to Pkmn Showdown")
    for stat, value in main_pokemon.ev.items():
        if value == 0:
            main_pokemon.ev[stat] += 1
    # Format the Pokemon info
    pokemon_info = "{} ({})\nAbility: {}\nLevel: {}\nType: {}\nEVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe\n IVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe ".format(
        main_pokemon.name,
        main_pokemon.gender,
        main_pokemon.ability,
        main_pokemon.level,
        main_pokemon.type,
        main_pokemon.ev["hp"],
        main_pokemon.ev["atk"],
        main_pokemon.ev["def"],
        main_pokemon.ev["spa"],
        main_pokemon.ev["spd"],
        main_pokemon.ev["spe"],
        main_pokemon.iv["hp"],
        main_pokemon.iv["atk"],
        main_pokemon.iv["def"],
        main_pokemon.iv["spa"],
        main_pokemon.iv["spd"],
        main_pokemon.iv["spe"]
    )
    for attack in main_pokemon.attacks:
        pokemon_info += f"\n- {attack}"
    # Information label
    info = "Pokemon Infos have been Copied to your Clipboard! \nNow simply paste this text into Teambuilder in PokemonShowdown. \nNote: Fight in the [Gen 9] Anything Goes - Battle Mode"
    info += f"\n Your Pokemon is considered Tier: {search_pokedex(main_pokemon.name.lower(), 'tier')} in PokemonShowdown"
    # Create labels to display the text
    label = QLabel(pokemon_info)
    info_label = QLabel(info)

    # Align labels
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align center
    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align center

    # Create a layout and add the labels
    layout = QVBoxLayout()
    layout.addWidget(info_label)
    layout.addWidget(label)

    # Set the layout for the main window
    window.setLayout(layout)

    # Copy text to clipboard in Anki
    mw.app.clipboard().setText(pokemon_info)

    # Show the window
    window.show()

POKEMON_INFO_FORMAT = """{}
Ability: {}
Level: {}
Type: {}
EVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe
IVs: {} HP / {} Atk / {} Def / {} SpA / {} SpD / {} Spe
"""

def export_all_pkmn_showdown():
    # Create a main window
    export_window = QDialog()
    #export_window.setWindowTitle("Export Pokemon to Pkmn Showdown")

    # Information label
    info = "Pokemon Infos have been Copied to your Clipboard! \nNow simply paste this text into Teambuilder in PokemonShowdown. \nNote: Fight in the [Gen 7] Anything Goes - Battle Mode"
    info_label = QLabel(info)

    # Get all pokemon data
    pokemon_info_complete_text = ""
    try:
        with (open(mypokemon_path, "r", encoding="utf-8") as json_file):
            captured_pokemon_data = json.load(json_file)

            # Check if there are any captured Pokémon
            if captured_pokemon_data:
                # Counter for tracking the column position
                column = 0
                row = 0
                for pokemon in captured_pokemon_data:
                    pokemon_name = pokemon['name']
                    pokemon_level = pokemon['level']
                    pokemon_ability = pokemon['ability']
                    pokemon_type = pokemon['type']
                    pokemon_type_text = pokemon_type[0].capitalize()
                    if len(pokemon_type) > 1:
                        pokemon_type_text = ""
                        pokemon_type_text += f"{pokemon_type[0].capitalize()}"
                        pokemon_type_text += f" {pokemon_type[1].capitalize()}"
                    pokemon_stats = pokemon['stats']
                    pokemon_hp = pokemon_stats["hp"]
                    pokemon_attacks = pokemon['attacks']
                    pokemon_ev = pokemon['ev']
                    pokemon_iv = pokemon['iv']

                    pokemon_info = POKEMON_INFO_FORMAT.format(
                        pokemon_name,
                        pokemon_ability.capitalize(),
                        pokemon_level,
                        pokemon_type_text,
                        pokemon_ev["hp"],
                        pokemon_ev["atk"],
                        pokemon_ev["def"],
                        pokemon_ev["spa"],
                        pokemon_ev["spd"],
                        pokemon_ev["spe"],
                        pokemon_iv["hp"],
                        pokemon_iv["atk"],
                        pokemon_iv["def"],
                        pokemon_iv["spa"],
                        pokemon_iv["spd"],
                        pokemon_iv["spe"]
                    )
                    for attack in pokemon_attacks:
                        pokemon_info += f"- {attack}\n"
                    pokemon_info += "\n"
                    pokemon_info_complete_text += pokemon_info

                    # Create labels to display the text
                    #label = QLabel(pokemon_info_complete_text)
                    # Align labels
                    #label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align center
                    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align center

                    # Create an input field for error code
                    error_code_input = QLineEdit()
                    error_code_input.setPlaceholderText("Enter Error Code")

                    # Create a button to save the input
                    save_button = QPushButton("Fix Pokemon Export Code")

                    # Create a layout and add the labels, input field, and button
                    layout = QVBoxLayout()
                    layout.addWidget(info_label)
                    #layout.addWidget(label)
                    layout.addWidget(error_code_input)
                    layout.addWidget(save_button)

                    # Copy text to clipboard in Anki
                    mw.app.clipboard().setText(pokemon_info_complete_text)

        save_button.clicked.connect(lambda: save_error_code(error_code_input.text(), logger=logger))

        # Set the layout for the main window
        export_window.setLayout(layout)

        export_window.exec()
    except Exception as e:
        show_warning_with_traceback(exception=e, message="An error occurred:")

def flex_pokemon_collection():
    # Create a main window
    export_window = QDialog()
    #export_window.setWindowTitle("Export Pokemon to Pkmn Showdown")

    # Information label
    info = "Pokemon Infos have been Copied to your Clipboard! \nNow simply paste this text into https://pokepast.es/.\nAfter pasting the infos in your clipboard and submitting the needed infos on the right,\n you will receive a link to send friends to flex."
    info_label = QLabel(info)

# Get all pokemon data
    pokemon_info_complete_text = ""
    try:
        with (open(mypokemon_path, "r", encoding="utf-8") as json_file):
            captured_pokemon_data = json.load(json_file)

            # Check if there are any captured Pokémon
            if captured_pokemon_data:
                # Counter for tracking the column position
                column = 0
                row = 0
                for pokemon in captured_pokemon_data:
                    pokemon_name = pokemon['name']
                    pokemon_level = pokemon['level']
                    pokemon_ability = pokemon['ability']
                    pokemon_type = pokemon['type']
                    pokemon_type_text = pokemon_type[0].capitalize()
                    if len(pokemon_type) > 1:
                        pokemon_type_text = ""
                        pokemon_type_text += f"{pokemon_type[0].capitalize()}"
                        pokemon_type_text += f" {pokemon_type[1].capitalize()}"
                    pokemon_stats = pokemon['stats']
                    pokemon_hp = pokemon_stats["hp"]
                    pokemon_attacks = pokemon['attacks']
                    pokemon_ev = pokemon['ev']
                    pokemon_iv = pokemon['iv']

                    pokemon_info = POKEMON_INFO_FORMAT.format(
                        pokemon_name,
                        pokemon_ability.capitalize(),
                        pokemon_level,
                        pokemon_type_text,
                        pokemon_ev["hp"],
                        pokemon_ev["atk"],
                        pokemon_ev["def"],
                        pokemon_ev["spa"],
                        pokemon_ev["spd"],
                        pokemon_ev["spe"],
                        pokemon_iv["hp"],
                        pokemon_iv["atk"],
                        pokemon_iv["def"],
                        pokemon_iv["spa"],
                        pokemon_iv["spd"],
                        pokemon_iv["spe"]
                    )
                    for attack in pokemon_attacks:
                        pokemon_info += f"- {attack}\n"
                    pokemon_info += "\n"
                    pokemon_info_complete_text += pokemon_info

                    # Create labels to display the text
                    #label = QLabel(pokemon_info_complete_text)
                    # Align labels
                    #label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align center
                    info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align center

                    # Create a layout and add the labels, input field, and button
                    layout = QVBoxLayout()
                    layout.addWidget(info_label)
                    #layout.addWidget(label)

                    # Copy text to clipboard in Anki
                    mw.app.clipboard().setText(pokemon_info_complete_text)
        #save_button.clicked.connect(lambda: save_error_code(error_code_input.text()))
        # Set the layout for the main window
        open_browser_for_pokepaste = QPushButton("Open Pokepaste")
        open_browser_for_pokepaste.clicked.connect(open_browser_window)
        layout.addWidget(open_browser_for_pokepaste)

        export_window.setLayout(layout)

        export_window.exec()
    except Exception as e:
        show_warning_with_traceback(exception=e, message="An error occurred:")
