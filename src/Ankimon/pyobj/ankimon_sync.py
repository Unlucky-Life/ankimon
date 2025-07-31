# ankimon_sync.py - Improved Ankimon data sync system with subfolder approach
import filecmp
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from aqt import mw, gui_hooks
from aqt.utils import showWarning, showInfo, tooltip

from ..resources import user_path, addon_dir

class AnkimonDataSync:
    """
    Handles syncing of Ankimon data files through Anki's media folder using a subfolder approach.
    This leverages Anki's built-in media sync to AnkiWeb while keeping files organized.
    """
    
    # Files to sync and their locations
    SYNC_FILES = {
        "meta.json": "addon_root",
        "mypokemon.json": "user_files", 
        "mainpokemon.json": "user_files",
        "badges.json": "user_files",
        "items.json": "user_files", 
        "teams.json": "user_files",
        "data.json": "user_files",
        "todays_shop.json": "user_files"
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
        if location == "addon_root":
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
                
                # Load and compare JSON data if both exist
                if file_diff['local_exists'] and file_diff['media_exists']:
                    try:
                        with open(source_file, 'r', encoding='utf-8') as f:
                            file_diff['local_data'] = json.load(f)
                        with open(media_file, 'r', encoding='utf-8') as f:
                            file_diff['media_data'] = json.load(f)
                        
                        file_diff['files_differ'] = not filecmp.cmp(source_file, media_file, shallow=False)
                    except json.JSONDecodeError as e:
                        file_diff['error'] = f"JSON decode error: {str(e)}"
                    except Exception as e:
                        file_diff['error'] = f"Error reading file: {str(e)}"
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
            
            showInfo(f"Imported {len(updated_files)} files from AnkiWeb: {', '.join(updated_files)}")
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

def save_ankimon_configs():
    """Convenience function to save configs - called before media sync."""
    try:
        return get_ankimon_sync().save_configs()
    except Exception as e:
        # Gracefully handle errors during startup
        return []

def read_ankimon_configs(media_sync_status: bool = False):
    """Convenience function to read configs - called after media sync."""
    try:
        return get_ankimon_sync().read_configs(media_sync_status)
    except Exception as e:
        # Gracefully handle errors during startup
        return []

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
    try:
        # Import here to avoid circular import
        from .sync_pokemon_data import ImprovedPokemonDataSync
        
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

# Global flag to track if automatic sync is enabled
_automatic_sync_enabled = False

def setup_ankimon_sync_hooks(settings_obj, logger):
    """Set up hooks for automatic Ankimon data syncing - but disabled by default."""
    
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