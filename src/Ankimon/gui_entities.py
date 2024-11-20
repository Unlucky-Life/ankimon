import markdown
import json
from PyQt6.QtGui import QMovie, QIcon
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QTextEdit, QCheckBox, QPushButton, QMessageBox, QWidget, QScrollArea, QGridLayout
from aqt import mw
from aqt.qt import QDialog, qconnect
from aqt.utils import showWarning, showInfo, tooltip
from PyQt6.QtCore import Qt

from .resources import icon_path, addon_dir, eff_chart_html_path, table_gen_id_html_path, mypokemon_path
from .texts import terms_text, pokedex_html_template
from .utils import read_local_file, read_github_file, compare_files, write_local_file, read_html_file


class MovieSplashLabel(QLabel):
    def __init__(self, gif_path, parent=None):
        super().__init__(parent)
        self.movie = QMovie(gif_path)
        self.movie.jumpToFrame(0)
        self.setMovie(self.movie)
        self.movie.frameChanged.connect(self.repaint)

    def showEvent(self, event):
        self.movie.start()

    def hideEvent(self, event):
        self.movie.stop()

class UpdateNotificationWindow(QDialog):
    """Custom Dialog class"""
    def __init__(self, content):
        super().__init__()
        self.setWindowTitle("Ankimon Notifications")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # For horizontal scrollbar, if you want it off
        self.text_edit.setHtml(content)
        layout.addWidget(self.text_edit)
        self.setWindowIcon(QIcon(str(icon_path)))

        self.setLayout(layout)


class AgreementDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Setup the dialog layout
        layout = QVBoxLayout()
        # Add a label with the warning message
        title = QLabel("""Please agree to the terms before downloading the information:""")
        subtitle = QLabel("""Terms and Conditions Clause""")
        terms = QLabel(terms_text)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(terms)
         # Ensure the terms QLabel is readable and scrolls if necessary
        terms.setWordWrap(True)
        terms.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Add a checkbox for the user to agree to the terms
        self.checkbox = QCheckBox("I agree to the above named terms.")
        layout.addWidget(self.checkbox)

        # Add a button to proceed
        proceed_button = QPushButton("Proceed")
        proceed_button.clicked.connect(self.on_proceed_clicked)
        layout.addWidget(proceed_button)

        self.setLayout(layout)

    def on_proceed_clicked(self):
        if self.checkbox.isChecked():
            self.accept()  # Close the dialog and return success
        else:
            QMessageBox.warning(self, "Agreement Required", "You must agree to the terms to proceed.")

class Version_Dialog(QDialog):
    """Custom Dialog class"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ankimon Notifications")
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # For horizontal scrollbar, if you want it off
        self.local_file_path = addon_dir / "update_notes.md"
        self.local_content = read_local_file(self.local_file_path)
        self.html_content = markdown.markdown(self.local_content)
        self.text_edit.setHtml(self.html_content)
        layout.addWidget(self.text_edit)
        self.setWindowIcon(QIcon(str(icon_path)))
        self.setLayout(layout)
    
    def open(self):
        self.exec()

class License(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AnkiMon License")

        # Create a label and set HTML content
        label = QLabel()
        html_content = self.read_html_file(f"{addon_dir}/license.html")  # Replace with the path to your HTML file
        # Create a QScrollArea to enable scrolling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create a layout for the scroll area using QGridLayout
        scroll_layout = QGridLayout()

        # Create a widget to hold the layout
        container = QWidget()

        label.setText(html_content)  # 'html_table' contains the HTML table string
        label.setWordWrap(True)

        #layout = QVBoxLayout()
        scroll_layout.addWidget(label)
        # Set the widget for the scroll area
        scroll_area.setWidget(container)

        # Set the layout for the container
        container.setLayout(scroll_layout)

        # Set the widget for the scroll area
        scroll_area.setWidget(container)

        # Add the scroll area to the dialog
        window_layout = QVBoxLayout()
        window_layout.addWidget(scroll_area)
        self.setLayout(window_layout)
    def read_html_file(self, file_path):
        """Reads an HTML file and returns its content as a string."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    def show_window(self):
        self.show()

