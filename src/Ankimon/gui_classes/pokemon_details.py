from ..functions.pokedex_functions import get_pokemon_diff_lang_name, get_pokemon_descriptions, get_all_pokemon_moves
from ..functions.pokemon_functions import find_experience_for_level
from aqt import mw
from aqt.utils import showWarning
from ..resources import (frontdefault, user_path_sprites, icon_path, addon_dir, mainpokemon_path, mypokemon_path)
from ..texts import attack_details_window_template, attack_details_window_template_end, remember_attack_details_window_template, remember_attack_details_window_template_end
from PyQt6.QtGui import QPixmap, QPainter, QIcon
from ..gui_entities import MovieSplashLabel
from ..business import split_string_by_length
from ..utils import load_custom_font
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QWidget
from aqt import qconnect
from ..functions.pokedex_functions import find_details_move
from ..functions.gui_functions import type_icon_path, move_category_path
import json
from ..pyobj.attack_dialog import AttackDialog
from ..pyobj.pokemon_trade import PokemonTrade
from ..functions.sprite_functions import get_sprite_path

def PokemonCollectionDetails(name, level, id, shiny, ability, type, detail_stats, attacks, base_experience, growth_rate, ev, iv, gender, nickname, individual_id, pokemon_defeated, everstone, captured_date, language, gif_in_collection, remove_levelcap, logger, refresh_callback):
    try:
        lang_name = get_pokemon_diff_lang_name(int(id), language).capitalize()
        lang_desc = get_pokemon_descriptions(int(id), language)
        description = lang_desc
        
        # Create a widget instead of a dialog
        details_widget = QWidget()
        
        # Create a layout for the widget
        layout = QVBoxLayout()
        typelayout = QHBoxLayout()
        attackslayout = QVBoxLayout()

        # Display the Pokémon image
        pkmnimage_label = QLabel()
        pkmnpixmap = QPixmap()
        pkmnimage_path = get_sprite_path("front", "gif" if gif_in_collection else "png", id, shiny, gender)

        if gif_in_collection:
            pkmnimage_label = MovieSplashLabel(pkmnimage_path)
        else:
            pkmnpixmap.load(str(pkmnimage_path))
            max_width = 150
            original_width = pkmnpixmap.width()
            original_height = pkmnpixmap.height()
            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pkmnpixmap = pkmnpixmap.scaled(new_width, new_height)

        typeimage_file = f"{type[0]}.png"
        typeimage_path = addon_dir / "addon_sprites" / "Types" / typeimage_file
        pkmntype_label = QLabel()
        pkmntypepixmap = QPixmap()
        pkmntypepixmap.load(str(typeimage_path))
        if len(type) > 1:
            type_image_file2 = f"{type[1]}.png"
            typeimage_path2 = addon_dir / "addon_sprites" / "Types" / type_image_file2
            pkmntype_label2 = QLabel()
            pkmntypepixmap2 = QPixmap()
            pkmntypepixmap2.load(str(typeimage_path2))

        # Custom font
        custom_font = load_custom_font(int(20), language)
        namefont = load_custom_font(int(30), language)
        namefont.setUnderline(True)

        # Capitalize the Pokémon's name
        if nickname is None:
            capitalized_name = f"{lang_name.capitalize()} {' ⭐ ' if shiny else ''}"
        else:
            capitalized_name = f"{nickname} {' ⭐ ' if shiny else ''} ({lang_name.capitalize()})"

        if language in [1, 2, 3, 4, 11, 12]:
            result = list(split_string_by_length(description, 30))
        else:
            result = list(split_string_by_length(description, 55))
        description_formated = '\n'.join(result)
        description_txt = f"Description: \n {description_formated}"
        growth_rate_txt = f"Growth Rate: {growth_rate.capitalize()}"
        lvl = f"Level: {level}"
        ability_txt = f"Ability: {ability.capitalize()}"
        type_txt = "Type:"
        stats_txt = f"Stats:\nHp: {detail_stats['hp']}\nAttack: {detail_stats['atk']}\nDefense: {detail_stats['def']}\nSpecial-attack: {detail_stats['spa']}\nSpecial-defense: {detail_stats['spd']}\nSpeed: {detail_stats['spe']}\nXP: {detail_stats['xp']}"
        attacks_txt = "Moves:"
        for attack in attacks:
            attacks_txt += f"\n{attack.capitalize()}"

        CompleteTable_layout = PokemonDetailsStats(detail_stats, growth_rate, level, remove_levelcap, language)

        # Convert gender to symbol
        gender_symbol = "♂" if gender == "M" else "♀" if gender == "F" else ""

        # Create labels
        name_label = QLabel(f"{capitalized_name} - {gender_symbol}")
        name_label.setFont(namefont)
        description_label = QLabel(description_txt)
        level_label = QLabel(lvl)
        growth_rate_label = QLabel(growth_rate_txt)
        base_exp_label = QLabel(f"Base XP: {base_experience}")
        ability_label = QLabel(ability_txt)
        attacks_label = QLabel(attacks_txt)
        type_label = QLabel(type_txt)

        level_label.setFont(custom_font)
        base_exp_label.setFont(custom_font)
        type_label.setFont(custom_font)
        ability_label.setFont(custom_font)
        attacks_label.setFont(custom_font)
        growth_rate_label.setFont(custom_font)
        description_font = load_custom_font(20 if language == 1 else 15, language)
        description_label.setFont(description_font)

        # Set pixmaps
        if not gif_in_collection:
            pkmnimage_label.setPixmap(pkmnpixmap)
        pkmntype_label.setPixmap(pkmntypepixmap)
        if len(type) > 1:
            pkmntype_label2.setPixmap(pkmntypepixmap2)

        # Styling
        level_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        base_exp_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        ability_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        growth_rate_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        type_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        pkmntype_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        if len(type) > 1:
            pkmntype_label2.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        level_label.setFixedWidth(230)
        growth_rate_label.setFixedWidth(230)
        base_exp_label.setFixedWidth(230)
        pkmnimage_label.setFixedHeight(100)
        ability_label.setFixedWidth(230)
        attacks_label.setFixedWidth(230)

        # Layouts
        first_layout = QHBoxLayout()
        TopR_layout_Box = QVBoxLayout()
        TopL_layout_Box = QVBoxLayout()
        typelayout_widget = QWidget()

        TopL_layout_Box.addWidget(level_label)
        TopL_layout_Box.addWidget(pkmnimage_label)
        typelayout.addWidget(type_label)
        typelayout.addWidget(pkmntype_label)
        pkmntype_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if len(type) > 1:
            typelayout.addWidget(pkmntype_label2)
            pkmntype_label2.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        typelayout_widget.setLayout(typelayout)
        typelayout_widget.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        typelayout_widget.setFixedWidth(230)
        TopL_layout_Box.addWidget(typelayout_widget)
        TopL_layout_Box.addWidget(ability_label)

        # Additional labels
        pokemon_defeated_label = QLabel(f"Pokemon Defeated: {pokemon_defeated}")
        pokemon_defeated_label.setFont(load_custom_font(15, language))
        everstone_label = QLabel(f"Everstone: {everstone}")
        everstone_label.setFont(load_custom_font(15, language))
        captured_date_label = QLabel(f"Captured: {captured_date}")
        captured_date_label.setFont(load_custom_font(15, language))

        # Buttons
        attacks_details_button = QPushButton("Attack Details")
        qconnect(attacks_details_button.clicked, lambda: attack_details_window(attacks))
        remember_attacks_details_button = QPushButton("Remember Attacks")
        all_attacks = get_all_pokemon_moves(name, level)
        qconnect(remember_attacks_details_button.clicked, lambda: remember_attack_details_window(id, attacks, all_attacks, logger))
        forget_attacks_details_button = QPushButton("Forget Attacks")
        qconnect(forget_attacks_details_button.clicked, lambda: forget_attack_details_window(id, attacks, logger))
        trade_pokemon_button = QPushButton("Trade Pokemon")
        qconnect(trade_pokemon_button.clicked, lambda: PokemonTrade(name, id, level, ability, iv, ev, gender, attacks, individual_id, logger, refresh_callback))
        free_pokemon_button = QPushButton("Release Pokemon")
        qconnect(free_pokemon_button.clicked, lambda: PokemonFree(individual_id, name, logger, refresh_callback))
        rename_button = QPushButton("Rename Pokemon")
        rename_input = QLineEdit()
        rename_input.setPlaceholderText("Enter a new Nickname for your Pokemon")
        qconnect(rename_button.clicked, lambda: rename_pkmn(rename_input.text(), name, individual_id, logger, refresh_callback))

        # Right layout
        attacks_label.setFixedHeight(150)
        TopR_layout_Box.addWidget(attacks_label)
        TopR_layout_Box.addWidget(attacks_details_button)
        TopR_layout_Box.addWidget(remember_attacks_details_button)
        TopR_layout_Box.addWidget(forget_attacks_details_button)
        TopR_layout_Box.addWidget(captured_date_label)
        TopR_layout_Box.addWidget(pokemon_defeated_label)
        TopR_layout_Box.addWidget(everstone_label)

        first_layout.addLayout(TopL_layout_Box)
        first_layout.addLayout(TopR_layout_Box)

        # Add to main layout
        layout.addWidget(name_label)
        layout.addLayout(first_layout)
        layout.addWidget(description_label)
        statstablelayout = QWidget()
        statstablelayout.setLayout(CompleteTable_layout)
        layout.addWidget(statstablelayout)
        statstablelayout.setStyleSheet("border: 2px solid white; padding: 5px;")
        statstablelayout.setFixedHeight(200)
        layout.addWidget(trade_pokemon_button)
        layout.addWidget(free_pokemon_button)
        layout.addWidget(rename_input)
        layout.addWidget(rename_button)

        # Alignments
        pkmnimage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        growth_rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        base_exp_label.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter)
        pkmntype_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ability_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        attacks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        attacks_label.setStyleSheet("border: 2px solid white; padding: 5px;")

        # Set the layout for the widget
        details_widget.setLayout(layout)
        return details_widget

    except Exception as e:
        showWarning(f"Error occurred in Pokemon Details: {e}")
        return QWidget()  # Return an empty widget on error

