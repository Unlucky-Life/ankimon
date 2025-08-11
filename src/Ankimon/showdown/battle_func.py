import json

from ..classes.choose_move_dialog import MoveSelectionDialog
from ..functions.battle_functions import calc_atk_dmg, status_effect
from ..functions.pokedex_functions import find_details_move, get_pokemon_diff_lang_name
from ..pyobj.InfoLogger import ShowInfoLogger
from ..pyobj.pokemon_obj import PokemonObject
from ..pyobj.translator import Translator
from ..pyobj.settings import Settings
from ..pyobj.ankimon_tracker import AnkimonTracker
from ..resources import (pkmnimgfolder, addon_dir, icon_path, battlescene_path,
                       battlescene_path_without_dialog, battle_ui_path, opponent_team, my_team)
from ..business import bP_none_moves, get_multiplier_stats
from aqt.qt import (QAction, QDialog, QFont, QGridLayout, QLabel, QPainter,
                    QPixmap, Qt, QVBoxLayout, QWidget, qconnect)
from PyQt6.QtCore import QPoint, QTimer, QThread, QEvent, QObject, QUrl, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor, QPalette, QDesktopServices, QPen, QFontDatabase
from PyQt6.QtWidgets import (QApplication, QDialog, QLabel,
                             QInputDialog, QVBoxLayout, QWidget, QComboBox, QPushButton, QTextEdit, QHBoxLayout, QComboBox, QLineEdit, QScrollArea,
                             QFrame, QMenu, QLayout, QProgressBar)
from aqt import mw
from aqt.utils import showWarning
from PyQt6.QtGui import QPalette, QColor, QIcon, QImage
import random

settings_obj = Settings()
ankimon_tracker_obj = AnkimonTracker(trainer_card=None, settings_obj=settings_obj)
translator = Translator(int(settings_obj.get("misc.language", int(9))))
logger = ShowInfoLogger(log_filename="showdown.log")
slp_counter = 0

def effect_status_moves(move_name, mainpokemon_stats, stats, msg, name, mainpokemon_name):
    global battle_status
    move = find_details_move(move_name)
    target = move.get("target")
    boosts = move.get("boosts", {})
    stat_boost_value = {
        "hp": boosts.get("hp", 0),
        "atk": boosts.get("atk", 0),
        "def": boosts.get("def", 0),
        "spa": boosts.get("spa", 0),
        "spd": boosts.get("spd", 0),
        "spe": boosts.get("spe", 0),
        "xp": mainpokemon_stats.get("xp", 0)
    }
    move_stat = move.get("status",None)
    status = move.get("secondary",None)
    battle_status = None
    if move_stat is not None:
        battle_status = move_stat
    if status is not None:
        random_number = random.random()
        chances = status["chance"] / 100
        if random_number < chances:
            battle_status = status["status"]
    if battle_status == "slp":
        slp_counter = random.randint(1, 3)
    if target == "self":
        for boost, stage in boosts.items():
            stat = get_multiplier_stats(stage)
            mainpokemon_stats[boost] = mainpokemon_stats.get(boost, 0) * stat
            msg += f" {mainpokemon_name.capitalize()}'s "
            if stage < 0:
                msg += f"{boost.capitalize()} {translator.translate('stat_decreased')}."
            elif stage > 0:
                msg += f"{boost.capitalize()} {translator.translate('stat_increased')}."
    elif target in ["normal", "allAdjacentFoes"]:
        for boost, stage in boosts.items():
            stat = get_multiplier_stats(stage)
            stats[boost] = stats.get(boost, 0) * stat
            msg += f" {name.capitalize()}'s "
            if stage < 0:
                msg += f"{boost.capitalize()} {translator.translate('stat_decreased')}."
            elif stage > 0:
                msg += f"{boost.capitalize()} {translator.translate('stat_increased')}."
    return msg

def move_with_status(move, move_stat, status):
    global battle_status
    target = move.get("target")
    bat_status = move.get("secondary", None).get("status", None)
    if target in ["normal", "allAdjacentFoes"]:
        if move_stat is not None:
            battle_status = move_stat
        if status is not None:
            random_number = random.random()
            chances = status["chance"] / 100
            if random_number < chances:
                battle_status = status["status"]
    if battle_status == "slp":
        slp_counter = random.randint(1, 3)

