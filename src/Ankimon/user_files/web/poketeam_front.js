document.addEventListener("DOMContentLoaded", function() {
    const body = document.body;

    // Create the center div
    const centerDiv = document.createElement('div');
    centerDiv.id = 'center';

    // Create and append the title
    const title = document.createElement('h1');
    title.innerText = 'Pokémon Team';
    centerDiv.appendChild(title);

    // Create a container div for the Poké Balls
    const pokeballContainer = document.createElement('div');
    pokeballContainer.className = 'pokeball-container';

    // Array of Pokémon images
    const pokemonImages = [
        'path/to/pokemon1.png',
        'path/to/pokemon2.png',
        'path/to/pokemon3.png',
        'path/to/pokemon4.png',
        'path/to/pokemon5.png',
        'path/to/pokemon6.png'
    ];

    // Function to create a Poké Ball with a Pokémon image
    function createPokeball(imageSrc) {
        const pokeballDiv = document.createElement('div');
        pokeballDiv.className = 'pokeball';

        const img = document.createElement('img');
        img.src = imageSrc;

        pokeballDiv.appendChild(img);
        return pokeballDiv;
    }

    // Append 6 Poké Balls to the pokeball container
    pokemonImages.forEach(imageSrc => {
        const pokeball = createPokeball(imageSrc);
        pokeballContainer.appendChild(pokeball);
    });

    // Append the pokeball container to the center div
    centerDiv.appendChild(pokeballContainer);

    // Insert the center div as the first item in the body
    body.insertBefore(centerDiv, body.firstChild);
});
