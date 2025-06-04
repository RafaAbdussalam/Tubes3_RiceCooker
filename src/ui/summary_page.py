from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from core.pdf_parser import extract_text_from_pdf
from core.regex_extractor import extract_candidate_info

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

    def update_candidate_info(self, candidate_name, cv_path=None, matched_keywords=None):
        """Update the candidate information on the summary page using extracted data."""
        # Clear previous information
        while self.info_layout.count():
            child = self.info_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Extract text from CV if path is provided
        cv_text = extract_text_from_pdf(cv_path) if cv_path else ""
        candidate_data = extract_candidate_info(cv_text) if cv_text else {}

        # Default values if extraction fails
        candidate_data.setdefault("name", candidate_name)
        candidate_data.setdefault("phone", "N/A")
        candidate_data.setdefault("email", "N/A")
        candidate_data.setdefault("skills", [])
        candidate_data.setdefault("job_history", [])
        candidate_data.setdefault("education", [])

        # Display candidate information
        name_label = QLabel(candidate_data["name"])
        name_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.info_layout.addWidget(name_label)

        phone_label = QLabel(f"Phone: {candidate_data['phone']}")
        self.info_layout.addWidget(phone_label)

        email_label = QLabel(f"Email: {candidate_data['email']}")
        self.info_layout.addWidget(email_label)

        # Skills (combine matched keywords with extracted skills)
        all_skills = list(set(candidate_data["skills"] + list(matched_keywords.keys() if matched_keywords else [])))
        if all_skills:
            skills_label = QLabel("Skills:")
            skills_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.info_layout.addWidget(skills_label)

            skills_layout = QHBoxLayout()
            for skill in all_skills:
                skill_button = QPushButton(skill)
                skill_button.setStyleSheet("background-color: #BBDEFB; color: black; border-radius: 5px; padding: 5px;")
                skills_layout.addWidget(skill_button)
            self.info_layout.addLayout(skills_layout)

        # Job History
        job_history_label = QLabel("Job History:")
        job_history_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.info_layout.addWidget(job_history_label)

        if candidate_data["job_history"]:
            for job in candidate_data["job_history"]:
                job_entry = QFrame()
                job_entry.setStyleSheet("background-color: #E0E0E0; border-radius: 5px; padding: 5px;")
                job_layout = QVBoxLayout(job_entry)
                job_layout.addWidget(QLabel(job["position"]))
                job_layout.addWidget(QLabel(f"Company: {job['company']}"))
                job_layout.addWidget(QLabel(f"Years: {job['years']}"))
                self.info_layout.addWidget(job_entry)
        else:
            job_entry = QFrame()
            job_entry.setStyleSheet("background-color: #E0E0E0; border-radius: 5px; padding: 5px;")
            job_layout = QVBoxLayout(job_entry)
            job_layout.addWidget(QLabel("No job history found"))
            self.info_layout.addWidget(job_entry)

        # Education
        education_label = QLabel("Education:")
        education_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.info_layout.addWidget(education_label)

        if candidate_data["education"]:
            for edu in candidate_data["education"]:
                edu_entry = QFrame()
                edu_entry.setStyleSheet("background-color: #E0E0E0; border-radius: 5px; padding: 5px;")
                edu_layout = QVBoxLayout(edu_entry)
                edu_layout.addWidget(QLabel(edu["degree"]))
                edu_layout.addWidget(QLabel(f"University: {edu['university']}"))
                edu_layout.addWidget(QLabel(f"Years: {edu['years']}"))
                self.info_layout.addWidget(edu_entry)
        else:
            edu_entry = QFrame()
            edu_entry.setStyleSheet("background-color: #E0E0E0; border-radius: 5px; padding: 5px;")
            edu_layout = QVBoxLayout(edu_entry)
            edu_layout.addWidget(QLabel("No education history found"))
            self.info_layout.addWidget(edu_entry)

        self.info_layout.addStretch()