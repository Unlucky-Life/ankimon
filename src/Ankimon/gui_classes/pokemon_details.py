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

def PokemonCollectionDetails(name, level, id, ability, type, detail_stats, attacks, base_experience, growth_rate, ev, iv, gender, nickname, individual_id, language, gif_in_collection, remove_levelcap, logger, refresh_callback):
    # Create the dialog
    try:
        lang_name = get_pokemon_diff_lang_name(int(id), language).capitalize()
        lang_desc = get_pokemon_descriptions(int(id), language)
        description = lang_desc
        wpkmn_details = QDialog(mw)
        if nickname is None:
            wpkmn_details.setWindowTitle(f"Infos to : {lang_name} ")
        else:
            wpkmn_details.setWindowTitle(f"Infos to : {nickname} ({lang_name}) ")

        wpkmn_details.setFixedWidth(500)
        wpkmn_details.setMaximumHeight(400)

        # Create a layout for the dialog
        layout = QVBoxLayout()
        typelayout = QHBoxLayout()
        attackslayout = QVBoxLayout()
        # Display the Pokémon image
        pkmnimage_label = QLabel()
        pkmnpixmap = QPixmap()
        if gif_in_collection is True:
            pkmnimage_path = str(user_path_sprites / "front_default_gif" / f"{int(id)}.gif")
            pkmnimage_label = MovieSplashLabel(pkmnimage_path)
        else:
            pkmnimage_path = str(frontdefault / f"{int(id)}.png")
            pkmnpixmap.load(str(pkmnimage_path))
            # Calculate the new dimensions to maintain the aspect ratio
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
        

        # Create a painter to add text on top of the image
        painter2 = QPainter(pkmnpixmap)

        #custom font
        custom_font = load_custom_font(int(20), language)

        # Capitalize the first letter of the Pokémon's name
        if nickname is None:
            capitalized_name = f"{lang_name.capitalize()}"
        else:
            capitalized_name = f"{nickname} ({lang_name.capitalize()})"
        # Create level text
        if (
            language == 11
            or language == 12
            or language == 4
            or language == 3
            or language == 2
            or language == 1
        ):
            result = list(split_string_by_length(description, 30))
        else:
            result = list(split_string_by_length(description, 55))
        description_formated = '\n'.join(result)
        description_txt = f"Description: \n {description_formated}"
        growth_rate_txt = (f"Growth Rate: {growth_rate.capitalize()}")
        lvl = (f" Level: {level}")
        ability_txt = (f" Ability: {ability.capitalize()}")
        type_txt = (f" Type:")
        stats_list = [
            detail_stats["hp"],
            detail_stats["atk"],
            detail_stats["def"],
            detail_stats["spa"],
            detail_stats["spd"],
            detail_stats["spe"],
            detail_stats["xp"]
        ]
        stats_txt = f"Stats:\n\
            Hp: {stats_list[0]}\n\
            Attack: {stats_list[1]}\n\
            Defense: {stats_list[2]}\n\
            Special-attack: {stats_list[3]}\n\
            Special-defense: {stats_list[4]}\n\
            Speed: {stats_list[5]}\n\
            XP: {stats_list[6]}"
        attacks_txt = "Moves:"
        for attack in attacks:
            attacks_txt += f"\n{attack.capitalize()}"

        CompleteTable_layout = PokemonDetailsStats(detail_stats, growth_rate, level, remove_levelcap, language)

        # Properties of the text of the image
        # custom font
        namefont = load_custom_font(int(30), language)
        namefont.setUnderline(True)
        painter2.setFont(namefont)
        font = load_custom_font(int(20), language)
        painter2.end()

        # Convert gender name to symbol - this function is from Foxy-null
        if gender == "M":
            gender_symbol = "♂"
        elif gender == "F":
            gender_symbol = "♀"
        elif gender == "N":
            gender_symbol = ""
        else:
            gender_symbol = ""  # None

        # Create a QLabel for the capitalized name
        name_label = QLabel(f"{capitalized_name} - {gender_symbol}")
        name_label.setFont(namefont)
        # Create a QLabel for the level
        description_label = QLabel(description_txt)
        level_label = QLabel(lvl)
        growth_rate_label = QLabel(growth_rate_txt)
        base_exp_label = QLabel(f"Base XP: {base_experience}")
        # Align to the center
        level_label.setFont(font)
        base_exp_label.setFont(font)
        type_label= QLabel("Type:")
        type_label.setFont(font)
        # Create a QLabel for the level
        ability_label = QLabel(ability_txt)
        ability_label.setFont(font)
        attacks_label = QLabel(attacks_txt)
        attacks_label.setFont(font)
        growth_rate_label.setFont(font)
        if language == 1:
            description_font = load_custom_font(int(20), language)
        else:
            description_font = load_custom_font(int(15), language)
        description_label.setFont(description_font)
        #stats_label = QLabel(stats_txt)

        # Set the merged image as the pixmap for the QLabel
        if gif_in_collection is False:
            pkmnimage_label.setPixmap(pkmnpixmap)
        # Set the merged image as the pixmap for the QLabel
        pkmntype_label.setPixmap(pkmntypepixmap)
        if len(type) > 1:
            pkmntype_label2.setPixmap(pkmntypepixmap2)
        #Border
        #description_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        level_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        base_exp_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        ability_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        growth_rate_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        type_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        level_label.setFixedWidth(230)
        growth_rate_label.setFixedWidth(230)
        base_exp_label.setFixedWidth(230)
        pkmnimage_label.setFixedHeight(100)
        ability_label.setFixedWidth(230)
        attacks_label.setFixedWidth(230)
        first_layout = QHBoxLayout() #Top Image Left and Direkt Info Right
        TopR_layout_Box = QVBoxLayout() #Top Right Info Direkt Layout
        TopL_layout_Box = QVBoxLayout() #Top Left Pokemon and Direkt Info Layout
        typelayout_widget = QWidget()
        TopL_layout_Box.addWidget(level_label)
        TopL_layout_Box.addWidget(pkmnimage_label)

        TopFirstLayout = QWidget()
        TopFirstLayout.setLayout(first_layout)
        layout.addWidget(name_label)
        layout.addWidget(TopFirstLayout)
        layout.addWidget(description_label)
        #.addWidget(growth_rate_label)
        #.addWidget(base_exp_label)
        typelayout.addWidget(type_label)
        typelayout.addWidget(pkmntype_label)
        pkmntype_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pkmntype_label.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        if len(type) > 1:
            typelayout.addWidget(pkmntype_label2)
            pkmntype_label2.setStyleSheet("border: 0px solid #000000; padding: 0px;")
            pkmntype_label2.setAlignment(Qt.AlignmentFlag.AlignLeft)
            pkmntype_label2.setAlignment(Qt.AlignmentFlag.AlignBottom)
        typelayout_widget.setLayout(typelayout)
        typelayout_widget.setStyleSheet("border: 0px solid #000000; padding: 0px;")
        typelayout_widget.setFixedWidth(230)
        TopL_layout_Box.addWidget(typelayout_widget)
        TopL_layout_Box.addWidget(ability_label)
        #attackslayout.addWidget(attacks_label)
        attacks_details_button = QPushButton("Attack Details") #add Details to Moves
        qconnect(attacks_details_button.clicked, lambda: attack_details_window(attacks))
        remember_attacks_details_button = QPushButton("Remember Attacks") #add Details to Moves
        all_attacks = get_all_pokemon_moves(name, level)
        qconnect(remember_attacks_details_button.clicked, lambda: remember_attack_details_window(id, attacks, all_attacks, logger))
        
        #free_pokemon_button = QPushButton("Release Pokemon") #add Details to Moves unneeded button
        attacks_label.setFixedHeight(150)
        TopR_layout_Box.addWidget(attacks_label)
        TopR_layout_Box.addWidget(attacks_details_button)
        TopR_layout_Box.addWidget(remember_attacks_details_button)
        first_layout.addLayout(TopL_layout_Box)
        first_layout.addLayout(TopR_layout_Box)
        layout.addLayout(first_layout)
        attacks_label.setStyleSheet("border: 2px solid white; padding: 5px;")
        #TopR_layout_Box.setStyleSheet("border: 2px solid white; padding: 5px;")
        statstablelayout = QWidget()
        statstablelayout.setLayout(CompleteTable_layout)
        layout.addWidget(statstablelayout)
        statstablelayout.setStyleSheet("border: 2px solid white; padding: 5px;")
        #statstablelayout.setFixedWidth(350)
        statstablelayout.setFixedHeight(200)
        free_pokemon_button = QPushButton("Release Pokemon") #add Details to Moves
        qconnect(free_pokemon_button.clicked, lambda: PokemonFree(individual_id, name, logger, refresh_callback))
        trade_pokemon_button = QPushButton("Trade Pokemon") #add Details to Moves
        qconnect(trade_pokemon_button.clicked, lambda: PokemonTrade(name, id, level, ability, iv, ev, gender, attacks, individual_id, logger, refresh_callback))
        layout.addWidget(trade_pokemon_button)
        layout.addWidget(free_pokemon_button)
        rename_button = QPushButton("Rename Pokemon") #add Details to Moves
        rename_input = QLineEdit()
        rename_input.setPlaceholderText("Enter a new Nickname for your Pokemon")
        qconnect(rename_button.clicked, lambda: rename_pkmn(rename_input.text(),name, individual_id, logger, refresh_callback))
        layout.addWidget(rename_input)
        layout.addWidget(rename_button)
        #qconnect()
        #layout.addLayout(CompleteTable_layout)

        #wpkmn_details.setFixedWidth(500)
        #wpkmn_details.setMaximumHeight(600)

        # align things needed to middle
        pkmnimage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        growth_rate_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        base_exp_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        base_exp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pkmntype_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        pkmntype_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        type_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align to the center
        ability_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        attacks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set the layout for the dialog
        wpkmn_details.setLayout(layout)

        # Show the dialog
        wpkmn_details.setWindowIcon(QIcon(str(icon_path))) # Add a Pokeball icon
        # Show the dialog
        wpkmn_details.exec()
    except Exception as e:
        showWarning(f"Error occured in Pokemon Details Button: {e}")


