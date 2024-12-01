document.addEventListener('keydown', function(event) {
    if (event.key === '8') { // Check for the '8' key
        // Toggle opacity for all elements with the class 'Ankimon'
        var ankimonElements = document.querySelectorAll('.Ankimon');
        ankimonElements.forEach(function(element) {
            if (element.style.opacity === '0') {
                element.style.opacity = '1'; // Set to fully opaque
            } else {
                element.style.opacity = '0'; // Set to 0 opacity
            }
        });
    }
});
