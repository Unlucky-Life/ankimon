from typing import Optional

from aqt.qt import QPainter
from PyQt6.QtGui import QColor

from ..pyobj.pokemon_obj import PokemonObject

def draw_gender_symbols(
    main_pokemon: PokemonObject,
    enemy_pokemon: PokemonObject,
    painter: QPainter,
    pos_main_pkmn: Optional[tuple[int, int]] = None,
    pos_enemy: Optional[tuple[int, int]] = None,
) -> None:
    """Draw gender symbols for the main and enemy Pokémon on the given painter canvas.

    This function draws gender symbols (♂ for male, ♀ for female) next to the main and enemy Pokémon
    on a canvas using the QPainter object. The gender symbols are drawn at specified positions,
    or default positions if none are provided.

    Args:
        main_pokemon (PokemonObject): The main Pokémon object whose gender symbol will be drawn.
        enemy_pokemon (PokemonObject): The enemy Pokémon object whose gender symbol will be drawn.
        painter (QPainter): The QPainter object used to draw on the canvas.
        pos_main_pkmn (Optional[tuple[int, int]], optional): The (x, y) position where the main
            Pokémon's gender symbol will be drawn. Defaults to aNone.
        pos_enemy (Optional[tuple[int, int]], optional): The (x, y) position where the enemy
            Pokémon's gender symbol will be drawn. Defaults to None.

    Returns:
        None: This function modifies the state of the QPainter object but does not return any value.
    """
    get_gender_symbol = lambda gender: {"M": "♂", "F": "♀"}.get(gender, "")  # Gets gender symbol. Returns "" by default
    get_pen_color = lambda gender: QColor(20, 100, 210) if gender == "M" else QColor(210, 20, 20)  # Blue if "M", else Red
    
    enemy_pokemon_gender_symbol = get_gender_symbol(enemy_pokemon.gender)
    main_pokemon_gender_symbol = get_gender_symbol(main_pokemon.gender)

    color_backup = painter.pen().color()  # Saving the pen's color to reset it after drawing gender symbols
    
    painter.setPen(get_pen_color(enemy_pokemon.gender))  # Text color of the gender symbol
    pos = pos_enemy or (175, 64)
    painter.drawText(pos[0], pos[1], enemy_pokemon_gender_symbol)

    painter.setPen(get_pen_color(main_pokemon.gender))  # Text color of the gender symbol
    pos = pos_main_pkmn or (457, 196)
    painter.drawText(pos[0], pos[1], main_pokemon_gender_symbol)

    painter.setPen(color_backup)  # Going back to the color we had before drawing gender symbols
