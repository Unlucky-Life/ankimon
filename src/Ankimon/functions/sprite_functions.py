from ..resources import pkmnimgfolder
import os

def get_sprite_path(side: str, sprite_type: str, id: int=132, shiny: bool=False, gender: str="M"):
        """Return the path to the sprite of the Pokémon with robust fallbacks."""
        base_path = f"{side}_default_gif" if sprite_type == "gif" else f"{side}_default"
        default_path = f"{pkmnimgfolder}/front_default/substitute.png"
        
        # 1. Try the most specific path: Shiny and Gendered
        if shiny and gender == "F":
            path = f"{pkmnimgfolder}/{base_path}/shiny/female/{id}.{sprite_type}"
            if os.path.exists(path):
                return path

        # 2. Try Shiny (non-gendered)
        if shiny:
            path = f"{pkmnimgfolder}/{base_path}/shiny/{id}.{sprite_type}"
            if os.path.exists(path):
                return path

        # 3. Try Gendered (non-shiny)
        if gender == "F":
            path = f"{pkmnimgfolder}/{base_path}/female/{id}.{sprite_type}"
            if os.path.exists(path):
                return path

        # 4. Try the default path: Non-shiny, non-gendered
        path = f"{pkmnimgfolder}/{base_path}/{id}.{sprite_type}"
        if os.path.exists(path):
            return path

        # 5. Fallback to the generic substitute image
        print(f"Unable to find sprite for ID {id} (Shiny: {shiny}, Gender: {gender}). Returning substitute.")
        return default_path
