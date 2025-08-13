from aqt import gui_hooks, mw, utils
from aqt.utils import showInfo
from ..functions.pokemon_functions import find_experience_for_level
from ..business import get_image_as_base64
from ..functions.create_css_for_reviewer import create_css_for_reviewer
import json
from ..functions.create_gui_functions import create_status_html
from ..resources import icon_path
from ..functions.pokedex_functions import get_pokemon_diff_lang_name

from .pokemon_obj import PokemonObject

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
        gui_hooks.reviewer_did_answer_card.append(self.update_life_bar)

    def reviewer_reset_life_bar_inject(self):
        self.life_bar_injected = False

    def get_boost_values_string(self, pokemon: PokemonObject, display_neutral_boost: bool=False) -> str:
        """Generates a formatted string representing the stat boost multipliers of a Pokémon.
        
        This function retrieves the stat boost values of a given Pokémon, converts them into their
        corresponding multiplier strings (e.g., x1.5 for +1), and compiles them into a single
        display string. Neutral boosts (value of 0) can optionally be omitted from the output.
        
        Args:
            pokemon (PokemonObject): The Pokémon object containing current stat boost information.
            display_neutral_boost (bool, optional): If False, stat boosts with a value of 0 (neutral)
                are omitted from the output. Defaults to False.
        
        Returns:
            str: A string representing the stat boost multipliers.
        """
        pokemon_dict = pokemon.to_engine_format()
        boosts = {
            "atk": pokemon_dict.get('attack_boost', 0),
            "def": pokemon_dict.get('defense_boost', 0),
            "SpA": pokemon_dict.get('special_attack_boost', 0),
            "SpD": pokemon_dict.get('special_defense_boost', 0),
            "SPE": pokemon_dict.get('speed_boost', 0),
            "ACC": pokemon_dict.get('accuracy_boost', 0),
            "EVD": pokemon_dict.get('evasion_boost', 0),
        }
        
        boost_to_mult = {
            0: "x1", 1: "x1.5", 2: "x2", 3: "x2.5", 4: "x3", 5: "x3.5", 6: "x4",
            -1: "x0.67", -2: "x0.5", -3: "x0.4", -4: "x0.33", -5: "x0.29", -6: "x0.25",
        }
        
        boost_display = " "
        for key, boost_val in boosts.items():
            if display_neutral_boost is False and boost_val == 0:
                continue  # Do no display a neutral boost
            mult_str = boost_to_mult[boost_val]
            boost_display += f" | {key} {mult_str} | "
        
        return boost_display

    def inject_life_bar(self, web_content, context):
        """This function is now a no-op. The HUD is injected via the Shadow DOM portal."""
        return web_content

    def update_life_bar(self, reviewer, card, ease):
        if int(self.settings.get("gui.show_mainpkmn_in_reviewer", 1)) == 3:
            reviewer.web.eval("if(window.__ankimonHud) window.__ankimonHud.clear();")
            return

        # Keep existing logic to compute all values
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

        # Build hud_html
        hud_html = '<div id="ankimon-hud">'
        if self.settings.get("gui.hp_bar_config", True) is True:
            hud_html += '<div id="life-bar" class="Ankimon"></div>'
        if self.settings.get("gui.xp_bar_config", False) is True:
            hud_html += '<div id="xp-bar" class="Ankimon"></div>'
            hud_html += '<div id="next_lvl_text" class="Ankimon">Next Level</div>'
            hud_html += '<div id="xp_text" class="Ankimon">XP</div>'
        
        enemy_lang_name = (get_pokemon_diff_lang_name(int(self.enemy_pokemon.id), int(self.settings.get('misc.language'))).capitalize())
        if self.enemy_pokemon.shiny is True:
            enemy_lang_name += " ⭐ "
        name_display_text = f"{enemy_lang_name} LvL: {self.enemy_pokemon.level}"
        name_display_text += self.get_boost_values_string(self.enemy_pokemon, display_neutral_boost=False)
        hud_html += f'<div id="name-display" class="Ankimon">{name_display_text}</div>'
        
        if self.enemy_pokemon.hp > 0:
            hud_html += f'{create_status_html(f"{self.enemy_pokemon.battle_status}", settings_obj=self.settings)}'
        else:
            hud_html += f'{create_status_html("fainted", settings_obj=self.settings)}'

        hud_html += f'<div id="hp-display" class="Ankimon">HP: {self.enemy_pokemon.hp}/{self.enemy_pokemon.max_hp}</div>'
        hud_html += f'<div id="PokeImage" class="Ankimon"><img src="data:image/png;base64,{image_base64}" alt="PokeImage" style="animation: shake {self.seconds}s ease;"></div>'
        
        if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
            hud_html += f'<div id="MyPokeImage" class="Ankimon"><img src="data:image/png;base64,{image_base64_mainpkmn}" alt="MyPokeImage" style="animation: shake {self.myseconds}s ease;"></div>'
            main_lang_name = (get_pokemon_diff_lang_name(int(self.main_pokemon.id), int(self.settings.get('misc.language'))).capitalize())
            if self.main_pokemon.shiny:
                main_lang_name += " ⭐ "
            main_name_display_text = f"{main_lang_name} LvL: {self.main_pokemon.level}"
            main_name_display_text += self.get_boost_values_string(self.main_pokemon, display_neutral_boost=False)
            hud_html += f'<div id="myname-display" class="Ankimon">{main_name_display_text}</div>'
            hud_html += f'<div id="myhp-display" class="Ankimon">HP: {self.main_pokemon.hp}/{self.main_pokemon.max_hp}</div>'
            if self.settings.get("gui.hp_bar_config", True) is True:
                hud_html += '<div id="mylife-bar" class="Ankimon"></div>'

        if self.ankimon_tracker.pokemon_in_collection == True:
            icon_base_64 = get_image_as_base64(icon_path)
            hud_html += f'<div id="PokeIcon" class="Ankimon"><img src="data:image/png;base64,{icon_base_64}" alt="PokeIcon"></div>'
        else:
            hud_html += '<div id="PokeIcon" class="Ankimon"></div>'
        
        hud_html += '</div>'

        # Build hud_css
        hud_css = create_css_for_reviewer(
            int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)),
            pokemon_hp_percent,
            self.settings.get("battle.hp_bar_thickness", 2) * 4,
            int(self.settings.compute_special_variable('xp_bar_spacer')),
            self.settings.compute_special_variable('view_main_front'),
            int((self.main_pokemon.hp / self.main_pokemon.max_hp) * 50),
            int(self.settings.compute_special_variable('hp_only_spacer')),
            int(self.settings.compute_special_variable('wild_hp_spacer')),
            self.settings.get("gui.xp_bar_config", False),
            self.main_pokemon,
            int(find_experience_for_level(self.main_pokemon.growth_rate, self.main_pokemon.level, self.settings.get("remove_levelcap", False))),
            self.settings.compute_special_variable('xp_bar_location')
        )
        hud_css += """
        #ankimon-hud #name-display, #ankimon-hud #myname-display, #ankimon-hud #hp-display, #ankimon-hud #myhp-display, #ankimon-hud #next_lvl_text, #ankimon-hud #xp_text {
            background: white !important;
            color: var(--text-fg, #6D6D6E);
            border-radius: 5px !important;
            padding: 4px 8px !important;
        }

        @media (prefers-color-scheme: dark) {
            #ankimon-hud #name-display, #ankimon-hud #myname-display, #ankimon-hud #hp-display, #ankimon-hud #myhp-display, #ankimon-hud #next_lvl_text, #ankimon-hud #xp_text {
                background: #2C2C2C !important;
                color: white !important;
                border-radius: 5px !important;
                padding: 4px 8px !important;
            }
        }

        .night_mode #ankimon-hud #name-display, .night_mode #ankimon-hud #myname-display, .night_mode #ankimon-hud #hp-display, 
        .night_mode #ankimon-hud #myhp-display, .night_mode #ankimon-hud #next_lvl_text, .night_mode #ankimon-hud #xp_text {
            background: #2C2C2C !important;
            color: white !important;
            border-radius: 5px !important;
            padding: 4px 8px !important;
        }
        """

        # Use reviewer.web.eval to call the portal
        js_code = f"""
        (function(h,c){{
            if(window.__ankimonHud && window.__ankimonHud.update){{
                window.__ankimonHud.update(h,c);
            }}
        }})({json.dumps(hud_html)}, {json.dumps(hud_css)});
        """
        reviewer.web.eval(js_code)
