from aqt import gui_hooks
from .utils import addon_config_editor_will_display_json

#Hook Clases for the setup
def setupHooks(check_data, ankimon_tracker_obj, prepare):
    gui_hooks.addon_config_editor_will_save_json.append(check_data.modify_json_configuration_on_save)
    gui_hooks.sync_did_finish.append(check_data.sync_on_anki_close)

    #On Save on Config, accept new config and add pokemon collection and mainpokemon to it
    gui_hooks.addon_config_editor_will_save_json.append(check_data.modify_json_configuration_on_save)
    gui_hooks.addon_config_editor_will_display_json.append(addon_config_editor_will_display_json)

    gui_hooks.card_will_show.append(prepare)