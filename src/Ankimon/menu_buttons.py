from aqt.utils import *
from aqt.qt import *
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction, QKeySequence
from aqt import mw  # The main window object
from aqt.utils import qconnect

def create_menu_actions(
    database_complete,
    online_connectivity,
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
    show_agreement_and_download_database,
    credits,
    license,
    open_help_window,
    report_bug,
    rate_addon_url,
    version_dialog,
    trainer_card,
    ankimon_tracker_window,
    logger,
    trainer_card_window,
    data_handler_window,
    settings_window,
    shop_manager
):
    actions = []

    if database_complete:
        # Pokémon collection
        pokecol_action = QAction("Show Pokemon Collection", mw)
        mw.pokemenu.addAction(pokecol_action)
        qconnect(pokecol_action.triggered, pokecollection_win.show)

        # Ankimon Window
        test_action10 = QAction("Open Ankimon Window", mw)
        mw.pokemenu.addAction(test_action10)
        qconnect(test_action10.triggered, test_window.open_dynamic_window)

        # Itembag
        test_action15 = QAction("Itembag", mw)
        test_action15.triggered.connect(item_window.show_window)
        mw.pokemenu.addAction(test_action15)

        # Achievements
        achievement_bag_action = QAction("Achievements", mw)
        achievement_bag_action.triggered.connect(achievement_bag.show_window)
        mw.pokemenu.addAction(achievement_bag_action)

        # Showdown Teambuilder
        test_action8 = QAction("Open Pokemon Showdown Teambuilder", mw)
        qconnect(test_action8.triggered, open_team_builder)
        mw.pokemenu.addAction(test_action8)

        # Export to Showdown
        test_action6 = QAction("Export Main Pokemon to PkmnShowdown", mw)
        qconnect(test_action6.triggered, export_to_pkmn_showdown)
        mw.pokemenu.addAction(test_action6)

        test_action7 = QAction("Export All Pokemon to PkmnShowdown", mw)
        qconnect(test_action7.triggered, export_all_pkmn_showdown)
        mw.pokemenu.addAction(test_action7)

        # Flexing Collection
        flex_pokecoll_action = QAction("Export All Pokemon to PokePast for flexing", mw)
        qconnect(flex_pokecoll_action.triggered, flex_pokemon_collection)
        mw.pokemenu.addAction(flex_pokecoll_action)

    # Effectiveness chart
    test_action11 = QAction("Check Effectiveness Chart", mw)
    test_action11.triggered.connect(eff_chart.show_eff_chart)
    mw.pokemenu.addAction(test_action11)

    # Generations and Pokémon chart
    test_action12 = QAction("Check Generations and Pokemon Chart", mw)
    test_action12.triggered.connect(gen_id_chart.show_gen_chart)
    mw.pokemenu.addAction(test_action12)

    # Download Resources
    test_action3 = QAction("Download Resources", mw)
    qconnect(test_action3.triggered, show_agreement_and_download_database)
    mw.pokemenu.addAction(test_action3)

    # Credits
    test_action14 = QAction("Credits", mw)
    test_action14.triggered.connect(credits.show_window)
    mw.pokemenu.addAction(test_action14)

    # About and License
    test_action13 = QAction("About and License", mw)
    test_action13.triggered.connect(license.show_window)
    mw.pokemenu.addAction(test_action13)

    # Help Guide
    help_action = QAction("Open Help Guide", mw)
    help_action.triggered.connect(lambda :open_help_window(online_connectivity))
    mw.pokemenu.addAction(help_action)

    # Report Bug
    test_action16 = QAction("Report Bug", mw)
    test_action16.triggered.connect(report_bug)
    mw.pokemenu.addAction(test_action16)

    # Rate Addon
    rate_action = QAction("Rate This", mw)
    rate_action.triggered.connect(rate_addon_url)
    mw.pokemenu.addAction(rate_action)

    # Version
    version_action = QAction("Version", mw)
    version_action.triggered.connect(version_dialog.open)
    mw.pokemenu.addAction(version_action)

    config_action = QAction("Settings", mw)
    config_action.triggered.connect(settings_window.show_window)
    # Show the Settings window
    mw.pokemenu.addAction(config_action)

    data_window_action = QAction("Data", mw)
    data_window_action.triggered.connect(data_handler_window.show_window)
    # Show the Settings window
    mw.pokemenu.addAction(data_window_action)

    tracker_window_action = QAction("Tracker", mw)
    tracker_window_action.triggered.connect(ankimon_tracker_window.toggle_window)
    tracker_window_action.setShortcut(QKeySequence("Ctrl+Shift+K"))
    # Show the Settings window
    mw.pokemenu.addAction(tracker_window_action)

    # Set up a shortcut (Ctrl+Shift+L) to open the log window
    ankimon_logger_action = QAction("Logger", mw)
    ankimon_logger_action.setShortcut(QKeySequence("Ctrl+Shift+L"))
    ankimon_logger_action.triggered.connect(logger.toggle_log_window)
    mw.pokemenu.addAction(ankimon_logger_action)

    # Set up a shortcut (Ctrl+L) to open the log window
    ankimon_trainer_card_action = QAction("Trainer Card", mw)
    ankimon_trainer_card_action.setShortcut(QKeySequence("Ctrl+Shift+Q"))
    ankimon_trainer_card_action.triggered.connect(trainer_card_window.toggle_window)
    mw.pokemenu.addAction(ankimon_trainer_card_action)

    # Add AnkimonShop Action to toggle the shop
    shop_manager_action = QAction("Item Shop", mw)
    shop_manager_action.triggered.connect(shop_manager.toggle_window)
    mw.pokemenu.addAction(shop_manager_action)