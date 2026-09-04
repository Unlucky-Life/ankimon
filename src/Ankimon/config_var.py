from aqt import mw
import platform

config = mw.addonManager.getConfig(__name__)

def get_config(key, default=None):
    """Read settings safely when loading a config from an older release."""
    return config.get(key, default)

pop_up_dialog_message_on_defeat = get_config("gui.pop_up_dialog_message_on_defeat", False)
reviewer_text_message_box = get_config("gui.reviewer_text_message_box", True)
reviewer_text_message_box_time = get_config("gui.reviewer_text_message_box_time", 3) #time in seconds for text message
reviewer_text_message_box_time = reviewer_text_message_box_time * 1000 #times 1000 for s => ms
reviewer_image_gif = get_config("gui.reviewer_image_gif", False)
show_mainpkmn_in_reviewer = get_config("gui.show_mainpkmn_in_reviewer", 1) #0 is off, 1 normal, 2 battle mode
xp_bar_config = get_config("gui.xp_bar_config", True)
review_hp_bar_thickness = get_config("gui.review_hp_bar_thickness", 2) #2 = 8px, 3# 12px, 4# 16px, 5# 20px
hp_bar_config = get_config("gui.hp_bar_config", True) #2 = 8px, 3# 12px, 4# 16px, 5# 20px
xp_bar_location = get_config("gui.xp_bar_location", 2) #1 top, 2 = bottom
animate_time = get_config("gui.animate_time", True) #default: true; false = animate for 0.8 seconds
view_main_front = get_config("gui.view_main_front", True) #default: true => -1; false = 1
gif_in_collection = get_config("gui.gif_in_collection", True) #default: true => -1; false = 1
styling_in_reviewer = get_config("gui.styling_in_reviewer", True) #default: true; false = no styling in reviewer

automatic_battle = get_config("battle.automatic_battle", 0) #default: 0; 1 = catch_pokemon; 2 = defeat_pokemon
dmg_in_reviewer = get_config("battle.dmg_in_reviewer", True) #default: false; true = mainpokemon is getting damaged in reviewer for false answers
cards_per_round = get_config("battle.cards_per_round", 2)

leaderboard = get_config("misc.leaderboard", False)
no_more_news = get_config("misc.YouShallNotPass_Ankimon_News", False) #default: false; true = no more news
remove_levelcap = get_config("misc.remove_level_cap", False) #default: false; true = no more news
ssh = get_config("misc.ssh", True) #for eduroam users - false ; default: true
language = get_config("misc.language", 9)

ankimon_key = get_config("controls.key_for_opening_closing_ankimon", "Ctrl+Shift+P")
defeat_shortcut = get_config("controls.defeat_key", "5") #default: 5; ; Else if not 5 => controll + Key for capture
catch_shortcut = get_config("controls.catch_key", "6") #default: 6; Else if not 6 => controll + Key for capture
reviewer_buttons = get_config("controls.pokemon_buttons", True) #default: true; false = no pokemon buttons in reviewer

sound_effects = get_config("audio.sound_effects", False) #default: false; true = sound_effects on
sounds = get_config("audio.sounds", True)
battle_sounds = get_config("audio.battle_sounds", False)


# Get the system name (e.g., 'Windows', 'Linux', 'Darwin')
system_name = platform.system()

# Determine system category
if system_name == "Windows" or system_name == "Linux":
    # Assign 'win_lin' for Windows or Linux
    system = "win_lin"
elif system_name == "Darwin":
    # Assign 'mac' for macOS
    system = "mac"

if sound_effects is True:
    from . import playsound
