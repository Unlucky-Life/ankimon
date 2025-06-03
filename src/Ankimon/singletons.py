"""
singletons.py

This module groups up some of the global variables that originally wer ein the __init__.py.
This module, hopefully, does not have vocation to remain permanently. This is but a transition step
in the splitting of the __init__.py file.

More detailed explanation if needed:
- Any important classes/functions
- Special behaviors, assumptions, or usage notes

Author: Axil
Created: 2025-06-03 (YYY-MM-DD)
"""
import json
import uuid

from aqt import mw

from .pyobj.ankimon_tracker import AnkimonTracker
from .pyobj.settings import Settings
from .pyobj.settings_window import SettingsWindow
from .pyobj.pokemon_obj import PokemonObject
from .pyobj.InfoLogger import ShowInfoLogger
from .pyobj.trainer_card import TrainerCard
from .pyobj.translator import Translator
from .pyobj.test_window import TestWindow
from .pyobj.achievement_window import AchievementWindow
from .functions.update_main_pokemon import update_main_pokemon

# start loggerobject for Ankimon
logger = ShowInfoLogger()

# Create the Settings object
settings_obj = Settings()

# Pass the correct attributes to SettingsWindow
settings_window = SettingsWindow(
    config=settings_obj.config,                 # Use settings_obj.config instead of settings_obj.settings.config
    set_config_callback=settings_obj.set,
    save_config_callback=settings_obj.save_config,
    load_config_callback=settings_obj.load_config
)

#Init Translator
translator = Translator(language=int(settings_obj.get("misc.language", int(9))))

# Not sure what this does, but from afar it looks like a bad idea
mw.settings_ankimon = settings_window
mw.logger = logger
mw.translator = translator
mw.settings_obj = settings_obj

main_pokemon, mainpokemon_empty = update_main_pokemon()

enemy_pokemon = PokemonObject(
    name="Rattata",             # Name of the Pokémon
    shiny=False,                # Shiny status (False for normal appearance)
    id=19,                      # ID number
    level=5,                    # Level
    ability="Run Away",         # Ability specific to Rattata
    type="Normal",              # Type (Normal type for Rattata)
    stats = {                     # Base stats for Rattata
      "hp": 39,
      "atk": 52,
      "def": 43,
      "spa": 60,
      "spd": 50,
      "spe": 65,
      "xp": 101
    },
    attacks=["Quick Attack", "Tackle", "Tail Whip"], # Typical moves for Rattata
    base_experience=58,          # Base experience points
    growth_rate="medium-slow",        # Growth rate
    hp=30,                       # Hit points (HP)
    ev={
      "hp": 3,
      "atk": 5,
      "def": 4,
      "spa": 1,
      "spd": 2,
      "spe": 3
    },  # EVs (Effort Values) for stats
    iv={
      "hp": 27,
      "atk": 24,
      "def": 3,
      "spa": 24,
      "spd": 16,
      "spe": 21
    }, # IVs (Individual Values) for stats
    gender="M",                   # Gender
    battle_status="Fighting",    # Status during battle
    xp=0,                         # XP (experience points)
    position=(5, 5)              # Position in battle
)

# Create a sample trainer card to test
trainer_card = TrainerCard(
    logger,
    main_pokemon,
    settings_obj,
    trainer_name=settings_obj.get("trainer.name", "Ash"),
    badge_count=8,
    trainer_id = ''.join(filter(str.isdigit, str(uuid.uuid4()).replace('-', ''))),
    xp=0,
    team="Pikachu (Level 25), Charizard (Level 50), Bulbasaur (Level 15)",
    league = 'Unranked',
)

ankimon_tracker_obj = AnkimonTracker(
    trainer_card=trainer_card,
    settings_obj=settings_obj,
)
# Set Pokémon in the tracker
ankimon_tracker_obj.set_main_pokemon(main_pokemon)
ankimon_tracker_obj.set_enemy_pokemon(enemy_pokemon)

# Create an instance of the MainWindow
test_window = TestWindow(
    main_pokemon=main_pokemon,
    enemy_pokemon=enemy_pokemon,
    settings_obj=settings_obj,
    ankimon_tracker_obj=ankimon_tracker_obj,
    translator=translator,
    parent=mw,
    )

achievement_bag = AchievementWindow()

# data_handler_obj = DataHandler()
# data_handler_window = DataHandlerWindow(
#     data_handler = data_handler_obj
# )

# # Log an startup message
# logger.log_and_showinfo('game', translator.translate("startup"))
# logger.log_and_showinfo('game', translator.translate("backing_up_files"))

# # Initialize the Pokémon Shop Manager
# shop_manager = PokemonShopManager(
#     logger=logger,
#     settings_obj=settings_obj,
#     set_callback=settings_obj.set,
#     get_callback=settings_obj.get
# )

# ankimon_tracker_window = AnkimonTrackerWindow(
#     tracker = ankimon_tracker_obj
# )

# pokedex_window = Pokedex(addon_dir, ankimon_tracker = ankimon_tracker_obj)

# reviewer_obj = Reviewer_Manager(
#     settings_obj=settings_obj,
#     main_pokemon=main_pokemon,
#     enemy_pokemon=enemy_pokemon,
#     ankimon_tracker=ankimon_tracker_obj,
# )

# pokecollection_win = PokemonCollectionDialog(logger=logger, settings_obj=settings_obj, mainpokemon_function = MainPokemon, main_pokemon = main_pokemon)



# # Create an instance of the MainWindow
# starter_window = StarterWindow()

# evo_window = EvoWindow()

# eff_chart = TableWidget()
# pokedex = Pokedex_Widget()
# gen_id_chart = IDTableWidget()

# license = License()

# credits = Credits()
    
# item_window = ItemWindow(
#     logger=logger,
#     main_pokemon=main_pokemon,
#     enemy_pokemon=enemy_pokemon,
#     itembagpath=itembag_path,
#     achievements=check_badges(),
#     starter_window = starter_window,
#     evo_window=evo_window,
# )

# version_dialog = Version_Dialog()
