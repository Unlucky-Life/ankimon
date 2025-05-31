#anki imports
from aqt import mw  # The main window object
from aqt.utils import *
from aqt.qt import *
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction, QKeySequence

# own scripts 
from .pyobj.trainer_card_window import TrainerCardGUI
from .pyobj.ankimon_leaderboard import show_api_key_dialog
from .gui_classes.choose_trainer_sprite import TrainerSpriteDialog
from .gui_classes.pokemon_team_window import PokemonTeamDialog
from .gui_classes.check_files import FileCheckerApp
from .user_files.download_sprites import show_agreement_and_download_dialog

# Enable / Disable Ankimon menu buttons module
debug = True

# Initialize the menu
# Create the main Ankimon menu and name it "Ankimon"
mw.pokemenu = QMenu('&' + mw.translator.translate("ankimon_button_title"), mw)

# Add submenus for different sections of the Ankimon menu
game_menu = mw.pokemenu.addMenu(mw.translator.translate("ankimon_game_button_title"))
profile_menu = mw.pokemenu.addMenu(mw.translator.translate("ankimon_profile_button_title"))
collection_menu = mw.pokemenu.addMenu(mw.translator.translate("ankimon_collection_button_title"))
export_menu = mw.pokemenu.addMenu(mw.translator.translate("ankimon_export_button_title"))
help_menu = mw.pokemenu.addMenu(mw.translator.translate("ankimon_help_button_title"))

# If debug mode is enabled, create a debug menu
if debug is True:
    debug_menu = mw.pokemenu.addMenu(mw.translator.translate("ankimon_debug_button_title"))

