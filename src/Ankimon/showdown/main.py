from .battle import Showdown, Win
from .import_export_team import export_team, import_opp, import_mine
from aqt import mw
from aqt.qt import QAction, qconnect
from PyQt6.QtGui import QAction
#from PyQt6.QtWidgets import QMenu

def run():
    show = Showdown()
    show.show()

shw_dn_menu = mw.pokemenu.addMenu("In-App Showdown")
run_btn = QAction("Run")
qconnect(run_btn.triggered, run)
shw_dn_menu.addAction(run_btn)

export_btn = QAction("Export Team")
qconnect(export_btn.triggered, export_team)
shw_dn_menu.addAction(export_btn)

import_btn = QAction("Import Team")
qconnect(import_btn.triggered, import_opp)
shw_dn_menu.addAction(import_btn)

save_btn = QAction("Save Team")
qconnect(save_btn.triggered, import_mine)
shw_dn_menu.addAction(save_btn)


#create_in_app_showdown_menu()
