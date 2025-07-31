from aqt import mw, gui_hooks
from aqt.utils import tooltip

from .sync_pokemon_data import check_and_sync_pokemon_data, ImprovedPokemonDataSync
from .ankimon_sync import save_ankimon_configs, read_ankimon_configs


def setup_ankimon_sync_hooks(settings_obj, logger):
    """
    Set up hooks for automatic Ankimon data syncing.
    Call this function during addon initialization.
    """
    
    # Hook: Before sync starts - save local data to media folder
    def on_sync_will_start():
        """Called before sync starts - save configs to media folder."""
        try:
            synced_files = save_ankimon_configs()
            if synced_files:
                logger.log("info", f"Prepared {len(synced_files)} Ankimon files for sync: {', '.join(synced_files)}")
        except Exception as e:
            logger.log("error", f"Failed to prepare Ankimon files for sync: {str(e)}")
    
    # Hook: After sync finishes - read updated data from media folder  
    def on_sync_did_finish():
        """Called after sync finishes - read configs from media folder."""
        try:
            updated_files = read_ankimon_configs(media_sync_status=False)
            if updated_files:
                logger.log("info", f"Updated {len(updated_files)} Ankimon files from sync: {', '.join(updated_files)}")
                tooltip(f"Updated {len(updated_files)} Ankimon files from AnkiWeb")
        except Exception as e:
            logger.log("error", f"Failed to read Ankimon files after sync: {str(e)}")
    
    # Hook: Profile loaded - check for sync conflicts
    def on_profile_did_open():
        """Called when profile is loaded - check for sync conflicts."""
        try:
            sync_dialog = check_and_sync_pokemon_data(settings_obj, logger)
            # Dialog will show automatically if there are conflicts
        except Exception as e:
            logger.log("error", f"Failed to check Ankimon sync status: {str(e)}")
    
    # Hook: Profile will close - save data before closing
    def on_profile_will_close():
        """Called before profile closes - ensure data is saved."""
        try:
            synced_files = save_ankimon_configs()
            if synced_files:
                logger.log("info", f"Saved {len(synced_files)} Ankimon files before closing")
        except Exception as e:
            logger.log("error", f"Failed to save Ankimon files before closing: {str(e)}")
    
    # Register the hooks with the CORRECT hook names
    gui_hooks.sync_will_start.append(on_sync_will_start)
    gui_hooks.sync_did_finish.append(on_sync_did_finish) 
    gui_hooks.profile_did_open.append(on_profile_did_open)
    gui_hooks.profile_will_close.append(on_profile_will_close)
    
    logger.log("info", "Ankimon sync hooks registered successfully")


def show_sync_dialog_manually(settings_obj, logger):
    """
    Manually show the sync dialog (for menu option or button).
    Returns the dialog instance.
    """
    try:
        dialog = ImprovedPokemonDataSync(settings_obj, logger)
        dialog.show()
        return dialog
    except Exception as e:
        logger.log("error", f"Failed to show sync dialog: {str(e)}")
        return None


def force_sync_to_ankiweb(logger):
    """Force sync all local data to AnkiWeb (for emergency use)."""
    try:
        from .ankimon_sync import get_ankimon_sync
        success = get_ankimon_sync().force_sync_to_media()
        if success:
            logger.log("info", "Force sync to AnkiWeb completed successfully")
        return success
    except Exception as e:
        logger.log("error", f"Force sync to AnkiWeb failed: {str(e)}")
        return False


def force_sync_from_ankiweb(logger):
    """Force sync all data from AnkiWeb to local (for emergency use)."""
    try:
        from .ankimon_sync import get_ankimon_sync
        success = get_ankimon_sync().force_sync_from_media()
        if success:
            logger.log("info", "Force sync from AnkiWeb completed successfully")
        return success
    except Exception as e:
        logger.log("error", f"Force sync from AnkiWeb failed: {str(e)}")
        return False


def trigger_manual_sync(logger):
    """Manually trigger a sync of Pokemon data (for use after Pokemon actions)."""
    try:
        synced_files = save_ankimon_configs()
        if synced_files:
            logger.log("info", f"Manually synced {len(synced_files)} files: {', '.join(synced_files)}")
        return len(synced_files) > 0
    except Exception as e:
        logger.log("error", f"Manual sync failed: {str(e)}")
        return False

