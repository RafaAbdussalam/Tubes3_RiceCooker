import re  # Added import for regular expressions
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTextEdit, QScrollArea, QSizePolicy
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
from core.pdf_parser import extract_text_for_regex
from core.regex_extractor import extract_all_sections
from datetime import date as datetime_date  # Mengubah nama import untuk menghindari konflik

class SummaryWindow(QWidget):
    """Widget for displaying the CV summary page."""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
            }
            QTextEdit {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
            }
            QTextEdit:focus {
                border: 2px solid #4CAF50;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title dengan frame
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #4CAF50;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("CV Summary")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        layout.addWidget(title_frame)

        # Scroll area untuk konten
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Container untuk candidate information
        self.info_container = QWidget()
        self.info_layout = QVBoxLayout(self.info_container)
        self.info_layout.setSpacing(20)
        scroll_area.setWidget(self.info_container)
        layout.addWidget(scroll_area)

        # Back button dengan style yang lebih baik
        back_button = QPushButton("Back to Search")
        back_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        back_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #757575, stop:1 #616161);
                color: white;
                padding: 12px;
                border-radius: 8px;
                min-height: 40px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9E9E9E, stop:1 #757575);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #616161, stop:1 #424242);
            }
        """)
        back_button.clicked.connect(self.controller.switch_to_search)
        layout.addWidget(back_button)

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
        
        # Konversi birthdate ke string jika berupa datetime.date
        try:
            if isinstance(birthdate, datetime_date):
                birthdate = birthdate.strftime('%d %B %Y')
            elif birthdate is None:
                birthdate = 'N/A'
        except Exception:
            birthdate = str(birthdate) if birthdate else 'N/A'
        
        # 1. Ambil 'skills' sebagai list, defaultnya list kosong jika tidak ada.
        skills_list = summary_data.get('skills', [])
        # Pastikan skills_list adalah list
        if not isinstance(skills_list, list):
            skills_list = []
            
        # Ubah dari work_experience menjadi experience
        experience_list = summary_data.get('experience', [])
        education_list = summary_data.get('education', [])
        
        # --- Tampilkan Informasi Pribadi (Kode tetap sama) ---
        personal_frame = QFrame()
        personal_frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 20px;")
        personal_layout = QVBoxLayout(personal_frame)
        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        personal_layout.addWidget(name_label)
        for label, value in [("Birthdate", birthdate), ("Address", address), ("Phone", phone)]:
            info_layout = QHBoxLayout()
            label_widget = QLabel(f"{label}:")
            label_widget.setFont(QFont("Segoe UI", 11, QFont.Bold))
            value_widget = QLabel(str(value))
            value_widget.setFont(QFont("Segoe UI", 11))
            info_layout.addWidget(label_widget)
            info_layout.addWidget(value_widget)
            info_layout.addStretch()
            personal_layout.addLayout(info_layout)
        self.info_layout.addWidget(personal_frame)
        
        # --- Tampilkan Keahlian (Skills) ---
        skills_header = QLabel("Skills")
        skills_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.info_layout.addWidget(skills_header)
        skills_frame = QFrame()
        skills_frame.setStyleSheet("background-color: white; border-radius: 10px; padding: 20px;")
        skills_layout = QVBoxLayout(skills_frame)
        
        if skills_list:
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
                            border: 2px solid #C8E6C9; 
                            border-radius: 15px; 
                            padding: 8px 15px;
                        }
                    """)
                    skill_tag.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
                    current_row.addWidget(skill_tag)
                    skill_count += 1
                    
                    # Jika sudah mencapai jumlah skill per baris, buat baris baru
                    if skill_count % skills_per_row == 0:
                        skills_layout.addLayout(current_row)
                        current_row = QHBoxLayout()
                        current_row.setSpacing(10)
            
            # Tambahkan baris terakhir jika masih ada skill yang belum ditampilkan
            if skill_count % skills_per_row != 0:
                current_row.addStretch()
                skills_layout.addLayout(current_row)
            
            skills_layout.addStretch()
        else:
            skills_layout.addWidget(QLabel("Tidak ada data keahlian."))
        self.info_layout.addWidget(skills_frame)

        # --- 5. Tampilkan Pengalaman Kerja (Job History) ---
        # Tampilkan Pengalaman Kerja
        exp_header = QLabel("Job History")
        exp_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.info_layout.addWidget(exp_header)
        if experience_list:
            for exp in experience_list:
                exp_frame = QFrame()
                exp_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #eee; padding: 15px;")
                exp_layout = QVBoxLayout(exp_frame)
                
                pos_label = QLabel(exp.get('position', 'N/A'))
                pos_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
                pos_label.setStyleSheet("color: #2E7D32;")
                
                comp_date_text = f"{exp.get('company', 'N/A')} | {exp.get('date_range', 'N/A')}"
                comp_date_label = QLabel(comp_date_text)
                comp_date_label.setStyleSheet("color: #666; margin-bottom: 10px;")
                
                desc_label = QLabel(exp.get('description', '').replace('\n', '<br>'))
                desc_label.setWordWrap(True)
                
                exp_layout.addWidget(pos_label)
                exp_layout.addWidget(comp_date_label)
                exp_layout.addWidget(desc_label)
                self.info_layout.addWidget(exp_frame)
        else:
            self.info_layout.addWidget(QLabel("Tidak ada data pengalaman kerja."))
        # --- 6. Tampilkan Riwayat Pendidikan (Education) ---
        edu_header = QLabel("Education")
        edu_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.info_layout.addWidget(edu_header)
        
        education_frame = QFrame()
        education_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        education_layout = QVBoxLayout(education_frame)
        
        education_display = QTextEdit()
        education_display.setReadOnly(True)
        education_display.setFont(QFont("Segoe UI", 11))
        education_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                line-height: 1.6;
            }
        """)
        
        # Format teks education
        if education_list:
            formatted_text = ""
            for edu in education_list:
                year_text = edu.get('year', 'N/A')
                formatted_text += f"""
                <div style='margin-bottom: 15px; padding: 12px; background-color: #f8f9fa; border-radius: 8px;'>
                    <p style='font-size: 13px; font-weight: bold; color: #2E7D32; margin: 0;'>{edu.get('degree', 'N/A')}</p>
                    <p style="font-size: 11px; color: #666; margin: 3px 0;">{edu.get('institution', 'N/A')}</p>
                    <p style="font-size: 11px; color: #666; margin: 3px 0;">{year_text}</p>
                </div>"""
            education_display.setHtml(formatted_text)
        else:
            education_display.setText("Tidak ada data riwayat pendidikan.")
        
        # Set tinggi minimum dan maksimum
        education_display.setMinimumHeight(200)
        education_display.setMaximumHeight(400)
        
        education_layout.addWidget(education_display)
        self.info_layout.addWidget(education_frame)

        # Menambahkan sisa ruang kosong di bagian bawah
        self.info_layout.addStretch()