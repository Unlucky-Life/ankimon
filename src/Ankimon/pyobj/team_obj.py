class TeamPokemonObject:
    def __init__(self, pokemon_1=None, pokemon_2=None, pokemon_3=None, pokemon_4=None, pokemon_5=None, pokemon_6=None):
        self.save_directory = team_json_path
        self.pokemon_1 = pokemon_1
        self.pokemon_2 = pokemon_2
        self.pokemon_3 = pokemon_3
        self.pokemon_4 = pokemon_4
        self.pokemon_5 = pokemon_5
        self.pokemon_6 = pokemon_6

    def trade_pokemon(self, team_position, PokemonObject):
        if team_position not in {1, 2, 3, 4, 5, 6}:
            raise ValueError("Invalid team position, must be 1 through 6")
        # Use setattr to dynamically set the attribute based on team_position
        setattr(self, f"pokemon_{team_position}", PokemonObject)
        mw.deckBrowser.refresh()
        tooltip(f"Pokemon {team_position} has been successfully switched out with {PokemonObject.name}.")
        self.save_team()
        #if team_position == 1:
        #    MainPokemonObject = pokemon_1

    def save_team(self):
        # Save the TeamPokemonObject as a JSON file
        team_pokemon_dict = {
            "pokemon_1": self.pokemon_1,
            "pokemon_2": self.pokemon_2,
            "pokemon_3": self.pokemon_3,
            "pokemon_4": self.pokemon_4,
            "pokemon_5": self.pokemon_5,
            "pokemon_6": self.pokemon_6
        }
        # Serialize PokemonObject instances using custom encoder
        serialized_team = {}
        for key, value in team_pokemon_dict.items():
            if isinstance(value, PokemonObject):
                serialized_team[key] = value

        with open(self.save_directory, "w") as file:
            json.dump(serialized_team, file, indent=4, cls=PokemonEncoder)
