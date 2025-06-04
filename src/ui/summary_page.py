from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

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
        back_button.setStyleSheet("background-color: #FA5053; color: white; padding: 5px; border-radius: 5px;")
        back_button.clicked.connect(self.controller.switch_to_search)
        layout.addWidget(back_button)

    def update_candidate_info(self, candidate_name):
        """Update the candidate information on the summary page."""
        # Clear previous information
        while self.info_layout.count():
            child = self.info_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Simulate candidate data
        candidate_data = {
            "name": candidate_name,
            "birthdate": "05-19-2025",
            "address": "Masjid Salman ITB",
            "phone": "0812 3456 7890",
            "skills": ["React", "Express", "HTML"],
            "job_history": {"CTO": "2003-2004"},
            "education": {"university": "Institut Teknologi Bandung", "years": "2002-2004"}
        }

        # Display candidate information
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

        # Job History
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