# import sys
# from PyQt5.QtWidgets import QApplication
# from ui.main_page import CVAnalyzerApp

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = CVAnalyzerApp()
#     window.show()
#     sys.exit(app.exec_())

# ========== TESTING CORE ==========

# Penting: Jalankan file ini dari direktori root proyek Anda (Tubes3_NamaKelompok),
# bukan dari dalam folder src/.
# Contoh command: python src/main.py

from core import pdf_parser, kmp, bm, levenshtein, regex_extractor
import time
import re

# --- Konfigurasi untuk Pengujian ---
PDF_PATH = 'data/10276858.pdf' 
KEYWORD_TO_SEARCH = 'kitchen'
WORD_1 = 'recipes'
WORD_2 = 'recipis'

def print_formatted_experience(text: str):
    """
    Fungsi helper untuk mencetak bagian Experience dengan format yang lebih rapi.
    Memecah teks berdasarkan pola tanggal (misal: 09/2010 - 04/2011) di awal baris.
    """
    if not text:
        print("[INFO] Bagian Experience tidak ditemukan.")
        return

    # Pola untuk memisahkan setiap entri pekerjaan berdasarkan tanggal di awal baris
    # Menggunakan lookahead `(?=...)` agar pola tanggal tidak ikut terhapus saat split
    job_entries = re.split(r'(?=^\s*\d{2,4}/\d{4})', text, flags=re.MULTILINE)

    for entry in job_entries:
        # Menghapus string kosong yang mungkin muncul dari hasil split
        if entry.strip():
            print(entry.strip())
            # Mencetak garis pemisah antar entri pekerjaan
            print("---")

def run_tests():
    """Fungsi utama untuk menjalankan semua pengujian."""
    
    print("="*40)
    print("MEMULAI PENGUJIAN CORE ALGORITHMS")
    print("="*40)
    
    # --- Langkah 1: Ekstraksi Teks dari PDF ---
    print(f"\n[INFO] Mengekstrak teks dari: {PDF_PATH}")
    cv_text_pm = pdf_parser.extract_text_for_pattern_matching(PDF_PATH)
    cv_text_regex = pdf_parser.extract_text_for_regex(PDF_PATH)
    
    if not cv_text_pm or not cv_text_regex:
        print("[ERROR] Gagal mengekstrak teks dari PDF. Pengujian dihentikan.")
        return
    
    print("[SUCCESS] Teks berhasil diekstrak untuk kedua mode.\n")
    
    # --- Pengujian Algoritma Pencarian (KMP & BM) ---
    # (Bagian ini tidak berubah)
    print("-" * 40)
    print("--- PENGUJIAN ALGORITMA KMP & BOYER-MOORE ---")
    kmp_results = kmp.kmp_search(cv_text_pm, KEYWORD_TO_SEARCH)
    bm_results = bm.bm_search(cv_text_pm, KEYWORD_TO_SEARCH)
    print(f"KMP menemukan '{KEYWORD_TO_SEARCH}' sebanyak {len(kmp_results)} kali.")
    print(f"Boyer-Moore menemukan '{KEYWORD_TO_SEARCH}' sebanyak {len(bm_results)} kali.")
    print("-" * 40)

    # --- Pengujian Algoritma Levenshtein Distance ---
    # (Bagian ini tidak berubah)
    print("\n" + "-" * 40)
    print("--- PENGUJIAN ALGORITMA LEVENSHTEIN DISTANCE ---")
    distance = levenshtein.levenshtein_distance(WORD_1, WORD_2)
    print(f"Jarak Levenshtein antara '{WORD_1}' dan '{WORD_2}' adalah {distance}.")
    print("-" * 40)

    # --- Pengujian Modul Regex Extractor (dengan output terformat) ---
    print("\n" + "-" * 40)
    print("--- PENGUJIAN REGEX EXTRACTOR ---")
    
    # Ekstrak Skills (outputnya sudah cukup rapi)
    print("\n-- HASIL EKSTRAKSI SKILLS --")
    skills = regex_extractor.extract_skills(cv_text_regex)
    print(skills if skills else "[INFO] Bagian Skills tidak ditemukan.")
    
    # Ekstrak Experience (menggunakan fungsi format baru)
    print("\n-- HASIL EKSTRAKSI EXPERIENCE --")
    experience = regex_extractor.extract_experience(cv_text_regex)
    print_formatted_experience(experience)

    # Ekstrak Education (outputnya sudah cukup rapi)
    print("\n-- HASIL EKSTRAKSI EDUCATION --")
    education = regex_extractor.extract_education(cv_text_regex)
    print(education if education else "[INFO] Bagian Education tidak ditemukan.")
    print("-" * 40)
    
    print("\n" + "="*40)
    print("PENGUJIAN SELESAI")
    print("="*40)


if __name__ == "__main__":
    run_tests()