import json
from typing import Dict, Any, List

from PyQt6.QtGui import QTextOption
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QTextEdit, QPushButton, QDialog, QHBoxLayout, QScrollArea, QWidget

from aqt import mw
from aqt.utils import showWarning, showInfo, tooltip

from .ankimon_sync import AnkimonDataSync


class ImprovedPokemonDataSync(QDialog):
    """
    Improved Pokemon data sync dialog using the new AnkimonDataSync system.
    Provides better file comparison and uses Anki's media sync for reliable syncing.
    """
    
    def __init__(self, settings_obj, logger):
        super().__init__()
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
            "Ankimon Data Sync:\n"
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
                f"Ankimon Data Sync:\n"
                f"⚠️ Found differences in {len(differences)} file(s). Please choose sync direction."
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
                            local_sub.extend([""] * (max_lines - len(local_sub)))
                            remote_sub.extend([""] * (max_lines - len(remote_sub)))
                            
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
            
            if filename.endswith('.json'):
                local_data = diff_info.get('local_data')
                media_data = diff_info.get('media_data')
                
                # Use smart comparison
                local_lines, remote_lines = detect_structure_and_compare(local_data, media_data, filename)
                
                if local_lines or remote_lines:
                    local_content.append("Differences:")
                    web_content.append("Differences:")
                    
                    # Pad the shorter list to align output
                    max_lines = max(len(local_lines), len(remote_lines))
                    local_lines.extend([""] * (max_lines - len(local_lines)))
                    remote_lines.extend([""] * (max_lines - len(remote_lines)))
                    
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
