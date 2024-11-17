from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QTextEdit, QScrollArea

class DataHandlerWindow(QMainWindow):
    def __init__(self, data_handler):
        super().__init__()
        self.data_handler = data_handler
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Data Viewer')

        # Create the central widget and the main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Create a scroll area and set it as the main widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Loop through the data handler attributes (mypokemon, mainpokemon, etc.)
        for attr_name in ['mypokemon', 'mainpokemon', 'items', 'team', 'data', 'badges']:
            if hasattr(self.data_handler, attr_name):
                label = QLabel(attr_name)
                text_edit = QTextEdit()
                content = getattr(self.data_handler, attr_name)
                text_edit.setPlainText(str(content))
                text_edit.setReadOnly(True)
                scroll_layout.addWidget(label)
                scroll_layout.addWidget(text_edit)

        # Display any error messages from data_handler.data
        for file, error_message in self.data_handler.data.items():
            error_label = QLabel(f"Error reading {file}")
            error_text_edit = QTextEdit()
            error_text_edit.setPlainText(error_message)
            error_text_edit.setReadOnly(True)
            scroll_layout.addWidget(error_label)
            scroll_layout.addWidget(error_text_edit)

        # Set the scrollable content
        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)

        # Add the scroll area to the main layout and set the central widget
        main_layout.addWidget(scroll_area)
        self.setCentralWidget(central_widget)

    def show_window(self):
        self.show()
