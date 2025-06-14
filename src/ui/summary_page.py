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

    def update_candidate_info(self, candidate_name, cv_path=None, matched_keywords=None, sections=None):
        """Update the candidate information on the summary page using extracted data."""
        # Clear previous information
        while self.info_layout.count():
            child = self.info_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Extract raw text from CV if path is provided
        raw_cv_text = extract_text_for_regex(cv_path) if cv_path else ""
        sections = sections or extract_all_sections(raw_cv_text) if raw_cv_text else {}

        # Extract basic candidate info
        candidate_data = {
            "name": candidate_name,
            "phone": "N/A",
            "email": "N/A",
            "skills": sections.get("skills", "").split("\n") if sections.get("skills") else [],
        }
        if raw_cv_text:
            # Simple regex to extract phone and email
            phone_match = re.search(r'\b\d{9,}\b', raw_cv_text)
            candidate_data["phone"] = phone_match.group(0) if phone_match else "N/A"
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_cv_text)
            candidate_data["email"] = email_match.group(0) if email_match else "N/A"

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
                if skill.strip():  # Skip empty strings
                    skill_button = QPushButton(skill.strip())
                    skill_button.setStyleSheet("background-color: #BBDEFB; color: black; border-radius: 5px; padding: 5px;")
                    skills_layout.addWidget(skill_button)
            self.info_layout.addLayout(skills_layout)

        # Experience
        experience_text = sections.get("experience", "").strip()
        if experience_text:
            experience_label = QLabel("Experience:")
            experience_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.info_layout.addWidget(experience_label)
            experience_display = QTextEdit(experience_text)
            experience_display.setReadOnly(True)
            experience_display.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
            experience_display.setFixedHeight(100)  # Adjust height as needed
            self.info_layout.addWidget(experience_display)
        else:
            experience_frame = QFrame()
            experience_frame.setStyleSheet("background-color: #E0E0E0; border-radius: 5px; padding: 5px;")
            experience_layout = QVBoxLayout(experience_frame)
            experience_layout.addWidget(QLabel("No experience found"))
            self.info_layout.addWidget(experience_frame)

        # Education
        education_text = sections.get("education", "").strip()
        if education_text:
            education_label = QLabel("Education:")
            education_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.info_layout.addWidget(education_label)
            education_display = QTextEdit(education_text)
            education_display.setReadOnly(True)
            education_display.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
            education_display.setFixedHeight(100)  # Adjust height as needed
            self.info_layout.addWidget(education_display)
        else:
            education_frame = QFrame()
            education_frame.setStyleSheet("background-color: #E0E0E0; border-radius: 5px; padding: 5px;")
            education_layout = QVBoxLayout(education_frame)
            education_layout.addWidget(QLabel("No education found"))
            self.info_layout.addWidget(education_frame)

        self.info_layout.addStretch()