# Remaining functions (PokemonDetailsStats, createStatBar, attack_details_window, etc.) remain unchanged
def PokemonDetailsStats(detail_stats, growth_rate, level, remove_levelcap, language):
    CompleteTable_layout = QVBoxLayout()
    experience = int(find_experience_for_level(growth_rate, level, remove_levelcap))
    stat_colors = {
        "hp": QColor(255, 0, 0),
        "atk": QColor(255, 165, 0),
        "def": QColor(255, 255, 0),
        "spa": QColor(0, 0, 255),
        "spd": QColor(0, 128, 0),
        "spe": QColor(255, 192, 203),
        "total": QColor(168, 168, 167),
        "xp": QColor(58, 155, 220),
        "current_hp": QColor(200, 0, 0),
        "max_hp": QColor(255, 0, 0)
    }
    custom_font = load_custom_font(int(20), language)
    for row, (stat, value) in enumerate(detail_stats.items()):
        if stat not in stat_colors:
            continue
        stat_item2 = QLabel(stat.capitalize())
        max_width_stat_item = 200
        stat_item2.setFixedWidth(max_width_stat_item)
        if stat == "xp":
            xp = value
            value = int((int(value) / int(experience)) * max_width_stat_item)
        value_item2 = QLabel(str(value))
        if stat == "xp":
            value_item2 = QLabel(str(xp))
        stat_item2.setFont(custom_font)
        value_item2.setFont(custom_font)
        bar_item2 = QLabel()
        pixmap2 = createStatBar(stat_colors[stat], value)
        icon = QIcon(pixmap2)
        bar_item2.setPixmap(icon.pixmap(200, 10))
        layout_row = QHBoxLayout()
        layout_row.addWidget(stat_item2)
        layout_row.addWidget(value_item2)
        layout_row.addWidget(bar_item2)
        stat_item2.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        bar_item2.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        value_item2.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        stat_item2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bar_item2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        CompleteTable_layout.addLayout(layout_row)
    return CompleteTable_layout

