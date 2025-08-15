class LegendaryCatching:
    def __init__(self):
        # Define dependencies
        self.dependencies = {
            150: {151},  # Mewtwo requires Mew
            250: {243, 244, 245},  # Ho-Oh requires Raikou, Entei, Suicune
            249: {243, 244, 245},  # Lugia requires Raikou, Entei, Suicune
            486: {377, 378, 379},  # Regigigas requires Regirock, Regice, Registeel
            384: {382, 383},  # Rayquaza requires Kyogre and Groudon
            487: {483, 484},  # Giratina requires Dialga and Palkia
        }

        # Define mythical Pokémon (always excluded)
        self.mythical = {151, 251, 386, 493, 649}

        # List of Pokémon initially excluded
        self.excluded = {
            144, 145, 146, 150, 243, 244, 245, 250, 249,
            377, 378, 379, 486, 380, 381, 382, 383, 384,
            483, 484, 487
        }

    def can_catch(self, caught_pokemon, target_pokemon):
        """
        Check if a Pokémon can be caught based on what's already caught.

        :param caught_pokemon: Set of Pokémon IDs already caught
        :param target_pokemon: Pokémon ID to check
        :return: True if the Pokémon can be caught, False otherwise
        """
        if target_pokemon in self.mythical:
            return False  # Mythical Pokémon cannot be caught

        if target_pokemon not in self.dependencies:
            return True  # Pokémon has no dependency, can be caught

        required = self.dependencies[target_pokemon]
        return required.issubset(caught_pokemon)

    def get_catchable_pokemon(self, caught_pokemon):
        """
        Get a list of Pokémon IDs that can be caught based on what's already caught.

        :param caught_pokemon: Set of Pokémon IDs already caught
        :return: Set of catchable Pokémon IDs
        """
        catchable = set()
        for pokemon in self.excluded:
            if self.can_catch(caught_pokemon, pokemon):
                catchable.add(pokemon)
        return catchable


# Example usage
caught = {151, 243, 244, 245}  # Already caught Mew, Raikou, Entei, Suicune
catching = LegendaryCatching()

print("Catchable Pokémon:", catching.get_catchable_pokemon(caught))