def create_menu_actions(
    database_complete: bool,
    online_connectivity: bool,
    pokecollection_win,
    item_window,
    test_window,
    achievement_bag,
    open_team_builder,
    export_to_pkmn_showdown,
    export_all_pkmn_showdown,
    flex_pokemon_collection,
    eff_chart,
    gen_id_chart,
    credits,
    license,
    open_help_window,
    report_bug,
    rate_addon_url,
    version_dialog,
    trainer_card,
    ankimon_tracker_window,
    logger,
    data_handler_window,
    settings_window,
    shop_manager,
    pokedex_window,
    ankimon_key,
    join_discord_url,
    open_leaderboard_url,
    settings_obj
) -> None:
    """
    Add buttons with actions to the Ankimon menu in the main window's menu bar.

    This function creates and connects all menu buttons for the Ankimon add-on,
    including Pokémon collection, export, help, debug, and customization buttons.
    Each button is added to the appropriate menu and connected to its handler.

    Args:
        database_complete (bool): True if the Pokémon database is complete.
        online_connectivity (bool): True if online connectivity is available.
        pokecollection_win: Window for Pokémon collection.
        item_window: Window for item bag.
        test_window: Main Ankimon window.
        achievement_bag: Achievements window.
        open_team_builder: Function to open the team builder.
        export_to_pkmn_showdown: Function to export main Pokémon to Showdown.
        export_all_pkmn_showdown: Function to export all Pokémon to Showdown.
        flex_pokemon_collection: Function to export all Pokémon to Pokepaste.
        eff_chart: Effectiveness chart window.
        gen_id_chart: Generation and Pokémon chart window.
        credits: Credits window.
        license: License/about window.
        open_help_window: Function to open the help guide.
        report_bug: Function to report a bug.
        rate_addon_url: Function to open the rate addon URL.
        version_dialog: Version dialog window.
        trainer_card: Trainer card data.
        ankimon_tracker_window: Tracker window.
        logger: Logger window.
        data_handler_window: Data handler window.
        settings_window: Settings window.
        shop_manager: Shop manager window.
        pokedex_window: Pokédex window.
        ankimon_key: Shortcut key for Ankimon window.
        join_discord_url: Function to join Discord.
        open_leaderboard_url: Function to open leaderboard.
        settings_obj: Settings object.

    Returns:
        None: This function modifies the menu bar but does not return a value.
    """
    # Add Pokémon-related buttons if the database is complete
    if database_complete:
        # Button: Show Pokémon collection window
        pokecollection_button = QAction(
            mw.translator.translate("show_collection_button"), mw
        )
        pokecollection_button.setMenuRole(QAction.MenuRole.NoRole)
        collection_menu.addAction(pokecollection_button)
        qconnect(pokecollection_button.triggered, pokecollection_win.show)

        # Button: Open main Ankimon window
        ankimon_window_button = QAction(
            mw.translator.translate("open_ankimon_window_button"), mw
        )
        ankimon_window_button.setMenuRole(QAction.MenuRole.NoRole)
        game_menu.addAction(ankimon_window_button)
        ankimon_window_button.setShortcut(QKeySequence(f"{ankimon_key}"))
        qconnect(ankimon_window_button.triggered, test_window.open_dynamic_window)

        # Button: Show item bag window
        itembag_button = QAction(
            mw.translator.translate("itembag_button"), mw
        )
        itembag_button.setMenuRole(QAction.MenuRole.NoRole)
        itembag_button.triggered.connect(item_window.show_window)
        collection_menu.addAction(itembag_button)

        # Button: Show achievements window
        achievement_bag_button = QAction(
            mw.translator.translate("achievements_button"), mw
        )
        achievement_bag_button.setMenuRole(QAction.MenuRole.NoRole)
        achievement_bag_button.triggered.connect(achievement_bag.show_window)
        profile_menu.addAction(achievement_bag_button)

        # Button: Open Showdown team builder
        showdown_teambuilder_button = QAction(
            mw.translator.translate("open_showdown_teambuilder_button"), mw
        )
        showdown_teambuilder_button.setMenuRole(QAction.MenuRole.NoRole)
        qconnect(showdown_teambuilder_button.triggered, open_team_builder)
        export_menu.addAction(showdown_teambuilder_button)

        # Button: Export main Pokémon as a code that can be copied to Showdown - for online battle
        export_main_button = QAction(
            mw.translator.translate("export_main_pokemon_button"), mw
        )
        export_main_button.setMenuRole(QAction.MenuRole.NoRole)
        qconnect(export_main_button.triggered, export_to_pkmn_showdown)
        export_menu.addAction(export_main_button)

        # Button: Export all Pokémon to Showdown
        export_all_button = QAction(
            mw.translator.translate("export_all_pokemon_button"), mw
        )
        export_all_button.setMenuRole(QAction.MenuRole.NoRole)
        qconnect(export_all_button.triggered, export_all_pkmn_showdown)
        export_menu.addAction(export_all_button)

        # Button: Export all Pokémon to Pokepaste
        flex_collection_button = QAction(
            mw.translator.translate("export_all_pokemon_to_pokepaste_button"), mw
        )
        flex_collection_button.setMenuRole(QAction.MenuRole.NoRole)
        qconnect(flex_collection_button.triggered, flex_pokemon_collection)
        export_menu.addAction(flex_collection_button)

        # Button: Open Pokédex window
        pokedex_button = QAction(
            mw.translator.translate("open_pokedex_button"), mw
        )
        pokedex_button.setMenuRole(QAction.MenuRole.NoRole)
        qconnect(pokedex_button.triggered, pokedex_window.show)
        collection_menu.addAction(pokedex_button)

    # Button: Show effectiveness chart
    eff_chart_button = QAction(
        mw.translator.translate("eff_chart_button"), mw
    )
    eff_chart_button.setMenuRole(QAction.MenuRole.NoRole)
    eff_chart_button.triggered.connect(eff_chart.show_eff_chart)
    help_menu.addAction(eff_chart_button)

    # Button: Show generation and Pokémon chart
    gen_chart_button = QAction(
        mw.translator.translate("gen_chart_button"), mw
    )
    gen_chart_button.setMenuRole(QAction.MenuRole.NoRole)
    gen_chart_button.triggered.connect(gen_id_chart.show_gen_chart)
    help_menu.addAction(gen_chart_button)

    # Button: Join Discord
    join_discord_button = QAction(
        mw.translator.translate("join_discord_button"), mw
    )
    join_discord_button.setMenuRole(QAction.MenuRole.NoRole)
    join_discord_button.triggered.connect(join_discord_url)
    help_menu.addAction(join_discord_button)

    # Button: Open Ankimon Leaderboard
    leaderboard_button = QAction(
        "Ankimon Leaderboard", mw
    )
    leaderboard_button.setMenuRole(QAction.MenuRole.NoRole)
    leaderboard_button.triggered.connect(open_leaderboard_url)
    game_menu.addAction(leaderboard_button)

    # Button: Show credits
    credits_button = QAction(
        mw.translator.translate("ankimon_credits_button"), mw
    )
    credits_button.setMenuRole(QAction.MenuRole.NoRole)
    credits_button.triggered.connect(credits.show_window)
    help_menu.addAction(credits_button)

    # Button: Show about and license
    about_license_button = QAction(
        mw.translator.translate("ankimon_about_and_license_button"), mw
    )
    about_license_button.setMenuRole(QAction.MenuRole.NoRole)
    about_license_button.triggered.connect(license.show_window)
    help_menu.addAction(about_license_button)

    # Button: Open help guide
    help_guide_button = QAction(
        mw.translator.translate("open_help_guide_button"), mw
    )
    help_guide_button.setMenuRole(QAction.MenuRole.NoRole)
    help_guide_button.triggered.connect(lambda: open_help_window(online_connectivity))
    help_menu.addAction(help_guide_button)

    # Button: Report bug
    report_bug_button = QAction(
        mw.translator.translate("report_bug_button"), mw
    )
    report_bug_button.setMenuRole(QAction.MenuRole.NoRole)
    report_bug_button.triggered.connect(report_bug)
    help_menu.addAction(report_bug_button)

    # Button: Rate addon
    rate_button = QAction(
        mw.translator.translate("rate_this_button"), mw
    )
    rate_button.setMenuRole(QAction.MenuRole.NoRole)
    rate_button.triggered.connect(rate_addon_url)
    mw.pokemenu.addAction(rate_button)

    # Button: Show version dialog
    version_button = QAction(
        mw.translator.translate("ankimon_version_button"), mw
    )
    version_button.setMenuRole(QAction.MenuRole.NoRole)
    version_button.triggered.connect(version_dialog.open)
    help_menu.addAction(version_button)

    # Button: Open settings
    settings_button = QAction(
        mw.translator.translate("ankimon_settings_button"), mw
    )
    settings_button.setMenuRole(QAction.MenuRole.NoRole)
    settings_button.triggered.connect(settings_window.show_window)
    mw.pokemenu.addAction(settings_button)

    # Debug menu buttons (if debug mode is enabled)
    if debug:
        # Button: Data handler window
        data_window_button = QAction(
            mw.translator.translate("ankimon_data_button"), mw
        )
        data_window_button.setMenuRole(QAction.MenuRole.NoRole)
        data_window_button.triggered.connect(data_handler_window.show_window)
        debug_menu.addAction(data_window_button)

        # Button: Tracker window
        tracker_button = QAction(
            mw.translator.translate("ankimon_tracker_button"), mw
        )
        tracker_button.setMenuRole(QAction.MenuRole.NoRole)
        tracker_button.triggered.connect(ankimon_tracker_window.toggle_window)
        tracker_button.setShortcut(QKeySequence("Ctrl+Shift+K"))
        debug_menu.addAction(tracker_button)

    # Button: Logger window
    logger_button = QAction(
        mw.translator.translate("logger_button"), mw
    )
    logger_button.setMenuRole(QAction.MenuRole.NoRole)
    logger_button.setShortcut(QKeySequence("Ctrl+Shift+L"))
    logger_button.triggered.connect(logger.toggle_log_window)
    game_menu.addAction(logger_button)

    # Button: Trainer card window
    trainer_card_button = QAction(
        mw.translator.translate("trainer_card_button"), mw
    )
    trainer_card_button.setMenuRole(QAction.MenuRole.NoRole)
    trainer_card_button.setShortcut(QKeySequence("Ctrl+Shift+Q"))
    trainer_card_button.triggered.connect(
        lambda: TrainerCardGUI(trainer_card, settings_obj, parent=mw)
    )
    profile_menu.addAction(trainer_card_button)

    # Button: Shop manager window
    shop_button = QAction(
        mw.translator.translate("item_shop_button"), mw
    )
    shop_button.setMenuRole(QAction.MenuRole.NoRole)
    shop_button.triggered.connect(shop_manager.toggle_window)
    game_menu.addAction(shop_button)

    # Button: Choose trainer sprite dialog
    trainer_sprite_button = QAction(
        mw.translator.translate("choose_trainer_sprite_button"), mw
    )
    trainer_sprite_button.setMenuRole(QAction.MenuRole.NoRole)
    trainer_sprite_button.triggered.connect(
        lambda: TrainerSpriteDialog(settings_obj=settings_obj).exec()
    )
    game_menu.addAction(trainer_sprite_button)

    # Button: Pokémon team dialog
    pokemon_team_button = QAction(
        mw.translator.translate("choose_pokemon_team_button"), mw
    )
    pokemon_team_button.setMenuRole(QAction.MenuRole.NoRole)
    pokemon_team_button.triggered.connect(
        lambda: PokemonTeamDialog(settings_obj, logger)
    )
    game_menu.addAction(pokemon_team_button)

    # Button: File checker dialog
    file_checker_button = QAction(
        mw.translator.translate("ankimon_file_checker_button"), mw
    )
    file_checker_button.setMenuRole(QAction.MenuRole.NoRole)
    file_checker_button.triggered.connect(lambda: FileCheckerApp().exec())
    help_menu.addAction(file_checker_button)

    # Button: Leaderboard credentials dialog - Add Leaderboard credentials for leaderboard
    leaderboard_credentials_button = QAction(
        mw.translator.translate("ankimon_leaderboard_credentials_button"), mw
    )
    leaderboard_credentials_button.setMenuRole(QAction.MenuRole.NoRole)
    leaderboard_credentials_button.triggered.connect(show_api_key_dialog)
    mw.pokemenu.addAction(leaderboard_credentials_button)

    # Button: Open resource downloader dialog to download sprites and other resources
    downloader_button = QAction(
        mw.translator.translate("download_resources_button"), mw
    )
    downloader_button.setMenuRole(QAction.MenuRole.NoRole)
    downloader_button.triggered.connect(show_agreement_and_download_dialog)
    help_menu.addAction(downloader_button)

    # Add the Ankimon menu to the main window's menu bar
    mw.form.menubar.addMenu(mw.pokemenu)