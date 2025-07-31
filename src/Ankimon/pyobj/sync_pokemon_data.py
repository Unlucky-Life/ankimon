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
        """Display the differences in the text areas."""
        local_content = []
        web_content = []
        
        for filename, diff_info in differences.items():
            local_content.append(f"=== {filename} ===")
            web_content.append(f"=== {filename} ===")
            
            if diff_info.get('error'):
                local_content.append(f"❌ Error: {diff_info['error']}")
                web_content.append(f"❌ Error: {diff_info['error']}")
            else:
                # Show file status
                local_exists = diff_info.get('local_exists', False)
                media_exists = diff_info.get('media_exists', False)
                
                local_content.append(f"Local file exists: {local_exists}")
                web_content.append(f"AnkiWeb file exists: {media_exists}")
                
                # Show data differences for JSON files
                if filename.endswith('.json'):
                    local_data = diff_info.get('local_data')
                    media_data = diff_info.get('media_data')
                    
                    if local_data is not None:
                        local_content.extend(self._format_json_data(local_data, filename))
                    else:
                        local_content.append("(No local data)")
                        
                    if media_data is not None:
                        web_content.extend(self._format_json_data(media_data, filename))
                    else:
                        web_content.append("(No AnkiWeb data)")
            
            local_content.append("")  # Add spacing
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
                tooltip("Data exported to AnkiWeb successfully!")
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
                tooltip("Data imported from AnkiWeb successfully!")
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


def check_and_sync_pokemon_data(settings_obj, logger):
    """
    Check for Pokemon data differences and show sync dialog if needed.
    This function should be called at startup to check for sync conflicts.
    """
    try:
        sync_handler = AnkimonDataSync()
        differences = sync_handler.get_file_differences()
        
        if differences:
            # Show the sync dialog
            dialog = ImprovedPokemonDataSync(settings_obj, logger)
            return dialog
        else:
            # No differences, try to sync any new local changes
            synced_files = sync_handler.save_configs()
            if synced_files:
                tooltip(f"Synced {len(synced_files)} files to AnkiWeb")
            return None
            
    except Exception as e:
        logger.log("error", f"Failed to check Pokemon data sync: {str(e)}")
        return None