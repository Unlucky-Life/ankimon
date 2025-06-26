from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QVBoxLayout, QTextEdit
from PyQt6.QtCore import Qt, QUrl
from aqt.qt import QDialog
from aqt.utils import showWarning, QWebEngineSettings

from ..resources import icon_path, addon_dir
from ..utils import read_local_file, read_github_file, compare_files, write_local_file

class HelpWindow(QDialog):
    """
    Modern Ankimon Help Guide window that displays interactive HTML content.
    
    Features:
    - Uses QWebEngineView when available for full browser capabilities
    - Falls back to QTextEdit when WebEngine isn't available
    - Loads content from GitHub with local fallback
    - Supports direct loading of remote images
    - Interactive page navigation within the HTML
    """
    def __init__(self, online_connectivity=True):
        super().__init__()
        self.setWindowTitle("Ankimon Guide")
        self.setWindowIcon(QIcon(str(icon_path)))
        self.setGeometry(100, 100, 1000, 700)
        
        # Check for QWebEngineView availability
        try:
            from PyQt6.QtWebEngineWidgets import QWebEngineView
            self.use_web_engine = True
        except ImportError:
            self.use_web_engine = False
            
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Load and display content
        if self.use_web_engine:
            self._setup_web_engine_view(layout, online_connectivity)
        else:
            self._setup_text_edit_view(layout, online_connectivity)
            
        self.setLayout(layout)
        
    def _setup_web_engine_view(self, layout, online_connectivity):
        """Setup QWebEngineView for full HTML/CSS/JS support"""
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        
        # Create web view
        self.web_view = QWebEngineView()
        
        # Configure settings
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        
        # Fetch HTML content
        html_content = self._get_html_content(online_connectivity)
        
        # Load content
        self.web_view.setHtml(html_content, QUrl("https://raw.githubusercontent.com/h0tp-ftw/ankimon/refs/heads/h0tp/assets-in-root/assets/HelpInfos/HelpInfos.html"))
        layout.addWidget(self.web_view)
        
    def _setup_text_edit_view(self, layout, online_connectivity):
        """Fallback to QTextEdit when QWebEngineView isn't available"""
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Fetch HTML content
        html_content = self._get_html_content(online_connectivity)
        
        # Display with warning about limited functionality
        limited_warning = """
        <div style="background-color: #ffcc00; color: black; padding: 10px; margin-bottom: 15px; border-radius: 5px;">
            <strong>Note:</strong> For the best experience, install PyQt6-WebEngine package.
            Some features like page navigation and images may not work correctly in this view.
        </div>
        """
        self.text_edit.setHtml(limited_warning + html_content)
        layout.addWidget(self.text_edit)
        
    def _get_html_content(self, online_connectivity):
        """Get HTML content from GitHub or local file"""
        html_content = ""
        help_local_file_path = addon_dir / "HelpInfos.html"
        
        try:
            if online_connectivity:
                # URL of the file on GitHub
                help_github_url = "https://raw.githubusercontent.com/h0tp-ftw/ankimon/refs/heads/h0tp/assets-in-root/assets/HelpInfos/HelpInfos.html"
                
                # Read local content
                local_content = read_local_file(help_local_file_path)
                
                # Read content from GitHub
                github_content, github_html_content = read_github_file(help_github_url)
                
                if local_content is not None and compare_files(local_content, github_content):
                    # If local file matches GitHub, use cached content
                    html_content = github_html_content
                else:
                    # Otherwise, save and use GitHub content
                    if github_content is not None:
                        write_local_file(help_local_file_path, github_content)
                        html_content = github_html_content
            else:
                # Use local file when offline
                local_content = read_local_file(help_local_file_path)
                html_content = local_content
        except Exception as e:
            showWarning(f"Failed to retrieve Ankimon HelpGuide: {str(e)}")
            local_content = read_local_file(help_local_file_path)
            html_content = local_content
            
        return html_content or "<h1>Help content not available</h1>"
