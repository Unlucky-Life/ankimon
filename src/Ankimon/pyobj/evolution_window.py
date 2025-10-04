import json
import random

from aqt import mw
from aqt.utils import showWarning
from aqt.qt import (
    QFont,
    QLabel,
    QPainter,
    QPixmap,
    QVBoxLayout,
    QWidget,
    QDialog,
    qconnect,
    )
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtWidgets import (
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    )

from ..utils import limit_ev_yield, load_custom_font
from ..functions.pokedex_functions import return_name_for_id, search_pokeapi_db_by_id, search_pokedex
from ..functions.pokemon_functions import get_random_moves_for_pokemon
from ..functions.battle_functions import calculate_hp
from ..functions.update_main_pokemon import update_main_pokemon
from ..functions.badges_functions import check_for_badge, receive_badge
from ..pyobj.attack_dialog import AttackDialog
from ..pyobj.settings import Settings
from ..pyobj.pokemon_obj import PokemonObject
from ..pyobj.InfoLogger import ShowInfoLogger
from ..pyobj.translator import Translator
from ..pyobj.test_window import TestWindow
from ..pyobj.reviewer_obj import Reviewer_Manager
from ..pyobj.error_handler import show_warning_with_traceback
from ..business import resize_pixmap_img
from ..resources import (
    addon_dir,
    frontdefault,
    evolve_image_path,
    mainpokemon_path,
    mypokemon_path,
)