def PokemonDetailsStats(detail_stats, growth_rate, level, remove_levelcap, language):
    CompleteTable_layout = QVBoxLayout()
    experience = int(find_experience_for_level(growth_rate, level, remove_levelcap))
    # Stat colors
    stat_colors = {
        "hp": QColor(255, 0, 0),  # Red
        "atk": QColor(255, 165, 0),  # Orange
        "def": QColor(255, 255, 0),  # Yellow
        "spa": QColor(0, 0, 255),  # Blue
        "spd": QColor(0, 128, 0),  # Green
        "spe": QColor(255, 192, 203),  # Pink
        "total": QColor(168, 168, 167),  # Beige
        "xp": QColor(58,155,220)  # lightblue
    }

    #custom font
    custom_font = load_custom_font(int(20), language)

    # Populate the table and create the stat bars
    for row, (stat, value) in enumerate(detail_stats.items()):
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
        # Create a bar item
        bar_item2 = QLabel()
        pixmap2 = createStatBar(stat_colors.get(stat), value)
        # Convert the QPixmap to an QIcon
        icon = QIcon(pixmap2)
        # Set the QIcon as the background for the QLabel
        bar_item2.setPixmap(icon.pixmap(200, 10))  # Adjust the size as needed
        layout_row = str(f"{row}" + "row")
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
    #pixmap.fill(Qt.transparent)
    pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
    painter = QPainter(pixmap)

    # Draw bar in the background
    painter.setPen(QColor(Qt.GlobalColor.black))
    # new change due to pyqt6.6.1
    painter.setBrush(QColor(0, 0, 0, 200))  # Semi-transparent black
    painter.drawRect(0, 0, 200, 10)

    # Draw the colored bar based on the value
    painter.setBrush(color)
    bar_width = int(value * 1)  # Adjust the width as needed
    painter.drawRect(0, 0, bar_width, 10)

    return pixmap

