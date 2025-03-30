from ..resources import pkmnimgfolder
import os

def get_sprite_path(side, sprite_type, id=132, shiny=False, gender="M"):
        """Return the path to the sprite of the Pokémon."""
        base_path = f"{side}_default_gif" if sprite_type == "gif" else f"{side}_default"
        
        shiny_path = "shiny/" if shiny else ""
        gender_path = "female/" if gender == "F" else ""
        
        path = f"{pkmnimgfolder}/{base_path}/{shiny_path}{gender_path}{id}.{sprite_type}"
        default_path = f"{pkmnimgfolder}/front_default/substitute.png"
        
        # Check if the file exists at the given path
        if os.path.exists(path):
            return path
        else:
            if gender == "F":
                gender_path = ""
                path = f"{pkmnimgfolder}/{base_path}/{shiny_path}{gender_path}{id}.{sprite_type}"
                return path
            elif shiny == "True":
                shiny_path = ""
                path = f"{pkmnimgfolder}/{base_path}/{shiny_path}{gender_path}{id}.{sprite_type}"
                return path
            else:
                return default_path