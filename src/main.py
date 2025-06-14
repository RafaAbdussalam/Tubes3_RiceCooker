import sys
from PyQt5.QtWidgets import QApplication
from ui.main_page import CVAnalyzerApp

def main():
    """Fungsi utama untuk menjalankan aplikasi."""
    # Inisialisasi QApplication
    app = QApplication(sys.argv)
    
    # Buat instance window utama
    window = CVAnalyzerApp()
    
    # Tampilkan window
    window.show()
    
    # Jalankan event loop aplikasi
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()