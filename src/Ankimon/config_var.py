from aqt import mw
import platform

config = mw.addonManager.getConfig(__name__)

pop_up_dialog_message_on_defeat = config["gui.pop_up_dialog_message_on_defeat"]
reviewer_text_message_box = config["gui.reviewer_text_message_box"]
reviewer_text_message_box_time = config["gui.reviewer_text_message_box_time"] #time in seconds for text message
reviewer_text_message_box_time = reviewer_text_message_box_time * 1000 #times 1000 for s => ms
reviewer_image_gif = config["gui.reviewer_image_gif"]
show_mainpkmn_in_reviewer = config["gui.show_mainpkmn_in_reviewer"] #0 is off, 1 normal, 2 battle mode
xp_bar_config = config["gui.xp_bar_config"]
review_hp_bar_thickness = config["gui.review_hp_bar_thickness"] #2 = 8px, 3# 12px, 4# 16px, 5# 20px
hp_bar_config = config["gui.hp_bar_config"] #2 = 8px, 3# 12px, 4# 16px, 5# 20px
xp_bar_location = config["gui.xp_bar_location"] #1 top, 2 = bottom
animate_time = config["gui.animate_time"] #default: true; false = animate for 0.8 seconds
view_main_front = config["gui.view_main_front"] #default: true => -1; false = 1
gif_in_collection = config["gui.gif_in_collection"] #default: true => -1; false = 1
styling_in_reviewer = config["gui.styling_in_reviewer"] #default: true; false = no styling in reviewer

automatic_battle = config["battle.automatic_battle"] #default: 0; 1 = catch_pokemon; 2 = defeat_pokemon
dmg_in_reviewer = config["battle.dmg_in_reviewer"] #default: false; true = mainpokemon is getting damaged in reviewer for false answers
cards_per_round = config["battle.cards_per_round"]

leaderboard = config.get("misc.leaderboard", False)  # Default to False if not found
ankiweb_sync = config.get("misc.ankiweb_sync", False)  # Default to False if not found
no_more_news = config["misc.YouShallNotPass_Ankimon_News"] #default: false; true = no more news
remove_levelcap = config["misc.remove_level_cap"] #default: false; true = no more news
ssh = config["misc.ssh"] #for eduroam users - false ; default: true
language = config["misc.language"]

ankimon_key = config["controls.key_for_opening_closing_ankimon"]
defeat_shortcut = config["controls.defeat_key"] #default: 5; ; Else if not 5 => controll + Key for capture
catch_shortcut = config["controls.catch_key"] #default: 6; Else if not 6 => controll + Key for capture
reviewer_buttons = config["controls.pokemon_buttons"] #default: true; false = no pokemon buttons in reviewer

sound_effects = config["audio.sound_effects"] #default: false; true = sound_effects on
sounds = config["audio.sounds"]
battle_sounds = config["audio.battle_sounds"]


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
