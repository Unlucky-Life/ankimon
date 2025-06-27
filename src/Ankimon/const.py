gen_ids = {
    "gen_1": 151,
    "gen_2": 251,
    "gen_3": 386,
    "gen_4": 493,
    "gen_5": 649,
    "gen_6": 721,
    "gen_7": 809,
    "gen_8": 905,
    "gen_9": 1025
}

#to create status symbols
# Define the background and outline colors for each status
status_colors_label = {
    "burned": {"background": "#FF4500", "outline": "#C13500"},
    "frozen": {"background": "#ADD8E6", "outline": "#91B0C0"},
    "paralysis": {"background": "#FFFF00", "outline": "#CCCC00"},
    "poisoned": {"background": "#A020F0", "outline": "#8000C0"},
    "asleep": {"background": "#FFC0CB", "outline": "#D895A1"},
    "confusion": {"background": "#FFA500", "outline": "#CC8400"},
    "flinching": {"background": "#808080", "outline": "#666666"},
    "fainted": {"background": "#000000", "outline": "#000000", "text_color": "#FFFFFF"},
}

status_colors_html = {
    "brn": {"background": "#FF4500", "outline": "#C13500", "name": "Burned"},
    "frz": {"background": "#ADD8E6", "outline": "#91B0C0", "name": "Frozen"},
    "par": {"background": "#FFFF00", "outline": "#CCCC00", "name": "Paralysis"},
    "psn": {"background": "#A020F0", "outline": "#8000C0", "name": "Poisoned"},
    "tox": {"background": "#A545FF", "outline": "#842BFF", "name": "Badly Poisoned"},
    "slp": {"background": "#FFC0CB", "outline": "#D895A1", "name": "Asleep"},
    "confusion": {"background": "#FFA500", "outline": "#CC8400", "name": "Confusion"},
    "flinching": {"background": "#808080", "outline": "#666666", "name": "Flinching"},
    "fainted": {"background": "#000000", "outline": "#000000", "text_color": "#FFFFFF", "name": "Fainted"},
    "fighting": {"background": "#C03028", "outline": "#7D1F1A", "name": "Fighting"},  # Example colors for Fighting
}

# Get the profile folder
#from aqt import mw
#from pathlib import Path
#profilename = mw.pm.name
#profilefolder = Path(mw.pm.profileFolder())
#mediafolder = Path(mw.col.media.dir())