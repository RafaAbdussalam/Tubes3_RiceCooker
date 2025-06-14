from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont, QIcon

class CandidateCard(QFrame):
    """Custom widget for displaying a candidate card in search results."""
    def __init__(self, candidate, on_summary_click, on_view_click):
        super().__init__()
        self.candidate = candidate
        self.on_summary_click = on_summary_click
        self.on_view_click = on_view_click
        self.init_ui()

    def init_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("background-color: #E0E0E0; border-radius: 5px; padding: 5px;")
        layout = QVBoxLayout(self)

        # Candidate name
        name_label = QLabel(self.candidate.get("name", "N/A"))
        name_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(name_label)

        # Matched keywords
        matches = self.candidate.get("match_count", 0)
        matches_label = QLabel(f"Matched keywords: {matches}")
        layout.addWidget(matches_label)

        # Keywords with occurrences
        keywords = self.candidate.get("matched_keywords", {})
        if keywords:
            keywords_text = ", ".join([f"{k}: {v} occurrence" for k, v in keywords.items()])
            keywords_label = QLabel(keywords_text)
            layout.addWidget(keywords_label)

        # Action buttons
        button_layout = QHBoxLayout()
        summary_button = QPushButton("Summary")
        summary_button.setStyleSheet("background-color: #2196F3; color: white; border-radius: 3px;")
        summary_button.setIcon(QIcon("assets/summary_icon.png"))  # Placeholder path for icon
        summary_button.clicked.connect(lambda: self.on_summary_click(self.candidate))
        view_button = QPushButton("View CV")
        view_button.setStyleSheet("background-color: #FF9800; color: white; border-radius: 3px;")
        view_button.setIcon(QIcon("assets/view_icon.png"))  # Placeholder path for icon
        view_button.clicked.connect(lambda: self.on_view_click(self.candidate.get("cv_path", "")))
        button_layout.addWidget(summary_button)
        button_layout.addWidget(view_button)
        layout.addLayout(button_layout)