def attack_details_window(attacks):
    window = QDialog()
    window.setWindowIcon(QIcon(str(icon_path)))
    layout = QVBoxLayout()
    # HTML content
    html_content = attack_details_window_template
    # Loop through the list of attacks and add them to the HTML content
    for attack in attacks:
        move = find_details_move(attack)
        if move is None:
            attack = attack.replace(" ", "")
            try:
                move = find_details_move(attack)
            except:
                logger.log_and_showinfo("info",f"Can't find the attack {attack} in the database.")
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

    # Create a QLabel to display the HTML content
    label = QLabel(html_content)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align the label's content to the top
    label.setScaledContents(True)  # Enable scaling of the pixmap

    layout.addWidget(label)
    window.setLayout(layout)
    window.exec()


def remember_attack_details_window(id, attack_set, all_attacks, logger):
    window = QDialog()
    window.setWindowIcon(QIcon(str(icon_path)))
    layout = QHBoxLayout()
    window.setWindowTitle("Remember Attacks")  # Optional: Set a window title
    # Outer layout contains everything
    outer_layout = QVBoxLayout(window)

    # Create a scroll area that will contain our main layout
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)

    # Main widget that contains the content
    content_widget = QWidget()
    layout = QHBoxLayout(content_widget)  # The main layout is now set on this widget

    # HTML content
    html_content = remember_attack_details_window_template
    # Loop through the list of attacks and add them to the HTML content
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

    # Create a QLabel to display the HTML content
    label = QLabel(html_content)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # Align the label's content to the top
    label.setScaledContents(True)  # Enable scaling of the pixmap
    attack_layout = QVBoxLayout()
    for attack in all_attacks:
        move = find_details_move(attack)
        remember_attack_button = QPushButton(f"Remember {attack}") #add Details to Moves
        remember_attack_button.clicked.connect(lambda checked, a=attack: remember_attack(id, attack_set, a, logger))
        attack_layout.addWidget(remember_attack_button)
    attack_layout_widget = QWidget()
    attack_layout_widget.setLayout(attack_layout)
    # Add the label and button layout widget to the main layout
    layout.addWidget(label)
    layout.addWidget(attack_layout_widget)

    # Set the main widget with content as the scroll area's widget
    scroll_area.setWidget(content_widget)

    # Add the scroll area to the outer layout
    outer_layout.addWidget(scroll_area)

    window.setLayout(outer_layout)
    window.resize(1000, 400)  # Optional: Set a default size for the window
    window.exec()

