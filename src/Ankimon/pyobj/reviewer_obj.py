from aqt import gui_hooks, mw, utils
from aqt.utils import showInfo
from ..functions.pokemon_functions import find_experience_for_level
from ..business import get_image_as_base64
from ..functions.create_css_for_reviewer import create_css_for_reviewer
import json
import os
from ..functions.create_gui_functions import create_status_html
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
        """Generates a formatted string representing the stat boost multipliers of a Pokémon."""
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
                continue
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

        # Check if the enemy pokemon is in the user's collection
        enemy_name_lower = self.enemy_pokemon.name.lower()
        is_pokemon_owned = False
        try:
            addon_package = mw.addonManager.addonFromModule(__name__)
            collection_path = os.path.join(mw.addonManager.addonsFolder(), addon_package, "user_files", "mypokemon.json")
            if os.path.exists(collection_path):
                with open(collection_path, 'r', encoding='utf-8') as f:
                    my_pokemon_list = json.load(f)
                for p in my_pokemon_list:
                    if p.get('name', '').lower() == enemy_name_lower:
                        is_pokemon_owned = True
                        break
        except Exception:
            pass

        image_format = "gif" if self.settings.get('gui.reviewer_image_gif', 1) else "png"
        mime_type = f"image/{image_format}"

        pokemon_image_file = self.enemy_pokemon.get_sprite_path("front", image_format)
        
        main_pkmn_imagefile_path = None
        side = "back" # Default side
        if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
            if image_format == "gif":
                if self.settings.compute_special_variable('view_main_front') == -1:
                    side = "front"
                else:
                    side = "back"
            else: # png
                side = "back"
            main_pkmn_imagefile_path = self.main_pokemon.get_sprite_path(side, image_format)

        if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
            pokemon_hp_percent = int((self.enemy_pokemon.hp / self.enemy_pokemon.max_hp) * 50) if self.enemy_pokemon.max_hp > 0 else 0
            mainpkmn_hp_percent = int((self.main_pokemon.hp / self.main_pokemon.max_hp) * 50) if self.main_pokemon.max_hp > 0 else 0
            image_base64_mainpkmn = get_image_as_base64(main_pkmn_imagefile_path)
        else:
            pokemon_hp_percent = int((self.enemy_pokemon.hp / self.enemy_pokemon.max_hp) * 100) if self.enemy_pokemon.max_hp > 0 else 0
            mainpkmn_hp_percent = 0 # Not used in this mode
        
        enemy_hp_true_percent = (self.enemy_pokemon.hp / self.enemy_pokemon.max_hp) * 100 if self.enemy_pokemon.max_hp > 0 else 0
        main_hp_true_percent = (self.main_pokemon.hp / self.main_pokemon.max_hp) * 100 if self.main_pokemon.max_hp > 0 else 0

        image_base64 = get_image_as_base64(pokemon_image_file)

        # Build hud_html
        hud_html = '<div id="ankimon-hud">'
        if self.settings.get("gui.hp_bar_config", True) is True:
            hud_html += '<div id="life-bar" class="Ankimon"></div>'
        if self.settings.get("gui.xp_bar_config", False) is True:
            hud_html += '<div id="xp-bar" class="Ankimon"></div>'
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
        
        indicator_html = ''
        if is_pokemon_owned:
            addon_package = mw.addonManager.addonFromModule(__name__)
            pokeball_url = f"/_addons/{addon_package}/user_files/web/images/pokeball.png"
            indicator_html = f'<img id="owned-indicator-badge" src="{pokeball_url}">'
        
        enemy_poke_animation_style = f"animation: ankimon-shake-normal {self.seconds}s ease;"
        hud_html += f'<div id="PokeImage" class="Ankimon">{indicator_html}<img src="data:{mime_type};base64,{image_base64}" alt="PokeImage" style="{enemy_poke_animation_style}"></div>'
        
        if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) > 0:
            
            my_poke_html_attributes = ""
            # SPECIAL CASE: For front-facing GIFs, the animation conflicts with the transform.
            # We will sacrifice the animation in this case to force the flip using a static class.
            if image_format == "gif" and side == "front":
                my_poke_html_attributes = 'class="force-flip"'
            else:
                # For all other cases, the flipped animation works correctly.
                animation_style = f"animation: ankimon-shake-flipped {self.myseconds}s ease;"
                my_poke_html_attributes = f'style="{animation_style}"'

            hud_html += (f'<div id="MyPokeImage" class="Ankimon">'
                         f'<img src="data:{mime_type};base64,{image_base64_mainpkmn}" alt="MyPokeImage" {my_poke_html_attributes}>'
                         f'</div>')

            main_lang_name = (get_pokemon_diff_lang_name(int(self.main_pokemon.id), int(self.settings.get('misc.language'))).capitalize())
            if self.main_pokemon.shiny:
                main_lang_name += " ⭐ "
            main_name_display_text = f"{main_lang_name} LvL: {self.main_pokemon.level}"
            main_name_display_text += self.get_boost_values_string(self.main_pokemon, display_neutral_boost=False)
            hud_html += f'<div id="myname-display" class="Ankimon">{main_name_display_text}</div>'
            hud_html += f'<div id="myhp-display" class="Ankimon">HP: {self.main_pokemon.hp}/{self.main_pokemon.max_hp}</div>'
            if self.settings.get("gui.hp_bar_config", True) is True:
                hud_html += '<div id="mylife-bar" class="Ankimon"></div>'

        hud_html += '</div>'

        # Build hud_css
        hud_css = create_css_for_reviewer(
            int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)),
            pokemon_hp_percent,
            self.settings.get("battle.hp_bar_thickness", 2) * 4,
            int(self.settings.compute_special_variable('xp_bar_spacer')),
            -1 if int(self.settings.get('gui.show_mainpkmn_in_reviewer', 1)) == 1 else self.settings.compute_special_variable('view_main_front'),
            mainpkmn_hp_percent,
            int(self.settings.compute_special_variable('hp_only_spacer')),
            int(self.settings.compute_special_variable('wild_hp_spacer')),
            self.settings.get("gui.xp_bar_config", False),
            self.main_pokemon,
            int(find_experience_for_level(self.main_pokemon.growth_rate, self.main_pokemon.level, self.settings.get("remove_levelcap", False))),
            self.settings.compute_special_variable('xp_bar_location'),
            enemy_hp_true_percent,
            main_hp_true_percent
        )
        hud_css += """
        #ankimon-hud #name-display, #ankimon-hud #myname-display, #ankimon-hud #hp-display, #ankimon-hud #myhp-display, #ankimon-hud #xp_text {
            font-family: Arial, sans-serif;
            background: white !important;
            color: var(--text-fg, #6D6D6E);
            border-radius: 5px !important;
            padding: 4px 8px !important;
        }

        @media (prefers-color-scheme: dark) {
            #ankimon-hud #name-display, #ankimon-hud #myname-display, #ankimon-hud #hp-display, #ankimon-hud #myhp-display, #ankimon-hud #xp_text {
                font-family: Arial, sans-serif;
                background: #1f1f1f !important;
                color: white !important;
                border-radius: 5px !important;
                padding: 4px 8px !important;
            }
        }

        .night_mode #ankimon-hud #name-display, .night_mode #ankimon-hud #myname-display, .night_mode #ankimon-hud #hp-display, 
        .night_mode #ankimon-hud #myhp-display, .night_mode #ankimon-hud{
            font-family: Arial, sans-serif;
            background: #1f1f1f !important;
            color: white !important;
            border-radius: 5px !important;
            padding: 4px 8px !important;
        }

        .night_mode #xp_text {
            font-color: rgba(0, 191, 255, 0.85)
            font-family: Arial, sans-serif;
            background: #1f1f1f !important;
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