def createStatBar(color, value):
    pixmap = QPixmap(200, 10)
    pixmap.fill(QColor(0, 0, 0, 0))
    if color is None:
        color = QColor(128, 128, 128)
    painter = QPainter(pixmap)
    painter.setPen(QColor(Qt.GlobalColor.black))
    painter.setBrush(QColor(0, 0, 0, 200))
    painter.drawRect(0, 0, 200, 10)
    painter.setBrush(color)
    painter.drawRect(0, 0, int(value * 1), 10)
    painter.end()
    return pixmap

def attack_details_window(attacks):
    window = QDialog()
    window.setWindowIcon(QIcon(str(icon_path)))
    layout = QVBoxLayout()
    html_content = attack_details_window_template
    for attack in attacks:
        move = find_details_move(attack)
        if move is None:
            attack = attack.replace(" ", "")
            try:
                move = find_details_move(attack)
            except:
                logger.log_and_showinfo("info", f"Can't find the attack {attack} in the database.")
                move = find_details_move("tackle")
        html_content += f"""
        <tr>
          <td class="move-name">{move['name']}</td>
          <td><img src="{type_icon_path(move['type'])}" alt="{move['type']}"/></td>
          <td><img src="{move_category_path(move['category'].lower())}" alt="{move['category']}"/></td>
          <td class="basePower">{move['basePower']}</td>
          <td class="no-accuracy">{move['accuracy']}</td>
          <td>{move['pp']}</td>
          <td>{move['shortDesc']}</td>
        </tr>
        """
    html_content += attack_details_window_template_end
    label = QLabel(html_content)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    label.setScaledContents(True)
    layout.addWidget(label)
    window.setLayout(layout)
    window.exec()

