import os
import zipfile
import requests
from ..resources import user_path
from ..gui_entities import AgreementDialog
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel, QPushButton

class DownloadThread(QThread):
    # Define custom signals for progress and completion
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)

    def __init__(self, url, dest_dir):
        super().__init__()
        self.url = url
        self.dest_dir = dest_dir
        self.zip_path = "sprites.zip"

    def run(self):
        # Step 1: Download the ZIP file
        response = requests.get(self.url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(self.zip_path, "wb") as f:
            for data in response.iter_content(chunk_size=1024):
                downloaded_size += len(data)
                f.write(data)

                # Emit progress signal to update the UI
                progress = int((downloaded_size / total_size) * 100)
                self.progress_signal.emit(progress)

        # Emit a status message when download is complete
        self.status_signal.emit(f"Downloaded {self.zip_path}.")

        # Step 2: Extract the ZIP file
        with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
            for file in zip_ref.namelist():
                dest_file = os.path.join(self.dest_dir, file)

                # Check if the file already exists to avoid overwriting
                if not os.path.exists(dest_file):
                    zip_ref.extract(file, self.dest_dir)
                    self.status_signal.emit(f"Extracted: {file}")
                else:
                    self.status_signal.emit(f"Skipped (file exists): {file}")

        # Clean up by removing the ZIP file after extraction
        os.remove(self.zip_path)
        self.status_signal.emit(f"Removed the temporary ZIP file: {self.zip_path}")


class DownloadDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Download Progress')
        self.setGeometry(300, 300, 400, 200)

        self.url = "https://github.com/Unlucky-Life/ankimon/releases/download/sprites/sprites.zip"
        self.dest_dir = user_path

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Press Start download...", self)
        layout.addWidget(self.status_label)

        self.start_button = QPushButton("Start Download", self)
        self.start_button.clicked.connect(self.start_download)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def start_download(self):
        # Start the download thread
        self.download_thread = DownloadThread(self.url, self.dest_dir)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.status_signal.connect(self.update_status)
        self.download_thread.start()
        self.status_label.setText("Download starting now")

        # Disable the button once the download starts
        self.start_button.setEnabled(False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.status_label.setText(status)
        if "Removed" in status:  # Re-enable the button and change text when done
            self.start_button.setEnabled(True)
            self.start_button.setText("Download Complete!")

def show_agreement_and_download_dialog():
    # Show the agreement dialog
    dialog = AgreementDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        dialog = DownloadDialog()
        dialog.exec()  # Show the dialog modally and block interaction with Anki until closed