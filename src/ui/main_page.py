from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QRadioButton, QPushButton, QScrollArea, QStackedWidget, QMessageBox, QSpinBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from ui.summary_page import SummaryWindow
from core.pdf_parser import extract_text_for_pattern_matching, extract_text_for_regex
from ui.widgets import CandidateCard
from core.pdf_parser import extract_text_for_pattern_matching
from core.kmp import kmp_search
from core.bm import bm_search
from core.levenshtein import levenshtein_distance
from core.regex_extractor import extract_all_sections
from db.operations import search_cvs, get_applicant_summary, close_db_connection
import time, os

class CVAnalyzerApp(QMainWindow):
    """Main window for the CV Analyzer application."""
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
        self.ac_radio = QRadioButton("Aho-Corasick")
        self.kmp_radio.setChecked(True)
        algo_layout.addWidget(algo_label)
        algo_layout.addWidget(self.kmp_radio)
        algo_layout.addWidget(self.bm_radio)
        algo_layout.addWidget(self.ac_radio)
        layout.addLayout(algo_layout)

        # Top Matches input
        top_matches_layout = QHBoxLayout()
        top_matches_label = QLabel("Top Matches: ")
        self.top_matches_input = QLineEdit("3")  # Default value
        self.top_matches_input.setFont(QFont("Segoe UI", 10))
        self.top_matches_input.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 5px; width: 50px;")
        self.top_matches_input.setMaxLength(2)  # Limit to 2 digits (max 99)
        top_matches_layout.addWidget(top_matches_label)
        top_matches_layout.addWidget(self.top_matches_input)
        top_matches_layout.addStretch()
        layout.addLayout(top_matches_layout)

        # Search button
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

    # Di dalam kelas CVAnalyzerApp di main_page.py
    def perform_search(self):
        # 1. Kumpulkan input dari UI
        keywords_text = self.keywords_input.text()
        if not keywords_text.strip():
            QMessageBox.warning(self, "Input Kosong", "Silakan masukkan kata kunci.")
            return
        
        keywords = [kw.strip() for kw in keywords_text.split(',')]
        algorithm = 'KMP' if self.kmp_radio.isChecked() else 'BM' if self.bm_radio.isChecked() else 'AHO-CORASICK' if self.ac_radio.isChecked() else 'KMP'
        top_n = int(self.top_matches_input.text())

        # 2. Panggil fungsi backend tunggal
        # Seluruh logika kompleks (PDF, KMP/BM, Levenshtein, DB) ada di dalam search_cvs
        search_result = search_cvs(keywords, algorithm, top_n)

        # 3. Tampilkan hasil yang dikembalikan oleh backend
        self.result_summary.setText(
            f"Exact Match: scanned in {search_result['execution_time_exact']:.2f}s.\n"
            f"Fuzzy Match: scanned in {search_result['execution_time_fuzzy']:.2f}s."
        )

        # Hapus hasil pencarian sebelumnya
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Tampilkan kartu kandidat baru
        if not search_result['data']:
            self.results_layout.addWidget(QLabel("Tidak ada CV yang cocok ditemukan."))
        else:
            for candidate_data in search_result['data']:
                # data `candidate_data` sudah dalam format yang benar dari backend
                card = CandidateCard(candidate_data, self.switch_to_summary, self.view_cv)
                self.results_layout.addWidget(card)
        
        self.results_layout.addStretch()
        
    # Di dalam kelas CVAnalyzerApp di main_page.py
    def switch_to_summary(self, candidate_data):
        """Beralih ke halaman ringkasan setelah mengambil data dari backend."""
        applicant_id = candidate_data['id']
        
        # Panggil backend untuk mendapatkan data ringkasan yang sudah diproses
        summary_data = get_applicant_summary(applicant_id)
        
        if summary_data:
            self.summary_page.update_candidate_info(summary_data)
            self.stack.setCurrentWidget(self.summary_page)
        else:
            QMessageBox.critical(self, "Error", f"Tidak dapat menemukan detail untuk applicant ID: {applicant_id}")

    def switch_to_search(self):
        """Switch back to the search page."""
        self.stack.setCurrentWidget(self.search_page)

    # Di dalam kelas CVAnalyzerApp di main_page.py
    def view_cv(self, cv_path):
        """Membuka file CV menggunakan penampil default sistem."""
        # Path dari DB sudah benar ('data/CATEGORY/file.pdf').
        # Kita hanya perlu membuat path ini absolut dari root project.
        try:
            # Menggunakan os.path.abspath untuk mendapatkan path lengkap yang pasti benar
            # Ini akan mengubah "../data/..." menjadi "C:\Tubes3_RiceCooker\data\..."
            absolute_path = os.path.abspath(os.path.join("..", cv_path))
            
            if os.path.exists(absolute_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(absolute_path))
            else:
                QMessageBox.warning(self, "File Tidak Ditemukan", f"File CV tidak dapat ditemukan di:\n{absolute_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal membuka file CV: {e}")

    # Di dalam kelas CVAnalyzerApp di main_page.py
    def closeEvent(self, event):
        """Menutup koneksi database saat aplikasi ditutup."""
        print("Menutup aplikasi dan koneksi database...")
        close_db_connection()
        event.accept()