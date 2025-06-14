import sys
from PyQt5.QtWidgets import QApplication
from ui.main_page import CVAnalyzerApp
from db.operations import close_db_connection 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CVAnalyzerApp()
    window.show()
    app.aboutToQuit.connect(close_db_connection)
    sys.exit(app.exec_())