import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QRadioButton, QComboBox, QPushButton, QFrame, QStackedWidget, QScrollArea)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

class CVAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CV Analyzer App")
        self.setGeometry(100, 100, 600, 500)  # Ukuran jendela

        # Widget utama dan stack untuk switching halaman
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.stack = QStackedWidget()
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.stack)

        # Buat halaman pencarian dan summary
        self.search_page = SearchPage(self)
        self.summary_page = SummaryPage(self)
        self.stack.addWidget(self.search_page)
        self.stack.addWidget(self.summary_page)

        # Tampilkan halaman pencarian sebagai default
        self.stack.setCurrentWidget(self.search_page)

    def switch_to_summary(self, candidate_name):
        """Switch ke halaman summary dan update data kandidat."""
        self.summary_page.update_candidate_info(candidate_name)
        self.stack.setCurrentWidget(self.summary_page)

    def switch_to_search(self):
        """Kembali ke halaman pencarian."""
        self.stack.setCurrentWidget(self.search_page)

class SearchPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Judul aplikasi
        title_label = QLabel("CV Analyzer App")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Kolom input keywords
        keywords_layout = QHBoxLayout()
        keywords_label = QLabel("Keywords: ")
        self.keywords_input = QLineEdit("React, Express, HTML")
        self.keywords_input.setFont(QFont("Segoe UI", 10))
        self.keywords_input.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
        keywords_layout.addWidget(keywords_label)
        keywords_layout.addWidget(self.keywords_input)
        layout.addLayout(keywords_layout)

        # Toggle algoritma (KMP/BM)
        algo_layout = QHBoxLayout()
        algo_label = QLabel("Search Algorithm: ")
        self.kmp_radio = QRadioButton("KMP")
        self.bm_radio = QRadioButton("BM")
        self.kmp_radio.setChecked(True)  # Default KMP
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.kmp_radio)
        algo_layout.addWidget(self.bm_radio)
        layout.addLayout(algo_layout)

        # Top Matches Selector
        top_matches_layout = QHBoxLayout()
        top_matches_label = QLabel("Top Matches: ")
        self.top_matches_combo = QComboBox()
        self.top_matches_combo.addItems(["1", "3", "5", "10"])
        self.top_matches_combo.setCurrentText("3")
        self.top_matches_combo.setStyleSheet("padding: 5px;")
        top_matches_layout.addWidget(top_matches_label)
        top_matches_layout.addWidget(self.top_matches_combo)
        top_matches_layout.addStretch()
        layout.addLayout(top_matches_layout)

        # Tombol Search (dengan gradien)
        self.search_button = QPushButton("Search")
        self.search_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.search_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4CAF50, stop:1 #2E7D32);
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #66BB6A, stop:1 #4CAF50);
            }
        """)
        self.search_button.clicked.connect(self.perform_search)
        layout.addWidget(self.search_button)

        # Summary Result Section
        self.result_summary = QLabel("")
        self.result_summary.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.result_summary)

        # Scroll Area untuk hasil pencarian
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.scroll_area.setWidget(self.results_container)
        layout.addWidget(self.scroll_area)

    def perform_search(self):
        """Simulasi hasil pencarian dan tampilkan kartu CV."""
        # Update summary result section
        self.result_summary.setText("Exact Match: 100 CVs scanned in 100ms.\nFuzzy Match: 100 CVs scanned in 101ms.")

        # Hapus hasil sebelumnya
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Simulasi data kandidat
        candidates = [
            {"name": "Farhan", "matches": 4, "keywords": {"React": 1, "HTML": 1}},
            {"name": "Aland", "matches": 1, "keywords": {"React": 1}},
            {"name": "Ariel", "matches": 1, "keywords": {"Express": 1}}
        ]

        # Buat kartu untuk setiap kandidat
        for candidate in candidates:
            card = QFrame()
            card.setFrameShape(QFrame.StyledPanel)
            card.setStyleSheet("background-color: #E0E0E0; border-radius: 5px; padding: 5px;")
            card_layout = QVBoxLayout(card)

            name_label = QLabel(candidate["name"])
            name_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
            card_layout.addWidget(name_label)

            matches_label = QLabel(f"Matched keywords: {candidate['matches']}")
            card_layout.addWidget(matches_label)

            keywords_text = ", ".join([f"{k}: {v} occurrence" for k, v in candidate["keywords"].items()])
            keywords_label = QLabel(keywords_text)
            card_layout.addWidget(keywords_label)

            # Tombol aksi
            button_layout = QHBoxLayout()
            summary_button = QPushButton("Summary")
            summary_button.setStyleSheet("background-color: #2196F3; color: white; border-radius: 3px;")
            summary_button.clicked.connect(lambda checked, name=candidate["name"]: self.controller.switch_to_summary(name))
            view_button = QPushButton("View CV")
            view_button.setStyleSheet("background-color: #FF9800; color: white; border-radius: 3px;")
            view_button.clicked.connect(lambda checked, name=candidate["name"]: print(f"Viewing CV for {name}"))
            button_layout.addWidget(summary_button)
            button_layout.addWidget(view_button)
            card_layout.addLayout(button_layout)

            self.results_layout.addWidget(card)

        self.results_layout.addStretch()

class SummaryPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Judul halaman summary
        title_label = QLabel("CV Summary")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Frame untuk informasi kandidat
        self.info_container = QWidget()
        self.info_layout = QVBoxLayout(self.info_container)
        layout.addWidget(self.info_container)

        # Tombol kembali ke halaman pencarian
        back_button = QPushButton("Back to Search")
        back_button.setStyleSheet("background-color: #757575; color: white; padding: 5px; border-radius: 5px;")
        back_button.clicked.connect(self.controller.switch_to_search)
        layout.addWidget(back_button)

    def update_candidate_info(self, candidate_name):
        """Update informasi kandidat di halaman summary."""
        # Hapus informasi sebelumnya
        while self.info_layout.count():
            child = self.info_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Simulasi data kandidat
        candidate_data = {
            "name": candidate_name,
            "birthdate": "05-19-2025",
            "address": "Masjid Salman ITB",
            "phone": "0812 3456 7890",
            "skills": ["React", "Express", "HTML"],
            "job_history": {"CTO": "2003-2004"},
            "education": {"university": "Institut Teknologi Bandung", "years": "2002-2004"}
        }

        # Tampilkan informasi kandidat
        name_label = QLabel(candidate_data["name"])
        name_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.info_layout.addWidget(name_label)

        birthdate_label = QLabel(f"Birthdate: {candidate_data['birthdate']}")
        self.info_layout.addWidget(birthdate_label)

        address_label = QLabel(f"Address: {candidate_data['address']}")
        self.info_layout.addWidget(address_label)

        phone_label = QLabel(f"Phone: {candidate_data['phone']}")
        self.info_layout.addWidget(phone_label)

        # Skills
        skills_label = QLabel("Skills:")
        skills_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.info_layout.addWidget(skills_label)

        skills_layout = QHBoxLayout()
        for skill in candidate_data["skills"]:
            skill_button = QPushButton(skill)
            skill_button.setStyleSheet("background-color: #BBDEFB; color: black; border-radius: 5px; padding: 5px;")
            skills_layout.addWidget(skill_button)
        self.info_layout.addLayout(skills_layout)

        job_history_label = QLabel("Job History:")
        job_history_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.info_layout.addWidget(job_history_label)

        for position, years in candidate_data["job_history"].items():
            job_entry = QFrame()
            job_entry.setStyleSheet("background-color: #E0E0E0; border-radius: 5px; padding: 5px;")
            job_layout = QVBoxLayout(job_entry)
            job_layout.addWidget(QLabel(position))
            job_layout.addWidget(QLabel(years))
            self.info_layout.addWidget(job_entry)

        # Education
        education_label = QLabel("Education:")
        education_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.info_layout.addWidget(education_label)

        for university, years in candidate_data["education"].items():
            edu_entry = QFrame()
            edu_entry.setStyleSheet("background-color: #E0E0E0; border-radius: 5px; padding: 5px;")
            edu_layout = QVBoxLayout(edu_entry)
            edu_layout.addWidget(QLabel(university))
            edu_layout.addWidget(QLabel(years))
            self.info_layout.addWidget(edu_entry)

        self.info_layout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CVAnalyzerApp()
    window.show()
    sys.exit(app.exec_())