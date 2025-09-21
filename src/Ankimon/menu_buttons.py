from typing import Callable
from pathlib import Path
from typing import Union

from aqt.utils import *
from aqt.qt import *
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction, QKeySequence
from aqt import mw  # The main window object
from aqt.utils import qconnect


from .gui_classes.choose_trainer_sprite_graphical import TrainerSpriteGraphicalDialog

from .pyobj.trainer_card_window import TrainerCardGUI
from .gui_classes.pokemon_team_window import PokemonTeamDialog
from .gui_classes.check_files import FileCheckerApp
from .pyobj.download_sprites import show_agreement_and_download_dialog
from .pyobj.ankimon_leaderboard import show_api_key_dialog
from .pyobj.settings import Settings
from .pyobj.translator import Translator
from .pyobj.InfoLogger import ShowInfoLogger
from .pyobj.collection_dialog import PokemonCollectionDialog
from .pyobj.item_window import ItemWindow
from .pyobj.pc_box import PokemonPC
from .pyobj.trainer_card import TrainerCard
from .pyobj.data_handler_window import DataHandlerWindow
from .pyobj.settings_window import SettingsWindow
from .pyobj.test_window import TestWindow
from .pyobj.data_handler import DataHandler
from .pyobj.ankimon_shop import PokemonShopManager
from .pokedex.pokedex_obj import Pokedex
from .pyobj.achievement_window import AchievementWindow
from .pyobj.ankimon_tracker_window import AnkimonTrackerWindow
from .pyobj.backup_manager import BackupManager
from .gui_classes.backup_manager_dialog import BackupManagerDialog
from .gui_entities import (
    License,
    Credits,
    TableWidget,
    IDTableWidget,
    Version_Dialog,
)

debug = True

# Initialize the menu
mw.translator = Translator(language=int(Settings().get("misc.language", int(9))))
mw.pokemenu = QMenu('&' + mw.translator.translate("ankimon_button_title"), mw)
game_menu = mw.pokemenu.addMenu(mw.translator.translate("ankimon_game_button_title"))
profile_menu = mw.pokemenu.addMenu(mw.translator.translate("ankimon_profile_button_title"))
collection_menu = mw.pokemenu.addMenu(mw.translator.translate("ankimon_collection_button_title"))
export_menu = mw.pokemenu.addMenu(mw.translator.translate("ankimon_export_button_title"))
help_menu = mw.pokemenu.addMenu(mw.translator.translate("ankimon_help_button_title"))
if debug is True:
    debug_menu = mw.pokemenu.addMenu(mw.translator.translate("ankimon_debug_button_title"))

