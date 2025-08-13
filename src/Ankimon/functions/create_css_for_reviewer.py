def create_css_for_reviewer(show_mainpkmn_in_reviewer, pokemon_hp_percent, hp_bar_thickness, xp_bar_spacer, view_main_front, mainpkmn_hp_percent, hp_only_spacer, wild_hp_spacer, xp_bar_config, main_pokemon, experience_for_next_lvl, xp_bar_location):
    css = ""
    if show_mainpkmn_in_reviewer == 0:
        css += f"""
        #ankimon-hud #life-bar {{
        width: {pokemon_hp_percent}%; /* Replace with the actual percentage */
        height: {hp_bar_thickness}px;
        background: linear-gradient(to right, 
                                    rgba(114, 230, 96, 0.7), /* Green with transparency */
                                    rgba(114, 230, 96, 0.7) 100%, /* Continue green to the percentage point */
                                    rgba(54, 54, 56, 0.7) 100%, /* Transition to dark background */
                                    rgba(54, 54, 56, 0.7)); /* Dark background with transparency */
        position: fixed;
        bottom: {10 + xp_bar_spacer}px;
        left: 0px;
        z-index: 9999;
        border-radius: 5px; /* Shorthand for all corners rounded */
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.8), /* Green glow effect */
                    0 0 30px rgba(54, 54, 56, 1);  /* Dark glow effect */
        }}
        #ankimon-hud #hp-display {{
        position: fixed;
        bottom: {40 + xp_bar_spacer}px;
        right: 10px;
        z-index: 9999;
        color: white;
        font-size: 16px;
        font-weight: bold; /* Make the text bold */
        background-color: rgb(54,54,56,0.7); 
        text-align: right;
        }}
        #ankimon-hud #name-display {{
        position: fixed;
        bottom: {40 + xp_bar_spacer}px;
        left: 10px;
        z-index: 9999;
        color: white;
        font-size: 16px;
        background-color: rgb(54,54,56, 0.7);
        text-align: left;
        }}
        #ankimon-hud #PokeImage {{
            position: fixed;
            bottom: {30 + xp_bar_spacer + hp_bar_thickness}px; /* Adjust as needed */
            left: 3px;
            z-index: 9999;
            width: 100px; /* Adjust as needed */
            height: 100px; /* Adjust as needed */
            background-size: cover; /* Cover the div area with the image */
        }}
        """
        css += f"""
            #ankimon-hud #PokeIcon {{
            position: fixed;
            bottom: {85 + xp_bar_spacer}px; /* Adjust as needed */
            left: 90px;
            z-index: 9999;
            width: 25px; /* Adjust as needed */
            height: 25px; /* Adjust as needed */
            }}
            """
    elif show_mainpkmn_in_reviewer == 2:
        css += f"""
        #ankimon-hud #life-bar {{
        width: {pokemon_hp_percent}%; /* Replace with the actual percentage */
        height: {hp_bar_thickness}px;
        background: linear-gradient(to right, 
                                    rgba(114, 230, 96, 0.7), /* Green with transparency */
                                    rgba(114, 230, 96, 0.7) 100%, /* Continue green to the percentage point */
                                    rgba(54, 54, 56, 0.7) 100%, /* Transition to dark background */
                                    rgba(54, 54, 56, 0.7)); /* Dark background with transparency */
        position: fixed;
        bottom: {130 + xp_bar_spacer}px;
        right: 0px;
        z-index: 9999;
        border-radius: 5px; /* Shorthand for all corners rounded */
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.8), /* Green glow effect */
                    0 0 30px rgba(54, 54, 56, 1);  /* Dark glow effect */
        }}
        #ankimon-hud #mylife-bar {{
        width: {mainpkmn_hp_percent}%; /* Replace with the actual percentage */
        height: {hp_bar_thickness}px;
        background: linear-gradient(to right, 
                                    rgba(114, 230, 96, 0.7), /* Green with transparency */
                                    rgba(114, 230, 96, 0.7) 100%, /* Continue green to the percentage point */
                                    rgba(54, 54, 56, 0.7) 100%, /* Transition to dark background */
                                    rgba(54, 54, 56, 0.7)); /* Dark background with transparency */
        position: fixed;
        bottom: {25 + xp_bar_spacer}px;
        left: 0px;
        z-index: 9999;
        border-radius: 5px; /* Shorthand for all corners rounded */
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.8), /* Green glow effect */
                    0 0 30px rgba(54, 54, 56, 1);  /* Dark glow effect */
        }}
        #ankimon-hud #myhp-display {{
        position: fixed;
        bottom: {25 + xp_bar_spacer + hp_bar_thickness}px;
        right: {40 + hp_only_spacer}%;
        z-index: 9999;
        color: white;
        font-size: 16px;
        font-weight: bold; /* Make the text bold */
        background-color: rgb(54,54,56,0.7); 
        text-align: right;
        }}
        #ankimon-hud #myname-display {{
        position: fixed;
        bottom: {25 + xp_bar_spacer + hp_bar_thickness}px;
        left: 10px;
        z-index: 9999;
        color: white;
        font-size: 16px;
        background-color: rgb(54,54,56, 0.7);
        text-align: left;
        }}
        #ankimon-hud #MyPokeImage {{
            position: fixed;
            bottom: {50 + xp_bar_spacer + hp_bar_thickness}px; /* Adjust as needed */
            left: 15px;
            z-index: 9999;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: bottom;
        }}
        #ankimon-hud #hp-display {{
        position: fixed;
        bottom: {160 - wild_hp_spacer + xp_bar_spacer}px;
        left: {50 + hp_only_spacer}%;
        z-index: 9999;
        color: white;
        font-size: 16px;
        font-weight: bold; /* Make the text bold */
        background-color: rgb(54,54,56,0.7); 
        text-align: right;
        }}
        #ankimon-hud #name-display {{
        position: fixed;
        bottom: {20 + xp_bar_spacer}px;
        right: 10px;
        z-index: 9999;
        color: white;
        font-size: 16px;
        background-color: rgb(54,54,56, 0.7);
        text-align: right;
        }}
        #ankimon-hud #PokeImage {{
            position: fixed;
            bottom: {30 + xp_bar_spacer}px; /* Adjust as needed */
            right: 3px;
            z-index: 9999;
            width: 100px; /* Adjust as needed */
            height: 100px; /* Adjust as needed */
            background-size: cover; /* Cover the div area with the image */
        }}"""
        css += f"""
            #ankimon-hud #PokeIcon {{
                position: fixed;
                bottom: {8 + xp_bar_spacer}px; /* Adjust as needed */
                right: 20%;
                z-index: 9999;
                width: 25px; /* Adjust as needed */
                height: 25px; /* Adjust as needed */
                background-size: cover; /* Cover the div area with the image */
            }}
            """
    elif show_mainpkmn_in_reviewer == 1:
        css += f"""
        #ankimon-hud #life-bar {{
        width: {pokemon_hp_percent}%; /* Replace with the actual percentage */
        height: {hp_bar_thickness}px;
        background: linear-gradient(to right, 
                                    rgba(114, 230, 96, 0.7), /* Green with transparency */
                                    rgba(114, 230, 96, 0.7) 100%, /* Continue green to the percentage point */
                                    rgba(54, 54, 56, 0.7) 100%, /* Transition to dark background */
                                    rgba(54, 54, 56, 0.7)); /* Dark background with transparency */
        position: fixed;
        bottom: {10 + xp_bar_spacer}px;
        right: 0px;
        z-index: 9999;
        border-radius: 5px; /* Shorthand for all corners rounded */
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.8), /* Green glow effect */
                    0 0 30px rgba(54, 54, 56, 1);  /* Dark glow effect */
        }}
        #ankimon-hud #mylife-bar {{
        width: {mainpkmn_hp_percent}%; /* Replace with the actual percentage */
        height: {hp_bar_thickness}px;
        background: linear-gradient(to right, 
                                    rgba(114, 230, 96, 0.7), /* Green with transparency */
                                    rgba(114, 230, 96, 0.7) 100%, /* Continue green to the percentage point */
                                    rgba(54, 54, 56, 0.7) 100%, /* Transition to dark background */
                                    rgba(54, 54, 56, 0.7)); /* Dark background with transparency */
        position: fixed;
        bottom: {10 + xp_bar_spacer}px;
        left: 0px;
        z-index: 9999;
        border-radius: 5px; /* Shorthand for all corners rounded */
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.8), /* Green glow effect */
                    0 0 30px rgba(54, 54, 56, 1);  /* Dark glow effect */
        }}
        #ankimon-hud #myhp-display {{
        position: fixed;
        bottom: {15 + xp_bar_spacer + hp_bar_thickness}px;
        right: {55}%;
        z-index: 9999;
        color: white;
        font-size: 16px;
        font-weight: bold; /* Make the text bold */
        background-color: rgb(54,54,56,0.7); 
        text-align: right;
        }}
        #ankimon-hud #myname-display {{
        position: fixed;
        bottom: {15 + xp_bar_spacer + hp_bar_thickness}px;
        left: 10px;
        z-index: 9999;
        color: white;
        font-size: 16px;
        background-color: rgb(54,54,56, 0.7);
        text-align: left;
        }}
        #ankimon-hud #MyPokeImage {{
            position: fixed;
            bottom: {50 + xp_bar_spacer + hp_bar_thickness}px; /* Adjust as needed */
            left: 3px;
            z-index: 9999;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: bottom;
            transform: scaleX({view_main_front});
        }}
        #ankimon-hud #hp-display {{
        position: fixed;
        bottom: {15 + xp_bar_spacer + hp_bar_thickness}px;
        left: {55}%;
        z-index: 9999;
        color: white;
        font-size: 16px;
        font-weight: bold; /* Make the text bold */
        background-color: rgb(54,54,56,0.7); 
        text-align: right;
        }}
        #ankimon-hud #name-display {{
        position: fixed;
        bottom: {15 + xp_bar_spacer + hp_bar_thickness}px;
        right: 10px;
        z-index: 9999;
        color: white;
        font-size: 16px;
        background-color: rgb(54,54,56, 0.7);
        text-align: right;
        }}
        #ankimon-hud #PokeImage {{
            position: fixed;
            bottom: {30 + xp_bar_spacer + hp_bar_thickness}px; /* Adjust as needed */
            right: 3px;
            z-index: 9999;
            width: 100px; /* Adjust as needed */
            height: 100px; /* Adjust as needed */
            background-size: cover; /* Cover the div area with the image */
        }}"""
        css += f"""
            #ankimon-hud #PokeIcon {{
                position: fixed;
                bottom: {8 + xp_bar_spacer + hp_bar_thickness}px; /* Adjust as needed */
                right: 20%;
                z-index: 9999;
                width: 25px; /* Adjust as needed */
                height: 25px; /* Adjust as needed */
                background-size: cover; /* Cover the div area with the image */
            }}
            """
    if xp_bar_config is True:
            css += f"""
            #ankimon-hud #xp-bar {{
            width: {int((main_pokemon.xp / int(experience_for_next_lvl)) * 100)}%; /* Replace with the actual percentage */
            height: 10px;
            background: linear-gradient(to right, 
                                        rgba(0, 191, 255, 0.7), /* Light Blue with transparency */
                                        rgba(0, 191, 255, 0.7) 100%, /* Continue light blue to the percentage point */
                                        rgba(25, 25, 112, 0.7) 100%, /* Transition to dark blue background */
                                        rgba(25, 25, 112, 0.7)); /* Dark blue background with transparency */
            position: fixed;
            {xp_bar_location}: 0px;
            left: 0px;
            z-index: 9999;
            border-radius: 5px; /* Shorthand for all corners rounded */
            box-shadow: 0 0 10px rgba(0, 191, 255, 0.8), /* Light blue glow effect */
                        0 0 30px rgba(25, 25, 112, 1);  /* Dark blue glow effect */
            }}
            #ankimon-hud #next_lvl_text {{
            position: fixed;
            {xp_bar_location}: 13px;
            right: 15px;
            z-index: 9999;
            color: white;
            font-size: 10px;
            background-color: rgb(54,54,56, 0.7);
            text-align: right;
            }}
            #ankimon-hud #xp_text {{
            position: fixed;
            {xp_bar_location}: 13px;
            left: 15px;
            z-index: 9999;
            color: white;
            font-size: 10px;
            background-color: rgb(54,54,56, 0.7);
            text-align: right;
            }}
            """
    return css