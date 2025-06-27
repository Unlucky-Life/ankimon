from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
from aqt.utils import showWarning, showInfo
from aqt import mw
import os
from ..resources import addon_dir, icon_path
from ..functions.pokedex_functions import search_pokedex

class TestWindow(QWidget):
    def __init__(self, pkmn_window, first_start, video, test, pokemon_encounter, system, ankimon_key):
        super().__init__()
        self.init_ui()
        self.pkmn_window = pkmn_window
        self.first_start = first_start
        self.video = video
        self.test = test
        self.pokemon_encounter = pokemon_encounter
        self.system = system
        self.ankimon_key = ankimon_key
        #self.update()

    def init_ui(self):
        layout = QVBoxLayout()
        # Main window layout
        layout = QVBoxLayout()
        image_file = "ankimon_logo.png"
        image_path = str(addon_dir) + "/" + image_file
        image_label = QLabel()
        pixmap = QPixmap()
        pixmap.load(str(image_path))
        if pixmap.isNull():
            showWarning("Failed to load image")
        else:
            image_label.setPixmap(pixmap)
        scaled_pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
        image_label.setPixmap(scaled_pixmap)
        layout.addWidget(image_label)
        self.first_start = True
        self.setLayout(layout)
        # Set window
        self.setWindowTitle('Ankimon Window')
        self.setWindowIcon(QIcon(str(icon_path))) # Add a Pokeball icon
        # Display the Pokémon image

    def open_dynamic_window(self):
        # Create and show the dynamic window
        try:
            if self.pkmn_window == False:
                self.display_first_encounter()
                self.pkmn_window = True
            self.show()
        except Exception as e:
            showWarning(f"Following Error occured when opening window: {e}")

    def display_first_start_up(self):
        if self.first_start == False:
            # Get the geometry of the main screen
            main_screen_geometry = mw.geometry()
            # Calculate the position to center the ItemWindow on the main screen
            x = int(main_screen_geometry.center().x() - self.width() / 2)
            y = int(main_screen_geometry.center().y() - self.height() / 2)
            self.setGeometry(x, y, 256, 256 )
            self.move(x,y)
            self.show()
            self.first_start = True
        self.pkmn_window = True

    def pokemon_display_first_encounter(self):
        # Main window layout
        layout = QVBoxLayout()
        global pokemon_encounter
        global hp, name, id, stats, level, max_hp, base_experience, ev, iv, gender
        global caught_pokemon, message_box_text
        global caught
        global mainpkmn
        global mainpokemon_id, mainpokemon_name, mainpokemon_level, mainpokemon_ability, mainpokemon_type, mainpokemon_xp, mainpokemon_stats, mainpokemon_attacks, mainpokemon_base_experience, mainpokemon_ev, mainpokemon_iv, mainpokemon_hp, mainpokemon_current_hp, mainpokemon_growth_rate
        global battlescene_file
        global attack_counter, merged_pixmap, window
        attack_counter = 0
        caught = 0
        id = int(search_pokedex(name.lower(), "num"))
        # Capitalize the first letter of the Pokémon's name
        lang_name = get_pokemon_diff_lang_name(int(id))
        name = name.capitalize()
        # calculate wild pokemon max hp
        max_hp = calculate_hp(stats["hp"], level, ev, iv)
        mainpkmn_max_hp = calculate_hp(mainpokemon_stats["hp"], mainpokemon_level, mainpokemon_ev, mainpokemon_iv)
        message_box_text = (f"A wild {lang_name.capitalize()} appeared !")
        if pokemon_encounter == 0:
            bckgimage_path = battlescene_path / battlescene_file
        elif pokemon_encounter > 0:
            bckgimage_path = battlescene_path_without_dialog / battlescene_file
        def window_show():
            ui_path = battle_ui_path
            pixmap_ui = QPixmap()
            pixmap_ui.load(str(ui_path))

            # Load the background image
            pixmap_bckg = QPixmap()
            pixmap_bckg.load(str(bckgimage_path))

            # Display the Pokémon image
            pkmnimage_file = f"{id}.png"
            pkmnimage_path = frontdefault / pkmnimage_file
            image_label = QLabel()
            pixmap = QPixmap()
            pixmap.load(str(pkmnimage_path))

            # Display the Main Pokémon image
            pkmnimage_file2 = f"{mainpokemon_id}.png"
            pkmnimage_path2 = backdefault / pkmnimage_file2
            pixmap2 = QPixmap()
            pixmap2.load(str(pkmnimage_path2))

            # Calculate the new dimensions to maintain the aspect ratio
            max_width = 150
            original_width = pixmap.width()
            original_height = pixmap.height()
            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pixmap = pixmap.scaled(new_width, new_height)

            # Calculate the new dimensions to maintain the aspect ratio
            max_width = 150
            original_width2 = pixmap2.width()
            original_height2 = pixmap2.height()

            new_width2 = max_width
            new_height2 = (original_height2 * max_width) // original_width2
            pixmap2 = pixmap2.scaled(new_width2, new_height2)

            # Merge the background image and the Pokémon image
            merged_pixmap = QPixmap(pixmap_bckg.size())
            #merged_pixmap.fill(Qt.transparent)
            merged_pixmap.fill(QColor(0, 0, 0, 0))
            # RGBA where A (alpha) is 0 for full transparency
            # merge both images together
            painter = QPainter(merged_pixmap)
            # draw background to a specific pixel
            painter.drawPixmap(0, 0, pixmap_bckg)

            def draw_hp_bar(x, y, h, w, hp, max_hp):
                pokemon_hp_percent = int((hp / max_hp) * 100)
                hp_bar_value = int(w * (hp / max_hp))
                # Draw the HP bar
                if pokemon_hp_percent < 25:
                    hp_color = QColor(255, 0, 0)  # Red
                elif pokemon_hp_percent < 50:
                    hp_color = QColor(255, 140, 0)  # Orange
                elif pokemon_hp_percent < 75:
                    hp_color = QColor(255, 255, 0)  # Yellow
                else:
                    hp_color = QColor(110, 218, 163)  # Green
                painter.setBrush(hp_color)
                painter.drawRect(int(x), int(y), int(hp_bar_value), int(h))

            draw_hp_bar(118, 76, 8, 116, hp, max_hp)  # enemy pokemon hp_bar
            draw_hp_bar(401, 208, 8, 116, mainpokemon_hp, mainpkmn_max_hp)  # main pokemon hp_bar

            painter.drawPixmap(0, 0, pixmap_ui)
            # Find the Pokemon Images Height and Width
            wpkmn_width = (new_width // 2)
            wpkmn_height = new_height
            mpkmn_width = (new_width2 // 2)
            mpkmn_height = new_height2
            # draw pokemon image to a specific pixel
            painter.drawPixmap((410 - wpkmn_width), (170 - wpkmn_height), pixmap)
            painter.drawPixmap((144 - mpkmn_width), (290 - mpkmn_height), pixmap2)

            experience = int(find_experience_for_level(mainpokemon_growth_rate, mainpokemon_level))
            mainxp_bar_width = 5
            mainpokemon_xp_value = int((mainpokemon_xp / experience) * 148)
            # Paint XP Bar
            painter.setBrush(QColor(58, 155, 220))
            painter.drawRect(int(366), int(246), int(mainpokemon_xp_value), int(mainxp_bar_width))

            # create level text
            lvl = (f"{level}")
            #gender_text = (f"{gender}")
            mainlvl = (f"{mainpokemon_level}")
            
            # Convert gender name to symbol - this function is from Foxy-null
            if gender == "M":
                gender_symbol = "♂"
            elif gender == "F":
                gender_symbol = "♀"
            elif gender == "N":
                gender_symbol = ""
            else:
                gender_symbol = ""  # None

            # custom font
            custom_font = load_custom_font(int(26), int(settings_obj.get("misc.language",11)))
            msg_font = load_custom_font(int(32), int(settings_obj.get("misc.language",11)))
            mainpokemon_lang_name = get_pokemon_diff_lang_name(int(mainpokemon_id))
            # Draw the text on top of the image
            # Adjust the font size as needed
            painter.setFont(custom_font)
            painter.setPen(QColor(31, 31, 39))  # Text color
            painter.drawText(48, 67, f"{lang_name} {gender_symbol}")
            painter.drawText(326, 200, mainpokemon_lang_name)
            painter.drawText(208, 67, lvl)
            #painter.drawText(55, 85, gender_text)
            painter.drawText(490, 199, mainlvl)
            painter.drawText(487, 238, f"{mainpkmn_max_hp}")
            painter.drawText(442, 238, f"{mainpokemon_hp}")
            painter.setFont(msg_font)
            painter.setPen(QColor(240, 240, 208))  # Text color
            painter.drawText(40, 320, message_box_text)
            painter.end()
            # Set the merged image as the pixmap for the QLabel
            image_label.setPixmap(merged_pixmap)
            return image_label, msg_font
        image_label, msg_font = window_show()
        return image_label

    def pokemon_display_battle(self):
        global pokemon_encounter, id
        pokemon_encounter += 1
        if pokemon_encounter == 1:
            bckgimage_path = battlescene_path / battlescene_file
        elif pokemon_encounter > 1:
            bckgimage_path = battlescene_path_without_dialog / battlescene_file
        ui_path = battle_ui_path
        pixmap_ui = QPixmap()
        pixmap_ui.load(str(ui_path))

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        # Display the Pokémon image
        pkmnimage_file = f"{id}.png"
        pkmnimage_path = frontdefault / pkmnimage_file
        image_label = QLabel()
        pixmap = QPixmap()
        pixmap.load(str(pkmnimage_path))

        # Display the Main Pokémon image
        pkmnimage_file2 = f"{mainpokemon_id}.png"
        pkmnimage_path2 = backdefault / pkmnimage_file2
        pixmap2 = QPixmap()
        pixmap2.load(str(pkmnimage_path2))

        # Calculate the new dimensions to maintain the aspect ratio
        max_width = 150
        original_width = pixmap.width()
        original_height = pixmap.height()
        new_width = max_width
        new_height = (original_height * max_width) //original_width
        pixmap = pixmap.scaled(new_width, new_height)

        # Calculate the new dimensions to maintain the aspect ratio
        max_width = 150
        original_width2 = pixmap2.width()
        original_height2 = pixmap2.height()

        new_width2 = max_width
        new_height2 = (original_height2 * max_width) // original_width2
        pixmap2 = pixmap2.scaled(new_width2, new_height2)

        # Merge the background image and the Pokémon image
        merged_pixmap = QPixmap(pixmap_bckg.size())
        #merged_pixmap.fill(Qt.transparent)
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)

        def draw_hp_bar(x, y, h, w, hp, max_hp):
            pokemon_hp_percent = int((hp / max_hp) * 100)
            hp_bar_value = int(w * (hp / max_hp))
            # Draw the HP bar
            if pokemon_hp_percent < 25:
                hp_color = QColor(255, 0, 0)  # Red
            elif pokemon_hp_percent < 50:
                hp_color = QColor(255, 140, 0)  # Orange
            elif pokemon_hp_percent < 75:
                hp_color = QColor(255, 255, 0)  # Yellow
            else:
                hp_color = QColor(110, 218, 163)  # Green
            painter.setBrush(hp_color)
            painter.drawRect(int(x), int(y), int(hp_bar_value), int(h))

        draw_hp_bar(118, 76, 8, 116, hp, max_hp)  # enemy pokemon hp_bar
        draw_hp_bar(401, 208, 8, 116, mainpokemon_current_hp, mainpokemon_hp)  # main pokemon hp_bar

        painter.drawPixmap(0, 0, pixmap_ui)
        # Find the Pokemon Images Height and Width
        wpkmn_width = (new_width // 2)
        wpkmn_height = new_height
        mpkmn_width = (new_width2 // 2)
        mpkmn_height = new_height2
        # draw pokemon image to a specific pixel
        painter.drawPixmap((410 - wpkmn_width), (170 - wpkmn_height), pixmap)
        painter.drawPixmap((144 - mpkmn_width), (290 - mpkmn_height), pixmap2)

        experience = int(find_experience_for_level(mainpokemon_growth_rate, mainpokemon_level))
        mainxp_bar_width = 5
        mainpokemon_xp_value = int((mainpokemon_xp / experience) * 148)
        # Paint XP Bar
        painter.setBrush(QColor(58, 155, 220))
        painter.drawRect(366, 246, int(mainpokemon_xp_value), int(mainxp_bar_width))

        # create level text
        lvl = (f"{level}")
        mainlvl = (f"{mainpokemon_level}")

        # custom font
        custom_font = load_custom_font(int(28), int(settings_obj.get("misc.language",11)))
        msg_font = load_custom_font(int(32), int(settings_obj.get("misc.language",11)))

        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(31, 31, 39))  # Text color
        lang_name = get_pokemon_diff_lang_name(int(id))
        painter.drawText(48, 67, lang_name)
        mainpokemon_lang_name = get_pokemon_diff_lang_name(int(mainpokemon_id))
        painter.drawText(326, 200, mainpokemon_lang_name)
        painter.drawText(208, 67, lvl)
        painter.drawText(490, 199, mainlvl)
        painter.drawText(487, 238, f"{mainpokemon_hp}")
        painter.drawText(442, 238, f"{mainpokemon_current_hp}")
        painter.setFont(msg_font)
        painter.setPen(QColor(240, 240, 208))  # Text color
        painter.drawText(40, 320, message_box_text)
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        image_label.setPixmap(merged_pixmap)
        return image_label

    def pokemon_display_item(self, item):
        global pokemon_encounter
        bckgimage_path =  addon_dir / "addon_sprites" / "starter_screen" / "bg.png"
        item_path = user_path_sprites / "items" / f"{item}.png"

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        # Display the Pokémon image
        item_label = QLabel()
        item_pixmap = QPixmap()
        item_pixmap.load(str(item_path))

        def resize_pixmap_img(pixmap):
            max_width = 100
            original_width = pixmap.width()
            original_height = pixmap.height()

            if original_width == 0:
                return pixmap  # Avoid division by zero

            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pixmap2 = pixmap.scaled(new_width, new_height)
            return pixmap2

        item_pixmap = resize_pixmap_img(item_pixmap)

        # Merge the background image and the Pokémon image
        merged_pixmap = QPixmap(pixmap_bckg.size())
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        #merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)
        #item = str(item)
        if item.endswith("-up") or item.endswith("-max") or item.endswith("protein") or item.endswith("zinc") or item.endswith("carbos") or item.endswith("calcium") or item.endswith("repel") or item.endswith("statue"):
            painter.drawPixmap(200,50,item_pixmap)
        elif item.endswith("soda-pop"):
            painter.drawPixmap(200,30,item_pixmap)
        elif item.endswith("-heal") or item.endswith("awakening") or item.endswith("ether") or item.endswith("leftovers"):
            painter.drawPixmap(200,50,item_pixmap)
        elif item.endswith("-berry") or item.endswith("potion"):
            painter.drawPixmap(200,80,item_pixmap)
        else:
            painter.drawPixmap(200,90,item_pixmap)

        # custom font
        custom_font = load_custom_font(int(26), int(settings_obj.get("misc.language",11)))
        message_box_text = f"You have received a item: {item.capitalize()} !"
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(50, 290, message_box_text)
        custom_font = load_custom_font(int(20), int(settings_obj.get("misc.language",11)))
        painter.setFont(custom_font)
        #painter.drawText(10, 330, "You can look this up in your item bag.")
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        image_label = QLabel()
        image_label.setPixmap(merged_pixmap)

        return image_label

    def pokemon_display_badge(self, badge_number):
        try:
            global pokemon_encounter, badges
            bckgimage_path = addon_dir / "addon_sprites" / "starter_screen" / "bg.png"
            badge_path = addon_dir / "user_files" / "sprites" / "badges" / f"{badge_number}.png"

            # Load the background image
            pixmap_bckg = QPixmap()
            pixmap_bckg.load(str(bckgimage_path))

            # Display the Pokémon image
            item_pixmap = QPixmap()
            item_pixmap.load(str(badge_path))

            def resize_pixmap_img(pixmap):
                max_width = 100
                original_width = pixmap.width()
                original_height = pixmap.height()

                if original_width == 0:
                    return pixmap  # Avoid division by zero

                new_width = max_width
                new_height = (original_height * max_width) // original_width
                pixmap2 = pixmap.scaled(new_width, new_height)
                return pixmap2

            item_pixmap = resize_pixmap_img(item_pixmap)

            # Merge the background image and the Pokémon image
            merged_pixmap = QPixmap(pixmap_bckg.size())
            merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
            #merged_pixmap.fill(Qt.transparent)
            # merge both images together
            painter = QPainter(merged_pixmap)
            # draw background to a specific pixel
            painter.drawPixmap(0, 0, pixmap_bckg)
            #item = str(item)
            painter.drawPixmap(200,90,item_pixmap)

            # custom font
            custom_font = load_custom_font(int(20), int(settings_obj.get("misc.language",11)))
            message_box_text = "You have received a badge for:"
            message_box_text2 = f"{badges[str(badge_number)]}!"
            # Draw the text on top of the image
            # Adjust the font size as needed
            painter.setFont(custom_font)
            painter.setPen(QColor(255,255,255))  # Text color
            painter.drawText(120, 270, message_box_text)
            painter.drawText(140, 290, message_box_text2)
            custom_font = load_custom_font(int(20), int(settings_obj.get("misc.language",11)))
            painter.setFont(custom_font)
            #painter.drawText(10, 330, "You can look this up in your item bag.")
            painter.end()
            # Set the merged image as the pixmap for the QLabel
            image_label = QLabel()
            image_label.setPixmap(merged_pixmap)

            return image_label
        except Exception as e:
            showWarning(f"An error occured in badges window {e}")

    def pokemon_display_dead_pokemon(self):
        global pokemon_hp, name, id, level, type, caught_pokemon, caught
        # Create the dialog
        lang_name = get_pokemon_diff_lang_name(int(id))
        window_title = (f"Would you want let the  wild {lang_name} free or catch the wild {lang_name} ?")
        # Display the Pokémon image
        pkmnimage_file = f"{int(search_pokedex(name.lower(),'num'))}.png"
        pkmnimage_path = frontdefault / pkmnimage_file
        pkmnimage_label = QLabel()
        pkmnpixmap = QPixmap()
        pkmnpixmap.load(str(pkmnimage_path))
        pkmnpixmap_bckg = QPixmap()
        pkmnpixmap_bckg.load(str(pokedex_image_path))
        # Calculate the new dimensions to maintain the aspect ratio
        pkmnpixmap = pkmnpixmap.scaled(230, 230)

        # Create a painter to add text on top of the image
        painter2 = QPainter(pkmnpixmap_bckg)
        painter2.drawPixmap(15,15,pkmnpixmap)
        # Capitalize the first letter of the Pokémon's name
        capitalized_name = lang_name.capitalize()
        # Create level text
        lvl = (f" Level: {level}")

        # Draw the text on top of the image
        font = QFont()
        font.setPointSize(20)  # Adjust the font size as needed
        painter2.setFont(font)
        painter2.drawText(270,107,f"{lang_name}")
        font.setPointSize(17)  # Adjust the font size as needed
        painter2.setFont(font)
        painter2.drawText(315,192,f"{lvl}")
        painter2.drawText(322,225,f"Type: {type[0].capitalize()}")
        painter2.setFont(font)
        fontlvl = QFont()
        fontlvl.setPointSize(12)
        painter2.end()

        # Create a QLabel for the capitalized name
        name_label = QLabel(capitalized_name)
        name_label.setFont(font)

        # Create a QLabel for the level
        level_label = QLabel(lvl)
        # Align to the center
        level_label.setFont(fontlvl)

        nickname_input = QLineEdit()
        nickname_input.setPlaceholderText("Choose Nickname")
        nickname_input.setStyleSheet("background-color: rgb(44,44,44);")
        nickname_input.setFixedSize(120, 30)  # Adjust the size as needed

        # Create buttons for catching and killing the Pokémon
        catch_button = QPushButton("Catch Pokémon")
        catch_button.setFixedSize(175, 30)  # Adjust the size as needed
        catch_button.setFont(QFont("Arial", 12))  # Adjust the font size and style as needed
        catch_button.setStyleSheet("background-color: rgb(44,44,44);")
        #catch_button.setFixedWidth(150)
        qconnect(catch_button.clicked, lambda: catch_pokemon(nickname_input.text()))

        kill_button = QPushButton("Defeat Pokémon")
        kill_button.setFixedSize(175, 30)  # Adjust the size as needed
        kill_button.setFont(QFont("Arial", 12))  # Adjust the font size and style as needed
        kill_button.setStyleSheet("background-color: rgb(44,44,44);")
        #kill_button.setFixedWidth(150)
        qconnect(kill_button.clicked, kill_pokemon)
        # Set the merged image as the pixmap for the QLabel
        pkmnimage_label.setPixmap(pkmnpixmap_bckg)


        # align things needed to middle
        pkmnimage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        return pkmnimage_label, kill_button, catch_button, nickname_input

    def display_first_encounter(self):
        # pokemon encounter image
        self.clear_layout(self.layout())
        #self.setFixedWidth(556)
        #self.setFixedHeight(371)
        layout = self.layout()
        battle_widget = self.pokemon_display_first_encounter()
        #battle_widget.setScaledContents(True) #scalable ankimon window
        layout.addWidget(battle_widget)
        self.setStyleSheet("background-color: rgb(44,44,44);")
        self.setLayout(layout)
        self.setMaximumWidth(556)
        self.setMaximumHeight(300)

    def rate_display_item(self, item):
        Receive_Window = QDialog(mw)
        layout = QHBoxLayout()
        item_name = item
        item_widget = self.pokemon_display_item(item_name)
        layout.addWidget(item_widget)
        Receive_Window.setStyleSheet("background-color: rgb(44,44,44);")
        Receive_Window.setMaximumWidth(512)
        Receive_Window.setMaximumHeight(320)
        Receive_Window.setLayout(layout)
        Receive_Window.show()
    
    def display_item(self):
        Receive_Window = QDialog(mw)
        layout = QHBoxLayout()
        item_name = random_item()
        item_widget = self.pokemon_display_item(item_name)
        layout.addWidget(item_widget)
        Receive_Window.setStyleSheet("background-color: rgb(44,44,44);")
        Receive_Window.setMaximumWidth(512)
        Receive_Window.setMaximumHeight(320)
        Receive_Window.setLayout(layout)
        Receive_Window.show()

    def display_badge(self, badge_num):
        Receive_Window = QDialog(mw)
        Receive_Window.setWindowTitle("You have received a Badge!")
        layout = QHBoxLayout()
        badge_widget = self.pokemon_display_badge(badge_num)
        layout.addWidget(badge_widget)
        Receive_Window.setStyleSheet("background-color: rgb(44,44,44);")
        Receive_Window.setMaximumWidth(512)
        Receive_Window.setMaximumHeight(320)
        Receive_Window.setLayout(layout)
        Receive_Window.show()

    def display_pokemon_death(self):
        # pokemon encounter image
        self.clear_layout(self.layout())
        layout = self.layout()
        pkmnimage_label, kill_button, catch_button, nickname_input = self.pokemon_display_dead_pokemon()
        layout.addWidget(pkmnimage_label)
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        button_layout.addWidget(kill_button)
        button_layout.addWidget(catch_button)
        button_layout.addWidget(nickname_input)
        button_widget.setLayout(button_layout)
        layout.addWidget(button_widget)
        self.setStyleSheet("background-color: rgb(177,147,209);")
        self.setLayout(layout)
        self.setMaximumWidth(500)
        self.setMaximumHeight(300)

    def keyPressEvent(self, event):
        global pokemon_encounter, system, ankimon_key
        open_window_key = getattr(Qt.Key, 'Key_' + ankimon_key.upper())
        if system == "mac":
            if event.key() == open_window_key and event.modifiers() == Qt.KeyboardModifier.MetaModifier:
                self.close()
        else:
            if event.key() == open_window_key and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.close()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def closeEvent(self,event):
        self.pkmn_window = False