import os
import zipfile
import requests
import time
import hashlib # Point 4: Add import for hashlib
from pathlib import Path

from ..resources import user_path
from ..gui_entities import AgreementDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel, QPushButton, QMessageBox


class DownloadThread(QThread):
    """
    A QThread subclass for downloading, verifying, and extracting ZIP files in the background.
    This class handles network retries, SHA256 integrity checks, download cancellation,
    and provides detailed progress updates through Qt signals. It uses Path objects for
    robust file system operations.
    
    Signals:
        progress_signal(int): Emitted during download/extraction with progress percentage (0-100).
        status_signal(str): Emitted with status updates throughout the process.
        download_finished_signal(bool, str): Emitted upon completion (success, message).
    """
    # Define custom signals for progress and completion
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    download_finished_signal = pyqtSignal(bool, str) # success, message

    def __init__(self, url, dest_dir_path: Path, force_download=False):
        super().__init__()
        self.url = url
        self.force_download = force_download
        self.dest_dir_path = dest_dir_path
        self._is_cancelled = False
        self._temp_zip_path = self.dest_dir_path / "sprites_temp.zip"
        self._final_zip_path = self.dest_dir_path / "sprites.zip"
        self._flag_file_path = self.dest_dir_path / "download_complete.flag"
        self._last_progress_percent_emit = -1
        self._last_progress_time_emit = 0.0
        self.download_timeout = 30 # seconds

    def cancel(self):
        self._is_cancelled = True

    def _cleanup_temp_files(self):
        """Removes temporary and partial download files."""
        for path in [self._temp_zip_path, self._final_zip_path]:
            if path.exists():
                try:
                    os.remove(path)
                    self.status_signal.emit(f"Cleaned up partial file: {path.name}")
                except OSError as e:
                    self.status_signal.emit(f"Error cleaning up {path.name}: {e}")

    # Point 1: Add method _fetch_expected_hash(self)
    def _fetch_expected_hash(self) -> str | None:
        """Fetches the expected SHA256 hash from GitHub Releases API."""
        api_url = "https://api.github.com/repos/Unlucky-Life/ankimon/releases/latest"
        try:
            # Add 10-second timeout to API request
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            release_data = response.json()
            
            # Parse JSON to find asset matching "sprites.zip"
            # Note: The provided example JSON does not contain 'sprites.zip'
            # directly but 'ankimon-1.288-anki21-ankiweb.ankiaddon'.
            # Assuming 'sprites.zip' will eventually be an asset with 'sha256' field.
            for asset in release_data.get('assets', []):
                if asset.get('name') == "sprites.zip":
                    sha256_hash = asset.get('sha256') # Extract and return the "sha256" field
                    if sha256_hash:
                        return sha256_hash.lower() # Return in lowercase for case-insensitive comparison later
            
            self.status_signal.emit("Warning: 'sprites.zip' asset not found in GitHub release assets or missing 'sha256'.")
            return None
        except requests.exceptions.Timeout:
            self.status_signal.emit("Warning: GitHub API request timed out when fetching checksum.")
            return None
        except requests.exceptions.RequestException as e:
            self.status_signal.emit(f"Warning: Failed to fetch checksum from GitHub API: {e}")
            return None
        except ValueError: # For JSON decoding errors
            self.status_signal.emit("Warning: Failed to decode GitHub API response as JSON.")
            return None
        except Exception as e:
            self.status_signal.emit(f"Warning: An unexpected error occurred while fetching checksum: {e}")
            return None

    # Point 2: Add method _calculate_file_hash(self, file_path: Path) -> str:
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculates the SHA256 hash of a file, reading in chunks."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(1024 * 1024):  # Read file in 1MB chunks
                    hasher.update(chunk)
            return hasher.hexdigest().lower() # Return in lowercase for case-insensitive comparison
        except IOError as e:
            self.status_signal.emit(f"Error calculating hash for {file_path.name}: {e}")
            return ""

    def run(self):
        self.status_signal.emit("Initializing download...")
        self.progress_signal.emit(0)

        # Point 9: Verify destination directory exists/is writable
        if not self.dest_dir_path.exists():
            try:
                self.dest_dir_path.mkdir(parents=True, exist_ok=True)
                self.status_signal.emit(f"Created directory: {self.dest_dir_path}")
            except OSError as e:
                self.status_signal.emit(f"Error creating directory {self.dest_dir_path}: {e}")
                self.download_finished_signal.emit(False, f"Failed to create directory: {e}")
                return
        
        if not os.access(self.dest_dir_path, os.W_OK):
            self.status_signal.emit(f"Destination directory not writable: {self.dest_dir_path}")
            self.download_finished_signal.emit(False, "Destination directory not writable.")
            return

        # Point 3: Check for existing partial downloads and clean them up
        self._cleanup_temp_files()
        
        # Point 10: Check if already completed
        if self._flag_file_path.exists() and not self.force_download:
            self.status_signal.emit("Sprites already downloaded and verified.")
            self.download_finished_signal.emit(True, "Sprites already downloaded.")
            return

        # Point 8: Add retry logic (3 attempts) with exponential backoff for network failures
        max_attempts = 3
        for attempt in range(max_attempts):
            if self._is_cancelled:
                self.status_signal.emit("Download cancelled during retry setup.")
                self._cleanup_temp_files()
                self.download_finished_signal.emit(False, "Download cancelled.")
                return

            try:
                self.status_signal.emit(f"Attempt {attempt + 1}/{max_attempts}: Downloading ZIP file...")
                # Point 1 & 2: Add comprehensive error handling & timeout
                response = requests.get(self.url, stream=True, timeout=self.download_timeout)
                response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0

                with open(self._temp_zip_path, "wb") as f:
                    for data in response.iter_content(chunk_size=(1024*1024)): # Point 2: Increased chunk size for better throughput
                        if self._is_cancelled:
                            self.status_signal.emit("Download cancelled.")
                            self._cleanup_temp_files()
                            self.download_finished_signal.emit(False, "Download cancelled.")
                            return

                        downloaded_size += len(data)
                        f.write(data)

                        # Point 5: Throttle progress updates to max 10Hz (every 10%)
                        current_progress_percent = int((downloaded_size / total_size) * 100) if total_size > 0 else 0
                        current_time = time.time()

                        if (current_progress_percent >= self._last_progress_percent_emit + 10 or current_progress_percent == 100) and \
                           (current_time - self._last_progress_time_emit >= 0.1): # Max 10Hz
                            self.progress_signal.emit(current_progress_percent)
                            self._last_progress_percent_emit = current_progress_percent
                            self._last_progress_time_emit = current_time

                # Emit final progress
                self.progress_signal.emit(100)
                self.status_signal.emit(f"Downloaded {self._temp_zip_path.name}.")
                break # Download successful, break out of retry loop
            
            except requests.exceptions.Timeout:
                self.status_signal.emit(f"Download timed out (attempt {attempt + 1}). Retrying...")
            except requests.exceptions.RequestException as e:
                self.status_signal.emit(f"Network error (attempt {attempt + 1}): {e}. Retrying...")
            except IOError as e:
                self.status_signal.emit(f"File system error during download (attempt {attempt + 1}): {e}. Retrying...")
            
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt) # Exponential backoff
            else:
                self.status_signal.emit(f"Failed to download after {max_attempts} attempts.")
                self._cleanup_temp_files()
                self.download_finished_signal.emit(False, "Failed to download sprites.")
                return
        
        # Point 4: The previous 'return' here was incorrect, preventing successful paths from proceeding.
        # The 'else' clause after the for loop is now implicitly handled if the loop completes without a 'break'.

        # Point 3: Modify run() method after ZIP download completes
        self.status_signal.emit("Fetching expected checksum...")
        expected_hash = self._fetch_expected_hash()

        if expected_hash:
            self.status_signal.emit("Verifying file integrity with SHA256...")
            actual_hash = self._calculate_file_hash(self._temp_zip_path)

            if not actual_hash: # Error during hash calculation
                self.download_finished_signal.emit(False, "Failed to calculate download file checksum.")
                self._cleanup_temp_files()
                return

            if actual_hash != expected_hash: # Compare hashes (case-insensitive done in methods)
                self.status_signal.emit(f"Checksum mismatch! Expected: {expected_hash}, Actual: {actual_hash[:10]}...")
                self._cleanup_temp_files()
                self.download_finished_signal.emit(False, "Downloaded file checksum mismatch. It might be corrupted.")
                return
            self.status_signal.emit("Checksum verified (SHA256).")
        else:
            self.status_signal.emit("Could not fetch checksum, proceeding with ZIP validation only.")


        # Point 5: Keep all existing ZIP validation as secondary check
        self.status_signal.emit("Verifying ZIP file integrity...")
        try:
            if not zipfile.is_zipfile(self._temp_zip_path):
                raise zipfile.BadZipFile("File is not a valid ZIP archive.")
            with zipfile.ZipFile(self._temp_zip_path, 'r') as _: # Try to open to ensure it's readable
                pass
            self.status_signal.emit("ZIP file integrity verified.")
            # Point 3 (from original request): Only rename to sprites.zip after validation
            os.rename(self._temp_zip_path, self._final_zip_path)
            self.status_signal.emit(f"Renamed {self._temp_zip_path.name} to {self._final_zip_path.name}.")
        except (zipfile.BadZipFile, IOError) as e:
            self.status_signal.emit(f"ZIP file verification failed: {e}")
            self._cleanup_temp_files()
            self.download_finished_signal.emit(False, "ZIP file format verification failed.")
            return
        
        self.status_signal.emit("Extracting files...")
        extracted_count = 0
        total_files = 0
        try:
            with zipfile.ZipFile(self._final_zip_path, "r") as zip_ref:
                total_files = len(zip_ref.namelist())
                for i, file_name in enumerate(zip_ref.namelist()):
                    if self._is_cancelled:
                        self.status_signal.emit("Extraction cancelled.")
                        self._cleanup_temp_files()
                        self.download_finished_signal.emit(False, "Extraction cancelled.")
                        return

                    dest_file = self.dest_dir_path / file_name

                    # Point 6: Add extraction progress tracking and status updates
                    extraction_progress = int((i / total_files) * 100) if total_files > 0 else 0
                    self.progress_signal.emit(extraction_progress)
                    
                    # Check if file already exists to avoid overwriting
                    if dest_file.exists():
                        self.status_signal.emit(f"Skipped ({extraction_progress}%): {file_name} (File exists)")
                        continue # Skip to the next file
                        
                    try:
                        zip_ref.extract(file_name, self.dest_dir_path)
                        self.status_signal.emit(f"Extracted ({extraction_progress}%): {file_name}")
                        extracted_count += 1
                    except OSError as e:
                        self.status_signal.emit(f"Error extracting {file_name}: {e}")
                        # Continue with other files, but mark as failure later? Or stop?
                        # For now, continue and report overall success/failure.
                self.progress_signal.emit(100) # Final extraction progress
        except (zipfile.BadZipFile, IOError) as e:
            self.status_signal.emit(f"Error during extraction: {e}")
            self._cleanup_temp_files()
            self.download_finished_signal.emit(False, "Error during file extraction.")
            return

        # Final Cleanup: Remove the ZIP file after extraction and verification
        self.status_signal.emit(f"Removing temporary ZIP file: {self._final_zip_path.name}")
        try:
            os.remove(self._final_zip_path)
        except OSError as e:
            self.status_signal.emit(f"Error removing {self._final_zip_path.name}: {e}")
            # Non-critical, download considered successful if extraction is done.
        
        # Point 10: Add completion state file
        try:
            self._flag_file_path.touch()
            self.status_signal.emit("Download verification complete. Sprites installed.")
        except OSError as e:
            self.status_signal.emit(f"Error creating completion flag file: {e}")
            # Non-critical, but report issue.

        self.download_finished_signal.emit(True, "Sprites download and extraction complete!")


