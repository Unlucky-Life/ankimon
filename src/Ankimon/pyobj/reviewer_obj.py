from aqt import gui_hooks, mw, utils
from aqt.utils import showInfo
from ..functions.pokemon_functions import find_experience_for_level
from ..business import get_image_as_base64
from ..functions.create_css_for_reviewer import create_css_for_reviewer
from ..texts import inject_life_bar_css_1, inject_life_bar_css_2
from ..functions.create_gui_functions import create_status_html
from ..resources import icon_path

class Reviewer_Manager:
    def __init__(self, settings_obj, main_pokemon, enemy_pokemon, ankimon_tracker):
        self.settings = settings_obj
        self.main_pokemon = main_pokemon
        self.enemy_pokemon = enemy_pokemon
        self.ankimon_tracker = ankimon_tracker
        self.life_bar_injected = False
        self.seconds = 0
        self.myseconds = 0
    
        # Register the functions for the hooks
        gui_hooks.reviewer_will_end.append(self.reviewer_reset_life_bar_inject)
        gui_hooks.webview_will_set_content.append(self.inject_life_bar)
        gui_hooks.reviewer_did_answer_card.append(self.update_life_bar)

    def reviewer_reset_life_bar_inject(self):
        self.life_bar_injected = False

    def inject_life_bar(self, web_content, context):
        if int(self.settings.get("gui.show_mainpkmn_in_reviewer", 1)) < 3:
            if self.settings.get('gui.reviewer_image_gif', 1) == False:
                pokemon_image_file = self.enemy_pokemon.get_sprite_path("front", "png")
                if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
                    main_pkmn_imagefile_path = self.main_pokemon.get_sprite_path("back", "png")
            else:
                pokemon_image_file = self.enemy_pokemon.get_sprite_path("front", "gif")
                if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
                    if int(self.settings.compute_special_variable('view_main_front')) == -1:
                        side = "front"
                    else:
                        side = "back"
                    main_pkmn_imagefile_path = self.main_pokemon.get_sprite_path(side, "gif")
            if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
                pokemon_hp_percent = int((self.enemy_pokemon.hp / self.enemy_pokemon.max_hp) * 50)
            else:    
                pokemon_hp_percent = int((self.enemy_pokemon.hp / self.enemy_pokemon.max_hp) * 100)
            is_reviewer = mw.state == "review"
            # Inject CSS and the life bar only if not injected before and in the reviewer
            self.ankimon_tracker.check_pokecoll_in_list()
            if not self.life_bar_injected and is_reviewer:
                css = create_css_for_reviewer(int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)), pokemon_hp_percent, self.settings.get("battle.hp_bar_thickness", 2) * 4, int(self.settings.compute_special_variable('xp_bar_spacer')), self.settings.compute_special_variable('view_main_front'), int((self.main_pokemon.hp / self.main_pokemon.max_hp) * 50), int(self.settings.compute_special_variable('hp_only_spacer')), int(self.settings.compute_special_variable('wild_hp_spacer')), self.settings.get("gui.xp_bar_config", False), self.main_pokemon, int(find_experience_for_level(self.main_pokemon.growth_rate, self.main_pokemon.level, self.settings.get("remove_levelcap", False))), self.settings.compute_special_variable('xp_bar_location'))
                css += inject_life_bar_css_1
                css += inject_life_bar_css_2
                # background-image: url('{pokemon_image_file}'); Change to your image path */
                if self.settings.get("gui.styling_in_reviewer", True) is True:
                    # Inject the CSS into the head of the HTML content
                    web_content.head += f"<style>{css}</style>"
                    # Inject a div element at the end of the body for the life bar
                    #web_content.body += f'<div id="pokebackground">' try adding backgroudns to battle
                    if self.settings.get("gui.hp_bar_config", True) is True:
                        web_content.body += '<div id="life-bar" class="Ankimon"></div>'
                    if self.settings.get("gui.xp_bar_config", False) is True:
                        web_content.body += '<div id="xp-bar" class="Ankimon"></div>'
                        web_content.body += '<div id="next_lvl_text" class="Ankimon">Next Level</div>'
                        web_content.body += '<div id="xp_text" class="Ankimon">XP</div>'
                    # Inject a div element for the text display
                    web_content.body += f'<div id="name-display" class="Ankimon">{self.enemy_pokemon.name.capitalize()} LvL: {self.enemy_pokemon.level}</div>'
                    if self.enemy_pokemon.hp > 0:
                        web_content.body += f'{create_status_html(f"{self.enemy_pokemon.battle_status}", settings_obj=self.settings)}'
                    else:
                        web_content.body += f'{create_status_html("fainted", settings_obj=self.settings)}'

                    web_content.body += f'<div id="hp-display" class="Ankimon">HP: {self.enemy_pokemon.hp}/{self.enemy_pokemon.max_hp}</div>'
                    # Inject a div element at the end of the body for the life bar
                    image_base64 = get_image_as_base64(pokemon_image_file)
                    web_content.body += f'<div id="PokeImage" class="Ankimon"><img src="data:image/png;base64,{image_base64}" alt="PokeImage style="animation: shake 0s ease;"></div>'
                    if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
                        image_base64_mypkmn = get_image_as_base64(main_pkmn_imagefile_path)
                        web_content.body += f'<div id="MyPokeImage" class="Ankimon"><img src="data:image/png;base64,{image_base64_mypkmn}" alt="MyPokeImage" style="animation: shake 0s ease;"></div>'
                        web_content.body += f'<div id="myname-display" class="Ankimon">{self.main_pokemon.name.capitalize()} LvL: {self.main_pokemon.level}</div>'
                        web_content.body += f'<div id="myhp-display" class="Ankimon">HP: {self.main_pokemon.hp}/{self.main_pokemon.max_hp}</div>'
                        # Inject a div element at the end of the body for the life bar
                        if self.settings.get("gui.hp_bar_config", True) is True:
                            web_content.body += '<div id="mylife-bar" class="Ankimon"></div>'
                    # Set the flag to True to indicate that the life bar has been injected
                    if self.ankimon_tracker.pokemon_in_collection == True:
                        icon_base_64 = get_image_as_base64(icon_path)
                        web_content.body += f'<div id="PokeIcon" class="Ankimon"><img src="data:image/png;base64,{icon_base_64}" alt="PokeIcon"></div>'
                    else:
                        web_content.body += '<div id="PokeIcon" class="Ankimon"></div>'
                    web_content.body += '</div>'
                    self.life_bar_injected = True
        return web_content

    def update_life_bar(self, reviewer, card, ease):
        if int(self.settings.get("gui.show_mainpkmn_in_reviewer", 1)) < 3:
            self.ankimon_tracker.check_pokecoll_in_list()
            if self.settings.get('gui.reviewer_image_gif', 1) == False:
                pokemon_image_file = self.enemy_pokemon.get_sprite_path("front", "png")
                if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
                    main_pkmn_imagefile_path = self.main_pokemon.get_sprite_path("back", "png")
            else:
                pokemon_image_file = self.enemy_pokemon.get_sprite_path("front", "gif")
                if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
                    if self.settings.compute_special_variable('view_main_front') == -1:
                        side = "front"
                    else:
                        side = "back"
                    main_pkmn_imagefile_path = self.main_pokemon.get_sprite_path(side, "gif")
            if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
                pokemon_hp_percent = int((self.enemy_pokemon.hp / self.enemy_pokemon.max_hp) * 50)
                image_base64_mainpkmn = get_image_as_base64(main_pkmn_imagefile_path)
            else:    
                pokemon_hp_percent = int((self.enemy_pokemon.hp / self.enemy_pokemon.max_hp) * 100)
            image_base64 = get_image_as_base64(pokemon_image_file)
            # Determine the color based on the percentage
            if self.enemy_pokemon.hp < int(0.25 * self.enemy_pokemon.max_hp):
                hp_color = "rgba(255, 0, 0, 0.7)"  # Red
            elif self.enemy_pokemon.hp < int(0.5 * self.enemy_pokemon.max_hp):
                hp_color = "rgba(255, 140, 0, 0.7)"  # Dark Orange
            elif self.enemy_pokemon.hp < int(0.75 * self.enemy_pokemon.max_hp):
                hp_color = "rgba(255, 255, 0, 0.7)"  # Yellow
            else:
                hp_color = "rgba(114, 230, 96, 0.7)"  # Green

            if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
                if self.main_pokemon.hp < int(0.25 * self.main_pokemon.hp):
                    myhp_color = "rgba(255, 0, 0, 0.7)"  # Red
                elif self.main_pokemon.hp < int(0.5 * self.main_pokemon.hp):
                    myhp_color = "rgba(255, 140, 0, 0.7)"  # Dark Orange
                elif self.main_pokemon.hp < int(0.75 * self.main_pokemon.hp):
                    myhp_color = "rgba(255, 255, 0, 0.7)"  # Yellow
                else:
                    myhp_color = "rgba(114, 230, 96, 0.7)"  # Green
            # Extract RGB values from the hex color code
            #hex_color = hp_color.lstrip('#')
            #rgb_values = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
            status_html = ""
            if self.enemy_pokemon.hp < 1:
                status_html = create_status_html('fainted', settings_obj=self.settings)
            elif self.enemy_pokemon.hp > 0:
                status_html = create_status_html(f"{self.enemy_pokemon.battle_status}", settings_obj=self.settings)
            if self.settings.get("gui.styling_in_reviewer", True) is True:
                # Refresh the reviewer content to apply the updated life bar
                reviewer.web.eval('document.getElementById("life-bar").style.width = "' + str(pokemon_hp_percent) + '%";')
                reviewer.web.eval('document.getElementById("life-bar").style.background = "linear-gradient(to right, ' + str(hp_color) + ', ' + str(hp_color) + ' ' + '100' + '%, ' + 'rgba(54, 54, 56, 0.7)' + '100' + '%, ' + 'rgba(54, 54, 56, 0.7)' + ')";')
                reviewer.web.eval('document.getElementById("life-bar").style.boxShadow = "0 0 10px ' + hp_color + ', 0 0 30px rgba(54, 54, 56, 1)";')
                if self.settings.get("xp_bar_config", False) is True:
                    experience_for_next_lvl = int(find_experience_for_level(self.main_pokemon.growth_rate, self.main_pokemon.level, self.settings.get("remove_levelcap", False)))
                    xp_bar_percent = int((self.main_pokemon.xp / int(experience_for_next_lvl)) * 100)
                    reviewer.web.eval('document.getElementById("xp-bar").style.width = "' + str(xp_bar_percent) + '%";')
                name_display_text = f"{self.enemy_pokemon.name.capitalize()} LvL: {self.enemy_pokemon.level}"
                hp_display_text = f"HP: {self.enemy_pokemon.hp}/{self.enemy_pokemon.max_hp}"
                reviewer.web.eval('document.getElementById("name-display").innerText = "' + name_display_text + '";')
                reviewer.web.eval('document.getElementById("hp-display").innerText = "' + hp_display_text + '";')
                new_html_content = f'<img src="data:image/png;base64,{image_base64}" alt="PokeImage" style="animation: shake {self.seconds}s ease;">'
                reviewer.web.eval(f'document.getElementById("PokeImage").innerHTML = `{new_html_content}`;')
                if self.ankimon_tracker.pokemon_in_collection == True:
                    image_icon_path = get_image_as_base64(icon_path)
                    pokeicon_html = f'<img src="data:image/png;base64,{image_icon_path}" alt="PokeIcon">'
                else:
                    pokeicon_html = ''
                reviewer.web.eval(f'document.getElementById("PokeIcon").innerHTML = `{pokeicon_html}`;')
                reviewer.web.eval(f'document.getElementById("pokestatus").innerHTML = `{status_html}`;')
                if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
                    new_html_content_mainpkmn = f'<img src="data:image/png;base64,{image_base64_mainpkmn}" alt="MyPokeImage" style="animation: shake {self.myseconds}s ease;">'
                    main_name_display_text = f"{self.main_pokemon.name.capitalize()} LvL: {self.main_pokemon.level}"
                    main_hp_display_text = f"HP: {self.main_pokemon.hp}/{self.main_pokemon.max_hp}"
                    reviewer.web.eval('document.getElementById("mylife-bar").style.width = "' + str(int((self.main_pokemon.hp / self.main_pokemon.max_hp) * 50)) + '%";')
                    reviewer.web.eval('document.getElementById("mylife-bar").style.background = "linear-gradient(to right, ' + str(myhp_color) + ', ' + str(myhp_color) + ' ' + '100' + '%, ' + 'rgba(54, 54, 56, 0.7)' + '100' + '%, ' + 'rgba(54, 54, 56, 0.7)' + ')";')
                    reviewer.web.eval('document.getElementById("mylife-bar").style.boxShadow = "0 0 10px ' + myhp_color + ', 0 0 30px rgba(54, 54, 56, 1)";')
                    reviewer.web.eval(f'document.getElementById("MyPokeImage").innerHTML = `{new_html_content_mainpkmn}`;')
                    reviewer.web.eval('document.getElementById("myname-display").innerText = "' + main_name_display_text + '";')
                    reviewer.web.eval('document.getElementById("myhp-display").innerText = "' + main_hp_display_text + '";')
        else:
            pass