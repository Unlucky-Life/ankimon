class FrameObject:
    #Object for the frame variables for the parameters
    def __init__(self, text, mainpokemon_object, enemy_pokemon_object):
        self.text = text
        self.display = "block"
        self.mainpokemon = mainpokemon_object
        self.enemy_pokemon_object = enemy_pokemon_object
        self.mainpokemon_attack = False
        self.enemypokemon_attack = False
        self.fx_top = None
        self.fx_bottom = None