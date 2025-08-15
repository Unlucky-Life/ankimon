def create_css_for_reviewer(
    show_mainpkmn_in_reviewer,
    pokemon_hp_percent,
    hp_bar_thickness,
    xp_bar_spacer,
    view_main_front,
    mainpkmn_hp_percent,
    hp_only_spacer,
    wild_hp_spacer,
    xp_bar_config,
    main_pokemon,
    experience_for_next_lvl,
    xp_bar_location,
    enemy_hp_true_percent,
    main_hp_true_percent
):
    css = ""

    # Determine HP bar colors
    if enemy_hp_true_percent <= 25:
        enemy_hp_color = "rgba(255, 0, 0, 0.85)"  # Red
    elif enemy_hp_true_percent <= 50:
        enemy_hp_color = "rgba(255, 255, 0, 0.85)"  # Yellow
    else:
        enemy_hp_color = "rgba(114, 230, 96, 0.85)"  # Green

    if main_hp_true_percent <= 25:
        main_hp_color = "rgba(255, 0, 0, 0.85)"  # Red
    elif main_hp_true_percent <= 50:
        main_hp_color = "rgba(255, 255, 0, 0.85)"  # Yellow
    else:
        main_hp_color = "rgba(114, 230, 96, 0.85)"  # Green


    # IMPORTANT: Provide clean, closed @media blocks and explicitly cancel any dark-mode inversion.
    # Many Anki themes/extensions use filter: invert(...) for dark mode. We neutralize that for the HUD,
    # and specifically for PokeImage/MyPokeImage. We also set vivid bars and outlined pills.
    css += """
/* Define custom animations to control transform property directly */
@keyframes ankimon-shake-normal {
  0%, 100% { transform: translateY(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateY(-2px); }
  20%, 40%, 60%, 80% { transform: translateY(2px); }
}

@keyframes ankimon-shake-flipped {
  0%, 100% { transform: scaleX(-1) translateY(0); }
  10%, 30%, 50%, 70%, 90% { transform: scaleX(-1) translateY(-2px); }
  20%, 40%, 60%, 80% { transform: scaleX(-1) translateY(2px); }
}

/* Special class to force flip without animation */
.force-flip {
  transform: scaleX(-1) !important;
}

/* Theme variables */
:host, :root {
  --ankimon-outline: #FFFFFF; /* Light mode outline */
}
@media (prefers-color-scheme: dark) {
  :host, :root {
    --ankimon-outline: #1F1F1F; /* Dark mode outline */
  }
}

/* If any parent applies invert, force HUD back to normal colors */
#ankimon-hud {
  filter: none !important;
  -webkit-filter: none !important;
  color-scheme: light dark; /* allow system forms, but no forced inversion */
}

/* Never invert or blend the Pokémon images */
#ankimon-hud #PokeImage,
#ankimon-hud #MyPokeImage {
  filter: none !important;
  -webkit-filter: none !important;
  mix-blend-mode: normal !important;
  opacity: 1 !important;
  isolation: isolate; /* keep separate compositing context */
  background-size: contain;
  background-repeat: no-repeat;
  background-position: bottom;
}

/* If a global inversion is applied above #ankimon-hud (e.g., body/html),
   double-invert these to visually cancel it. This only takes effect if parent is inverted. */
@supports (filter: invert(100%)) {
  html[style*="invert("] #ankimon-hud #PokeImage,
  html[style*="invert("] #ankimon-hud #MyPokeImage,
  body[style*="invert("] #ankimon-hud #PokeImage,
  body[style*="invert("] #ankimon-hud #MyPokeImage {
    filter: invert(100%) hue-rotate(180deg) !important;
  }
}

/* Also counter popular dark-mode classes some themes add */
html.dark #ankimon-hud,
body.dark #ankimon-hud,
.night_mode #ankimon-hud,
.theme-dark #ankimon-hud {
  filter: none !important;
  -webkit-filter: none !important;
}
html.dark #ankimon-hud #PokeImage,
html.dark #ankimon-hud #MyPokeImage,
body.dark #ankimon-hud #PokeImage,
body.dark #ankimon-hud #MyPokeImage,
.night_mode #ankimon-hud #PokeImage,
.night_mode #ankimon-hud #MyPokeImage,
.theme-dark #ankimon-hud #PokeImage,
.theme-dark #ankimon-hud #MyPokeImage {
  filter: none !important;
  -webkit-filter: none !important;
  mix-blend-mode: normal !important;
}

/* Shared pill style (more vivid than 25%, outlined, no glow) */
#ankimon-hud .ankimon-pill {
  z-index: 9999;
  color: #FFFFFF;
  font-size: 16px;
  font-weight: bold;
  text-align: right;
  background-color: rgba(0, 0, 0, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  outline-offset: 0;
  border-radius: 5px;
  padding: 2px 6px;
}

/* Small pill for XP labels */
#ankimon-hud .ankimon-pill--small {
  font-size: 10px;
  padding: 2px 4px;
}


"""

    if show_mainpkmn_in_reviewer == 0:
        css += f"""
/* Enemy life bar - vivid matte (less transparent), outlined, no glow */
#ankimon-hud #life-bar {{
  width: {pokemon_hp_percent}%;
  height: {hp_bar_thickness}px;
  position: fixed;
  bottom: {10 + xp_bar_spacer}px;
  left: 0px;
  z-index: 9999;
  border-radius: 5px;
  background: {enemy_hp_color};
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  max-width: calc(50% - 7px);
}}

#ankimon-hud #hp-display {{
  position: fixed;
  bottom: {40 + xp_bar_spacer}px;
  right: 10px;
  z-index: 9999;
  color: #FFFFFF;
  font-size: 16px;
  font-weight: bold;
  text-align: right;
  background-color: rgba(0, 0, 0, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  border-radius: 5px;
  padding: 2px 6px;
}}

#ankimon-hud #name-display {{
  position: fixed;
  bottom: {40 + xp_bar_spacer}px;
  left: 10px;
  z-index: 9999;
  color: #FFFFFF;
  font-size: 16px;
  text-align: left;
  background-color: rgba(0, 0, 0, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  border-radius: 5px;
  padding: 2px 6px;
}}

#ankimon-hud #PokeImage {{
  position: fixed;
  bottom: {50 + xp_bar_spacer + hp_bar_thickness}px;
  left: 3px;
  z-index: 9999;
  transform: scaleX(-1);
}}
"""
    elif show_mainpkmn_in_reviewer == 2:
        css += f"""
/* Enemy life bar (top-right) */
#ankimon-hud #life-bar {{
  width: {pokemon_hp_percent}%;
  height: {hp_bar_thickness}px;
  position: fixed;
  bottom: {130 + xp_bar_spacer}px;
  right: 5px;
  z-index: 9999;
  border-radius: 5px;
  background: {enemy_hp_color};
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  max-width: calc(50% - 7px);
}}

/* My life bar (bottom-left) */
#ankimon-hud #mylife-bar {{
  width: {mainpkmn_hp_percent}%;
  height: {hp_bar_thickness}px;
  position: fixed;
  bottom: {25 + xp_bar_spacer}px;
  left: 5px;
  z-index: 9999;
  border-radius: 5px;
  background: {main_hp_color};
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  max-width: calc(50% - 7px);
}}

/* My HP display */
#ankimon-hud #myhp-display {{
  position: fixed;
  bottom: {25 + xp_bar_spacer + hp_bar_thickness}px;
  right: {40 + hp_only_spacer}%;
  z-index: 9999;
  color: #FFFFFF;
  font-size: 16px;
  font-weight: bold;
  text-align: right;
  background-color: rgba(0, 0, 0, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  border-radius: 5px;
  padding: 2px 6px;
}}

#ankimon-hud #myname-display {{
  position: fixed;
  bottom: {25 + xp_bar_spacer + hp_bar_thickness}px;
  left: 10px;
  z-index: 9999;
  color: #FFFFFF;
  font-size: 16px;
  text-align: left;
  background-color: rgba(0, 0, 0, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  border-radius: 5px;
  padding: 2px 6px;
}}

#ankimon-hud #MyPokeImage {{
  position: fixed;
  bottom: {50 + xp_bar_spacer + hp_bar_thickness}px;
  left: 15px;
  z-index: 9999;
}}

#ankimon-hud #hp-display {{
  position: fixed;
  bottom: {160 - wild_hp_spacer + xp_bar_spacer}px;
  left: {50 + hp_only_spacer}%;
  z-index: 9999;
  color: #FFFFFF;
  font-size: 16px;
  font-weight: bold;
  text-align: right;
  background-color: rgba(0, 0, 0, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  border-radius: 5px;
  padding: 2px 6px;
}}

#ankimon-hud #name-display {{
  position: fixed;
  bottom: {20 + xp_bar_spacer}px;
  right: 10px;
  z-index: 9999;
  color: #FFFFFF;
  font-size: 16px;
  text-align: right;
  background-color: rgba(0, 0, 0, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  border-radius: 5px;
  padding: 2px 6px;
}}

#ankimon-hud #PokeImage {{
  position: fixed;
  bottom: {50 + xp_bar_spacer}px;
  right: 15px;
  z-index: 9999;
}}

"""
    elif show_mainpkmn_in_reviewer == 1:
        css += f"""
/* Enemy life bar (bottom-right) */
#ankimon-hud #life-bar {{
  width: {pokemon_hp_percent}%;
  height: {hp_bar_thickness}px;
  position: fixed;
  bottom: {10 + xp_bar_spacer}px;
  right: 5px;
  z-index: 9999;
  border-radius: 5px;
  background: {enemy_hp_color};
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  max-width: calc(50% - 7px);
}}

/* My life bar (bottom-left) */
#ankimon-hud #mylife-bar {{
  width: {mainpkmn_hp_percent}%;
  height: {hp_bar_thickness}px;
  position: fixed;
  bottom: {10 + xp_bar_spacer}px;
  left: 5px;
  z-index: 9999;
  border-radius: 5px;
  background: {main_hp_color};
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  max-width: calc(50% - 7px);
}}

#ankimon-hud #myhp-display {{
  position: fixed;
  bottom: {15 + xp_bar_spacer + hp_bar_thickness}px;
  right: 55%;
  z-index: 9999;
  color: #FFFFFF;
  font-size: 16px;
  font-weight: bold;
  text-align: right;
  background-color: rgba(0, 0, 0, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  border-radius: 5px;
  padding: 2px 6px;
}}

#ankimon-hud #myname-display {{
  position: fixed;
  bottom: {15 + xp_bar_spacer + hp_bar_thickness}px;
  left: 10px;
  z-index: 9999;
  color: #FFFFFF;
  font-size: 16px;
  text-align: left;
  background-color: rgba(0, 0, 0, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  border-radius: 5px;
  padding: 2px 6px;
}}

#ankimon-hud #MyPokeImage {{
  position: fixed;
  bottom: {50 + xp_bar_spacer + hp_bar_thickness}px;
  left: 3px;
  z-index: 9999;
}}

#ankimon-hud #hp-display {{
  position: fixed;
  bottom: {15 + xp_bar_spacer + hp_bar_thickness}px;
  left: 55%;
  z-index: 9999;
  color: #FFFFFF;
  font-size: 16px;
  font-weight: bold;
  text-align: right;
  background-color: rgba(0, 0, 0, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  border-radius: 5px;
  padding: 2px 6px;
}}

#ankimon-hud #name-display {{
  position: fixed;
  bottom: {15 + xp_bar_spacer + hp_bar_thickness}px;
  right: 10px;
  z-index: 9999;
  color: #FFFFFF;
  font-size: 16px;
  text-align: right;
  background-color: rgba(0, 0, 0, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  border-radius: 5px;
  padding: 2px 6px;
}}

#ankimon-hud #PokeImage {{
  position: fixed;
  bottom: {50 + xp_bar_spacer + hp_bar_thickness}px;
  right: 15px;
  z-index: 9999;
}}

"""

    if xp_bar_config is True:
        css += f"""
/* XP bar - matte, outlined, no glow */
#ankimon-hud #xp-bar {{
  position: fixed;
  {xp_bar_location}: 7px;
  left: 50px;
  right: 5px;
  z-index: 9999;
  width: {int((main_pokemon.xp / int(experience_for_next_lvl)) * 100)}%;
  height: 10px;
  border-radius: 5px;
  background: rgba(0, 191, 255, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
}}

#ankimon-hud #xp_text {{
  position: fixed;
  {xp_bar_location}: 2px;
  left: 15px;
  z-index: 9999;
  font-color: rgba(0, 191, 255, 0.85);
  font-size: 10px;
  font-weight: bold;
  text-align: center;
  background-color: rgba(0, 0, 0, 0.85);
  box-shadow: none !important;
  filter: none !important;
  outline: 1.5px solid var(--ankimon-outline);
  border-radius: 5px;
  padding: 2px 4px;
}}
"""

    return css