class Credits(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AnkiMon License")

        # Create a label and set HTML content
        label = QLabel()
        html_content = self.read_html_file(f"{addon_dir}/credits.html")  # Replace with the path to your HTML file
        # Create a QScrollArea to enable scrolling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create a layout for the scroll area using QGridLayout
        scroll_layout = QGridLayout()

        # Create a widget to hold the layout
        container = QWidget()

        label.setText(html_content)  # 'html_table' contains the HTML table string
        label.setWordWrap(True)

        #layout = QVBoxLayout()
        scroll_layout.addWidget(label)
        # Set the widget for the scroll area
        scroll_area.setWidget(container)

        # Set the layout for the container
        container.setLayout(scroll_layout)

        # Set the widget for the scroll area
        scroll_area.setWidget(container)

        # Add the scroll area to the dialog
        window_layout = QVBoxLayout()
        window_layout.addWidget(scroll_area)
        self.setLayout(window_layout)
    def read_html_file(self, file_path):
        """Reads an HTML file and returns its content as a string."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    def show_window(self):
        self.show()

class HelpWindow(QDialog):
    def __init__(self, online_connectivity):
        super().__init__()
        html_content = " "
        help_local_file_path = addon_dir / "HelpInfos.html"
        try:
            if online_connectivity != False:
                # URL of the file on GitHub
                help_local_file_path = addon_dir / "HelpInfos.html"
                help_github_url = "https://raw.githubusercontent.com/Unlucky-Life/ankimon/main/src/Ankimon/HelpInfos.html"
                # Path to the local file
                local_content = read_local_file(help_local_file_path)
                # Read content from GitHub
                github_content, github_html_content = read_github_file(help_github_url)
                if local_content is not None and compare_files(local_content, github_content):
                    html_content = github_html_content
                else: 
                    # Download new content from GitHub
                    if github_content is not None:
                        # Write new content to the local file
                        write_local_file(help_local_file_path, github_content)
                        html_content = github_html_content
            else:
                help_local_file_path = addon_dir / "HelpInfos.html"
                local_content = read_local_file(help_local_file_path)
                html_content = local_content
        except:
            showWarning("Failed to retrieve Ankimon HelpGuide from GitHub.")
            local_content = read_local_file(help_local_file_path)
            html_content = local_content
        self.setWindowTitle("Ankimon HelpGuide")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setHtml(html_content)
        layout.addWidget(self.text_edit)
        self.setWindowIcon(QIcon(str(icon_path)))
        self.setLayout(layout)

class TableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Pokémon Type Effectiveness Table")

        # Create a label and set HTML content
        label = QLabel()
        html_content = read_html_file(f"{eff_chart_html_path}")  # Replace with the path to your HTML file
        label.setText(html_content)  # 'html_table' contains the HTML table string
        label.setWordWrap(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

    def show_eff_chart(self):
        self.show()

class IDTableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Pokémon - Generations and ID")
        # Create a label and set HTML content
        label = QLabel()
        html_content = read_html_file(f"{table_gen_id_html_path}")  # Replace with the path to your HTML file
        label.setText(html_content)  # 'html_table' contains the HTML table string
        label.setWordWrap(True)
        label.setStyleSheet("background-color: rgb(44,44,44);")
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

    def show_gen_chart(self):
        self.show()

class Pokedex_Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.read_poke_coll()
        self.initUI()

    def read_poke_coll(self):
        with (open(mypokemon_path, "r") as json_file):
            self.captured_pokemon_data = json.load(json_file)

    def initUI(self):
        self.setWindowTitle("Pokédex")

        # Create a label and set HTML content
        label = QLabel()
        # Extract the IDs of the Pokémon listed in the JSON file
        self.available_pokedex_ids = {pokemon['id'] for pokemon in self.captured_pokemon_data}

        # Now we generate the HTML rows for each Pokémon in the range 1-898, graying out those not in the JSON file
        table_rows = [self.generate_table_row(i, i not in self.available_pokedex_ids) for i in range(1, 899)]

        # Combine the HTML template with the generated rows
        html_content = pokedex_html_template.replace('<!-- Table Rows Will Go Here -->', ''.join(table_rows))

        #html_content = self.read_html_file(f"{pokedex_html_path}")  # Replace with the path to your HTML file
        label.setText(html_content)  # 'html_table' contains the HTML table string
        label.setWordWrap(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

    # Helper function to generate table rows
    def generate_table_row(self, pokedex_number, is_gray):
        name = f"Pokemon #{pokedex_number}" # Placeholder, actual name should be fetched from a database or API
        image_class = "pokemon-gray" if is_gray else ""
        return f'''
        <tr>
            <td>{pokedex_number}</td>
            <td>{name}</td>
            <td><img src="{pokedex_number}.png" alt="{name}" class="pokemon-image {image_class}" /></td>
        </tr>
        '''
        
    def show_pokedex(self):
        self.read_poke_coll()
        self.show()

class CheckFiles(QDialog):
    # TODO: database_complete must not be in constructor?
    def __init__(self, database_complete):
        super().__init__()
        check_files_message = "Ankimon Files:"
        if database_complete != True:
            check_files_message += " \n Resource Files incomplete. \n  Please go to Ankimon => 'Download Resources' to download the needed files"
        check_files_message += "\n Once all files have been downloaded: Restart Anki"
        # Set the window title for the dialog
        self.setWindowTitle("Ankimon Files Checker")

        # Create a QLabel instance
        self.label = QLabel(f"{check_files_message}", self)

        # Create a QVBoxLayout instance
        self.layout = QVBoxLayout()

        # Add the QLabel to the layout
        self.layout.addWidget(self.label)

        # Set the dialog's layout
        self.setLayout(self.layout)

class CheckPokemonData(QDialog):
    def __init__(self, mainpokemon_path, mypokemon_path, settings_obj, logger):
        super().__init__()
        self.mainpokemon_path = mainpokemon_path
        self.mypokemon_path = mypokemon_path
        self.config = settings_obj
        self.logger = logger
        self.sync_pokemons()
        message = "Ankimon Pokemon Sync:"
        message += "There is a difference between the Ankiweb Synced Pokémon data and the local Pokémon data. \n"
        message += "Please choose to either load the local data and sync to Ankiweb or sync Ankiweb data to your local storage \n"
        # Set the window title for the dialog
        self.setWindowTitle("Ankimon Pokemon Sync:")

        # Create a QLabel instance
        self.label = QLabel(f"{message}", self)

        # Create two QPushButtons for syncing options
        self.sync_local_button = QPushButton("Load Local Data and Sync to Ankiweb", self)
        self.sync_ankiweb_button = QPushButton("Sync Ankiweb Data to Local Storage", self)
        qconnect(self.sync_local_button.clicked, self.sync_data_to_ankiweb)
        qconnect(self.sync_ankiweb_button.clicked, self.sync_data_to_local)
        # Create a QVBoxLayout instance
        self.layout = QVBoxLayout()
        # Add the QLabel and QPushButtons to the layout
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.sync_local_button)
        self.layout.addWidget(self.sync_ankiweb_button)
        # Set the dialog's layout
        self.setLayout(self.layout)

    def get_pokemon_data(self):
        with open(str(self.mypokemon_path), 'r', encoding='utf-8') as file:
            self.pokemon_collection_sync_data = json.load(file)
        with open(str(self.mainpokemon_path), 'r', encoding='utf-8') as file:
            self.mainpokemon_sync_data = json.load(file)

    def sync_pokemons(self):
        try:
            self.mainpokemon_web_data = self.config.get('mainpokemon', [])
            self.pokemon_collection_web_data = self.config.get('pokemon_collection', [])
        except Exception as e:
            showWarning("Failed to retrieve Pokémon data from AnkiWeb.")
            self.mainpokemon_web_data = []
            self.pokemon_collection_web_data = []
        #showInfo("Pokémon data synced.")
        #showInfo(f"Mainpokemon {mainpokemon}")
        #showInfo(f"Pokémon Collection {pokemon_collection}")    #function to sync pokemon data to ankiweb and local files
        
        self.get_pokemon_data()

        if self.mainpokemon_web_data != self.mainpokemon_sync_data or self.pokemon_collection_web_data != self.pokemon_collection_sync_data:
            # Show dialog window with two buttons
            self.show()
    
    def sync_data_to_local(self):
        with open(str(self.mypokemon_path), 'w', encoding='utf-8') as file:
            json.dump(self.pokemon_collection_web_data, file, ensure_ascii=False, indent=4)
        with open(str(self.mainpokemon_path), 'w', encoding='utf-8') as file:
            json.dump(self.mainpokemon_web_data, file, ensure_ascii=False, indent=4)
        showInfo("Ankiweb Data synced to local.")
        self.close()
    
    def sync_data_to_ankiweb(self):
        self.config.set("pokemon_collection", self.pokemon_collection_sync_data)
        self.config.set("mainpokemon", self.mainpokemon_sync_data)
        showInfo("Local Data synced to AnkiWeb.")
        self.close()

    def sync_on_anki_close(self):
        tooltip("Syncing PokemonData to AnkiWeb")
        self.get_pokemon_data()
        self.config.set("pokemon_collection", self.pokemon_collection_sync_data)
        self.config.set("mainpokemon", self.mainpokemon_sync_data)

    def modify_json_configuration_on_save(self, text: str) -> str:
        try:
            # Load the JSON text
            config = json.loads(text)
            # Iterate through the configuration and update fields
            #for key in config:
                #if key not in ["mainPokemon", "pokemon_collection"]:
                    #pass
            self.get_pokemon_data()
            # Set mainPokemon and pokemon_collection to predefined values
            self.config.set("pokemon_collection", self.pokemon_collection_sync_data)
            self.config.set("mainpokemon", self.mainpokemon_sync_data)
            tooltip("Saved Ankimon Configuration, Please Restart Anki")

            # Convert the modified JSON object back to a string
            modified_text = json.dumps(config, indent=4)
            return modified_text

        except json.JSONDecodeError:
            # Handle JSON decoding errors
            print("Invalid JSON format")
            return text