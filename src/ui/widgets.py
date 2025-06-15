from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

class CandidateCard(QFrame):
    """Custom widget for displaying a candidate card in search results."""
    def __init__(self, candidate, on_summary_click, on_view_click):
        super().__init__()
        self.candidate = candidate
        self.on_summary_click = on_summary_click
        self.on_view_click = on_view_click
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
            QLabel {
                color: #333333;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Candidate name dengan style yang lebih baik
        name_label = QLabel(self.candidate.get("name", "N/A"))
        name_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        name_label.setStyleSheet("color: #2E7D32;")
        layout.addWidget(name_label)

        # Matched keywords dengan style yang lebih baik
        matches = self.candidate.get("match_count", 0)
        matches_label = QLabel(f"Matched keywords: {matches}")
        matches_label.setFont(QFont("Segoe UI", 11))
        matches_label.setStyleSheet("""
            QLabel {
                background-color: #E8F5E9;
                color: #2E7D32;
                padding: 5px 10px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(matches_label)

        # Keywords with occurrences dengan style yang lebih baik
        keywords = self.candidate.get("matched_keywords", {})
        if keywords:
            keywords_frame = QFrame()
            keywords_frame.setStyleSheet("""
                QFrame {
                    background-color: #F5F5F5;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
            keywords_layout = QVBoxLayout(keywords_frame)
            keywords_layout.setSpacing(5)
            
            for keyword, count in keywords.items():
                keyword_layout = QHBoxLayout()
                keyword_label = QLabel(f"• {keyword}")
                keyword_label.setFont(QFont("Segoe UI", 10))
                count_label = QLabel(f"{count} occurrence{'s' if count > 1 else ''}")
                count_label.setFont(QFont("Segoe UI", 10))
                count_label.setStyleSheet("color: #757575;")
                keyword_layout.addWidget(keyword_label)
                keyword_layout.addWidget(count_label)
                keyword_layout.addStretch()
                keywords_layout.addLayout(keyword_layout)
            
            layout.addWidget(keywords_frame)

        # Action buttons dengan style yang lebih baik
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        summary_button = QPushButton("Summary")
        summary_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        summary_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2196F3, stop:1 #1976D2);
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #42A5F5, stop:1 #2196F3);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1976D2, stop:1 #1565C0);
            }
        """)
        summary_button.clicked.connect(lambda: self.on_summary_click(self.candidate))
        
        view_button = QPushButton("View CV")
        view_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        view_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FF9800, stop:1 #F57C00);
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFA726, stop:1 #FF9800);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F57C00, stop:1 #EF6C00);
            }
        """)
        view_button.clicked.connect(lambda: self.on_view_click(self.candidate.get("cv_path", "")))
        
        button_layout.addWidget(summary_button)
        button_layout.addWidget(view_button)
        layout.addLayout(button_layout)