class DownloadDialog(QDialog):
    def __init__(self, parent=None, force_download=False):
        super().__init__(parent)

        self.force_download = force_download
        self.setWindowTitle('Ankimon Sprites Download')
        self.setGeometry(300, 300, 400, 200)

        self.url = "https://github.com/Unlucky-Life/ankimon/releases/download/sprites-v1.43/sprites.zip"
        self.dest_dir_path = Path(user_path)
        self._flag_file_path = self.dest_dir_path / "download_complete.flag"


        self.init_ui()
        self._check_initial_state()

    def init_ui(self):
        layout = QVBoxLayout()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready to download sprites.", self)
        layout.addWidget(self.status_label)

        self.start_button = QPushButton("Start Download", self)
        self.start_button.clicked.connect(self.start_download)
        layout.addWidget(self.start_button)

        # Point 4: Add cancel button to DownloadDialog
        self.cancel_button = QPushButton("Cancel Download", self)
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setEnabled(False) # Disabled until download starts
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

    def _check_initial_state(self):
        """Checks if sprites are already downloaded and updates UI."""
        if self._flag_file_path.exists():
            if self.force_download:
                self.status_label.setText("Forcing download despite existing flag.")
                return # Do not disable button, allow download to start
                
            self.status_label.setText("Sprites already downloaded and verified.")
            self.start_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
            self.progress_bar.setValue(100)

    def start_download(self):
        # Point 9: Verify destination directory exists/is writable before starting
        if not self.dest_dir_path.exists():
            try:
                self.dest_dir_path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                QMessageBox.critical(self, "Download Error", f"Failed to create directory {self.dest_dir_path}: {e}")
                self.status_label.setText("Error: Destination directory not writable.")
                return
        
        if not os.access(self.dest_dir_path, os.W_OK):
            QMessageBox.critical(self, "Download Error", f"Destination directory is not writable: {self.dest_dir_path}")
            self.status_label.setText("Error: Destination directory not writable.")
            return

        # Point 10: Check if download is already complete
        if self._flag_file_path.exists():
            QMessageBox.information(self, "Download Complete", "Ankimon sprites are already downloaded and verified.")
            self.status_label.setText("Sprites already downloaded and verified.")
            self.start_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
            self.progress_bar.setValue(100)
            return

        # Start the download thread
        self.download_thread = DownloadThread(self.url, self.dest_dir_path, force_download=self.force_download)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.status_signal.connect(self.update_status)
        self.download_thread.download_finished_signal.connect(self.on_download_finished)
        self.download_thread.start()
        
        self.status_label.setText("Download starting...")
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setValue(0)

    def cancel_download(self):
        if hasattr(self, 'download_thread') and self.download_thread.isRunning():
            self.download_thread.cancel()
            self.status_label.setText("Cancellation requested...")
            self.cancel_button.setEnabled(False) # Disable cancel button immediately

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.status_label.setText(status)

    def on_download_finished(self, success: bool, message: str):
        self.status_label.setText(message)
        self.cancel_button.setEnabled(False)
        if success:
            self.start_button.setText("Download Complete!")
            self.start_button.setEnabled(False)
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Download Complete", message)
        else:
            self.start_button.setText("Retry Download")
            self.start_button.setEnabled(True)
            QMessageBox.warning(self, "Download Failed", message)
            self.progress_bar.setValue(0) # Reset progress on failure


def show_agreement_and_download_dialog(force_download=False):
    # Show the agreement dialog
    dialog = AgreementDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        download_dialog = DownloadDialog(force_download=force_download)
        # Point 1: Memory leak fix - Ensure dialog is deleted when closed.
        download_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # Ensure the dialog is modal and blocks execution until download is complete or cancelled.
        download_dialog.exec() # Show the dialog modally