def remember_attack_details_window(id, attack_set, all_attacks, logger):
    window = QDialog()
    window.setWindowIcon(QIcon(str(icon_path)))
    window.setWindowTitle("Remember Attacks")
    outer_layout = QVBoxLayout(window)
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    content_widget = QWidget()
    layout = QHBoxLayout(content_widget)
    html_content = remember_attack_details_window_template
    for attack in all_attacks:
        move = find_details_move(attack)
        html_content += f"""
        <tr>
          <td class="move-name">{move['name']}</td>
          <td><img src="{type_icon_path(move['type'])}" alt="{move['type']}"/></td>
          <td><img src="{move_category_path(move['category'].lower())}" alt="{move['category']}"/></td>
          <td class="basePower">{move['basePower']}</td>
          <td class="no-accuracy">{move['accuracy']}</td>
          <td>{move['pp']}</td>
          <td>{move['shortDesc']}</td>
        </tr>
        """
    html_content += remember_attack_details_window_template_end
    label = QLabel(html_content)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    label.setScaledContents(True)
    attack_layout = QVBoxLayout()
    for attack in all_attacks:
        move = find_details_move(attack)
        remember_attack_button = QPushButton(f"Remember {attack}")
        remember_attack_button.clicked.connect(lambda checked, a=attack: remember_attack(id, attack_set, a, logger))
        attack_layout.addWidget(remember_attack_button)
    attack_layout_widget = QWidget()
    attack_layout_widget.setLayout(attack_layout)
    layout.addWidget(label)
    layout.addWidget(attack_layout_widget)
    scroll_area.setWidget(content_widget)
    outer_layout.addWidget(scroll_area)
    window.setLayout(outer_layout)
    window.resize(1000, 400)
    window.exec()

