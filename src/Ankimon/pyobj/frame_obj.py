class FrameObject:
    #Object for the frame variables for the parameters
    def __init__(self, text, main_pokemon, enemy_pokemon):
        self.text = text
        self.display = "block"
        self.main_pokemon = main_pokemon
        self.enemy_pokemon = enemy_pokemon
        self.mainpokemon_attack = False
        self.enemypokemon_attack = False
        self.fx_top = None
        self.fx_bottom = None