class EvoWindow(QWidget):
    def __init__(
            self,
            logger: ShowInfoLogger,
            settings_obj: Settings,
            main_pokemon: PokemonObject,
            enemy_pokemon: PokemonObject,
            translator: Translator,
            reviewer_obj: Reviewer_Manager,
            test_window: TestWindow,
            achievements: dict,
            ):
        super().__init__()
        self.init_ui()

        # To avoid circular imports, instead of importing those things, we
        # save a reference to them as an attribute
        self.logger = logger
        self.settings_obj = settings_obj
        self.main_pokemon = main_pokemon
        self.enemy_pokemon = enemy_pokemon
        self.translator = translator
        self.reviewer_obj = reviewer_obj
        self.test_window = test_window
        self.achievements = achievements

    def init_ui(self):
        basic_layout = QVBoxLayout()
        self.setWindowTitle('Your Pokemon is about to Evolve')
        self.setLayout(basic_layout)

    def open_dynamic_window(self):
        self.show()

    def display_evo_pokemon(self, prevo_id, evo_id):
        self.clear_layout(self.layout())
        layout = self.layout()
        pkmn_label = self.pokemon_display_evo(prevo_id, evo_id)
        layout.addWidget(pkmn_label)
        self.setStyleSheet("background-color: rgb(14,14,14);")
        self.setLayout(layout)
        self.setMaximumWidth(500)
        self.setMaximumHeight(300)
        self.show()

    def pokemon_display_evo(self, prevo_id, evo_id):
        bckgimage_path = addon_dir / "addon_sprites" / "starter_screen" / "bg.png"
        prevo_name = return_name_for_id(prevo_id)
        evo_name = return_name_for_id(evo_id)

        # Load the background image
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(bckgimage_path))

        # Display the Pokémon image
        image_path = frontdefault / f"{evo_id}.png"
        image_label = QLabel()
        image_pixmap = QPixmap()
        image_pixmap.load(str(image_path))
        image_pixmap = resize_pixmap_img(image_pixmap, 250)

        # Merge the background image and the Pokémon image
        merged_pixmap = QPixmap(pixmap_bckg.size())
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        #merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        # draw background to a specific pixel
        painter.drawPixmap(0, 0, pixmap_bckg)
        painter.drawPixmap(125,10,image_pixmap)

        # custom font
        custom_font = load_custom_font(int(20), int(self.settings_obj.get("misc.language",11)))
        message_box_text = f"{(prevo_name).capitalize()} has evolved to {(evo_name).capitalize()} !"
        self.logger.log("game", message_box_text)
        # Draw the text on top of the image
        # Adjust the font size as needed
        painter.setFont(custom_font)
        painter.setPen(QColor(255,255,255))  # Text color
        painter.drawText(40, 290, message_box_text)
        painter.end()
        # Set the merged image as the pixmap for the QLabel
        pkmn_label = QLabel()
        pkmn_label.setPixmap(merged_pixmap)

        return pkmn_label

    def display_pokemon_evo(self, individual_id, prevo_id, evo_id):
        self.setMaximumWidth(600)
        self.setMaximumHeight(530)
        self.clear_layout(self.layout())
        layout = self.layout()
        pokemon_images, evolve_button, dont_evolve_button = self.pokemon_display_evo_pokemon(individual_id, prevo_id, evo_id)
        layout.addWidget(pokemon_images)
        layout.addWidget(evolve_button)
        layout.addWidget(dont_evolve_button)
        self.setStyleSheet("background-color: rgb(44,44,44);")
        self.setLayout(layout)
        self.show()

    def pokemon_display_evo_pokemon(self, individual_id, prevo_id, evo_id):
        # Update mainpokemon_evolution and handle evolution logic
        prevo_name = return_name_for_id(prevo_id)
        evo_name = return_name_for_id(evo_id)

        # Display the Pokémon image
        pkmnimage_path = frontdefault / f"{prevo_id}.png"
        pkmnimage_path2 = frontdefault / f"{(evo_id)}.png"
        pkmnpixmap = QPixmap()
        pkmnpixmap.load(str(pkmnimage_path))
        pkmnpixmap2 = QPixmap()
        pkmnpixmap2.load(str(pkmnimage_path2))
        pixmap_bckg = QPixmap()
        pixmap_bckg.load(str(evolve_image_path))
        # Calculate the new dimensions to maintain the aspect ratio
        max_width = 200
        original_width = pkmnpixmap.width()
        original_height = pkmnpixmap.height()

        if original_width > max_width:
            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pkmnpixmap = pkmnpixmap.scaled(new_width, new_height)


        # Calculate the new dimensions to maintain the aspect ratio
        max_width = 200
        original_width = pkmnpixmap.width()
        original_height = pkmnpixmap.height()

        if original_width > max_width:
            new_width = max_width
            new_height = (original_height * max_width) // original_width
            pkmnpixmap2 = pkmnpixmap2.scaled(new_width, new_height)

        # Merge the background image and the Pokémon image
        merged_pixmap = QPixmap(pixmap_bckg.size())
        merged_pixmap.fill(QColor(0, 0, 0, 0))  # RGBA where A (alpha) is 0 for full transparency
        #merged_pixmap.fill(Qt.transparent)
        # merge both images together
        painter = QPainter(merged_pixmap)
        painter.drawPixmap(0,0,pixmap_bckg)
        painter.drawPixmap(255,70,pkmnpixmap)
        painter.drawPixmap(255,285,pkmnpixmap2)
        # Draw the text on top of the image
        font = QFont()
        font.setPointSize(12)  # Adjust the font size as needed
        painter.setFont(font)
        #fontlvl = QFont()
        #fontlvl.setPointSize(12)
        # Create a QPen object for the font color
        pen = QPen()
        pen.setColor(QColor(255, 255, 255))
        painter.setPen(pen)
        painter.drawText(150,35,f"{prevo_name.capitalize()} is evolving to {evo_name.capitalize()}")
        painter.drawText(95,430,"Please Choose to Evolve Your Pokemon or Cancel Evolution")
        # Capitalize the first letter of the Pokémon's name
        #name_label = QLabel(capitalized_name)
        painter.end()
        # Capitalize the first letter of the Pokémon's name

        # Create buttons for catching and killing the Pokémon
        evolve_button = QPushButton("Evolve Pokémon")
        dont_evolve_button = QPushButton("Cancel Evolution")
        qconnect(evolve_button.clicked, lambda: self.evolve_pokemon(individual_id, prevo_name, evo_id, evo_name, self.main_pokemon))
        qconnect(dont_evolve_button.clicked, lambda: self.cancel_evolution(individual_id, prevo_name))

        # Set the merged image as the pixmap for the QLabel
        evo_image_label = QLabel()
        evo_image_label.setPixmap(merged_pixmap)

        return evo_image_label, evolve_button, dont_evolve_button

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def evolve_pokemon(self, individual_id, prevo_name, evo_id, evo_name, main_pokemon):
        #global achievements
        try:
            with open(mypokemon_path, "r", encoding="utf-8") as json_file:
                captured_pokemon_data = json.load(json_file)
                pokemon = None
                if captured_pokemon_data:
                    for pokemon_data in captured_pokemon_data:
                        if pokemon_data['individual_id'] == individual_id:
                            pokemon = pokemon_data
                            if pokemon is not None:
                                prevo_id = pokemon["id"]
                                pokemon["name"] = evo_name.capitalize()
                                pokemon["id"] = evo_id
                                pokemon["type"] = search_pokedex(evo_name.lower(), "types")
                                pokemon["evos"] = []
                                attacks = pokemon["attacks"]
                                new_attacks = get_random_moves_for_pokemon(evo_name.lower(), int(pokemon["level"]))
                                for new_attack in new_attacks:
                                    if new_attack not in new_attacks:
                                        if len(attacks) < 4:
                                            attacks.append(new_attack)
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
                                                    self.logger.log_and_showinfo("info", self.translator.translate("replaced_selected_attack", selected_attack=selected_attack, new_attack=new_attack))
                                                else:
                                                    self.logger.log_and_showinfo("info", self.translator.translate("selected_attack_not_found", selected_attack=selected_attack))
                                            else:
                                                # Handle the case where the user cancels the dialog
                                                self.logger.log_and_showinfo("info", self.translator.translate("no_attack_selected"))
                                pokemon["attacks"] = attacks
                                base_stats = search_pokedex(evo_name.lower(), "baseStats")
                                pokemon["base_stats"] = base_stats
                                pokemon["stats"] = base_stats
                                pokemon["xp"] = 0
                                hp_stat = int(base_stats['hp'])
                                iv = pokemon["iv"]
                                ev = pokemon["ev"]
                                level = pokemon["level"]
                                hp = calculate_hp(hp_stat, level, ev, iv)
                                pokemon["current_hp"] = int(hp)
                                pokemon["growth_rate"] = search_pokeapi_db_by_id(evo_id,"growth_rate")
                                pokemon["base_experience"] = search_pokeapi_db_by_id(evo_id,"base_experience")
                                abilities = search_pokedex(evo_name.lower(), "abilities")
                                numeric_abilities = None
                                try:
                                    numeric_abilities = {k: v for k, v in abilities.items() if k.isdigit()}
                                except Exception:
                                    ability = self.translator.translate("no_ability")
                                if numeric_abilities:
                                    abilities_list = list(numeric_abilities.values())
                                    pokemon["ability"] = random.choice(abilities_list)
                                else:
                                    pokemon["ability"] = self.translator.translate("no_ability")
                                with open(str(mypokemon_path), "r", encoding="utf-8") as output_file:
                                    mypokemondata = json.load(output_file)
                                    # Find and replace the specified Pokémon's data in mypokemondata
                                    for index, pokemon_data in enumerate(mypokemondata):
                                        if pokemon_data["individual_id"] == individual_id:
                                            mypokemondata[index] = pokemon
                                            break
                                            # Save the modified data to the output JSON file
                                    with open(str(mypokemon_path), "w") as output_file:
                                        json.dump(mypokemondata, output_file, indent=2)
                                self.logger.log_and_showinfo("info", self.translator.translate("mainpokemon_has_evolved", prevo_name=prevo_name, evo_name=evo_name))
        except Exception as e:
            show_warning_with_traceback(parent=mw, exception=e, message=f"Error occured in evolving pokemon")
            self.logger.log(f"{e}")

        try:  # Update Main Pokemon Object and sync with file
            if main_pokemon is not None and main_pokemon.individual_id == individual_id:
                # Update the in-memory main_pokemon object with the evolved data                # Call update_main_pokemon to ensure file and object are in sync (this will also save to disk)
                main_pokemon, _ = update_main_pokemon(main_pokemon)
                # Update UI as before
                class Container(object):
                    pass
                reviewer = Container()
                reviewer.web = mw.reviewer.web
                self.reviewer_obj.update_life_bar(reviewer, 0, 0)
                if self.test_window.isVisible() is True:
                    self.test_window.display_first_encounter()
        except Exception as e:
            show_warning_with_traceback(parent=mw, exception=e, message=f"Error occured in updating main_pokemon obj")
        self.display_evo_pokemon(prevo_id, evo_id)
        check = check_for_badge(self.achievements, 16)
        if check is False:
            receive_badge(16, self.achievements)

    def cancel_evolution(self, individual_id, prevo_name):
        try:
            with open(mypokemon_path, "r+", encoding="utf-8") as f:
                all_pokemon = json.load(f)

                pokemon_to_update = None
                for p in all_pokemon:
                    if p.get("individual_id") == individual_id:
                        pokemon_to_update = p
                        break
                
                if not pokemon_to_update:
                    self.logger.log(f"Could not find pokemon with individual_id {individual_id} to cancel evolution.")
                    return

                # Add logic to learn new moves, similar to the original function
                attacks = pokemon_to_update.get("attacks", [])
                # The level should come from the pokemon itself, not self.main_pokemon
                level = pokemon_to_update.get("level", 1) 
                new_attacks = get_random_moves_for_pokemon(prevo_name.lower(), int(level))
                
                for new_attack in new_attacks:
                    if new_attack not in attacks:
                        if len(attacks) < 4:
                            attacks.append(new_attack)
                        else:
                            # Attack replacement dialog
                            dialog = AttackDialog(attacks, new_attack)
                            if dialog.exec() == QDialog.DialogCode.Accepted:
                                selected_attack = dialog.selected_attack
                                try:
                                    index_to_replace = attacks.index(selected_attack)
                                    attacks[index_to_replace] = new_attack
                                    self.logger.log_and_showinfo("info", self.translator.translate("replaced_attack", selected_attack=selected_attack, new_attack=new_attack))
                                except ValueError:
                                    self.logger.log_and_showinfo("info", self.translator.translate("selected_attack_not_found", selected_attack=selected_attack))
                            else:
                                self.logger.log_and_showinfo("info", self.translator.translate("no_attack_selected"))
                
                pokemon_to_update["attacks"] = attacks
                # Set everstone to true to prevent evolution loop
                pokemon_to_update["everstone"] = True

                # Write the changes back to the file
                f.seek(0)
                json.dump(all_pokemon, f, indent=2)
                f.truncate()

            # If the main pokemon was the one, update its object in memory
            if self.main_pokemon and self.main_pokemon.individual_id == individual_id:
                # This function reloads from file, so it will get the changes we just saved
                self.main_pokemon, _ = update_main_pokemon(self.main_pokemon)

            self.logger.log_and_showinfo("info", f"Canceled evolution for {prevo_name}.")
            self.close() # Close the window after action is taken

        except Exception as e:
            show_warning_with_traceback(parent=mw, exception=e, message="Error occurred while canceling evolution")
            self.logger.log(f"Error in cancel_evolution: {e}")