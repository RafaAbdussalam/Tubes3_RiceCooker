import re
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTextEdit, QScrollArea, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from datetime import date as datetime_date

class SummaryWindow(QWidget):
    """Widget untuk menampilkan halaman ringkasan CV yang telah di-parsing."""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setStyleSheet("""
            QWidget { background-color: #f5f5f5; }
            QLabel { color: #333333; font-family: "Segoe UI"; }
            QTextEdit { background-color: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 10px; }
            QFrame { background-color: white; border-radius: 10px; padding: 20px; }
            QScrollArea { border: none; }
            QScrollBar:vertical { border: none; background: #e0e0e0; width: 10px; margin: 0px; }
            QScrollBar::handle:vertical { background: #b0b0b0; min-height: 20px; border-radius: 5px; }
        """)
        self.init_ui()

    def init_ui(self):
        """Menginisialisasi semua elemen UI pada halaman."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        title_frame = QFrame()
        title_frame.setStyleSheet("background-color: #4CAF50; border-radius: 10px; padding: 15px;")
        title_layout = QVBoxLayout(title_frame)
        title_label = QLabel("CV Summary")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        layout.addWidget(title_frame)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        self.info_container = QWidget()
        self.info_layout = QVBoxLayout(self.info_container)
        self.info_layout.setSpacing(15)
        self.info_layout.setAlignment(Qt.AlignTop)
        scroll_area.setWidget(self.info_container)
        layout.addWidget(scroll_area)

        back_button = QPushButton("Back to Search")
        back_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        back_button.setMinimumHeight(45)
        back_button.setStyleSheet("""
            QPushButton { background: #616161; color: white; padding: 12px; border-radius: 8px; border: none; }
            QPushButton:hover { background: #757575; }
            QPushButton:pressed { background: #515151; }
        """)
        back_button.clicked.connect(self.controller.switch_to_search)
        layout.addWidget(back_button)

    def _create_section_header(self, title):
        """Helper untuk membuat judul seksi yang konsisten."""
        header_label = QLabel(title)
        header_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header_label.setStyleSheet("color: #333; margin-top: 10px; margin-bottom: 5px;")
        return header_label

    def update_candidate_info(self, summary_data: dict):
        """Memperbarui UI dengan data kandidat yang telah di-parsing."""
        while self.info_layout.count():
            child = self.info_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        profile = summary_data.get('profile', {})
        name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
        birthdate_raw = profile.get('date_of_birth', 'N/A')
        address = profile.get('address', 'N/A')
        phone = profile.get('phone_number', 'N/A')
        
        birthdate = str(birthdate_raw)
        if isinstance(birthdate_raw, datetime_date):
            birthdate = birthdate_raw.strftime('%d %B %Y')

        skills_list = summary_data.get('skills', [])
        experience_list = summary_data.get('experience', [])
        education_list = summary_data.get('education', [])

        # --- Tampilkan Informasi Pribadi ---
        personal_frame = QFrame()
        personal_layout = QVBoxLayout(personal_frame)
        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        personal_layout.addWidget(name_label)
        for label, value in [("Birthdate", birthdate), ("Address", address), ("Phone", phone)]:
            info_layout = QHBoxLayout()
            label_widget = QLabel(f"<b>{label}:</b>")
            value_widget = QLabel(str(value))
            info_layout.addWidget(label_widget)
            info_layout.addWidget(value_widget, 1)
            personal_layout.addLayout(info_layout)
        self.info_layout.addWidget(personal_frame)

        # --- Tampilkan Keahlian (Skills) - Menggunakan kembali gaya Tombol/Tag ---
        self.info_layout.addWidget(self._create_section_header("Skills"))
        skills_frame = QFrame()
        skills_layout = QVBoxLayout(skills_frame)
        if skills_list and isinstance(skills_list, list):
            current_row = QHBoxLayout()
            current_row.setSpacing(10)
            skills_per_row = 3  # Jumlah skill per baris
            skill_count = 0
            
            for skill in skills_list:
                if skill.strip():
                    skill_tag = QPushButton(skill.strip())
                    skill_tag.setFont(QFont("Segoe UI", 10))
                    skill_tag.setStyleSheet("""
                        QPushButton { 
                            background-color: #E8F5E9; 
                            color: #2E7D32; 
                            border: 1px solid #C8E6C9; 
                            border-radius: 12px; 
                            padding: 8px 15px;
                        }
                    """)
                    skill_tag.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
                    current_row.addWidget(skill_tag)
                    skill_count += 1
                    
                    if skill_count % skills_per_row == 0:
                        skills_layout.addLayout(current_row)
                        current_row = QHBoxLayout()
                        current_row.setSpacing(10)
            
            if current_row.count() > 0:
                current_row.addStretch()
                skills_layout.addLayout(current_row)
        else:
            skills_layout.addWidget(QLabel("Tidak ada data keahlian."))
        self.info_layout.addWidget(skills_frame)

        # --- Tampilkan Pengalaman Kerja ---
        self.info_layout.addWidget(self._create_section_header("Job History"))
        if experience_list:
            for exp in experience_list:
                exp_frame = QFrame()
                exp_frame.setStyleSheet("background-color: #fafafa; border: 1px solid #eee; padding: 15px; border-radius: 8px;")
                exp_layout = QVBoxLayout(exp_frame)
                
                pos_label = QLabel(exp.get('position', 'N/A'))
                pos_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
                pos_label.setStyleSheet("color: #2E7D32;")
                
                comp_date_text = f"{exp.get('company', 'N/A')} | {exp.get('date_range', 'N/A')}"
                comp_date_label = QLabel(comp_date_text)
                comp_date_label.setStyleSheet("color: #666; margin-bottom: 10px; font-style: italic;")
                
                desc_label = QLabel(exp.get('description', 'Tidak ada deskripsi.').replace('\n', '<br>'))
                desc_label.setWordWrap(True)
                
                exp_layout.addWidget(pos_label)
                exp_layout.addWidget(comp_date_label)
                exp_layout.addWidget(desc_label)
                self.info_layout.addWidget(exp_frame)
        else:
            no_exp_frame = QFrame()
            no_exp_frame.setLayout(QVBoxLayout())
            no_exp_frame.layout().addWidget(QLabel("Tidak ada data pengalaman kerja."))
            self.info_layout.addWidget(no_exp_frame)

        # --- Tampilkan Riwayat Pendidikan ---
        self.info_layout.addWidget(self._create_section_header("Education"))
        if education_list:
            for edu in education_list:
                edu_frame = QFrame()
                edu_frame.setStyleSheet("background-color: #fafafa; border: 1px solid #eee; padding: 15px; border-radius: 8px;")
                edu_layout = QVBoxLayout(edu_frame)
                
                degree_label = QLabel(edu.get('degree', 'N/A'))
                degree_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
                degree_label.setStyleSheet("color: #2E7D32;")

                inst_year_text = f"{edu.get('institution', 'N/A')} | {edu.get('year', 'N/A')}"
                inst_year_label = QLabel(inst_year_text)
                inst_year_label.setStyleSheet("color: #666;")
                
                edu_layout.addWidget(degree_label)
                edu_layout.addWidget(inst_year_label)
                
                if edu.get('description'):
                    desc_label = QLabel(edu.get('description'))
                    desc_label.setWordWrap(True)
                    desc_label.setStyleSheet("font-style: italic; color: #555;")
                    edu_layout.addWidget(desc_label)
                    
                self.info_layout.addWidget(edu_frame)
        else:
            no_edu_frame = QFrame()
            no_edu_frame.setLayout(QVBoxLayout())
            no_edu_frame.layout().addWidget(QLabel("Tidak ada data riwayat pendidikan."))
            self.info_layout.addWidget(no_edu_frame)
            
        self.info_layout.addStretch()