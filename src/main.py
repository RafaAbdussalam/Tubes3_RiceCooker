import sys
from PyQt5.QtWidgets import QApplication
from ui.main_page import CVAnalyzerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CVAnalyzerApp()
    window.show()
    sys.exit(app.exec_())