def forget_attack_details_window(id, attack_set, logger):
    window = QDialog()
    window.setWindowIcon(QIcon(str(icon_path)))
    window.setWindowTitle("Forget Attacks")
    outer_layout = QVBoxLayout(window)
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    content_widget = QWidget()
    layout = QHBoxLayout(content_widget)
    html_content = remember_attack_details_window_template
    for attack in attack_set:
        move = find_details_move(attack)
        html_content += f"""
        <tr>
          <td class="move-name">{move['name']}</td>
          <td><img src="{type_icon_path(move['type'])}" alt="{move['type']}"/></td>
          <td><img src="{move_category_path(move['category'].lower())}" alt="{move['category']}"/></td>
          <td class="basePower">{move['basePower']}</td>
          <td class="no-accuracy">{move['accuracy']}</td>
          <td>{move['pp']}</td>
          <td>{move['shortDesc']}</td>
        </tr>
        """
    html_content += remember_attack_details_window_template_end
    label = QLabel(html_content)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    label.setScaledContents(True)
    attack_layout = QVBoxLayout()
    for attack in attack_set:
        move = find_details_move(attack)
        forget_attack_button = QPushButton(f"Forget {attack}")
        forget_attack_button.clicked.connect(lambda checked, a=attack: forget_attack(id, attack_set, a, logger))
        attack_layout.addWidget(forget_attack_button)
    attack_layout_widget = QWidget()
    attack_layout_widget.setLayout(attack_layout)
    layout.addWidget(label)
    layout.addWidget(attack_layout_widget)
    scroll_area.setWidget(content_widget)
    outer_layout.addWidget(scroll_area)
    window.setLayout(outer_layout)
    window.resize(1000, 400)
    window.exec()

def remember_attack(id, attacks, new_attack, logger):
    if new_attack in attacks:
        logger.log_and_showinfo("warning", "Your pokemon already knows this move!")
        return
    if not mainpokemon_path.is_file():
        logger.log_and_showinfo("warning", "Missing Mainpokemon Data !")
        return
    with open(mainpokemon_path, "r", encoding="utf-8") as json_file:
        main_pokemon_data = json.load(json_file)
    for mainpkmndata in main_pokemon_data:
        if mainpkmndata["id"] == id:
            mainpokemon_name = mainpkmndata["name"]
            attacks = mainpkmndata["attacks"]
            if new_attack:
                msg = f"Your {mainpkmndata['name'].capitalize()} can learn a new attack !"
                if len(attacks) < 4:
                    attacks.append(new_attack)
                    msg += f"\n Your {mainpkmndata['name'].capitalize()} has learned {new_attack} !"
                    logger.log_and_showinfo("info", f"{msg}")
                else:
                    dialog = AttackDialog(attacks, new_attack)
                    if dialog.exec() == QDialog.DialogCode.Accepted:
                        selected_attack = dialog.selected_attack
                        index_to_replace = None
                        for index, attack in enumerate(attacks):
                            if attack == selected_attack:
                                index_to_replace = index
                                break
                        if index_to_replace is not None:
                            attacks[index_to_replace] = new_attack
                            logger.log_and_showinfo("info", f"Replaced '{selected_attack}' with '{new_attack}'")
                        else:
                            logger.log_and_showinfo("info", f"{new_attack} will be discarded.")
            mainpkmndata["attacks"] = attacks
            mypkmndata = mainpkmndata
            mainpkmndata = [mainpkmndata]
            with open(str(mainpokemon_path), "w") as json_file:
                json.dump(mainpkmndata, json_file, indent=2)
            with open(str(mypokemon_path), "r", encoding="utf-8") as output_file:
                mypokemondata = json.load(output_file)
            for index, pokemon_data in enumerate(mypokemondata):
                if pokemon_data["name"] == mainpokemon_name:
                    mypokemondata[index] = mypkmndata
                    break
            with open(str(mypokemon_path), "w") as output_file:
                json.dump(mypokemondata, output_file, indent=2)
        else:
            logger.log_and_showinfo("info", "Please Select this Pokemon first as Main Pokemon ! \n Only Mainpokemons can re-learn attacks!")