def remember_attack(id, attacks, new_attack, logger):
    if new_attack in attacks:
        logger.log_and_showinfo("warning","Your pokemon already knows this move!")
        return
    if not mainpokemon_path.is_file():
        logger.log_and_showinfo("warning","Missing Mainpokemon Data !")
        return
    with open(mainpokemon_path, "r", encoding="utf-8") as json_file:
        main_pokemon_data = json.load(json_file)
    for mainpkmndata in main_pokemon_data:
        if mainpkmndata["id"] == id:
            mainpokemon_name = mainpkmndata["name"]
            attacks = mainpkmndata["attacks"]
            if new_attack:
                msg = ""
                msg += f"Your {mainpkmndata['name'].capitalize()} can learn a new attack !"
                if len(attacks) < 4:
                        attacks.append(new_attack)
                        msg += f"\n Your {mainpkmndata['name'].capitalize()} has learned {new_attack} !"
                        logger.log_and_showinfo("info",f"{msg}")
                else:
                        dialog = AttackDialog(attacks, new_attack)
                        if dialog.exec() == QDialog.DialogCode.Accepted:
                            selected_attack = dialog.selected_attack
                            index_to_replace = None
                            for index, attack in enumerate(attacks):
                                if attack == selected_attack:
                                    index_to_replace = index
                                    pass
                                else:
                                    pass
                            # If the attack is found, replace it with 'new_attack'
                            if index_to_replace is not None:
                                attacks[index_to_replace] = new_attack
                                logger.log_and_showinfo("info",f"Replaced '{selected_attack}' with '{new_attack}'")
                            else:
                                # Handle the case where the user cancels the dialog
                                logger.log_and_showinfo("info",f"{new_attack} will be discarded.")
            mainpkmndata["attacks"] = attacks
            mypkmndata = mainpkmndata
            mainpkmndata = [mainpkmndata]
            # Save the caught Pokémon's data to a JSON file
            with open(str(mainpokemon_path), "w") as json_file:
                json.dump(mainpkmndata, json_file, indent=2)
            
            with open(str(mypokemon_path), "r", encoding="utf-8") as output_file:
                mypokemondata = json.load(output_file)

            # Find and replace the specified Pokémon's data in mypokemondata
            for index, pokemon_data in enumerate(mypokemondata):
                if pokemon_data["name"] == mainpokemon_name:
                    mypokemondata[index] = mypkmndata
                    break
            # Save the modified data to the output JSON file
            with open(str(mypokemon_path), "w") as output_file:
                json.dump(mypokemondata, output_file, indent=2)
        else:
            logger.log_and_showinfo("info","Please Select this Pokemon first as Main Pokemon ! \n Only Mainpokemons can re-learn attacks!")