def tooltipWithColour(msg, color, x=0, y=20, xref=1, parent=None, width=0, height=0, centered=False):
    period = int(settings_obj.get("gui.reviewer_text_message_box_time", 3) * 1000)  # time for pop up message

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

    if True:
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
        logger.log_and_showinfo("game", msg)


def attack(enemy_pokemon, main_pokemon):
    battle_status = enemy_pokemon.battle_status
    mainpokemon_type = main_pokemon.type
    mainpokemon_name = main_pokemon.name
    multiplier = int(ankimon_tracker_obj.multiplier)
    msg = ""
    msg += f"{multiplier}x {translator.translate('multiplier')}"
    # failed card = enemy attack
    dmg = 0
    random_attack = random.choice(main_pokemon.attacks)
    if settings_obj.get("controls.allow_to_choose_moves", True):
        dialog = MoveSelectionDialog(main_pokemon.attacks)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.selected_move:
                random_attack = dialog.selected_move
    msg += "\n"
    msg += translator.translate("pokemon_chose_attack", pokemon_name=main_pokemon.name.capitalize(),
                                pokemon_attack=random_attack.capitalize())
    move = find_details_move(random_attack)
    category = move.get("category")
    acc = move.get("accuracy")
    if battle_status != "Fighting":
        msg, acc, battle_status, enemy_pokemon.stats = status_effect(enemy_pokemon, move, slp_counter, msg, acc)
    if acc is True:
        acc = 100
    if acc != 0:
        calc_acc = 100 / acc
    else:
        calc_acc = 0
    if battle_status == "slp":
        calc_acc = 0
        msg += "\n" + translator.translate("pokemon_asleep", pokemon_name=enemy_pokemon.name.capitalize())
        # slp_counter -= 1
    elif battle_status == "par":
        msg += "\n" + translator.translate("pokemon_is_paralyzed", pokemon_name=enemy_pokemon.name.capitalize())
        missing_chance = 1 / 4
        random_number = random.random()
        if random_number < missing_chance:
            acc = 0
    if random.random() > calc_acc:
        msg += "\n" + translator.translate("move_has_missed")
    else:
        if category == "Status":
            color = "#F7DC6F"
            msg = effect_status_moves(random_attack, main_pokemon.stats, enemy_pokemon.stats, msg,
                                      enemy_pokemon.name, main_pokemon.name)
        elif category == "Physical" or category == "Special":
            try:
                critRatio = move.get("critRatio", 1)
                if category == "Physical":
                    color = "#F0B27A"
                elif category == "Special":
                    color = "#D2B4DE"
                if move["basePower"] == 0:
                    dmg = bP_none_moves(move)
                    enemy_pokemon.hp -= dmg
                    if dmg == 0:
                        msg += "\n" + translator.translate("move_has_missed")
                        # dmg = 1
                else:
                    if category == "Special":
                        def_stat = enemy_pokemon.stats["spd"]
                        atk_stat = main_pokemon.stats["spa"]
                    elif category == "Physical":
                        def_stat = enemy_pokemon.stats["def"]
                        atk_stat = main_pokemon.stats["atk"]
                    try:
                        dmg = int(calc_atk_dmg(main_pokemon.level, multiplier, move["basePower"], atk_stat, def_stat,
                                               main_pokemon.type, move["type"], enemy_pokemon.type, critRatio))
                    except ZeroDivisionError:
                        dmg = 0
                    if dmg == 0:
                        dmg = 1
                    enemy_pokemon.hp -= dmg
                    msg += translator.translate("dmg_dealt", dmg=dmg, pokemon_name=enemy_pokemon.name.capitalize())
                    move_stat = move.get("status", None)
                    secondary = move.get("secondary", None)
                    if secondary is not None:
                        bat_status = move.get("secondary", None).get("status", None)
                        if bat_status is not None:
                            move_with_status(move, move_stat, secondary)
                    if move_stat is not None:
                        move_with_status(move, move_stat, secondary)
                    if dmg == 0:
                        msg += "\n" + translator.translate("move_has_missed")
            except:
                if category == "Special":
                    def_stat = enemy_pokemon.stats["spd"]
                    atk_stat = main_pokemon.stats["spa"]
                elif category == "Physical":
                    def_stat = enemy_pokemon.stats["def"]
                    atk_stat = main_pokemon.stats["atk"]
                try:
                    dmg = int(calc_atk_dmg(main_pokemon.level, multiplier, random.randint(60, 100), atk_stat, def_stat,
                                       main_pokemon.type, "Normal", enemy_pokemon.type, critRatio))
                except ZeroDivisionError:
                    dmg = 0
                enemy_pokemon.hp -= dmg
            if enemy_pokemon.hp < 0:
                enemy_pokemon.hp = 0
                msg += translator.translate("pokemon_fainted", enemy_pokemon_name=enemy_pokemon.name.capitalize())

        tooltipWithColour(msg, color)

