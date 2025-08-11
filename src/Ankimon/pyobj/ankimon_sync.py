# ankimon_sync.py - Improved Ankimon data sync system with subfolder approach
import base64
import filecmp
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any

from aqt import mw, gui_hooks
from aqt.utils import showWarning, showInfo, tooltip

from ..resources import user_path, addon_dir
from ..config_var import ankiweb_sync
from ..utils import close_anki

from PyQt6.QtGui import QTextOption
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QTextEdit, QPushButton, QDialog, QHBoxLayout, QScrollArea, QWidget

class ImprovedPokemonDataSync(QDialog):
    """
    Improved Pokemon data sync dialog using the new AnkimonDataSync system.
    Provides better file comparison and uses Anki's media sync for reliable syncing.
    """
    
    def __init__(self, settings_obj, logger):
        super().__init__(mw)
        self.config = settings_obj
        self.logger = logger
        self.sync_handler = AnkimonDataSync()
        
        self.setup_ui()
        self.check_for_differences()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Ankimon Data Sync")
        self.setMinimumSize(800, 600)
        
        # Main layout
        main_layout = QVBoxLayout()
        
        # Header message
        header_text = (
            "Sync your Pokemon data between devices using AnkiWeb.\n"
            "Choose to export your local data to AnkiWeb or import data from AnkiWeb to your device."
        )
        self.header_label = QLabel(header_text)
        main_layout.addWidget(self.header_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        self.export_button = QPushButton("Export Local Data to AnkiWeb")
        self.import_button = QPushButton("Import Data from AnkiWeb") 
        self.refresh_button = QPushButton("Refresh Comparison")
        
        self.export_button.clicked.connect(self.export_to_ankiweb)
        self.import_button.clicked.connect(self.import_from_ankiweb)
        self.refresh_button.clicked.connect(self.check_for_differences)
        
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(button_layout)
        
        # Comparison area
        comparison_layout = QHBoxLayout()
        
        # Local data area
        local_widget = QWidget()
        local_layout = QVBoxLayout(local_widget)
        local_layout.addWidget(QLabel("Local Data:"))
        
        self.local_text_area = QTextEdit()
        self.local_text_area.setReadOnly(True)
        self.local_text_area.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        local_layout.addWidget(self.local_text_area)
        
        # AnkiWeb data area  
        web_widget = QWidget()
        web_layout = QVBoxLayout(web_widget)
        web_layout.addWidget(QLabel("AnkiWeb Data:"))
        
        self.web_text_area = QTextEdit()
        self.web_text_area.setReadOnly(True)
        self.web_text_area.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        web_layout.addWidget(self.web_text_area)
        
        comparison_layout.addWidget(local_widget)
        comparison_layout.addWidget(web_widget)
        
        main_layout.addLayout(comparison_layout)
        
        self.setLayout(main_layout)
        
    def check_for_differences(self):
        """Check for differences between local and AnkiWeb data."""
        try:
            differences = self.sync_handler.get_file_differences()
            
            if not differences:
                self.header_label.setText(
                    "Ankimon Data Sync:\n"
                    "✅ All data is synchronized. No differences found."
                )
                self.local_text_area.setPlainText("No differences found.")
                self.web_text_area.setPlainText("No differences found.")
                self.export_button.setEnabled(False)
                self.import_button.setEnabled(False)
                return
            
            self.header_label.setText(
                f"⚠️ Found differences in {len(differences)} file(s). Please choose sync direction:\n"
            )
            self.export_button.setEnabled(True)
            self.import_button.setEnabled(True)
            
            self._display_differences(differences)
            self.show()
            
        except Exception as e:
            self.logger.log("error", f"Failed to check for differences: {str(e)}")
            showWarning(f"Error checking for differences: {str(e)}")
    
    def _display_differences(self, differences: Dict[str, Dict]):
        """Display improved JSON differences, showing only what changed per file with specific key differences."""
        import json
        from typing import Any, Dict, List, Tuple, Set
        
        def format_value(value: Any) -> str:
            """Format a value for display."""
            if isinstance(value, str):
                return f'"{value}"'
            elif isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, bool):
                return str(value).lower()
            elif isinstance(value, list):
                if len(value) <= 3:
                    return f"[{', '.join(format_value(v) for v in value)}]"
                else:
                    return f"[{', '.join(format_value(v) for v in value[:2])}, ... +{len(value)-2} more]"
            elif isinstance(value, dict):
                if len(value) <= 2:
                    items = [f"{k}: {format_value(v)}" for k, v in value.items()]
                    return "{" + ", ".join(items) + "}"
                else:
                    items = list(value.items())[:2]
                    formatted = [f"{k}: {format_value(v)}" for k, v in items]
                    return "{" + ", ".join(formatted) + f", ... +{len(value)-2} more" + "}"
            else:
                return str(value)[:50] + ("..." if len(str(value)) > 50 else "")
        
        def compare_dicts(local_dict: Dict, remote_dict: Dict, path: str = "") -> Tuple[List[str], List[str]]:
            """Compare two dictionaries and return differences with specific key details."""
            local_lines = []
            remote_lines = []
            
            all_keys = set(local_dict.keys()) | set(remote_dict.keys())
            
            for key in sorted(all_keys):
                current_path = f"{path}.{key}" if path else key
                local_val = local_dict.get(key, "<MISSING>")
                remote_val = remote_dict.get(key, "<MISSING>")
                
                if local_val == "<MISSING>":
                    local_lines.append(f"  {current_path}: <MISSING>")
                    remote_lines.append(f"+ {current_path}: {format_value(remote_val)}")
                elif remote_val == "<MISSING>":
                    local_lines.append(f"- {current_path}: {format_value(local_val)}")
                    remote_lines.append(f"  {current_path}: <MISSING>")
                elif local_val != remote_val:
                    # Show the actual different values
                    local_lines.append(f"- {current_path}: {format_value(local_val)}")
                    remote_lines.append(f"+ {current_path}: {format_value(remote_val)}")
                    
                    # If both are dicts, recursively compare them (but don't double-nest)
                    if isinstance(local_val, dict) and isinstance(remote_val, dict) and not path:
                        sub_local, sub_remote = compare_dicts(local_val, remote_val, current_path)
                        local_lines.extend([f"    {line}" for line in sub_local])
                        remote_lines.extend([f"    {line}" for line in sub_remote])
                # Don't show unchanged values
            
            return local_lines, remote_lines
        
        def get_pokemon_identifier(pokemon: Dict) -> str:
            """Get a unique identifier for a Pokemon."""
            # Try individual_id first (most unique)
            if 'individual_id' in pokemon and pokemon['individual_id']:
                return pokemon['individual_id']
            
            # Fall back to a combination of name, level, and captured_date
            name = pokemon.get('name', 'Unknown')
            level = pokemon.get('level', 0)
            captured = pokemon.get('captured_date', '')
            
            return f"{name}_L{level}_{captured}"
        
        def compare_pokemon_lists(local_list: List[Dict], remote_list: List[Dict]) -> Tuple[List[str], List[str]]:
            """Compare two lists of Pokemon with detailed differences."""
            local_lines = []
            remote_lines = []
            
            # Index by unique identifier
            local_map = {}
            remote_map = {}
            
            for i, pokemon in enumerate(local_list):
                if isinstance(pokemon, dict):
                    identifier = get_pokemon_identifier(pokemon)
                    local_map[identifier] = pokemon
                else:
                    local_map[f"invalid_pokemon_{i}"] = pokemon
            
            for i, pokemon in enumerate(remote_list):
                if isinstance(pokemon, dict):
                    identifier = get_pokemon_identifier(pokemon)
                    remote_map[identifier] = pokemon
                else:
                    remote_map[f"invalid_pokemon_{i}"] = pokemon
            
            all_identifiers = set(local_map.keys()) | set(remote_map.keys())
            
            local_lines.append(f"Total Pokemon: {len(local_list)}")
            remote_lines.append(f"Total Pokemon: {len(remote_list)}")
            
            changes_found = False
            
            for identifier in sorted(all_identifiers):
                local_pokemon = local_map.get(identifier)
                remote_pokemon = remote_map.get(identifier)
                
                # Get display name
                if local_pokemon and isinstance(local_pokemon, dict):
                    display_name = f"{local_pokemon.get('name', 'Unknown')} (L{local_pokemon.get('level', '?')})"
                elif remote_pokemon and isinstance(remote_pokemon, dict):
                    display_name = f"{remote_pokemon.get('name', 'Unknown')} (L{remote_pokemon.get('level', '?')})"
                else:
                    display_name = identifier[:20] + "..." if len(identifier) > 20 else identifier
                
                if local_pokemon is None:
                    remote_lines.append(f"+ {display_name}: (new Pokemon)")
                    local_lines.append(f"  {display_name}: <MISSING>")
                    changes_found = True
                elif remote_pokemon is None:
                    local_lines.append(f"- {display_name}: (removed Pokemon)")
                    remote_lines.append(f"  {display_name}: <MISSING>")
                    changes_found = True
                elif local_pokemon != remote_pokemon:
                    # Show what changed in this Pokemon
                    if isinstance(local_pokemon, dict) and isinstance(remote_pokemon, dict):
                        local_sub, remote_sub = compare_dicts(local_pokemon, remote_pokemon)
                        if local_sub or remote_sub:
                            local_lines.append(f"~ {display_name}: (modified)")
                            remote_lines.append(f"~ {display_name}: (modified)")
                            
                            # Show specific field differences
                            max_lines = max(len(local_sub), len(remote_sub))
                            local_sub.extend(["" ] * (max_lines - len(local_sub)))
                            remote_sub.extend(["" ] * (max_lines - len(remote_sub)))
                            
                            for l_line, r_line in zip(local_sub, remote_sub):
                                local_lines.append(f"    {l_line}")
                                remote_lines.append(f"    {r_line}")
                            
                            changes_found = True
                    else:
                        # Non-dict Pokemon (shouldn't happen, but handle it)
                        local_lines.append(f"- {display_name}: {format_value(local_pokemon)}")
                        remote_lines.append(f"+ {display_name}: {format_value(remote_pokemon)}")
                        changes_found = True
            
            if not changes_found:
                local_lines = ["No Pokemon differences detected"]
                remote_lines = ["No Pokemon differences detected"]
            
            return local_lines, remote_lines
        
        def compare_item_lists(local_list: List[Dict], remote_list: List[Dict]) -> Tuple[List[str], List[str]]:
            """Compare two lists of items with detailed differences."""
            local_lines = []
            remote_lines = []
            
            # Index by item name
            local_map = {item.get('item', f"item_{i}"): item for i, item in enumerate(local_list) if isinstance(item, dict)}
            remote_map = {item.get('item', f"item_{i}"): item for i, item in enumerate(remote_list) if isinstance(item, dict)}
            
            all_keys = set(local_map.keys()) | set(remote_map.keys())
            
            local_lines.append(f"Total items: {len(local_list)}")
            remote_lines.append(f"Total items: {len(remote_list)}")
            
            changes_found = False
            
            for key in sorted(all_keys):
                local_item = local_map.get(key)
                remote_item = remote_map.get(key)
                
                if local_item is None:
                    remote_lines.append(f"+ {key}: {remote_item.get('quantity', '?')}")
                    local_lines.append(f"  {key}: <MISSING>")
                    changes_found = True
                elif remote_item is None:
                    local_lines.append(f"- {key}: {local_item.get('quantity', '?')}")
                    remote_lines.append(f"  {key}: <MISSING>")
                    changes_found = True
                elif local_item != remote_item:
                    # Most likely quantity changed
                    local_qty = local_item.get('quantity', '?')
                    remote_qty = remote_item.get('quantity', '?')
                    
                    if local_qty != remote_qty:
                        local_lines.append(f"- {key}: {local_qty}")
                        remote_lines.append(f"+ {key}: {remote_qty}")
                        changes_found = True
                    else:
                        # Some other field changed, show full comparison
                        local_sub, remote_sub = compare_dicts(local_item, remote_item)
                        if local_sub or remote_sub:
                            local_lines.append(f"~ {key}: (other changes)")
                            remote_lines.append(f"~ {key}: (other changes)")
                            
                            for l_line, r_line in zip(local_sub, remote_sub):
                                local_lines.append(f"    {l_line}")
                                remote_lines.append(f"    {r_line}")
                            
                            changes_found = True
            
            if not changes_found:
                local_lines = ["No item differences detected"]
                remote_lines = ["No item differences detected"]
            
            return local_lines, remote_lines
        
        def compare_simple_lists(local_list: List, remote_list: List) -> Tuple[List[str], List[str]]:
            """Compare two simple lists with specific differences."""
            local_set = set(str(item) for item in local_list)
            remote_set = set(str(item) for item in remote_list)
            
            local_lines = []
            remote_lines = []
            
            # Items only in local
            only_local = local_set - remote_set
            for item in sorted(only_local):
                local_lines.append(f"- {item}")
                remote_lines.append("  <removed>")
            
            # Items only in remote
            only_remote = remote_set - local_set
            for item in sorted(only_remote):
                local_lines.append("  <added>")
                remote_lines.append(f"+ {item}")
            
            # Show counts for context
            if only_local or only_remote:
                local_lines.insert(0, f"Total items: {len(local_list)}")
                remote_lines.insert(0, f"Total items: {len(remote_list)}")
            else:
                local_lines = ["No list differences detected"]
                remote_lines = ["No list differences detected"]
            
            return local_lines, remote_lines
        
        def detect_structure_and_compare(local_data: Any, remote_data: Any, filename: str) -> Tuple[List[str], List[str]]:
            """Detect the data structure and apply appropriate comparison."""
            
            # Handle None/missing data cases
            if local_data is None and remote_data is None:
                return ["Both files are empty"], ["Both files are empty"]
            elif local_data is None:
                return ["Local file is empty"], [f"Remote has data: {type(remote_data).__name__}"]
            elif remote_data is None:
                return [f"Local has data: {type(local_data).__name__}"], ["Remote file is empty"]
            
            # Both are lists
            if isinstance(local_data, list) and isinstance(remote_data, list):
                # Special handling for Pokemon files
                if filename in ['mypokemon.json', 'mainpokemon.json']:
                    return compare_pokemon_lists(local_data, remote_data)
                
                # Special handling for items
                elif filename == 'items.json':
                    if (local_data and isinstance(local_data[0], dict) and 'item' in local_data[0]) or \
                    (remote_data and isinstance(remote_data[0], dict) and 'item' in remote_data[0]):
                        return compare_item_lists(local_data, remote_data)
                
                # Fall back to simple list comparison
                return compare_simple_lists(local_data, remote_data)
            
            # Both are dictionaries
            elif isinstance(local_data, dict) and isinstance(remote_data, dict):
                return compare_dicts(local_data, remote_data)
            
            # Different types or simple values
            else:
                local_lines = [f"Type: {type(local_data).__name__}"]
                remote_lines = [f"Type: {type(remote_data).__name__}"]
                
                if local_data is not None:
                    local_lines.append(f"- Value: {format_value(local_data)}")
                else:
                    local_lines.append("- Value: <no data>")
                    
                if remote_data is not None:
                    remote_lines.append(f"+ Value: {format_value(remote_data)}")
                else:
                    remote_lines.append("+ Value: <no data>")
                    
                return local_lines, remote_lines
        
        # Main display logic
        local_content = []
        web_content = []
        
        for filename, diff_info in differences.items():
            local_content.append(f"=== {filename} ===")
            web_content.append(f"=== {filename} ===")
            
            if diff_info.get('error'):
                error_msg = f"❌ Error: {diff_info['error']}"
                local_content.append(error_msg)
                web_content.append(error_msg)
                local_content.append("")
                web_content.append("")
                continue
            
            local_exists = diff_info.get('local_exists', False)
            media_exists = diff_info.get('media_exists', False)
            
            # Show file existence status
            local_content.append(f"Local file exists: {local_exists}")
            web_content.append(f"AnkiWeb file exists: {media_exists}")
            
            if filename.endswith(('.json', '.obf')):
                local_data = diff_info.get('local_data')
                media_data = diff_info.get('media_data')
                
                # Use smart comparison
                local_lines, remote_lines = detect_structure_and_compare(local_data, media_data, filename)
                
                if local_lines or remote_lines:
                    local_content.append("Differences:")
                    web_content.append("Differences:")
                    
                    # Pad the shorter list to align output
                    max_lines = max(len(local_lines), len(remote_lines))
                    local_lines.extend(["" ] * (max_lines - len(local_lines)))
                    remote_lines.extend(["" ] * (max_lines - len(remote_lines)))
                    
                    local_content.extend(local_lines)
                    web_content.extend(remote_lines)
                else:
                    local_content.append("No differences detected")
                    web_content.append("No differences detected")
            else:
                local_content.append("(Binary/Non-JSON file - cannot show detailed diff)")
                web_content.append("(Binary/Non-JSON file - cannot show detailed diff)")
            
            local_content.append("")
            web_content.append("")
        
        self.local_text_area.setPlainText("\n".join(local_content))
        self.web_text_area.setPlainText("\n".join(web_content))

    def _format_json_data(self, data: Any, filename: str) -> List[str]:
        """Format JSON data for display, showing key differences."""
        lines = []
        
        if filename in ['mypokemon.json', 'mainpokemon.json']:
            # Special handling for Pokemon data
            if isinstance(data, list):
                lines.append(f"Pokemon count: {len(data)}")
                for i, pokemon in enumerate(data[:3]):  # Show first 3
                    if isinstance(pokemon, dict):
                        lines.extend(self._format_pokemon_data(pokemon, i))
                if len(data) > 3:
                    lines.append(f"... and {len(data) - 3} more Pokemon")
            else:
                lines.append("Invalid Pokemon data format")
        else:
            # Generic JSON formatting
            try:
                if isinstance(data, dict):
                    lines.append(f"Keys: {list(data.keys())}")
                    for key, value in list(data.items())[:5]:  # Show first 5 items
                        if isinstance(value, (str, int, float, bool)):
                            lines.append(f"  {key}: {value}")
                        else:
                            lines.append(f"  {key}: {type(value).__name__}")
                elif isinstance(data, list):
                    lines.append(f"Array with {len(data)} items")
                    for i, item in enumerate(data[:3]):
                        lines.append(f"  [{i}]: {type(item).__name__}")
                else:
                    lines.append(str(data)[:100] + "..." if len(str(data)) > 100 else str(data))
            except Exception as e:
                lines.append(f"Error formatting data: {str(e)}")
        
        return lines
    
    def _format_pokemon_data(self, pokemon: Dict, index: int) -> List[str]:
        """Format Pokemon data for display showing all relevant fields."""
        lines = [f"Pokemon {index + 1}:"]
        
        # Core identification
        if 'name' in pokemon:
            lines.append(f"  Name: {pokemon['name']}")
        if 'individual_id' in pokemon:
            lines.append(f"  ID: {pokemon['individual_id'][:8]}...")
        if 'level' in pokemon:
            lines.append(f"  Level: {pokemon['level']}")
        
        # Stats and characteristics
        important_fields = [
            'gender', 'ability', 'type', 'current_hp', 'xp', 'friendship',
            'pokemon_defeated', 'shiny', 'tier', 'everstone', 'captured_date'
        ]
        
        for field in important_fields:
            if field in pokemon:
                value = pokemon[field]
                if isinstance(value, list):
                    lines.append(f"  {field.capitalize()}: {', '.join(map(str, value))}")
                else:
                    lines.append(f"  {field.capitalize()}: {value}")
        
        # Complex fields summary
        if 'stats' in pokemon and isinstance(pokemon['stats'], dict):
            lines.append(f"  Stats: {len(pokemon['stats'])} stat values")
        if 'ev' in pokemon and isinstance(pokemon['ev'], dict):
            ev_total = sum(pokemon['ev'].values()) if pokemon['ev'] else 0
            lines.append(f"  EVs: {ev_total} total")
        if 'iv' in pokemon and isinstance(pokemon['iv'], dict):
            iv_avg = sum(pokemon['iv'].values()) / len(pokemon['iv']) if pokemon['iv'] else 0
            lines.append(f"  IVs: {iv_avg:.1f} average")
        if 'attacks' in pokemon and isinstance(pokemon['attacks'], list):
            lines.append(f"  Moves: {len(pokemon['attacks'])} moves")
        
        return lines
    
    def export_to_ankiweb(self):
        """Export local data to AnkiWeb."""
        try:
            success = self.sync_handler.force_sync_to_media()
            if success:
                # Enable automatic sync after successful manual sync
                from .ankimon_sync import enable_automatic_sync
                enable_automatic_sync()
                
                tooltip("Data exported to AnkiWeb successfully! Automatic sync is now enabled.")
                self.close()
            else:
                showWarning("Failed to export data to AnkiWeb.")
        except Exception as e:
            self.logger.log("error", f"Failed to export to AnkiWeb: {str(e)}")
            showWarning(f"Error exporting to AnkiWeb: {str(e)}")

    def import_from_ankiweb(self):
        """Import data from AnkiWeb to local storage."""
        try:
            success = self.sync_handler.force_sync_from_media()
            if success:
                # Enable automatic sync after successful manual sync
                from .ankimon_sync import enable_automatic_sync
                enable_automatic_sync()
                
                tooltip("Data imported from AnkiWeb successfully! Automatic sync is now enabled.")
                self.close()
                close_anki()
            else:
                showWarning("Failed to import data from AnkiWeb.")
        except Exception as e:
            self.logger.log("error", f"Failed to import from AnkiWeb: {str(e)}")
            showWarning(f"Error importing from AnkiWeb: {str(e)}")

    def auto_sync_on_close(self):
        """Automatically sync data when Anki closes."""
        try:
            synced_files = self.sync_handler.save_configs()
            if synced_files:
                tooltip(f"Synced {len(synced_files)} Ankimon files to AnkiWeb")
        except Exception as e:
            self.logger.log("error", f"Auto-sync failed: {str(e)}")

