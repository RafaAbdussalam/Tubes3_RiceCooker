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
        
        # Ambil data yang diekstrak dari CV oleh backend
        skills_text = summary_data.get('skills', 'Tidak ditemukan').strip()
        experience_text = summary_data.get('experience', 'Tidak ditemukan').strip()
        education_text = summary_data.get('education', 'Tidak ditemukan').strip()

        # --- 3. Tampilkan Informasi Pribadi ---
        personal_frame = QFrame()
        personal_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        personal_layout = QVBoxLayout(personal_frame)
        personal_layout.setSpacing(10)
        
        name_label = QLabel(name)
        name_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        personal_layout.addWidget(name_label)
        
        # Detail info dengan style yang lebih baik
        for label, value in [
            ("Birthdate", birthdate),
            ("Address", address),
            ("Phone", phone)
        ]:
            info_layout = QHBoxLayout()
            label_widget = QLabel(f"{label}:")
            label_widget.setFont(QFont("Segoe UI", 11, QFont.Bold))
            value_widget = QLabel(str(value))  # Konversi value ke string
            value_widget.setFont(QFont("Segoe UI", 11))
            info_layout.addWidget(label_widget)
            info_layout.addWidget(value_widget)
            info_layout.addStretch()
            personal_layout.addLayout(info_layout)
        
        self.info_layout.addWidget(personal_frame)

        # --- 4. Tampilkan Keahlian (Skills) ---
        skills_header = QLabel("Skills")
        skills_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.info_layout.addWidget(skills_header)

        skills_frame = QFrame()
        skills_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        skills_layout = QVBoxLayout(skills_frame)
        skills_layout.setSpacing(10)
        
        if skills_text and skills_text != 'Tidak ditemukan':
            # Buat grid layout untuk skills
            current_row = QHBoxLayout()
            current_row.setSpacing(10)
            row_width = 0
            max_width = 800  # Maksimum lebar yang diizinkan
            
            for skill in skills_text.split('\n'):
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
                            text-align: left;
                        }
                        QPushButton:hover {
                            background-color: #C8E6C9;
                        }
                    """)
                    
                    # Hitung lebar minimum yang dibutuhkan
                    skill_tag.setMinimumWidth(100)
                    skill_tag.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                    
                    # Tambahkan ke row saat ini
                    current_row.addWidget(skill_tag)
                    row_width += skill_tag.sizeHint().width()
                    
                    # Jika row sudah penuh, tambahkan ke layout utama dan buat row baru
                    if row_width >= max_width:
                        skills_layout.addLayout(current_row)
                        current_row = QHBoxLayout()
                        current_row.setSpacing(10)
                        row_width = 0
            
            # Tambahkan row terakhir jika masih ada isinya
            if current_row.count() > 0:
                skills_layout.addLayout(current_row)
                
            # Tambahkan stretch di akhir untuk memastikan alignment yang benar
            skills_layout.addStretch()
        else:
            no_skills = QLabel("Tidak ada data keahlian.")
            no_skills.setFont(QFont("Segoe UI", 11))
            no_skills.setStyleSheet("color: #757575;")
            skills_layout.addWidget(no_skills)
        
        self.info_layout.addWidget(skills_frame)

        # --- 5. Tampilkan Pengalaman Kerja (Job History) ---
        exp_header = QLabel("Job History")
        exp_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.info_layout.addWidget(exp_header)
        
        experience_frame = QFrame()
        experience_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        experience_layout = QVBoxLayout(experience_frame)
        
        # Buat QTextEdit dengan styling yang lebih baik
        experience_display = QTextEdit()
        experience_display.setReadOnly(True)
        experience_display.setFont(QFont("Segoe UI", 11))
        experience_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                line-height: 1.6;
            }
        """)
        
        # Format teks experience
        if experience_text and experience_text != 'Tidak ditemukan':
            # Pisahkan setiap job entry
            job_entries = experience_text.split('\n\n')
            formatted_text = ""
            
            for entry in job_entries:
                if entry.strip():
                    # Pisahkan judul, lokasi, tanggal, dan deskripsi
                    parts = [p.strip() for p in entry.split('\n') if p.strip()]
                    if len(parts) >= 1:
                        title = parts[0]
                        location = parts[1] if len(parts) > 1 and not re.search(r'\d{2}/\d{4}', parts[1]) else ""
                        date = next((p for p in parts if re.search(r'\d{2}/\d{4}', p)), "")
                        description = '\n'.join(p for p in parts if p not in [title, location, date])
                        
                        # Format dengan HTML untuk styling yang lebih baik
                        formatted_text += f"""
                        <div style='margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 8px;'>
                            <p style='font-size: 14px; font-weight: bold; color: #2E7D32; margin: 0;'>{title}</p>
                            {f'<p style="font-size: 12px; color: #666; margin: 3px 0;">{location}</p>' if location else ''}
                            {f'<p style="font-size: 12px; color: #666; margin: 3px 0;">{date}</p>' if date else ''}
                            <div style='margin-left: 20px; color: #333;'>
                                {description.replace('•', '<br>•')}
                            </div>
                        </div>
                        """
            
            experience_display.setHtml(formatted_text)
        else:
            experience_display.setText("Tidak ada data pengalaman kerja.")
        
        # Set tinggi minimum dan maksimum
        experience_display.setMinimumHeight(300)
        experience_display.setMaximumHeight(500)
        
        experience_layout.addWidget(experience_display)
        self.info_layout.addWidget(experience_frame)

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
        if education_text and education_text != 'Tidak ditemukan':
            # Pisahkan setiap entri pendidikan
            edu_entries = education_text.split('\n\n')
            formatted_text = ""
            
            for entry in edu_entries:
                if entry.strip():
                    # Pisahkan judul, institusi, tanggal, dan deskripsi
                    parts = [p.strip() for p in entry.split('\n') if p.strip()]
                    if len(parts) >= 1:
                        title = parts[0]
                        institution = parts[1] if len(parts) > 1 and not re.search(r'\d{4}', parts[1]) else ""
                        date = next((p for p in parts if re.search(r'\d{4}', p)), "")
                        description = '\n'.join(p for p in parts if p not in [title, institution, date])
                        
                        # Format dengan HTML untuk styling yang lebih baik
                        formatted_text += f"""
                        <div style='margin-bottom: 15px; padding: 12px; background-color: #f8f9fa; border-radius: 8px;'>
                            <p style='font-size: 13px; font-weight: bold; color: #2E7D32; margin: 0;'>{title}</p>
                            {f'<p style="font-size: 11px; color: #666; margin: 3px 0;">{institution}</p>' if institution else ''}
                            {f'<p style="font-size: 11px; color: #666; margin: 3px 0;">{date}</p>' if date else ''}
                            <div style='margin-left: 15px; color: #333; font-size: 12px;'>
                                {description.replace('•', '<br>•')}
                            </div>
                        </div>
                        """
            
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