default_pokemon_data = {
    "name": "Pikachu", "gender": "M", "level": 5, "id": 25, "ability": "Static",
    "type": ["Electric"], "stats": {"hp": 20, "atk": 30, "def": 15, "spa": 50, "spd": 40, "spe": 60, "xp": 0},
    "ev": {"hp": 0, "atk": 1, "def": 0, "spa": 0, "spd": 0, "spe": 0}, "iv": {"hp": 15, "atk": 20, "def": 10, "spa": 10, "spd": 10, "spe": 10},
    "attacks": ["Thunderbolt", "Quick Attack"], "base_experience": 112, "current_hp": 20, "growth_rate": "medium", "evos": ["Pikachu"]
}


class PokeTeam:
    switched = pyqtSignal()
    def __init__(self, path=opponent_team, name="Opponent", vs_size=1, team_size=6):
        assert team_size >= vs_size
        self.poke: list[PokemonObject] = []
        self.name = name
        with open(path, "r") as file:
            try:
                data = json.load(file)
                if isinstance(data, list):
                    for poke in data:
                        main_pokemon = PokemonObject(**poke) if poke else PokemonObject(**default_pokemon_data)
                        main_pokemon.xp = main_pokemon.stats["xp"]
                        if main_pokemon.current_hp > main_pokemon.max_hp:
                            main_pokemon.current_hp = main_pokemon.max_hp
                        self.poke.append(main_pokemon)
            except Exception as e:
                showWarning(f"Team at \"{path}\" could not be loaded.\n{e}")
                for i in range(team_size):
                    main_pokemon = PokemonObject(**default_pokemon_data)
                    main_pokemon.xp = main_pokemon.stats["xp"]
                    if main_pokemon.current_hp > main_pokemon.max_hp:
                        main_pokemon.current_hp = main_pokemon.max_hp
                    self.poke.append(main_pokemon)
        if len(self.poke) < team_size:
            for i in range(team_size-len(self.poke)):
                main_pokemon = PokemonObject(**default_pokemon_data)
                main_pokemon.xp = main_pokemon.stats["xp"]
                if main_pokemon.current_hp > main_pokemon.max_hp:
                    main_pokemon.current_hp = main_pokemon.max_hp
                self.poke.append(main_pokemon)
        self.active = [i for i in range(vs_size)]
        if len(self.poke) > team_size:
            self.poke = self.poke[:team_size]
    def switch(self, pokemon, act_ind):
        possible = [i for ind, i in enumerate(self.poke) if i.hp > 0 and ind not in self.active]
        if len(possible) == 0:
            return
        ans = QInputDialog.getItem(mw, "Ankimon Showdown", f"Switch{pokemon.name} for ?:", [p.name for p in possible])
        if ans[1]:
            new_poke = possible[[p.name for p in possible].index(ans[0])]
            new_ind = self.poke.index(new_poke)
            self.active[act_ind] = new_ind

class Win(QDialog):
    def __init__(self, main_msg):
        super().__init__(mw)
        self.main_lay = QVBoxLayout(self)
        self.main_lay.addStretch(1)
        self.pic = QLabel(self)
        self.pic.setPixmap(QPixmap(str(addon_dir / "ankimon_logo.png")).scaled(300, 300))
        self.main_lay.addWidget(self.pic)
        self.main_msg = QLabel(f"<a style=\"font-weight: bold; height: 2cm;\">{main_msg}</a>", self)
        self.main_lay.addWidget(self.main_msg)
        self.btn = QPushButton("OK!", self)
        self.btn.pressed.connect(self.close)
        self.main_lay.addWidget(self.btn)
        self.setModal(True)
        self.open()




