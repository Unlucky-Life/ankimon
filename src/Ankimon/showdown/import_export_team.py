import json
from ..resources import (my_team, opponent_team,
team_pokemon_path, mypokemon_path)
from aqt import mw
from PyQt6.QtWidgets import QMessageBox, QInputDialog


def export_code():
    with open(mypokemon_path, "r") as file:
        my_poke = json.load(file)
    with open(team_pokemon_path, "r") as file:
        poke_team = json.load(file)
    rtn = []

    for code in poke_team:
        for p in my_poke:
            if p["individual_id"] == code["individual_id"]:
                rtn.append(p)
    return json.dumps(rtn)

def import_code(code, path):#Fix W's
    with open(path, "w") as file:
        try:
            json.loads(code)
        except json.JSONDecodeError:
            return
        file.write(code)

def export_team():
    mw.app.clipboard().setText(export_code())
    id = QMessageBox(QMessageBox.Icon.Information, "Ankimon Showdown", "Your team code is copied to your clipboard!", parent=mw)
    id.exec()

def import_opp():
    ans = QInputDialog.getText(mw, "Ankimon Showdown", "Import String:")
    if ans[1]:
        import_code(ans[0], opponent_team)
        id = QMessageBox(QMessageBox.Icon.Information, "Ankimon Showdown", "You have imported your opponent's team code!",
                        parent=mw)
        id.exec()

def import_mine():
    import_code(export_code(), my_team)
    id = QMessageBox(QMessageBox.Icon.Information, "Ankimon Showdown", "Your team has been saved to your showdown!",
                      parent=mw)
    id.exec()
