import re  # Added import for regular expressions
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTextEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from core.pdf_parser import extract_text_for_regex
from core.regex_extractor import extract_all_sections

class SummaryWindow(QWidget):
    """Widget for displaying the CV summary page."""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("CV Summary")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Container for candidate information
        self.info_container = QWidget()
        self.info_layout = QVBoxLayout(self.info_container)
        layout.addWidget(self.info_container)

        # Back button
        back_button = QPushButton("Back to Search")
        back_button.setStyleSheet("background-color: #757575; color: white; padding: 5px; border-radius: 5px;")
        back_button.clicked.connect(self.controller.switch_to_search)
        layout.addWidget(back_button)

    # Di dalam kelas SummaryWindow di file ui/summary_page.py

    def update_candidate_info(self, summary_data: dict):
        """
        Memperbarui halaman ringkasan dengan data yang sudah diproses dari backend.
        Fungsi ini hanya bertugas untuk menampilkan data.
        """
        # 1. Hapus semua widget dari info layout sebelumnya untuk membersihkan halaman
        while self.info_layout.count():
            child = self.info_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # 2. Ekstrak data dari dictionary 'summary_data'
        profile = summary_data.get('profile', {})
        name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}"
        
        # Ambil data dari tabel profil
        birthdate = profile.get('date_of_birth', 'N/A')
        address = profile.get('address', 'N/A')
        phone = profile.get('phone_number', 'N/A')
        
        # Ambil data yang diekstrak dari CV oleh backend
        skills_text = summary_data.get('skills', 'Tidak ditemukan').strip()
        experience_text = summary_data.get('experience', 'Tidak ditemukan').strip()
        education_text = summary_data.get('education', 'Tidak ditemukan').strip()

        # --- 3. Tampilkan Informasi Pribadi ---
        personal_frame = QFrame()
        personal_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 10px;")
        personal_layout = QVBoxLayout(personal_frame)
        
        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        personal_layout.addWidget(name_label)
        
        # Tampilkan detail lainnya dari database
        personal_layout.addWidget(QLabel(f"Birthdate: {birthdate}"))
        personal_layout.addWidget(QLabel(f"Address: {address}"))
        personal_layout.addWidget(QLabel(f"Phone: {phone}"))
        personal_layout.addWidget(QLabel(f"Skin Color: Black"))
        
        self.info_layout.addWidget(personal_frame)

        # --- 4. Tampilkan Keahlian (Skills) ---
        skills_header = QLabel("Skills")
        skills_header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.info_layout.addWidget(skills_header)

        skills_frame = QFrame()
        skills_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px; padding: 10px;")
        skills_layout = QHBoxLayout(skills_frame)
        
        # Pisahkan skill berdasarkan newline dan tampilkan sebagai tag
        if skills_text and skills_text != 'Tidak ditemukan':
            for skill in skills_text.split('\n'):
                if skill.strip():
                    skill_tag = QPushButton(skill.strip())
                    skill_tag.setStyleSheet("background-color: #e0e0e0; border-radius: 5px; padding: 5px;")
                    skills_layout.addWidget(skill_tag)
        else:
            skills_layout.addWidget(QLabel("Tidak ada data keahlian."))
        skills_layout.addStretch()
        self.info_layout.addWidget(skills_frame)

        # --- 5. Tampilkan Pengalaman Kerja (Job History) ---
        exp_header = QLabel("Job History")
        exp_header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.info_layout.addWidget(exp_header)
        
        experience_display = QTextEdit(experience_text)
        experience_display.setReadOnly(True)
        experience_display.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
        experience_display.setFixedHeight(120)  # Sesuaikan tinggi sesuai kebutuhan
        self.info_layout.addWidget(experience_display)

        # --- 6. Tampilkan Riwayat Pendidikan (Education) ---
        edu_header = QLabel("Education")
        edu_header.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.info_layout.addWidget(edu_header)
        
        education_display = QTextEdit(education_text)
        education_display.setReadOnly(True)
        education_display.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
        education_display.setFixedHeight(100) # Sesuaikan tinggi sesuai kebutuhan
        self.info_layout.addWidget(education_display)

        # Menambahkan sisa ruang kosong di bagian bawah
        self.info_layout.addStretch()