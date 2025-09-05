from typing import Optional

from aqt.qt import QPainter, QLabel, Qt
from PyQt6.QtGui import QColor, QFont, QColor, QPalette
from PyQt6.QtCore import Qt, QRect, QPoint, QSize, QPoint, QTimer
from PyQt6.QtWidgets import QApplication, QLabel, QFrame

from ..pyobj.pokemon_obj import PokemonObject
from ..pyobj.InfoLogger import ShowInfoLogger
from ..pyobj.settings import Settings

def tooltipWithColour(msg, color, x=0, y=20, xref=1, parent=None, width=0, height=0, centered=False):
    from ..config_var import reviewer_text_message_box
    period = int(Settings().get("gui.reviewer_text_message_box_time", 3) * 1000) #time for pop up message
    class CustomLabel(QLabel):
        def mousePressEvent(self, evt):
            evt.accept()
            self.hide()
    aw = parent or QApplication.activeWindow()
    if aw is None:
        return

    if color == "#6A4DAC":
        y_offset = 40
    elif color == "#F7DC6F":
        y_offset = -40
    elif color == "#F0B27A":
        y_offset = -40
    elif color == "#D2B4DE":
        y_offset = -40
    else:
        y_offset = 0

    if reviewer_text_message_box != False:
        x = aw.mapToGlobal(QPoint(x + round(aw.width() / 2), 0)).x()
        y = aw.mapToGlobal(QPoint(0, aw.height() - (180 + y_offset))).y()
        lab = CustomLabel(aw)
        lab.setFrameShape(QFrame.Shape.StyledPanel)
        lab.setLineWidth(2)
        lab.setWindowFlags(Qt.WindowType.ToolTip)
        lab.setText(msg)
        lab.setAlignment(Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter)

        if width > 0:
            lab.setFixedWidth(width)
        if height > 0:
            lab.setFixedHeight(height)

        p = QPalette()
        p.setColor(QPalette.ColorRole.Window, QColor(color))
        p.setColor(QPalette.ColorRole.WindowText, QColor("#000000"))
        lab.setPalette(p)
        lab.show()
        lab.move(QPoint(x - round(lab.width() * 0.5 * xref), y))
        try:
            QTimer.singleShot(period, lambda: lab.hide())
        except:
            QTimer.singleShot(3000, lambda: lab.hide())
        ShowInfoLogger().log_and_showinfo("game", msg)

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

def draw_stat_boosts(
    main_pokemon: PokemonObject,
    enemy_pokemon: PokemonObject,
    painter: QPainter,
    pos_for_main_pkmn: Optional[tuple[int, int]] = None,
    pos_for_enemy: Optional[tuple[int, int]] = None,
) -> None:
    """Draws visual indicators of stat boosts for two Pokémon using QPainter.

    This function displays the stat boosts (e.g., ATK, DEF, SpA) for both a main Pokémon
    and an enemy Pokémon on a GUI. Each non-neutral boost is represented as a colored rectangle
    containing an abbreviated stat name and its corresponding multiplier.

    Args:
        main_pokemon (PokemonObject): The player's Pokémon whose stat boosts will be drawn.
        enemy_pokemon (PokemonObject): The opposing Pokémon whose stat boosts will be drawn.
        painter (QPainter): The QPainter object used to draw the boost indicators.
        pos_for_main_pkmn (Optional[tuple[int, int]]): The top-left position (x, y) to draw
            the main Pokémon's boosts. If None, nothing will be drawn for the main Pokémon.
        pos_for_enemy (Optional[tuple[int, int]]): The top-left position (x, y) to draw
            the enemy Pokémon's boosts. If None, nothing will be drawn for the enemy Pokémon.

    Returns:
        None: This function performs drawing operations directly via the provided QPainter.

    Notes:
        - Stat stages with a value of 0 (neutral) are not rendered.
        - The function temporarily modifies the painter's pen, brush, and font,
          which are restored to their original state before returning.
    """

    boost_to_mult = {
        0: "x1",
        1: "x1.5",
        2: "x2",
        3: "x2.5",
        4: "x3",
        5: "x3.5",
        6: "x4",
        -1: "x0.67",
        -2: "x0.5",
        -3: "x0.4",
        -4: "x0.33",
        -5: "x0.29",
        -6: "x0.25",
        }

    boost_name_to_abbreviation = {
        'atk': "ATK",
        'def': "DEF",
        'spa': "SpA",
        'spd': "SpD",
        'spe': "SPE",
        'accuracy': "ACC",
        'evasion': "EVD",
    }

    pen_color_backup = painter.pen().color()  # Saving the pen's color to reset it after drawing gender symbols
    brush_color_backup = painter.brush().color()
    font_backup = painter.font()

    w, h = 60, 20

    zipped = zip([main_pokemon, enemy_pokemon], [pos_for_main_pkmn, pos_for_enemy])
    for pokemon, (x, y) in zipped:
        boosts = pokemon.stat_stages
        counter = 0
        for key, val in boosts.items():
            if val == 0:  # Don't draw neutral boost values
                continue

            rect = QRect(QPoint(x + counter * (w + 3), y), QSize(w, h))

            painter.setBrush(QColor(150, 220, 150))
            painter.setPen(QColor(50, 150, 50))
            font = QFont("Early GameBoy", 8, QFont.Weight.Bold)
            if val < 0:
                painter.setBrush(QColor(250, 233, 229))  # Light red background
                painter.setPen(QColor(211, 73, 41))      # Dark red border
            elif val > 0:
                painter.setBrush(QColor(229, 255, 233))  # Light green background
                painter.setPen(QColor(97, 164, 52))      # Dark green border
            painter.setFont(font)

            painter.drawRect(rect)
            painter.drawText(
                rect,
                Qt.AlignmentFlag.AlignCenter,
                f"{boost_name_to_abbreviation[key]} {boost_to_mult[val]}"
                )

            counter += 1

    painter.setPen(pen_color_backup)  # Going back to the color we had before drawing gender symbols
    painter.setBrush(brush_color_backup)
    painter.setFont(font_backup)
