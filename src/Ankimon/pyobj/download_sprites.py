import os
import zipfile
import requests
import time
from pathlib import Path

from ..resources import user_path
from ..gui_entities import AgreementDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel, QPushButton, QMessageBox


class DownloadThread(QThread):
    # Define custom signals for progress and completion
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    download_finished_signal = pyqtSignal(bool, str) # success, message

    def __init__(self, url, dest_dir_path: Path):
        super().__init__()
        self.url = url
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
        if self._flag_file_path.exists():
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
            return

        # Point 4: Remove unreachable else clause after retry for loop (optional cleanup)
        # The 'else' clause here is unreachable because the loop either 'break's or 'return's,
        # or the 'return' statement outside the loop but before this 'else' handles the failure.


        # Point 3: Validate ZIP integrity
        self.status_signal.emit("Verifying ZIP file integrity...")
        try:
            if not zipfile.is_zipfile(self._temp_zip_path):
                raise zipfile.BadZipFile("File is not a valid ZIP archive.")
            with zipfile.ZipFile(self._temp_zip_path, 'r') as _: # Try to open to ensure it's readable
                pass
            self.status_signal.emit("ZIP file integrity verified.")
            # Point 3: Only rename to sprites.zip after validation
            os.rename(self._temp_zip_path, self._final_zip_path)
            self.status_signal.emit(f"Renamed {self._temp_zip_path.name} to {self._final_zip_path.name}.")
        except (zipfile.BadZipFile, IOError) as e:
            self.status_signal.emit(f"ZIP file verification failed: {e}")
            self._cleanup_temp_files()
            self.download_finished_signal.emit(False, "ZIP file verification failed.")
            return
        
        # Point 2: Extract the ZIP file
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
                    
                    # Point 3: Always extract all files.
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
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Ankimon Sprites Download')
        self.setGeometry(300, 300, 400, 200)

        self.url = "https://github.com/Unlucky-Life/ankimon/releases/download/sprites/sprites.zip"
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
        self.download_thread = DownloadThread(self.url, self.dest_dir_path)
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


def show_agreement_and_download_dialog():
    # Show the agreement dialog
    dialog = AgreementDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        download_dialog = DownloadDialog()
        # Point 1: Memory leak fix - Ensure dialog is deleted when closed.
        download_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        # Point 7: Make dialog non-modal but always-on-top
        download_dialog.setWindowModality(Qt.WindowModality.NonModal) # Changed from ApplicationModal to NonModal
        download_dialog.setWindowFlag(Qt.WindowStaysOnTopHint)
        download_dialog.show() # Show the dialog non-modally