def forget_attack(id, attacks, attack_to_forget, logger):
    if not mainpokemon_path.is_file():
        logger.log_and_showinfo("warning", "Missing Mainpokemon Data !")
        return
    with open(mainpokemon_path, "r", encoding="utf-8") as json_file:
        main_pokemon_data = json.load(json_file)
    for mainpkmndata in main_pokemon_data:
        if mainpkmndata["id"] == id:
            mainpokemon_name = mainpkmndata["name"]
            attacks = mainpkmndata["attacks"]
            if attack_to_forget:
                if attack_to_forget in attacks:
                    if len(attacks) > 1:
                        attacks.remove(attack_to_forget)
                        msg = f"Your {mainpkmndata['name'].capitalize()} forgot {attack_to_forget}."
                        logger.log_and_showinfo("info", f"{msg}")
                    else:
                        msg = f"Your {mainpkmndata['name'].capitalize()} only knows this move, you can't forget it !"
                        logger.log_and_showinfo("info", f"{msg}")
                else:
                    msg = f"Your {mainpkmndata['name'].capitalize()} does not know {attack_to_forget}."
                    logger.log_and_showinfo("info", f"{msg}")
            mainpkmndata["attacks"] = attacks
            mypkmndata = mainpkmndata
            mainpkmndata = [mainpkmndata]
            with open(str(mainpokemon_path), "w") as json_file:
                json.dump(mainpkmndata, json_file, indent=2)
            with open(str(mypokemon_path), "r", encoding="utf-8") as output_file:
                mypokemondata = json.load(output_file)
            for index, pokemon_data in enumerate(mypokemondata):
                if pokemon_data["name"] == mainpokemon_name:
                    mypokemondata[index] = mypkmndata
                    break
            with open(str(mypokemon_path), "w") as output_file:
                json.dump(mypokemondata, output_file, indent=2)
        else:
            logger.log_and_showinfo("info", "Please Select this Pokemon first as Main Pokemon ! \n Only Mainpokemons can forget attacks!")

def rename_pkmn(nickname, pkmn_name, individual_id, logger, refresh_callback):
    try:
        with open(mypokemon_path, "r", encoding="utf-8") as json_file:
            captured_pokemon_data = json.load(json_file)
            pokemon = None
            for index, pokemon_data in enumerate(captured_pokemon_data):
                if pokemon_data["individual_id"] == individual_id:
                    pokemon = pokemon_data
                    break
            if pokemon is not None:
                pokemon["nickname"] = nickname
                with open(str(mypokemon_path), "r", encoding="utf-8") as output_file:
                    mypokemondata = json.load(output_file)
                for idx, data in enumerate(mypokemondata):
                    if data["individual_id"] == individual_id:
                        mypokemondata[idx] = pokemon
                        break
                with open(str(mypokemon_path), "w") as output_file:
                    json.dump(mypokemondata, output_file, indent=2)
                logger.log_and_showinfo("info", f"Your {pkmn_name.capitalize()} has been renamed to {nickname}!")
                refresh_callback()
            else:
                showWarning("Pokémon not found.")
    except Exception as e:
        showWarning(f"An error occurred: {e}")

def PokemonFree(individual_id, name, logger, refresh_callback):
    reply = QMessageBox.question(
        None, 
        "Confirm Release", 
        f"Are you sure you want to release {name}?", 
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
        QMessageBox.StandardButton.No
    )
    if reply == QMessageBox.StandardButton.No:
        logger.log_and_showinfo("info", "Release cancelled.")
        return
    with open(mainpokemon_path, "r", encoding="utf-8") as file:
        pokemon_data = json.load(file)
    for pokemon in pokemon_data:
        if pokemon["individual_id"] == individual_id:
            logger.log_and_showinfo("info", "You can't free your Main Pokémon!")
            return
    try:
        with open(mypokemon_path, "r", encoding="utf-8") as file:
            pokemon_list = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.log_and_showinfo("info", "Error: Could not load Pokémon data.")
        return
    position = -1
    for idx, pokemon in enumerate(pokemon_list):
        if pokemon.get("individual_id") == individual_id:
            position = idx
            break
    if position != -1:
        pokemon_list.pop(position)
        with open(mypokemon_path, 'w') as file:
            json.dump(pokemon_list, file, indent=2)
        logger.log_and_showinfo("info", f"{name.capitalize()} has been let free.")
    else:
        logger.log_and_showinfo("info", "No Pokémon found with the specified ID.")
    refresh_callback()