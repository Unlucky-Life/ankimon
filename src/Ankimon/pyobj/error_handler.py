import os
import re
import json
import random
import traceback
import requests
import platform
import sys
from pathlib import Path
from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from aqt import mw
from anki.buildinfo import version as anki_version

# Path configurations
addon_dir = Path(__file__).parents[1]
pyobj_path = addon_dir / "pyobj"
manifest_path = addon_dir / "manifest.json"

def get_environment_info() -> str:
    """Collect add-on, Anki, Python, and OS version information."""
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        addon_ver = manifest.get("version", "unknown")
    except Exception:
        addon_ver = "unknown"
    
    py_ver = sys.version.split()[0]
    os_info = platform.platform()
    return f"Ankimon v{addon_ver} | Anki {anki_version} | Python {py_ver} | {os_info}"

def set_image_from_url(label: QLabel, url: str, width: int = 140) -> None:
    """Load and display an image from URL in a QLabel."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        image = QImage()
        image.loadFromData(response.content)
        pixmap = QPixmap.fromImage(image)
        if not pixmap.isNull():
            pixmap = pixmap.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        else:
            label.setText("Image failed to load")
    except Exception:
        label.setText("Image failed to load")

def scrub_traceback(tb_text: str) -> str:
    """Sanitize traceback text by removing user paths."""
    username = os.path.expanduser("~").split(os.sep)[-1]
    patterns = [
        rf"/home/{username}",
        rf"/Users/{username}",
        rf"[A-Z]:/Users/{username}",
        rf"[A-Z]:\\Users\\{username}",
        rf"/usr/home/{username}",
        rf"/export/home/{username}",
    ]
    for pattern in patterns:
        tb_text = re.sub(pattern, "/home/USER", tb_text, flags=re.IGNORECASE)
    return tb_text

def load_error_images(json_path: Path) -> Dict[str, str]:
    """Load and select random error image metadata."""
    default_image = {"path": "", "credit": "", "url": ""}
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            error_images = json.load(f)
        return random.choice(error_images)
    except Exception as e:
        mw.logger.log("error", f"Failed to load error images: {str(e)}")
        return default_image

def create_error_label(message: str, exception: Exception) -> QLabel:
    """Create error label with just the message and exception (no environment info)."""
    html = (
        f"<span style='font-size:32px; color:#ffcc00; vertical-align:middle;'>&#9888;</span> "
        f"<span style='font-size:15px; font-weight:600; vertical-align:middle;'>{message}</span><br>"
        f"<pre style='font-size:12px; margin-top:6px; color:#a0a0a0;'>"
        f"{str(exception)}"
        "</pre>"
    )
    label = QLabel(html)
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setWordWrap(True)
    return label

def create_credit_label(chosen_image: Dict[str, str]) -> Optional[QLabel]:
    """Create image credit label with optional link."""
    if not chosen_image.get("credit") or not chosen_image.get("url"):
        return None
        
    label = QLabel(f'<a href="{chosen_image["url"]}">{chosen_image["credit"]}</a>')
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setOpenExternalLinks(True)
    label.setAlignment(Qt.AlignmentFlag.AlignRight)
    label.setStyleSheet("font-size:10px; color:#aaa;")
    label.setWordWrap(True)
    label.setFixedWidth(140)
    label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
    return label

def build_dialog_ui(dialog: QDialog, message: str, exception: Exception, 
                   chosen_image: Dict[str, str]) -> None:
    """Construct dialog UI layout without environment info display."""
    main_layout = QHBoxLayout(dialog)
    main_layout.setContentsMargins(24, 18, 24, 18)
    main_layout.setSpacing(18)

    # Left panel (error information)
    left_layout = QVBoxLayout()
    left_layout.setSpacing(10)
    left_layout.addWidget(create_error_label(message, exception))
    
    # Friendly message
    friendly_label = QLabel("<i>But no worries, just stay cool!</i> 😎")
    friendly_label.setStyleSheet("color: #a6dcef; font-size: 13px; margin-bottom: 2px;")
    friendly_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    friendly_label.setWordWrap(True)
    left_layout.addWidget(friendly_label)

    # Report links
    links = (
        '<a href="https://discord.gg/rGNywfX436"><b>Report on Discord</b></a> | '
        '<a href="https://github.com/Unlucky-Life/ankimon/issues">Report on GitHub</a>'
    )
    links_label = QLabel(links)
    links_label.setTextFormat(Qt.TextFormat.RichText)
    links_label.setOpenExternalLinks(True)
    links_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    links_label.setStyleSheet("margin-bottom: 4px; font-size: 12px;")
    left_layout.addWidget(links_label)

    # Action buttons
    button_layout = QHBoxLayout()
    for btn in [("Copy Debug Info", "copy"), ("OK", "ok")]:
        button = QPushButton(btn[0])
        button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        button.setObjectName(btn[1])
        button_layout.addWidget(button)
    left_layout.addLayout(button_layout)

    # Right panel (image and credit)
    right_layout = QVBoxLayout()
    right_layout.setSpacing(6)

    # Image display
    image_label = QLabel()
    if chosen_image["path"].startswith("http"):
        set_image_from_url(image_label, chosen_image["path"], width=140)
    elif chosen_image["path"]:
        local_path = addon_dir / chosen_image["path"]
        if local_path.exists():
            pixmap = QPixmap(str(local_path))
            if not pixmap.isNull():
                pixmap = pixmap.scaledToWidth(140, Qt.TransformationMode.SmoothTransformation)
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
            else:
                image_label.setText("Image failed to load")
    right_layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignRight)

    # Credit display
    if credit_label := create_credit_label(chosen_image):
        right_layout.addWidget(credit_label, alignment=Qt.AlignmentFlag.AlignRight)

    right_layout.addStretch()
    
    # Combine layouts
    main_layout.addLayout(left_layout)
    main_layout.addLayout(right_layout)
    dialog.setLayout(main_layout)

def setup_dialog_style(dialog: QDialog) -> None:
    """Apply consistent visual styling to the dialog."""
    dialog.setStyleSheet("""
        QDialog {
            background: #23272e;
            border-radius: 10px;
        }
        QLabel {
            color: #f3f3f3;
        }
        QPushButton {
            font-size: 13px;
            min-width: 100px;
            min-height: 28px;
            border-radius: 5px;
            padding: 5px 12px;
            background: #363b45;
            color: #fff;
            border: 1.2px solid #4b5162;
        }
        QPushButton:focus, QPushButton:hover {
            background: #434a5b;
            border: 1.2px solid #43d675;
            color: #43d675;
        }
        QPushButton:pressed {
            background: #23272e;
            color: #43d675;
        }
    """)

def show_warning_with_traceback(
    parent: QDialog = mw,
    exception: Optional[Exception] = None,
    message: str = "An error occurred during execution."
) -> None:
    """Display error dialog with environment info only in debug clipboard."""
    if not exception:
        raise ValueError("An exception must be provided.")

    # Generate and sanitize traceback
    tb_text = scrub_traceback(traceback.format_exc())
    env_info = get_environment_info()
    mw.logger.log("error", f"{message}: {exception}\n{env_info}\n{tb_text}")

    # Load error images
    error_json_path = pyobj_path / 'error_images.json'
    chosen_image = load_error_images(error_json_path)

    # Create and configure dialog
    dialog = QDialog(parent)
    dialog.setWindowTitle("Ankimon Error")
    dialog.setModal(True)
    
    # Build UI components (without env_info parameter)
    build_dialog_ui(dialog, message, exception, chosen_image)
    setup_dialog_style(dialog)
    
    # Configure button actions
    copy_button = dialog.findChild(QPushButton, "copy")
    ok_button = dialog.findChild(QPushButton, "ok")
    
    def copy_debug_info():
        # Wrap in triple backticks for markdown code block formatting
        full_debug = f"```python\n{env_info}\n\n{tb_text}\n```"
        mw.app.clipboard().setText(full_debug)
        
        # Update dialog to show copy confirmation (without env_info)
        dialog.findChild(QLabel).setText(
            f"<span style='font-size:32px; color:#ffcc00; vertical-align:middle;'>&#9888;</span> "
            f"<span style='font-size:15px; font-weight:600; vertical-align:middle;'>{message}</span><br>"
            f"<pre style='font-size:12px; margin-top:6px; color:#a0a0a0;'>{str(exception)}</pre>"
            "<br><span style='color:#43d675; font-size:12px;'>Debug info copied!</span>"
        )
    
    copy_button.clicked.connect(copy_debug_info)
    ok_button.clicked.connect(dialog.accept)

    # Finalize and show dialog
    dialog.adjustSize()
    dialog.exec()
