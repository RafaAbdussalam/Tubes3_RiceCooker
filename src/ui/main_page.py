import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QRadioButton, QPushButton, QScrollArea, QStackedWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.summary_page import SummaryWindow
from ui.widgets import CandidateCard

class CVAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CV Analyzer App")
        self.setGeometry(100, 100, 600, 500)

        # Central widget and stack for switching pages
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.stack = QStackedWidget()
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.stack)

        # Create search page (this class) and summary page
        self.search_page = QWidget()
        self.init_search_ui()
        self.summary_page = SummaryWindow(self)
        self.stack.addWidget(self.search_page)
        self.stack.addWidget(self.summary_page)

        # Show search page by default
        self.stack.setCurrentWidget(self.search_page)
        

    def init_search_ui(self):
        """Initialize the UI for the search page."""
        layout = QVBoxLayout(self.search_page)

        # Title
        title_label = QLabel("CV Analyzer App")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Keywords input
        keywords_layout = QHBoxLayout()
        keywords_label = QLabel("Keywords: ")
        self.keywords_input = QLineEdit("React, Express, HTML")
        self.keywords_input.setFont(QFont("Segoe UI", 10))
        self.keywords_input.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px;")
        keywords_layout.addWidget(keywords_label)
        keywords_layout.addWidget(self.keywords_input)
        layout.addLayout(keywords_layout)

        # Algorithm selection (KMP/BM)
        algo_layout = QHBoxLayout()
        algo_label = QLabel("Search Algorithm: ")
        self.kmp_radio = QRadioButton("KMP")
        self.bm_radio = QRadioButton("BM")
        self.kmp_radio.setChecked(True)
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.kmp_radio)
        algo_layout.addWidget(self.bm_radio)
        layout.addLayout(algo_layout)

        top_matches_layout = QHBoxLayout()
        top_matches_label = QLabel("Top Matches: ")
        self.top_matches_input = QLineEdit("3") 
        self.top_matches_input.setFont(QFont("Segoe UI", 10))
        self.top_matches_input.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px; width: 50px;")
        self.top_matches_input.setMaxLength(2) 
        top_matches_layout.addWidget(top_matches_label)
        top_matches_layout.addWidget(self.top_matches_input)
        top_matches_layout.addStretch()
        layout.addLayout(top_matches_layout)

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

        # Summary result section
        self.result_summary = QLabel("")
        self.result_summary.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.result_summary)

        # Scroll area for search results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.scroll_area.setWidget(self.results_container)
        layout.addWidget(self.scroll_area)

    def perform_search(self):
        self.result_summary.setText("Exact Match: 100 CVs scanned in 100ms.\nFuzzy Match: 100 CVs scanned in 101ms.")

        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        try:
            top_matches = int(self.top_matches_input.text())
            if top_matches <= 0:
                top_matches = 1 
            elif top_matches > 50: 
                top_matches = 50
        except ValueError:
            top_matches = 3 

        candidates = [
            {"name": "Farhan", "matches": 4, "keywords": {"React": 1, "HTML": 1}, "cv_path": "../data/farhan_cv.pdf"},
            {"name": "Aland", "matches": 1, "keywords": {"React": 1}, "cv_path": "../data/aland_cv.pdf"},
            {"name": "Ariel", "matches": 1, "keywords": {"Express": 1}, "cv_path": "../data/ariel_cv.pdf"},
            {"name": "Budi", "matches": 3, "keywords": {"Python": 2, "HTML": 1}, "cv_path": "../data/budi_cv.pdf"},
            {"name": "Citra", "matches": 2, "keywords": {"Java": 1, "SQL": 1}, "cv_path": "../data/citra_cv.pdf"}
        ]

        candidates.sort(key=lambda x: x["matches"], reverse=True)
        displayed_candidates = candidates[:top_matches]

        for candidate in displayed_candidates:
            card = CandidateCard(candidate, self.switch_to_summary, self.view_cv)
            self.results_layout.addWidget(card)

        self.results_layout.addStretch()

    def switch_to_summary(self, candidate_name):
        """Switch to the summary page and update candidate data."""
        self.summary_page.update_candidate_info(candidate_name)
        self.stack.setCurrentWidget(self.summary_page)

    def switch_to_search(self):
        """Switch back to the search page."""
        self.stack.setCurrentWidget(self.search_page)

    def view_cv(self, cv_path):
        """Open the CV file using the default system viewer."""
        import os
        try:
            os.startfile(cv_path) 
        except AttributeError:
            os.system(f"open {cv_path}") 
        except Exception as e:
            print(f"Error opening CV: {e}")