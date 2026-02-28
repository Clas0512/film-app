import sys
import requests
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLineEdit, QPushButton, QListWidget, QLabel, QFormLayout,
    QSpinBox, QDoubleSpinBox, QListWidgetItem, QTabWidget,
    QComboBox, QTextEdit, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt

API_URL = 'http://127.0.0.1:5000/api'

class FilmApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Film Database Explorer")
        self.setGeometry(100, 100, 900, 700)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Create Search Tab
        self.search_tab = QWidget()
        self.tabs.addTab(self.search_tab, "Search Films")
        self.setup_search_tab()

        # Create Add Film Tab
        self.add_film_tab = QWidget()
        self.tabs.addTab(self.add_film_tab, "Add Film")
        self.setup_add_film_tab()

        # Create Add Artist Tab
        self.add_artist_tab = QWidget()
        self.tabs.addTab(self.add_artist_tab, "Add Artist")
        self.setup_add_artist_tab()

        # Create Add Cast Tab
        self.add_cast_tab = QWidget()
        self.tabs.addTab(self.add_cast_tab, "Add Cast to Film")
        self.setup_add_cast_tab()

        # Status Bar
        self.statusBar().showMessage("Ready - Using SQLite database")

    # ============ SEARCH TAB ============
    def setup_search_tab(self):
        layout = QVBoxLayout(self.search_tab)

        # Search Area
        search_form = QFormLayout()
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Search by film title...")
        search_form.addRow("Title:", self.title_input)

        self.year_input = QSpinBox()
        self.year_input.setRange(1888, 2100)
        self.year_input.setValue(1888)
        self.year_input.setSpecialValueText("Any")
        search_form.addRow("Year:", self.year_input)

        self.rating_input = QDoubleSpinBox()
        self.rating_input.setRange(0.0, 10.0)
        self.rating_input.setSingleStep(0.1)
        self.rating_input.setValue(0.0)
        search_form.addRow("Min Rating:", self.rating_input)

        self.cast_input = QLineEdit()
        self.cast_input.setPlaceholderText("Search by cast name...")
        search_form.addRow("Cast:", self.cast_input)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        search_form.addRow(self.search_button)

        layout.addLayout(search_form)

        # Results Area
        layout.addWidget(QLabel("Results:"))
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)

    def perform_search(self):
        self.results_list.clear()
        self.statusBar().showMessage("Searching...")

        params = {
            'q': self.title_input.text(),
            'cast': self.cast_input.text(),
            'rating': self.rating_input.value() if self.rating_input.value() > 0 else None
        }
        
        if self.year_input.value() > 1888:
            params['year'] = self.year_input.value()

        try:
            response = requests.get(API_URL + '/films/search', params=params)
            
            if response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Internal Server Error')
                except:
                    error_msg = "Internal Server Error"
                self.results_list.addItem("Server Error: " + error_msg)
                self.statusBar().showMessage("Search failed.")
                return

            response.raise_for_status()
            films = response.json()

            if not films:
                self.results_list.addItem("No films found.")
                self.statusBar().showMessage("No results.")
                return

            for film in films:
                cast_names = ", ".join([c['name'] for c in film.get('cast', [])[:3]])
                item_text = "{} ({}) - Rating: {}\nCast: {}".format(
                    film['title'], film['release_year'], film['rating'], cast_names
                )
                self.results_list.addItem(item_text)
            
            self.statusBar().showMessage("Found {} films.".format(len(films)))

        except Exception as e:
            self.results_list.addItem("Error: " + str(e))
            self.statusBar().showMessage("Search failed.")

    # ============ ADD FILM TAB ============
    def setup_add_film_tab(self):
        layout = QVBoxLayout(self.add_film_tab)

        form = QFormLayout()
        
        self.film_title = QLineEdit()
        form.addRow("Title *:", self.film_title)

        self.film_original_title = QLineEdit()
        form.addRow("Original Title:", self.film_original_title)

        self.film_year = QSpinBox()
        self.film_year.setRange(1888, 2100)
        self.film_year.setValue(2024)
        form.addRow("Release Year:", self.film_year)

        self.film_rating = QDoubleSpinBox()
        self.film_rating.setRange(0.0, 10.0)
        self.film_rating.setSingleStep(0.1)
        form.addRow("Rating:", self.film_rating)

        self.film_duration = QSpinBox()
        self.film_duration.setRange(1, 600)
        form.addRow("Duration (min):", self.film_duration)

        self.film_language = QLineEdit()
        form.addRow("Language:", self.film_language)

        self.film_country = QLineEdit()
        form.addRow("Country:", self.film_country)

        self.film_age_rating = QLineEdit()
        self.film_age_rating.setPlaceholderText("e.g., PG-13, R")
        form.addRow("Age Rating:", self.film_age_rating)

        self.film_description = QTextEdit()
        self.film_description.setMaximumHeight(100)
        form.addRow("Description:", self.film_description)

        self.film_genres = QLineEdit()
        self.film_genres.setPlaceholderText("Comma separated: Action, Drama, Comedy")
        form.addRow("Genres:", self.film_genres)

        layout.addLayout(form)

        self.add_film_btn = QPushButton("Add Film")
        self.add_film_btn.clicked.connect(self.add_film)
        layout.addWidget(self.add_film_btn)

        layout.addStretch()

    def add_film(self):
        title = self.film_title.text().strip()
        if not title:
            QMessageBox.warning(self, "Error", "Title is required!")
            return

        data = {
            'title': title,
            'original_title': self.film_original_title.text() or None,
            'release_year': self.film_year.value(),
            'rating': self.film_rating.value(),
            'duration_minutes': self.film_duration.value(),
            'language': self.film_language.text() or None,
            'country': self.film_country.text() or None,
            'age_rating': self.film_age_rating.text() or None,
            'description': self.film_description.toPlainText() or None
        }

        genres_text = self.film_genres.text().strip()
        if genres_text:
            data['genres'] = [g.strip() for g in genres_text.split(',') if g.strip()]

        try:
            response = requests.post(API_URL + '/films', json=data)
            if response.status_code == 201:
                result = response.json()
                QMessageBox.information(self, "Success", "Film added! ID: " + str(result.get('id')))
                self.clear_film_form()
            else:
                error = response.json().get('error', 'Unknown error')
                QMessageBox.warning(self, "Error", error)
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to connect: " + str(e))

    def clear_film_form(self):
        self.film_title.clear()
        self.film_original_title.clear()
        self.film_year.setValue(2024)
        self.film_rating.setValue(0.0)
        self.film_duration.setValue(0)
        self.film_language.clear()
        self.film_country.clear()
        self.film_age_rating.clear()
        self.film_description.clear()
        self.film_genres.clear()

    # ============ ADD ARTIST TAB ============
    def setup_add_artist_tab(self):
        layout = QVBoxLayout(self.add_artist_tab)

        form = QFormLayout()
        
        self.artist_first_name = QLineEdit()
        form.addRow("First Name:", self.artist_first_name)

        self.artist_last_name = QLineEdit()
        form.addRow("Last Name:", self.artist_last_name)

        self.artist_full_name = QLineEdit()
        self.artist_full_name.setPlaceholderText("Leave empty to auto-generate")
        form.addRow("Full Name *:", self.artist_full_name)

        self.artist_nationality = QLineEdit()
        form.addRow("Nationality:", self.artist_nationality)

        self.artist_gender = QLineEdit()
        form.addRow("Gender:", self.artist_gender)

        self.artist_biography = QTextEdit()
        self.artist_biography.setMaximumHeight(100)
        form.addRow("Biography:", self.artist_biography)

        layout.addLayout(form)

        self.add_artist_btn = QPushButton("Add Artist")
        self.add_artist_btn.clicked.connect(self.add_artist)
        layout.addWidget(self.add_artist_btn)

        layout.addStretch()

    def add_artist(self):
        full_name = self.artist_full_name.text().strip()
        first_name = self.artist_first_name.text().strip()
        last_name = self.artist_last_name.text().strip()

        if not full_name and not (first_name or last_name):
            QMessageBox.warning(self, "Error", "Full name or first/last name is required!")
            return

        if not full_name:
            full_name = (first_name + " " + last_name).strip()

        data = {
            'first_name': first_name or None,
            'last_name': last_name or None,
            'full_name': full_name,
            'nationality': self.artist_nationality.text() or None,
            'gender': self.artist_gender.text() or None,
            'biography': self.artist_biography.toPlainText() or None
        }

        try:
            response = requests.post(API_URL + '/artists', json=data)
            if response.status_code == 201:
                result = response.json()
                QMessageBox.information(self, "Success", "Artist added! ID: " + str(result.get('id')))
                self.clear_artist_form()
            else:
                error = response.json().get('error', 'Unknown error')
                QMessageBox.warning(self, "Error", error)
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to connect: " + str(e))

    def clear_artist_form(self):
        self.artist_first_name.clear()
        self.artist_last_name.clear()
        self.artist_full_name.clear()
        self.artist_nationality.clear()
        self.artist_gender.clear()
        self.artist_biography.clear()

    # ============ ADD CAST TAB ============
    def setup_add_cast_tab(self):
        layout = QVBoxLayout(self.add_cast_tab)

        # Film selection
        film_group = QGroupBox("Select Film")
        film_layout = QFormLayout(film_group)
        
        self.film_combo = QComboBox()
        self.refresh_films_btn = QPushButton("Refresh")
        self.refresh_films_btn.clicked.connect(self.load_films)
        film_layout.addRow("Film:", self.film_combo)
        film_layout.addRow("", self.refresh_films_btn)
        layout.addWidget(film_group)

        # Artist selection
        artist_group = QGroupBox("Select Artist")
        artist_layout = QFormLayout(artist_group)
        
        self.artist_combo = QComboBox()
        self.refresh_artists_btn = QPushButton("Refresh")
        self.refresh_artists_btn.clicked.connect(self.load_artists)
        artist_layout.addRow("Artist:", self.artist_combo)
        artist_layout.addRow("", self.refresh_artists_btn)
        layout.addWidget(artist_group)

        # Cast details
        cast_form = QFormLayout()
        
        self.role_type = QLineEdit()
        self.role_type.setText("Actor")
        self.role_type.setPlaceholderText("Actor, Director, Producer, etc.")
        cast_form.addRow("Role Type:", self.role_type)

        self.character_name = QLineEdit()
        cast_form.addRow("Character Name:", self.character_name)

        self.billing_order = QSpinBox()
        self.billing_order.setRange(1, 1000)
        cast_form.addRow("Billing Order:", self.billing_order)

        layout.addLayout(cast_form)

        self.add_cast_btn = QPushButton("Add Cast Member")
        self.add_cast_btn.clicked.connect(self.add_cast_member)
        layout.addWidget(self.add_cast_btn)

        layout.addStretch()

        # Load initial data
        self.load_films()
        self.load_artists()

    def load_films(self):
        try:
            response = requests.get(API_URL + '/films')
            films = response.json()
            self.film_combo.clear()
            for film in films:
                self.film_combo.addItem(
                    "{} ({})".format(film['title'], film['release_year']),
                    film['id']
                )
        except Exception as e:
            self.statusBar().showMessage("Failed to load films: " + str(e))

    def load_artists(self):
        try:
            response = requests.get(API_URL + '/artists')
            artists = response.json()
            self.artist_combo.clear()
            for artist in artists:
                self.artist_combo.addItem(artist['full_name'], artist['id'])
        except Exception as e:
            self.statusBar().showMessage("Failed to load artists: " + str(e))

    def add_cast_member(self):
        film_id = self.film_combo.currentData()
        artist_id = self.artist_combo.currentData()

        if not film_id or not artist_id:
            QMessageBox.warning(self, "Error", "Please select both a film and an artist!")
            return

        data = {
            'artist_id': artist_id,
            'role_type': self.role_type.text() or 'Actor',
            'character_name': self.character_name.text() or None,
            'billing_order': self.billing_order.value()
        }

        try:
            response = requests.post(API_URL + '/films/{}/cast'.format(film_id), json=data)
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Cast member added!")
                self.character_name.clear()
            else:
                error = response.json().get('error', 'Unknown error')
                QMessageBox.warning(self, "Error", error)
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to connect: " + str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FilmApp()
    window.show()
    sys.exit(app.exec())
