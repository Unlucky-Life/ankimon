import json, requests

def create_pokeapidb(id):
    def get_pokemon_data(pokemon_id):
        url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}/'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to retrieve data for Pokemon with ID {pokemon_id}")
            return None

    def get_pokemon_species_data(pokemon_id):
        url = f'https://pokeapi.co/api/v2/pokemon-species/{pokemon_id}/'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to retrieve species data for Pokemon with ID {pokemon_id}")
            return None

    def fetch_pokemon_data(url):
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to fetch data from {url}")
            return None

    def create_pokedex():
        pokedex = []

        for pokemon_id in range(1, id):  # Assuming 151 Pokemon per generation
            #print(pokemon_id)
            progress = int((pokemon_id / id) * 100)
            self.progress_updated.emit(progress)
            pokemon_data = get_pokemon_data(pokemon_id)
            species_data = get_pokemon_species_data(pokemon_id)

            if pokemon_data and species_data:
                evolution_data = get_evolution_chain(pokemon_data["name"])

                entry = {
                    "name": pokemon_data["name"],
                    "id": pokemon_id,
                    "effort_values": {
                        stat["stat"]["name"]: stat["effort"] for stat in pokemon_data["stats"]
                    },
                    "base_experience": pokemon_data["base_experience"],
                    "height": pokemon_data["height"],
                    "weight": pokemon_data["weight"],
                    "description": species_data["flavor_text_entries"][0]["flavor_text"].replace("\n", " "),
                    "growth_rate": species_data["growth_rate"]["name"]
                }
                pokedex.append(entry)
        return pokedex

    create_pokedex()