from PyQt6.QtWidgets import (QMainWindow, QInputDialog,
QWidget, QGroupBox, QLabel, QProgressBar, QVBoxLayout, QHBoxLayout,
)
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtCore import QTimer
from aqt import mw
from aqt.qt import qconnect
from aqt.utils import showInfo
from ..resources import addon_dir, opponent_team, my_team, type_icon_path_resources, frontdefault
from .battle_func import attack, PokeTeam, PokemonObject, Win

class Showdown(QMainWindow):
    def __init__(self):
        super().__init__(mw)
        self.vs_size = QInputDialog.getInt(self, "Ankimon Showdown", "? vs. ?:", 1, 1, 3)[0]
        self.team_size = QInputDialog.getInt(self, "Ankimon Showdown", "Team size:", 6, self.vs_size, 6)[0]
        self.opp_team = PokeTeam(opponent_team, vs_size=self.vs_size, team_size=self.team_size)
        self.my_team = PokeTeam(my_team, name="Home", vs_size=self.vs_size, team_size=self.team_size)
        self.in_round = False
        self.setCentralWidget(self._createCentral())
        self._createMenuBar()

    def createPokeWid(self, pokemon: PokemonObject, cwid):
        pwid = QGroupBox(pokemon.name, cwid)
        # Initialize Layouts
        main_lay = QVBoxLayout(pwid)
        main_lay.addStretch(1)
        sec_lay = QHBoxLayout()
        sec_lay.addStretch(1)
        status_lay = QVBoxLayout()
        status_lay.addStretch(1)
        type_lay = QVBoxLayout()
        type_lay.addStretch(1)
        # Status Layout
        status_label = QLabel(f"Battle Status: {pokemon.battle_status}")
        status_lay.addWidget(status_label)
        hp_label = QLabel(f"HP:{pokemon.hp}/{pokemon.max_hp}")
        status_lay.addWidget(hp_label)
        # Type Layout
        type1 = QLabel()
        type1.setPixmap(QPixmap(str(type_icon_path_resources / f"{pokemon.type[0].lower()}.png")))
        type_lay.addWidget(type1)
        if len(pokemon.type) > 1:
            type2 = QLabel()
            type2.setPixmap(QPixmap(str(type_icon_path_resources / f"{pokemon.type[1].lower()}.png")))
            type_lay.addWidget(type2)
        # Secondary Layout
        sec_lay.addLayout(status_lay)
        sec_lay.addLayout(type_lay)
        poke_img = QLabel()
        poke_img.setPixmap(QPixmap(str(frontdefault / f"{pokemon.id}.png")))
        sec_lay.addWidget(poke_img)
        # Main Layout
        main_lay.addLayout(sec_lay)
        hp_bar = QProgressBar()
        hp_bar.setMaximum(pokemon.hp)
        hp_bar.setValue(pokemon.hp)
        main_lay.addWidget(hp_bar)
        pwid.hp_bar = hp_bar
        pwid.hp_label = hp_label
        pwid.status_label = status_label
        return pwid

    def _createCentral(self):
        self.poke_wids = [[], []]
        self.cwid = cwid = QWidget(self)
        self.cmain_lay = QHBoxLayout(cwid)
        self.copp_lay = QVBoxLayout()
        self.cmy_lay = QVBoxLayout()
        #My team
        for a_ind in self.my_team.active:
            pwid = self.createPokeWid(self.my_team.poke[a_ind], cwid)
            self.poke_wids[0].append(pwid)
            self.cmy_lay.addWidget(pwid)
        #His team
        for a_ind in self.opp_team.active:
            pwid = self.createPokeWid(self.opp_team.poke[a_ind], cwid)
            self.poke_wids[1].append(pwid)
            self.copp_lay.addWidget(pwid)
        self.cmain_lay.addLayout(self.cmy_lay)
        self.cmain_lay.addSpacing(50)
        self.cmain_lay.addLayout(self.copp_lay)
        return cwid

    def pokeTurn(self, team: PokeTeam, act_ind):
        #showInfo(f"PokeTurn act_ind:{act_ind}")
        main_pokemon = team.poke[team.active[act_ind]]
        showInfo(f"{team.name}: {main_pokemon.name}\n"
                 f"At:{main_pokemon.stats['atk']},Df:{main_pokemon.stats['def']}"
                 f",Sp.At:{main_pokemon.stats['spa']},Sp.Df:{main_pokemon.stats['spd']}\n"
                 f"Spe:{main_pokemon.stats['spe']},XP:{main_pokemon.stats['xp']}"
                 f",Type:{' '.join(main_pokemon.type)}\nBattle Status:{main_pokemon.battle_status}")
        at_sw = QInputDialog.getItem(self, "Ankimon Showdown", "Attack or Switch:", ["Attack", "Switch"], editable=False)[0]
        if main_pokemon.hp <= 0:
            at_sw = "Switch"
        if "Attack" == at_sw:
            enm_team = self.opp_team if team == self.my_team else self.my_team
            enm_names = [enm_team.poke[ind].name for ind in enm_team.active]
            enm_ind = enm_names.index(QInputDialog.getItem(self, "Ankimon Showdown", "Target Pokemon", enm_names, editable=False)[0])
            enm_poke = enm_team.poke[enm_team.active[enm_ind]]
            attack(enm_poke, main_pokemon)
            wid = self.poke_wids[1 if team == self.my_team else 0][enm_ind]
            wid.hp_bar.setValue(enm_poke.hp)
            wid.hp_label.setText(f"Hp:{enm_poke.hp}/{enm_poke.max_hp}")
            wid.status_label.setText(f"Battle Status:{enm_poke.battle_status}")
        else:
            team.switch(main_pokemon, act_ind)
            new_poke = team.poke[team.active[act_ind]]
            wid = self.createPokeWid(new_poke, self.cwid)
            old_wid: QWidget = self.poke_wids[0 if team == self.my_team else 1][act_ind]
            if team == self.my_team:
                self.cmy_lay.replaceWidget(old_wid, wid)
            else:
                 self.copp_lay.replaceWidget(old_wid, wid)
            old_wid.deleteLater()
            self.poke_wids[0 if team == self.my_team else 1][act_ind] = wid
            showInfo(self.poke_wids[0 if team == self.my_team else 1][act_ind].title())
            self.cwid.update()

    def battleRound(self):
        if not self.in_round:
            self.in_round = True
            all_poke = [[self.my_team.poke[i] for i in self.my_team.active], [self.opp_team.poke[i] for i in self.opp_team.active]]
            def into_act_ind(poke: PokemonObject, team: PokeTeam):
                ind = team.poke.index(poke)
                return team.active.index(ind)
            def one_loop():
                if len(all_poke[0])+len(all_poke[1]) > 0:
                    #showInfo(f"M:{[p.name for p in all_poke[0]]},O:{[p.name for p in all_poke[1]]}")
                    fst = [0, None, None]
                    for i, p in enumerate(all_poke[1]):
                        if p.stats["spe"] >= fst[0]:
                            fst = [p.stats["spe"], 1, into_act_ind(p, self.opp_team), p]
                    for i, p in enumerate(all_poke[0]):
                        if p.stats["spe"] >= fst[0]:
                            fst = [p.stats["spe"], 0, into_act_ind(p, self.my_team), p]
                    self.pokeTurn(self.my_team if fst[1] == 0 else self.opp_team, fst[2])
                    all_poke[fst[1]].remove(fst[3])
                    if self.checkWin():
                        self.finishBattle()
                        return
                    if len(all_poke[0]) + len(all_poke[1]) > 0:
                        QTimer(self).singleShot(3000, one_loop)
                    else:
                        self.in_round = False
                else:
                    self.in_round = False
            one_loop()

    def checkWin(self):
        opp_win = all([p.hp <= 0 for p in self.my_team.poke])
        I_win = all([p.hp <= 0 for p in self.opp_team.poke])
        if opp_win:
            Win("Opponent Team Wins!!!")
            return True
        if I_win:
            Win("Home Team Wins!!!")
            return True
        return False

    def finishBattle(self):
        self.in_round = False
        self.close()
    def _createMenuBar(self):
        bar = self.menuBar()
        self.start_round = QAction("Start Battle Round", bar)
        qconnect(self.start_round.triggered, self.battleRound)
        bar.addAction(self.start_round)