from PyQt6.QtWidgets import QMessageBox
from aqt.utils import showWarning
import json
from ..resources import mainpokemon_path, mypokemon_path

def rename_pkmn(nickname, pkmn_name, individual_id, logger, refresh_callback):
    try:
        # Load the captured Pokémon data
        with open(mypokemon_path, "r", encoding="utf-8") as json_file:
            captured_pokemon_data = json.load(json_file)
            pokemon = None

            # Find the Pokémon by individual_id
            for index, pokemon_data in enumerate(captured_pokemon_data):
                if pokemon_data["individual_id"] == individual_id:
                    pokemon = pokemon_data
                    break

            if pokemon is not None:
                # Update the nickname
                pokemon["nickname"] = nickname
                # Reflect the change in the output JSON file
                with open(str(mypokemon_path), "r", encoding="utf-8") as output_file:
                    mypokemondata = json.load(output_file)
                    # Update the specified Pokémon's data
                    for idx, data in enumerate(mypokemondata):
                        if data["individual_id"] == individual_id:
                            mypokemondata[idx] = pokemon
                            break
                # Save the modified data
                with open(str(mypokemon_path), "w") as output_file:
                    json.dump(mypokemondata, output_file, indent=2)
                # Logging and UI update
                logger.log_and_showinfo("info", f"Your {pkmn_name.capitalize()} has been renamed to {nickname}!")
                refresh_callback()
            else:
                showWarning("Pokémon not found.")
    except Exception as e:
        showWarning(f"An error occurred: {e}")

def PokemonFree(individual_id, name, logger, refresh_callback):
    # Confirmation dialog
    reply = QMessageBox.question(
        None, 
        "Confirm Release", 
        f"Are you sure you want to release {name}?", 
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
        QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.No:
        logger.log_and_showinfo("info","Release cancelled.")
        return

    # Check if the Pokémon is in the main Pokémon file
    with open(mainpokemon_path, "r", encoding="utf-8") as file:
        pokemon_data = json.load(file)

    for pokemon in pokemon_data:
        if pokemon["individual_id"] == individual_id:
            logger.log_and_showinfo("info","You can't free your Main Pokémon!")
            return  # Exit the function if it's a Main Pokémon

    # Load Pokémon list from 'mypokemon_path' file
    try:
        with open(mypokemon_path, "r", encoding="utf-8") as file:
            pokemon_list = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logger.log_and_showinfo("info","Error: Could not load Pokémon data.")
        return

    # Find the position of the Pokémon with the given individual_id
    position = -1
    for idx, pokemon in enumerate(pokemon_list):
        if pokemon.get("individual_id") == individual_id:
            position = idx
            break

    # If the Pokémon was found, remove it from the list
    if position != -1:
        pokemon_list.pop(position)
        with open(mypokemon_path, 'w') as file:
            json.dump(pokemon_list, file, indent=2)
        logger.log_and_showinfo("info",f"{name.capitalize()} has been let free.")
    else:
        logger.log_and_showinfo("info","No Pokémon found with the specified ID.")
    
    refresh_callback()