def create_menu_actions(
    database_complete: bool,
    online_connectivity: bool,
    pokecollection_win: Union[PokemonCollectionDialog, None],
    item_window: ItemWindow,
    test_window: TestWindow,
    achievement_bag: AchievementWindow,
    open_team_builder: Callable,
    export_to_pkmn_showdown: Callable,
    export_all_pkmn_showdown: Callable,
    flex_pokemon_collection: Callable,
    eff_chart: TableWidget,
    gen_id_chart: IDTableWidget,
    credits: Credits,
    license: License,
    open_help_window: Callable,
    report_bug: Callable,
    rate_addon_url: Callable,
    version_dialog: Version_Dialog,
    trainer_card: TrainerCard,
    ankimon_tracker_window: AnkimonTrackerWindow,
    logger: ShowInfoLogger,
    data_handler_window: DataHandlerWindow,
    settings_window: SettingsWindow,
    shop_manager: PokemonShopManager,
    pokedex_window: Pokedex,
    ankimon_key,
    join_discord_url: Callable,
    open_leaderboard_url: Callable,
    settings_obj: Settings,
    addon_dir: Path,
    data_handler_obj: DataHandler,
    pokemon_pc: PokemonPC,
    backup_manager: BackupManager,
):
    actions = []

    if database_complete:
        # Pokémon collection
        if pokecollection_win is not None:
            pokecol_action = QAction(mw.translator.translate("show_collection_button"), mw)
            pokecol_action.setMenuRole(QAction.MenuRole.NoRole)
            collection_menu.addAction(pokecol_action)
            qconnect(pokecol_action.triggered, pokecollection_win.show)

        # Pokémon PC
        pokemon_pc_action = QAction("Pokémon PC", mw)
        pokemon_pc_action.setMenuRole(QAction.MenuRole.NoRole)
        collection_menu.addAction(pokemon_pc_action)
        qconnect(pokemon_pc_action.triggered, pokemon_pc.show)

        # Ankimon Window
        ankimon_window_action = QAction(mw.translator.translate("open_ankimon_window_button"), mw)
        ankimon_window_action.setMenuRole(QAction.MenuRole.NoRole)
        game_menu.addAction(ankimon_window_action)
        ankimon_window_action.setShortcut(QKeySequence(f"{ankimon_key}"))
        qconnect(ankimon_window_action.triggered, test_window.open_dynamic_window)

        # Itembag
        itembag_action = QAction(mw.translator.translate("itembag_button"), mw)
        itembag_action.setMenuRole(QAction.MenuRole.NoRole)
        itembag_action.triggered.connect(item_window.show_window)
        collection_menu.addAction(itembag_action)

        # Achievements
        def show_achievements_window():
            from .pyobj.achievements_dialog import AchievementsDialog
            if not hasattr(mw, "_achievements_dialog") or mw._achievements_dialog is None:
                mw._achievements_dialog = AchievementsDialog(addon_dir, data_handler_obj)
            mw._achievements_dialog.setWindowModality(Qt.WindowModality.NonModal)
            mw._achievements_dialog.show()
            mw._achievements_dialog.raise_()
            mw._achievements_dialog.activateWindow()

        achievement_bag_action = QAction(mw.translator.translate("achievements_button"), mw)
        achievement_bag_action.setMenuRole(QAction.MenuRole.NoRole)
        achievement_bag_action.triggered.connect(show_achievements_window)
        profile_menu.addAction(achievement_bag_action)

        # Showdown Teambuilder
        pokemon_showdown_action = QAction(mw.translator.translate("open_showdown_teambuilder_button"), mw)
        pokemon_showdown_action.setMenuRole(QAction.MenuRole.NoRole)
        qconnect(pokemon_showdown_action.triggered, open_team_builder)
        export_menu.addAction(pokemon_showdown_action)

        # Export to Showdown
        export_main_to_showdown = QAction(mw.translator.translate("export_main_pokemon_button"), mw)
        export_main_to_showdown.setMenuRole(QAction.MenuRole.NoRole)
        qconnect(export_main_to_showdown.triggered, export_to_pkmn_showdown)
        export_menu.addAction(export_main_to_showdown)

        export_all_to_showdown = QAction(mw.translator.translate("export_all_pokemon_button"), mw)
        export_all_to_showdown.setMenuRole(QAction.MenuRole.NoRole)
        qconnect(export_all_to_showdown.triggered, export_all_pkmn_showdown)
        export_menu.addAction(export_all_to_showdown)

        # Flexing Collection
        flex_pokecoll_action = QAction(mw.translator.translate("export_all_pokemon_to_pokepaste_button"), mw)
        flex_pokecoll_action.setMenuRole(QAction.MenuRole.NoRole)
        qconnect(flex_pokecoll_action.triggered, flex_pokemon_collection)
        export_menu.addAction(flex_pokecoll_action)

        pokedex_action = QAction(mw.translator.translate("open_pokedex_button"), mw)
        pokedex_action.setMenuRole(QAction.MenuRole.NoRole)
        qconnect(pokedex_action.triggered, pokedex_window.show)
        collection_menu.addAction(pokedex_action)

    # Backup Manager
    backup_manager_action = QAction("Backup Manager", mw)
    backup_manager_action.setMenuRole(QAction.MenuRole.NoRole)
    backup_manager_action.triggered.connect(lambda: BackupManagerDialog(backup_manager, mw).exec())
    game_menu.addAction(backup_manager_action)

    # Effectiveness chart
    eff_chart_action = QAction(mw.translator.translate("eff_chart_button"), mw)
    eff_chart_action.setMenuRole(QAction.MenuRole.NoRole)
    eff_chart_action.triggered.connect(eff_chart.show_eff_chart)
    help_menu.addAction(eff_chart_action)

    # Generations and Pokémon chart
    gen_and_poke_chart_action = QAction(mw.translator.translate("gen_chart_button"), mw)
    gen_and_poke_chart_action.setMenuRole(QAction.MenuRole.NoRole)
    gen_and_poke_chart_action.triggered.connect(gen_id_chart.show_gen_chart)
    help_menu.addAction(gen_and_poke_chart_action)

    # Join Discord
    join_discord_action = QAction(mw.translator.translate("join_discord_button"), mw)
    join_discord_action.setMenuRole(QAction.MenuRole.NoRole)
    join_discord_action.triggered.connect(join_discord_url)
    help_menu.addAction(join_discord_action)

    # Open Ankimon Leaderboard
    open_leaderboard_action = QAction(("Ankimon Leaderboard"), mw)
    open_leaderboard_action.setMenuRole(QAction.MenuRole.NoRole)
    open_leaderboard_action.triggered.connect(open_leaderboard_url)
    game_menu.addAction(open_leaderboard_action)

    # Credits
    credits_action = QAction(mw.translator.translate("ankimon_credits_button"), mw)
    credits_action.setMenuRole(QAction.MenuRole.NoRole)
    credits_action.triggered.connect(credits.show_window)
    help_menu.addAction(credits_action)

    # About and License
    about_and_license_action = QAction(mw.translator.translate("ankimon_about_and_license_button"), mw)
    about_and_license_action.setMenuRole(QAction.MenuRole.NoRole)
    about_and_license_action.triggered.connect(license.show_window)
    help_menu.addAction(about_and_license_action)

    # Help Guide
    help_action = QAction(mw.translator.translate("open_help_guide_button"), mw)
    help_action.setMenuRole(QAction.MenuRole.NoRole)
    help_action.triggered.connect(lambda: open_help_window(online_connectivity))
    help_menu.addAction(help_action)

    # Report Bug
    report_bug_action = QAction(mw.translator.translate("report_bug_button"), mw)
    report_bug_action.setMenuRole(QAction.MenuRole.NoRole)
    report_bug_action.triggered.connect(report_bug)
    help_menu.addAction(report_bug_action)

    # Rate Addon
    rate_action = QAction(mw.translator.translate("rate_this_button"), mw)
    rate_action.setMenuRole(QAction.MenuRole.NoRole)
    rate_action.triggered.connect(rate_addon_url)
    mw.pokemenu.addAction(rate_action)

    # Version
    version_action = QAction(mw.translator.translate("ankimon_version_button"), mw)
    version_action.setMenuRole(QAction.MenuRole.NoRole)
    version_action.triggered.connect(version_dialog.open)
    help_menu.addAction(version_action)

    config_action = QAction(mw.translator.translate("ankimon_settings_button"), mw)
    config_action.setMenuRole(QAction.MenuRole.NoRole)
    config_action.triggered.connect(settings_window.show_window)
    # Show the Settings window
    mw.pokemenu.addAction(config_action)

    if debug is True:
        data_window_action = QAction(mw.translator.translate("ankimon_data_button"), mw)
        data_window_action.setMenuRole(QAction.MenuRole.NoRole)
        data_window_action.triggered.connect(data_handler_window.show_window)
        # Show the Settings window
        debug_menu.addAction(data_window_action)

        tracker_window_action = QAction(mw.translator.translate("ankimon_tracker_button"), mw)
        tracker_window_action.setMenuRole(QAction.MenuRole.NoRole)
        tracker_window_action.triggered.connect(ankimon_tracker_window.toggle_window)
        tracker_window_action.setShortcut(QKeySequence("Ctrl+Shift+K"))
        # Show the Settings window
        debug_menu.addAction(tracker_window_action)

    # Set up a shortcut (Ctrl+Shift+L) to open the log window
    ankimon_logger_action = QAction(mw.translator.translate("logger_button"), mw)
    ankimon_logger_action.setMenuRole(QAction.MenuRole.NoRole)
    ankimon_logger_action.setShortcut(QKeySequence("Ctrl+Shift+L"))
    ankimon_logger_action.triggered.connect(logger.toggle_log_window)
    game_menu.addAction(ankimon_logger_action)

    # Set up a shortcut (Ctrl+L) to open the log window
    ankimon_trainer_card_action = QAction(mw.translator.translate("trainer_card_button"), mw)
    ankimon_trainer_card_action.setMenuRole(QAction.MenuRole.NoRole)
    ankimon_trainer_card_action.setShortcut(QKeySequence("Ctrl+Shift+Q"))
    # Create the TrainerCard GUI and show it inside Anki's main window
    ankimon_trainer_card_action.triggered.connect(lambda: TrainerCardGUI(trainer_card, settings_obj, parent=mw))
    profile_menu.addAction(ankimon_trainer_card_action)

    # Add AnkimonShop Action to toggle the shop
    shop_manager_action = QAction(mw.translator.translate("item_shop_button"), mw)
    shop_manager_action.setMenuRole(QAction.MenuRole.NoRole)
    shop_manager_action.triggered.connect(shop_manager.toggle_window)
    game_menu.addAction(shop_manager_action)

    # Choose Trainer Sprite Action
    choose_trainer_sprite_action = QAction(mw.translator.translate("choose_trainer_sprite_button"), mw)
    choose_trainer_sprite_action.setMenuRole(QAction.MenuRole.NoRole)
    choose_trainer_sprite_action.triggered.connect(lambda: TrainerSpriteGraphicalDialog(settings_obj=settings_obj).exec())
    game_menu.addAction(choose_trainer_sprite_action)

    pokemon_team_action = QAction(mw.translator.translate("choose_pokemon_team_button"), mw)
    pokemon_team_action.setMenuRole(QAction.MenuRole.NoRole)
    pokemon_team_action.triggered.connect(lambda: PokemonTeamDialog(settings_obj, logger))
    game_menu.addAction(pokemon_team_action)

    file_check_action = QAction(mw.translator.translate("ankimon_file_checker_button"), mw)
    file_check_action.setMenuRole(QAction.MenuRole.NoRole)
    file_check_action.triggered.connect(lambda: FileCheckerApp().exec())
    help_menu.addAction(file_check_action)

    file_check_action = QAction(mw.translator.translate("ankimon_leaderboard_credentials_button"), mw)
    file_check_action.setMenuRole(QAction.MenuRole.NoRole)
    file_check_action.triggered.connect(show_api_key_dialog)
    mw.pokemenu.addAction(file_check_action)

    downloader_action = QAction(mw.translator.translate("download_resources_button"), mw)
    downloader_action.setMenuRole(QAction.MenuRole.NoRole)
    downloader_action.triggered.connect(show_agreement_and_download_dialog)
    help_menu.addAction(downloader_action)

    mw.form.menubar.addMenu(mw.pokemenu)
