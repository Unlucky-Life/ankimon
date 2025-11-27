import json

from aqt import mw

from aqt.qt import (
    QDialog,
    QFont,
    QLabel,
    QPainter,
    QPixmap,
    Qt,
    QVBoxLayout,
    QWidget,
    qconnect
)

from aqt.utils import showWarning

from PyQt6.QtGui import QIcon, QColor, QPainterPath

from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QLineEdit,
)

from ..utils import random_item, load_custom_font

from ..functions.drawing_utils import draw_gender_symbols, draw_stat_boosts

from ..functions.pokedex_functions import get_pokemon_diff_lang_name, search_pokedex

from ..functions.pokemon_functions import find_experience_for_level

from ..pyobj.ankimon_tracker import AnkimonTracker
from ..pyobj.InfoLogger import ShowInfoLogger

from ..pyobj.translator import Translator

from .error_handler import show_warning_with_traceback

from ..resources import (
    pkmnimgfolder,
    addon_dir,
    icon_path,
    battlescene_path,
    battlescene_path_without_dialog,
    battle_ui_path,
    user_path_sprites,
    frontdefault,
    badges_list_path,
    pokedex_image_path,
)


class TestWindow(QWidget):

    def __init__(
        self,
        main_pokemon,
        enemy_pokemon,
        settings_obj,
        parent=mw,
        ankimon_tracker_obj: AnkimonTracker=None,
        translator: Translator=None,
        logger: ShowInfoLogger=None,
    ):
        super().__init__(parent)  # <-- set parent here

        # Set as a tool window so it stays above parent but not above all apps
        self.setWindowFlag(Qt.WindowType.Tool, True)

        # Optionally: ensure it raises above the parent when shown
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)  # Explicitly disable global always-on-top

        self.pkmn_window = False  #if fighting window open
        self.first_start = False
        self.enemy_pokemon = enemy_pokemon
        self.main_pokemon = main_pokemon
        self.settings_obj = settings_obj
        self.ankimon_tracker_obj = ankimon_tracker_obj
        self.logger = logger
        self.translator = translator

        if translator is None:
            self.translator = Translator(language=int(settings_obj.get("misc.language")))

        self.test = 1

        self.default_path = f"{pkmnimgfolder}/front_default/substitute.png"

        self.init_ui()
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
            showWarning("Failed to load Ankimon Logo image")
        else:
            image_label.setPixmap(pixmap)

        scaled_pixmap = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio)
        image_label.setPixmap(scaled_pixmap)

        layout.addWidget(image_label)

        self.first_start = True

        self.setLayout(layout)

        # Set window
        self.setWindowTitle('Ankimon Window')
        self.setWindowIcon(QIcon(str(icon_path)))  # Add a Pokeball icon

        # Display the Pokémon image

    def open_dynamic_window(self):
        # Create and show the dynamic window
        try:
            if self.pkmn_window == False:
                self.display_first_encounter()
                self.pkmn_window = True
                #self.show()

            if self.isVisible():
                self.close()  # Testfenster schließen, wenn Shift gedrückt wird
            else:
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

        global message_box_text
        global merged_pixmap, window

        self.ankimon_tracker_obj.attack_counter = 0
        self.ankimon_tracker_obj.caught = 0

        # Capitalize the first letter of the Pokémon's name
        lang_name = get_pokemon_diff_lang_name(int(self.enemy_pokemon.id), int(self.settings_obj.get('misc.language')))

        # calculate wild pokemon max hp
        message_box_text = f"{mw.translator.translate('wild_pokemon_appeared', enemy_pokemon_name=lang_name.capitalize())}"

        bckgimage_path = battlescene_path / self.ankimon_tracker_obj.battlescene_file

        if self.ankimon_tracker_obj.pokemon_encouter > 0:
            bckgimage_path = battlescene_path_without_dialog / self.ankimon_tracker_obj.battlescene_file

        msg_font = load_custom_font(int(32), int(self.settings_obj.get("misc.language")))

        image_label, msg_font = self.window_show(bckgimage_path, lang_name)

        return image_label

    def window_show(self, bckgimage_path, lang_name):
        ui_path = battle_ui_path

        pixmap_ui = QPixmap()
        pixmap_ui.load(str(ui_path))

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        # Display the Pokémon image
        image_label = QLabel()
        pixmap = QPixmap()

        try:
            pixmap.load(str(self.enemy_pokemon.get_sprite_path('front', 'png')))
        except:
            pixmap.load(str(self.default_path))

        # Display the Main Pokémon image
        pixmap2 = QPixmap()

        try:
            pixmap2.load(str(self.main_pokemon.get_sprite_path('back', 'png')))
        except:
            pixmap2.load(str(self.default_path))

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

        # Create rounded rectangle path for clipping
        path = QPainterPath()
        path.addRoundedRect(0, 0, merged_pixmap.width(), merged_pixmap.height(), 10, 10)
        painter.setClipPath(path)

        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)

        painter = self.draw_hp_bar(118, 76, 8, 116, self.enemy_pokemon.current_hp, self.enemy_pokemon.max_hp, painter)  # enemy pokemon hp_bar

        painter = self.draw_hp_bar(401, 208, 8, 116, self.main_pokemon.hp, self.main_pokemon.max_hp, painter)  # main pokemon hp_bar

        painter.drawPixmap(0, 0, pixmap_ui)

        # Find the Pokemon Images Height and Width
        wpkmn_width = (new_width // 2)
        wpkmn_height = new_height

        mpkmn_width = (new_width2 // 2)
        mpkmn_height = new_height2

        # draw pokemon image to a specific pixel
        painter.drawPixmap((410 - wpkmn_width), (170 - wpkmn_height), pixmap)
        painter.drawPixmap((144 - mpkmn_width), (290 - mpkmn_height), pixmap2)

        experience = int(find_experience_for_level(self.main_pokemon.growth_rate, self.main_pokemon.level, self.settings_obj.get("misc.remove_level_cap")))

        mainxp_bar_width = 5
        mainpokemon_xp_value = int((self.main_pokemon.xp / experience) * 148)

        # Paint XP Bar
        painter.setBrush(QColor(58, 155, 220))
        painter.drawRect(int(366), int(246), int(mainpokemon_xp_value), int(mainxp_bar_width))

        # custom font
        custom_font = load_custom_font(int(26), int(self.settings_obj.get("misc.language")))
        hp_enemy_text_font = load_custom_font(int(18), int(self.settings_obj.get("misc.language")))
        msg_font = load_custom_font(int(32), int(self.settings_obj.get("misc.language")))

        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(31, 31, 39))  # Text color

        enemy_name = get_pokemon_diff_lang_name(int(self.enemy_pokemon.id), int(self.settings_obj.get('misc.language')))

        main_name = get_pokemon_diff_lang_name(int(self.main_pokemon.id), int(self.settings_obj.get('misc.language')))

        if self.enemy_pokemon.shiny:
            enemy_name += " 🌠 "

        if self.main_pokemon.shiny:
            main_name += " 🌠 "

        painter.drawText(48, 67, enemy_name)
        painter.drawText(326, 200, main_name)

        # Drawing the gender of each Pokemon
        draw_gender_symbols(self.main_pokemon, self.enemy_pokemon, painter, (457, 196), (175, 64))

        draw_stat_boosts(self.main_pokemon, self.enemy_pokemon, painter, (326, 155), (48, 25))

        painter.drawText(208, 67, f"{self.enemy_pokemon.level}")
        #painter.drawText(55, 85, gender_text)
        painter.drawText(490, 199, f"{self.main_pokemon.level}")

        hp_x = 442 if int(self.main_pokemon.hp) < 100 else 430  # Shift left if 3 digits
        max_hp_x = 487 if int(self.main_pokemon.max_hp) < 100 else 480  # Shift left if 3 digits

        painter.drawText(max_hp_x, 238, str(int(self.main_pokemon.max_hp)))
        painter.drawText(hp_x, 238, str(int(self.main_pokemon.hp)))

        painter.setFont(msg_font)
        painter.setPen(QColor(240, 240, 208))  # Text color

        painter.drawText(40, 320, message_box_text)

        painter.setFont(hp_enemy_text_font)
        painter.setPen(QColor(31, 31, 39))  # Text color
        enemy_hp_x = 41 if int(self.enemy_pokemon.max_hp) < 100 else 40  # Shift left if 3 digits
        enemy_max_hp_x = 64 if int(self.enemy_pokemon.max_hp) < 100 else 56  # Shift left if 3 digits
        painter.drawText(enemy_hp_x, 84 if int(self.enemy_pokemon.max_hp) < 100 else 80 , str(int(self.enemy_pokemon.hp)) + "/")
        painter.drawText(enemy_max_hp_x, 84 if int(self.enemy_pokemon.max_hp) < 100 else 88, str(int(self.enemy_pokemon.max_hp)))

        painter.end()

        # Set the merged image as the pixmap for the QLabel
        image_label.setPixmap(merged_pixmap)

        return image_label, msg_font

    def draw_hp_bar(self, x, y, h, w, hp, max_hp, painter):
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

        return painter

    def pokemon_display_battle(self):
        self.ankimon_tracker_obj.pokemon_encouter += 1

        bckgimage_path = battlescene_path / self.ankimon_tracker_obj.battlescene_file

        if self.ankimon_tracker_obj.pokemon_encouter > 1:
            bckgimage_path = battlescene_path_without_dialog / self.ankimon_tracker_obj.battlescene_file

        ui_path = battle_ui_path

        pixmap_ui = QPixmap()
        pixmap_ui.load(str(ui_path))

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        image_label = QLabel()

        # Display the Pokémon image
        pixmap = QPixmap()

        try:
            pixmap.load(str(self.enemy_pokemon.get_sprite_path('front', 'png')))
        except:
            pixmap.load(str(self.default_path))

        # Display the Main Pokémon image
        pixmap2 = QPixmap()

        try:
            pixmap2.load(str(self.main_pokemon.get_sprite_path('back', 'png')))
        except:
            pixmap2.load(str(self.default_path))

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

        # Create rounded rectangle path for clipping
        path = QPainterPath()
        path.addRoundedRect(0, 0, merged_pixmap.width(), merged_pixmap.height(), 10, 10)
        painter.setClipPath(path)

        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)

        painter = self.draw_hp_bar(118, 76, 8, 116, self.enemy_pokemon.hp, self.enemy_pokemon.max_hp, painter)  # enemy pokemon hp_bar

        painter = self.draw_hp_bar(401, 208, 8, 116, self.main_pokemon.hp, self.main_pokemon.max_hp, painter)  # main pokemon hp_bar

        painter.drawPixmap(0, 0, pixmap_ui)

        # Find the Pokemon Images Height and Width
        wpkmn_width = (new_width // 2)
        wpkmn_height = new_height

        mpkmn_width = (new_width2 // 2)
        mpkmn_height = new_height2

        # draw pokemon image to a specific pixel
        painter.drawPixmap((410 - wpkmn_width), (170 - wpkmn_height), pixmap)
        # Reposition main pokemon to be fully visible when message box disappears
        painter.drawPixmap((144 - mpkmn_width), (270 - mpkmn_height), pixmap2)

        experience = int(find_experience_for_level(self.main_pokemon.growth_rate, self.main_pokemon.level, self.settings_obj.get("misc.remove_level_cap")))

        mainxp_bar_width = 5
        mainpokemon_xp_value = int((self.main_pokemon.xp / experience) * 148)

        # Paint XP Bar
        painter.setBrush(QColor(58, 155, 220))
        painter.drawRect(int(366), int(246), int(mainpokemon_xp_value), int(mainxp_bar_width))

        # custom font
        custom_font = load_custom_font(int(26), int(self.settings_obj.get("misc.language")))
        hp_enemy_text_font = load_custom_font(int(18), int(self.settings_obj.get("misc.language")))
        msg_font = load_custom_font(int(28), int(self.settings_obj.get("misc.language")))

        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(31, 31, 39))  # Text color

        enemy_name = get_pokemon_diff_lang_name(int(self.enemy_pokemon.id), int(self.settings_obj.get('misc.language')))

        main_name = get_pokemon_diff_lang_name(int(self.main_pokemon.id), int(self.settings_obj.get('misc.language')))

        if self.enemy_pokemon.shiny:
            enemy_name += f" 🌠"  # Green sparkle

        if self.main_pokemon.shiny:
            main_name += f" 🌠"  # Green sparkles

        painter.drawText(48, 67, enemy_name)
        painter.drawText(326, 200, main_name)

        # Drawing the gender of each Pokemon
        draw_gender_symbols(self.main_pokemon, self.enemy_pokemon, painter, (457, 196), (175, 64))

        draw_stat_boosts(self.main_pokemon, self.enemy_pokemon, painter, (326, 155), (48, 25))

        painter.drawText(208, 67, f"{self.enemy_pokemon.level}")
        painter.drawText(490, 199, f"{self.main_pokemon.level}")

        hp_x = 442 if int(self.main_pokemon.hp) < 100 else 430  # Shift left if 3 digits
        max_hp_x = 487 if int(self.main_pokemon.max_hp) < 100 else 480  # Shift left if 3 digits

        painter.drawText(max_hp_x, 238, str(int(self.main_pokemon.max_hp)))
        painter.drawText(hp_x, 238, str(int(self.main_pokemon.hp)))

        painter.setFont(msg_font)
        painter.setPen(QColor(31, 31, 39))  # Text color
        
        #Drawing enemy pokemon hp
        painter.setFont(hp_enemy_text_font)
        painter.setPen(QColor(31, 31, 39))  # Text color
        enemy_hp_x = 41 if int(self.enemy_pokemon.max_hp) < 100 else 40  # Shift left if 3 digits
        enemy_max_hp_x = 64 if int(self.enemy_pokemon.max_hp) < 100 else 56  # Shift left if 3 digits
        painter.drawText(enemy_hp_x, 84 if int(self.enemy_pokemon.max_hp) < 100 else 80 , str(int(self.enemy_pokemon.hp)) + "/")
        painter.drawText(enemy_max_hp_x, 84 if int(self.enemy_pokemon.max_hp) < 100 else 88, str(int(self.enemy_pokemon.max_hp)))

        painter.end()

        # Set the merged image as the pixmap for the QLabel
        image_label.setPixmap(merged_pixmap)

        return image_label

    def pokemon_display_item(self, item):
        bckgimage_path = addon_dir / "addon_sprites" / "starter_screen" / "bg.png"
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
        custom_font = load_custom_font(int(26), int(self.settings_obj.get("misc.language")))

        message_box_text = f"{self.translator.translate('received_an_item', item_name=item.capitalize())} !"

        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color

        painter.drawText(50, 290, message_box_text)

        custom_font = load_custom_font(int(20), int(self.settings_obj.get("misc.language")))
        painter.setFont(custom_font)
        #painter.drawText(10, 330, "You can look this up in your item bag.")

        painter.end()

        # Set the merged image as the pixmap for the QLabel
        image_label = QLabel()
        image_label.setPixmap(merged_pixmap)

        return image_label

    def pokemon_display_badge(self, badge_number):
        try:
            global badges

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
            custom_font = load_custom_font(int(20), int(self.settings_obj.get("misc.language")))

            message_box_text = self.translator.translate("received_a_badge")

            with open(badges_list_path, "r", encoding="utf-8") as json_file:
                badges = json.load(json_file)

            message_box_text2 = f"{badges[str(badge_number)]}!"

            # Draw the text on top of the image
            # Adjust the font size as needed
            painter.setFont(custom_font)
            painter.setPen(QColor(255,255,255))  # Text color

            painter.drawText(120, 270, message_box_text)
            painter.drawText(140, 290, message_box_text2)

            custom_font = load_custom_font(int(20), int(self.settings_obj.get("misc.language")))
            painter.setFont(custom_font)
            #painter.drawText(10, 330, "You can look this up in your item bag.")

            painter.end()

            # Set the merged image as the pixmap for the QLabel
            image_label = QLabel()
            image_label.setPixmap(merged_pixmap)

            return image_label

        except Exception as e:
            show_warning_with_traceback(parent=self, exception=e, message=f"An error occured in badges window {e}")

    def pokemon_display_dead_pokemon(self):
        caught = self.ankimon_tracker_obj.caught
        id = self.enemy_pokemon.id
        level = self.enemy_pokemon.level
        type = self.enemy_pokemon.type

        # Create the dialog
        lang_name = get_pokemon_diff_lang_name(int(id), int(self.settings_obj.get('misc.language')))

        self.setWindowTitle(f"{self.translator.translate('catch_or_free', enemy_pokemon_name=lang_name.capitalize())}")

        # Display the Pokémon image
        pkmnimage_file = f"{int(search_pokedex(self.enemy_pokemon.name.lower(),'num'))}.png"
        pkmnimage_path = frontdefault / pkmnimage_file

        pkmnimage_label = QLabel()
        pkmnpixmap = QPixmap()

        try:
            pkmnpixmap.load(str(pkmnimage_path))
        except:
            pkmnpixmap.load(str(self.default_path))

        pkmnpixmap_bckg = QPixmap()

        try:
            pkmnpixmap_bckg.load(str(pokedex_image_path))
        except:
            pkmnpixmap_bckg.load(str(self.default_path))

        # Calculate the new dimensions to maintain the aspect ratio
        pkmnpixmap = pkmnpixmap.scaled(230, 230)

        # Create a painter to add text on top of the image
        painter2 = QPainter(pkmnpixmap_bckg)
        painter2.drawPixmap(15,15,pkmnpixmap)

        # Create level text
        # Draw the text on top of the image
        font = QFont()
        font.setPointSize(20)  # Adjust the font size as needed
        painter2.setFont(font)

        painter2.drawText(270,107,f"{lang_name}")

        font.setPointSize(17)  # Adjust the font size as needed
        painter2.setFont(font)

        painter2.drawText(315,192,f"Level: {level}")
        types = self.enemy_pokemon.type or []
        type_text = ", ".join(t.capitalize() for t in types) if types else "Unknown"
        painter2.drawText(322, 225, f"Type: {type_text}")


        painter2.setFont(font)

        fontlvl = QFont()
        fontlvl.setPointSize(12)

        painter2.end()

        # Create a QLabel for the capitalized name
        name_label = QLabel(lang_name.capitalize())
        name_label.setFont(font)

        # Create a QLabel for the level
        level_label = QLabel(f"Level: {level}")
        # Align to the center
        level_label.setFont(fontlvl)

        nickname_input = QLineEdit()
        nickname_input.setPlaceholderText(self.translator.translate("choose_nickname"))
        nickname_input.setStyleSheet("background-color: rgb(44,44,44);")
        nickname_input.setFixedSize(120, 30)  # Adjust the size as needed

        # Create buttons for catching and killing the Pokémon
        catch_button = QPushButton(self.translator.translate("catch_button"))
        catch_button.setFixedSize(175, 30)  # Adjust the size as needed
        catch_button.setFont(QFont("Arial", 12))  # Adjust the font size and style as needed
        catch_button.setStyleSheet("background-color: rgb(44,44,44);")
        #catch_button.setFixedWidth(150)
        qconnect(catch_button.clicked, lambda: mw.catchpokemon())

        kill_button = QPushButton(self.translator.translate("defeat_button"))
        kill_button.setFixedSize(175, 30)  # Adjust the size as needed
        kill_button.setFont(QFont("Arial", 12))  # Adjust the font size and style as needed
        kill_button.setStyleSheet("background-color: rgb(44,44,44);")
        #kill_button.setFixedWidth(150)
        qconnect(kill_button.clicked,  lambda: mw.defeatpokemon())

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

    def display_battle(self):
        # pokemon encounter image
        self.clear_layout(self.layout())
        #self.setFixedWidth(556)
        #self.setFixedHeight(371)

        layout = self.layout()

        battle_widget = self.pokemon_display_battle()
        #battle_widget.setScaledContents(True) #scalable ankimon window

        layout.addWidget(battle_widget)

        self.setStyleSheet("background-color: rgb(44,44,44);")
        self.setLayout(layout)

        self.setMaximumWidth(556)
        self.setMaximumHeight(300)

    def rate_display_item(self, item):
        Receive_Window = QDialog(mw)
        layout = QHBoxLayout()

        item_widget = self.pokemon_display_item(item)

        layout.addWidget(item_widget)

        Receive_Window.setStyleSheet("background-color: rgb(44,44,44);")
        Receive_Window.setMaximumWidth(512)
        Receive_Window.setMaximumHeight(320)

        Receive_Window.setLayout(layout)
        Receive_Window.show()

    def display_item(self):
        Receive_Window = QDialog(mw)
        layout = QHBoxLayout()

        item_widget = self.pokemon_display_item(random_item())

        layout.addWidget(item_widget)

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

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()

            if widget:
                widget.deleteLater()

    def closeEvent(self,event):
        self.pkmn_window = False