class AnkimonDataSync:
    """
    Handles syncing of Ankimon data files through Anki's media folder using a subfolder approach.
    This leverages Anki's built-in media sync to AnkiWeb while keeping files organized.
    """
    
    _OBFUSCATION_KEY = "H0tP-!s-N0t-4-C@tG!rL_v2"
    
    # Files to sync and their locations
    SYNC_FILES = {
        "mypokemon.json": "user_files", 
        "mainpokemon.json": "user_files",
        "badges.json": "user_files",
        "items.json": "user_files", 
        "teams.json": "user_files",
        "data.json": "user_files",
        "todays_shop.json": "user_files",
        "config.obf": "user_files"
    }
    
    def __init__(self, addon_name: str = None):
        """Initialize with addon name for folder naming."""
        self.addon_name = addon_name or self._get_addon_name()
        self.addon_path = addon_dir
        self.user_files_path = user_path
        
        # Initialize paths as None - will be set when first accessed
        self._media_path = None
        self._media_sync_path = None
        self._sync_folder_name = None
        
    def _get_addon_name(self) -> str:
        """Get the addon name from the current addon folder."""
        try:
            current_file = Path(__file__)
            addon_dir = current_file.parents[2]  # Go up to addon root
            return addon_dir.name
        except:
            return "ankimon"  # fallback
    
    def _ensure_paths_initialized(self):
        """Ensure media paths are initialized. Call this before using any media path."""
        if self._media_path is None:
            profile_folder = mw.pm.profileFolder()
            if profile_folder is None:
                raise RuntimeError("No Anki profile loaded. Cannot initialize sync paths.")
            
            self._media_path = Path(profile_folder) / "collection.media"
            self._sync_folder_name = f"Ankimon"
            self._media_sync_path = self._media_path
    
    @property
    def media_path(self) -> Path:
        """Get media path, initializing if needed."""
        self._ensure_paths_initialized()
        return self._media_path
    
    @property
    def media_sync_path(self) -> Path:
        """Get media sync path, initializing if needed."""
        self._ensure_paths_initialized()
        return self._media_sync_path
    
    @property
    def sync_folder_name(self) -> str:
        """Get sync folder name, initializing if needed."""
        self._ensure_paths_initialized()
        return self._sync_folder_name
    
    def _get_source_path(self, filename: str) -> Path:
        """Get the source path for a file based on its location."""
        location = self.SYNC_FILES.get(filename)
        if location == "addon_root" or filename == "meta.json":
            return self.addon_path / filename
        elif location == "user_files":
            return self.user_files_path / filename
        else:
            raise ValueError(f"Unknown location for file: {filename}")
    
    def _get_media_path(self, filename: str) -> Path:
        """Get the media subfolder path for a synced file."""
        return self.media_sync_path / filename
    
    def _get_legacy_media_path(self, filename: str) -> Path:
        """Get the old media folder path for migration from old format."""
        return self.media_path / f"_{self.addon_name}_{filename}"
    
    def _ensure_sync_folder_exists(self):
        """Ensure the sync subfolder exists in media directory."""
        try:
            self.media_sync_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            showWarning(f"Failed to create sync folder: {str(e)}")
            return False
    
    def _migrate_legacy_files(self) -> List[str]:
        """Migrate files from old flat structure to subfolder structure."""
        migrated_files = []
        
        for filename in self.SYNC_FILES.keys():
            legacy_path = self._get_legacy_media_path(filename)
            new_path = self._get_media_path(filename)
            
            # If legacy file exists and new file doesn't, migrate it
            if legacy_path.is_file() and not new_path.is_file():
                try:
                    if self._ensure_sync_folder_exists():
                        shutil.copy2(legacy_path, new_path)
                        os.remove(legacy_path)  # Remove old file
                        migrated_files.append(filename)
                except Exception as e:
                    showWarning(f"Failed to migrate {filename}: {str(e)}")
                    
        return migrated_files
    
    def _obfuscate_data(self, data: dict) -> str:
        """Obfuscates dictionary data into a string."""
        json_str = json.dumps(data)
        obfuscated_bytes = bytearray()
        key_bytes = self._OBFUSCATION_KEY.encode('utf-8')
        for i, byte in enumerate(json_str.encode('utf-8')):
            obfuscated_bytes.append(byte ^ key_bytes[i % len(key_bytes)])
        return base64.b64encode(obfuscated_bytes).decode('utf-8')

    def _deobfuscate_data(self, obfuscated_str: str) -> dict:
        """De-obfuscates string back into a dictionary."""
        separator = "---DATA_START---\n"
        parts = obfuscated_str.split(separator)
        if len(parts) > 1:
            obfuscated_data = parts[1]
        else:
            obfuscated_data = parts[0] # Fallback for old format

        obfuscated_bytes = base64.b64decode(obfuscated_data)
        deobfuscated_bytes = bytearray()
        key_bytes = self._OBFUSCATION_KEY.encode('utf-8')
        for i, byte in enumerate(obfuscated_bytes):
            deobfuscated_bytes.append(byte ^ key_bytes[i % len(key_bytes)])
        return json.loads(deobfuscated_bytes.decode('utf-8'))

    def _save_obfuscated_config(self):
        try:
            meta_path = self._get_source_path("meta.json")
            if not meta_path.is_file():
                return

            with open(meta_path, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
            
            config_data = meta_data.get("config")
            if not config_data:
                return

            obfuscated_str = self._obfuscate_data(config_data)
            
            warning_message = "WARNING: This file contains important user data. Do not delete or modify this file. Deleting or modifying this file can lead to data loss in the Ankimon addon.\n---DATA_START---\n"
            
            file_content = warning_message + obfuscated_str

            obfuscated_config_path = self.user_files_path / "config.obf"
            with open(obfuscated_config_path, 'w', encoding='utf-8') as f:
                f.write(file_content)

        except Exception as e:
            print(f"Ankimon: Could not save obfuscated config: {e}")

    def _load_and_update_config_from_obfuscated_file(self):
        try:
            obfuscated_config_path = self.user_files_path / "config.obf"
            if not obfuscated_config_path.is_file():
                return

            with open(obfuscated_config_path, 'r', encoding='utf-8') as f:
                obfuscated_str = f.read()
            
            if not obfuscated_str:
                return

            stored_config = self._deobfuscate_data(obfuscated_str)

            meta_path = self._get_source_path("meta.json")
            if not meta_path.is_file():
                return

            with open(meta_path, 'r', encoding='utf-8') as f:
                meta_data = json.load(f)
            
            current_config = meta_data.get("config", {})
            
            current_config.update(stored_config)
            meta_data["config"] = current_config

            with open(meta_path, 'w', encoding='utf-8') as f:
                json.dump(meta_data, f, indent=4)

        except Exception as e:
            print(f"Ankimon: Could not load obfuscated config: {e}")
            
    def save_configs(self) -> List[str]:
        """
        Save configs from addon folder to media subfolder to trigger AnkiWeb sync.
        Returns list of files that were synced.
        """
        try:
            # First, migrate any legacy files
            migrated_files = self._migrate_legacy_files()
            if migrated_files:
                showInfo(f"Migrated {len(migrated_files)} files to new subfolder structure")
            
            # Ensure sync folder exists
            if not self._ensure_sync_folder_exists():
                return []
                
            synced_files = []
            
            for filename in self.SYNC_FILES.keys():
                try:
                    source_file = self._get_source_path(filename)
                    dest_file = self._get_media_path(filename)
                    
                    # Skip if source file doesn't exist
                    if not source_file.is_file():
                        continue
                    
                    # Copy if destination doesn't exist or files differ
                    if not dest_file.is_file():
                        shutil.copy2(source_file, dest_file)
                        synced_files.append(filename)
                    elif not filecmp.cmp(source_file, dest_file, shallow=False):
                        # Remove old file and copy new one to trigger sync
                        os.remove(dest_file)
                        shutil.copy2(source_file, dest_file)
                        synced_files.append(filename)
                        
                except Exception as e:
                    showWarning(f"Failed to sync {filename}: {str(e)}")
                    continue
                    
            return synced_files
        except RuntimeError as e:
            # Profile not loaded yet
            return []
    
    def read_configs(self, media_sync_status: bool = False) -> List[str]:
        """
        Read configs from media subfolder and copy to addon folder.
        Returns list of files that were updated.
        """
        if media_sync_status:
            return []  # Don't read while sync is in progress
        
        try:
            # Check for legacy files first
            migrated_files = self._migrate_legacy_files()
            
            updated_files = []
            
            for filename in self.SYNC_FILES.keys():
                try:
                    source_file = self._get_source_path(filename)
                    media_file = self._get_media_path(filename)
                    
                    # Skip if media file doesn't exist
                    if not media_file.is_file():
                        continue
                    
                    # Ensure source directory exists
                    source_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy if source doesn't exist or files differ
                    if not source_file.is_file() or not filecmp.cmp(source_file, media_file, shallow=False):
                        shutil.copy2(media_file, source_file)
                        updated_files.append(filename)
                        
                except Exception as e:
                    showWarning(f"Failed to read {filename}: {str(e)}")
                    continue
                    
            return updated_files
        except RuntimeError as e:
            # Profile not loaded yet
            return []
    
    def get_file_differences(self) -> Dict[str, Dict]:
        """
        Compare local files with media files and return differences.
        Returns dict with file differences for UI display.
        """
        try:
            # Migrate legacy files first
            self._migrate_legacy_files()
            
            differences = {}
            
            for filename in self.SYNC_FILES.keys():
                source_file = self._get_source_path(filename)
                media_file = self._get_media_path(filename)
                
                # Skip if neither file exists
                if not source_file.is_file() and not media_file.is_file():
                    continue
                    
                file_diff = {
                    'local_exists': source_file.is_file(),
                    'media_exists': media_file.is_file(),
                    'files_differ': False,
                    'local_data': None,
                    'media_data': None
                }
                
                if filename.endswith('.obf'):
                    try:
                        if file_diff['local_exists']:
                            with open(source_file, 'r', encoding='utf-8') as f:
                                obfuscated_local_data = f.read()
                            file_diff['local_data'] = self._deobfuscate_data(obfuscated_local_data)
                        
                        if file_diff['media_exists']:
                            with open(media_file, 'r', encoding='utf-8') as f:
                                obfuscated_media_data = f.read()
                            file_diff['media_data'] = self._deobfuscate_data(obfuscated_media_data)

                        file_diff['files_differ'] = file_diff['local_data'] != file_diff['media_data']
                    except Exception as e:
                        file_diff['error'] = f"Error deobfuscating file: {str(e)}"

                # Load and compare JSON data if both exist
                elif file_diff['local_exists'] and file_diff['media_exists']:
                    try:
                        with open(source_file, 'r', encoding='utf-8') as f:
                            file_diff['local_data'] = json.load(f)
                        with open(media_file, 'r', encoding='utf-8') as f:
                            file_diff['media_data'] = json.load(f)
                        
                        # First, compare the loaded data. This is the most reliable check.
                        if file_diff['local_data'] != file_diff['media_data']:
                            file_diff['files_differ'] = True
                        else:
                            # If data is semantically the same, we don't need to check further.
                            file_diff['files_differ'] = False

                    except (json.JSONDecodeError, Exception) as e:
                        # If we can't parse the JSON, we can't compare data.
                        # Fall back to the binary file comparison.
                        file_diff['error'] = f"Could not parse JSON, falling back to binary comparison: {e}"
                        file_diff['files_differ'] = not filecmp.cmp(source_file, media_file, shallow=False)

                elif file_diff['local_exists']:
                    try:
                        with open(source_file, 'r', encoding='utf-8') as f:
                            file_diff['local_data'] = json.load(f)
                        file_diff['files_differ'] = True
                    except:
                        pass
                elif file_diff['media_exists']:
                    try:
                        with open(media_file, 'r', encoding='utf-8') as f:
                            file_diff['media_data'] = json.load(f)
                        file_diff['files_differ'] = True
                    except:
                        pass
                
                if file_diff['files_differ'] or file_diff.get('error'):
                    differences[filename] = file_diff
                    
            return differences
        except RuntimeError as e:
            # Profile not loaded yet
            return {}
    
    def force_sync_to_media(self) -> bool:
        """Force sync all LOCAL files TO media subfolder (Export to AnkiWeb)."""
        try:
            if not self._ensure_sync_folder_exists():
                return False
                
            synced_files = []
            for filename in self.SYNC_FILES.keys():
                source_file = self._get_source_path(filename)  # LOCAL file
                dest_file = self._get_media_path(filename)     # MEDIA file
                
                if source_file.is_file():
                    # Remove existing media file if it exists
                    if dest_file.is_file():
                        os.remove(dest_file)
                    
                    # Copy LOCAL to MEDIA (Export direction)
                    shutil.copy2(source_file, dest_file)
                    synced_files.append(filename)
            
            showInfo(f"Exported {len(synced_files)} files to AnkiWeb: {', '.join(synced_files)}")
            return True
        except Exception as e:
            showWarning(f"Failed to export to AnkiWeb: {str(e)}")
            return False

    def force_sync_from_media(self) -> bool:
        """Force sync all MEDIA files FROM subfolder to local folder (Import from AnkiWeb)."""
        try:
            updated_files = []
            for filename in self.SYNC_FILES.keys():
                media_file = self._get_media_path(filename)    # MEDIA file  
                source_file = self._get_source_path(filename)  # LOCAL file
                
                if media_file.is_file():
                    # Ensure source directory exists
                    source_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy MEDIA to LOCAL (Import direction)
                    shutil.copy2(media_file, source_file)
                    updated_files.append(filename)
            
            showInfo(f"Imported {len(updated_files)} files from AnkiWeb: {', '.join(updated_files)}\n\nAnki will now close. Please reopen Anki to apply changes!")
            return True
        except Exception as e:
            showWarning(f"Failed to import from AnkiWeb: {str(e)}")
            return False
    
    def get_sync_folder_info(self) -> Dict[str, str]:
        """Get information about the sync folder for debugging."""
        try:
            return {
                'sync_folder_path': str(self.media_sync_path),
                'sync_folder_exists': self.media_sync_path.exists(),
                'files_in_sync_folder': [f.name for f in self.media_sync_path.iterdir()] if self.media_sync_path.exists() else [],
                'addon_name': self.addon_name,
                'media_path': str(self.media_path)
            }
        except RuntimeError as e:
            return {
                'error': str(e),
                'addon_name': self.addon_name,
                'media_path': 'Not initialized (no profile loaded)'
            }


# Global instance for easy access - but will be lazy initialized
_ankimon_sync_instance = None

def get_ankimon_sync() -> AnkimonDataSync:
    """Get the global AnkimonDataSync instance, creating it if needed."""
    global _ankimon_sync_instance
    if _ankimon_sync_instance is None:
        _ankimon_sync_instance = AnkimonDataSync()
    return _ankimon_sync_instance

def get_sync_info():
    """Get sync folder information for debugging."""
    try:
        return get_ankimon_sync().get_sync_folder_info()
    except Exception as e:
        return {'error': str(e)}

def check_and_sync_pokemon_data(settings_obj, logger):
    """
    Check for Pokemon data differences and show sync dialog ONLY if needed.
    Returns dialog instance only if differences exist.
    """
    
    # Check if sync is disabled
    if not ankiweb_sync:
        logger.log("info", "AnkiWeb sync is disabled in settings - skipping sync check")
        return None
    
    try:
        sync_handler = AnkimonDataSync()
        differences = sync_handler.get_file_differences()

        if differences:
            # Show the sync dialog only if there are differences
            dialog = ImprovedPokemonDataSync(settings_obj, logger)
            dialog.show() # Show immediately
            return dialog
        else:
            # No differences found - enable automatic sync
            enable_automatic_sync()
            logger.log("info", "No sync differences found - automatic sync enabled")
            return None

    except Exception as e:
        logger.log("error", f"Failed to check Pokemon data sync: {str(e)}")
        return None

def save_ankimon_configs():
    """Convenience function to save configs - called before media sync."""
    # Check if sync is disabled
    if not ankiweb_sync:
        return []
        
    try:
        sync_handler = get_ankimon_sync()
        sync_handler._save_obfuscated_config()
        return sync_handler.save_configs()
    except Exception as e:
        # Gracefully handle errors during startup
        return []

def read_ankimon_configs(media_sync_status: bool = False):
    """Convenience function to read configs - called after media sync."""
    # Check if sync is disabled
    if not ankiweb_sync:
        return []
        
    try:
        sync_handler = get_ankimon_sync()
        sync_handler._load_and_update_config_from_obfuscated_file()
        return sync_handler.read_configs(media_sync_status)
    except Exception as e:
        # Gracefully handle errors during startup
        return []

# Global flag to track if automatic sync is enabled
_automatic_sync_enabled = False

def setup_ankimon_sync_hooks(settings_obj, logger):
    """Set up hooks for automatic Ankimon data syncing - but disabled by default."""
    
    # Check if sync is disabled
    if not ankiweb_sync:
        logger.log("info", "AnkiWeb sync is disabled in settings - skipping hook setup")
        return
    
    def on_sync_will_start():
        """Called before sync starts - only auto-sync if enabled."""
        if not _automatic_sync_enabled:
            logger.log("info", "Anki sync starting - automatic Ankimon sync disabled (awaiting manual sync)")
            return

        try:
            synced_files = save_ankimon_configs()
            if synced_files:
                logger.log("info", f"Prepared {len(synced_files)} files for sync")
        except Exception as e:
            logger.log("error", f"Failed to prepare files for sync: {str(e)}")

    def on_sync_did_finish():
        """Called after sync finishes - only auto-read if enabled."""
        if not _automatic_sync_enabled:
            logger.log("info", "Anki sync finished - automatic Ankimon sync disabled (awaiting manual sync)")
            return

        try:
            updated_files = read_ankimon_configs(media_sync_status=False)
            if updated_files:
                logger.log("info", f"Updated {len(updated_files)} files from sync")
                tooltip(f"Updated {len(updated_files)} Ankimon files from AnkiWeb")
        except Exception as e:
            logger.log("error", f"Failed to read files after sync: {str(e)}")

    # Register hooks (but they won't auto-sync until enabled)
    gui_hooks.sync_will_start.append(on_sync_will_start)
    gui_hooks.sync_did_finish.append(on_sync_did_finish)

    logger.log("info", "Ankimon sync hooks registered (automatic sync disabled until manual sync)")


def enable_automatic_sync():
    """Enable automatic sync after user has made their first manual sync decision."""
    global _automatic_sync_enabled
    _automatic_sync_enabled = True
    
def is_automatic_sync_enabled():
    """Check if automatic sync is enabled."""
    return _automatic_sync_enabled
