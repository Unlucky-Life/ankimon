// Given numbers to check
const givenNumbers = [1, 2, 3, 4, 5]; // Add the numbers you want to check

// Function to update the image
function updatePokemonImages() {
    // Select all app-pokemon-item elements
    const pokemonItems = document.querySelectorAll('app-pokemon-item');
    console.log(pokemonItems)
    // Loop through each item
    pokemonItems.forEach(item => {
        // Find the element that contains the card-id
        const cardIdElement = item.querySelector('.card-id');
        if (cardIdElement) {
            const cardId = parseInt(cardIdElement.textContent, 10);
            
            // Check if the card-id matches any of the given numbers
            if (givenNumbers.includes(cardId)) {
                // Find the image element
                const imgElement = item.querySelector('.pokemon-card-img');
                if (imgElement) {
                    // Update the image source to the question mark image
                    imgElement.src = 'question-mark.png'; // Path to your question mark image
                }
            }
        }
    });
}

// Run the function
updatePokemonImages();
