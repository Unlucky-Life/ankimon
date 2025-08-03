from aqt import gui_hooks
from .utils import addon_config_editor_will_display_json


#Hook Classes for the setup
def setupHooks(check_data, ankimon_tracker_obj, prepare):
    """Set up Ankimon hooks - updated to handle None check_data"""
    
    # Only set up sync hooks if check_data exists and has the required methods
    if check_data is not None:
        if hasattr(check_data, 'modify_json_configuration_on_save'):
            gui_hooks.addon_config_editor_will_save_json.append(check_data.modify_json_configuration_on_save)
        
        if hasattr(check_data, 'sync_on_anki_close'):
            gui_hooks.sync_did_finish.append(check_data.sync_on_anki_close)
    
    # Always set up these hooks regardless of check_data
    gui_hooks.addon_config_editor_will_display_json.append(addon_config_editor_will_display_json)
    gui_hooks.card_will_show.append(prepare)
