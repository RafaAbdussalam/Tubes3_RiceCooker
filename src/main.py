# Penting: Jalankan file ini dari direktori root proyek Anda (Tubes3_NamaKelompok),
# bukan dari dalam folder src/.
# Contoh command: python src/main.py

from core import pdf_parser, kmp, bm, levenshtein, regex_extractor
import time # <- Tambahkan import ini
import re

# --- Konfigurasi untuk Pengujian ---
PDF_PATH = 'data/10276858.pdf' 
KEYWORD_TO_SEARCH = 'kitchen'
WORD_1 = 'recipes'
WORD_2 = 'recipis' # Typo dari 'recipes'

def print_formatted_experience(text: str):
    """
    Fungsi helper untuk mencetak bagian Experience dengan format yang lebih rapi.
    """
    if not text:
        print("[INFO] Bagian Experience tidak ditemukan.")
        return
    job_entries = re.split(r'(?=^\s*\d{2,4}/\d{4})', text, flags=re.MULTILINE)
    for entry in job_entries:
        if entry.strip():
            print(entry.strip())
            print("---")

def run_tests():
    """Fungsi utama untuk menjalankan semua pengujian."""
    
    print("="*40)
    print("MEMULAI PENGUJIAN CORE ALGORITHMS")
    print("="*40)
    
    print(f"\n[INFO] Mengekstrak teks dari: {PDF_PATH}")
    cv_text_pm = pdf_parser.extract_text_for_pattern_matching(PDF_PATH)
    cv_text_regex = pdf_parser.extract_text_for_regex(PDF_PATH)
    
    if not cv_text_pm or not cv_text_regex:
        print("[ERROR] Gagal mengekstrak teks dari PDF. Pengujian dihentikan.")
        return
    
    print("[SUCCESS] Teks berhasil diekstrak untuk kedua mode.\n")
    
    # --- Pengujian Algoritma Knuth-Morris-Pratt (KMP) ---
    print("-" * 40)
    print("--- PENGUJIAN ALGORITMA KMP ---")
    print(f"Mencari kata kunci: '{KEYWORD_TO_SEARCH}'")
    
    # MODIFIKASI: Catat waktu mulai
    start_time_kmp = time.perf_counter()
    kmp_results = kmp.kmp_search(cv_text_pm, KEYWORD_TO_SEARCH)
    # MODIFIKASI: Catat waktu selesai
    end_time_kmp = time.perf_counter()
    duration_kmp_ms = (end_time_kmp - start_time_kmp) * 1000
    
    print(f"Hasil: Ditemukan {len(kmp_results)} kali.")
    # MODIFIKASI: Tampilkan waktu eksekusi
    print(f"Waktu eksekusi KMP: {duration_kmp_ms:.4f} ms")
    print("-" * 40)

    # --- Pengujian Algoritma Boyer-Moore (BM) ---
    print("\n" + "-" * 40)
    print("--- PENGUJIAN ALGORITMA BOYER-MOORE ---")
    print(f"Mencari kata kunci: '{KEYWORD_TO_SEARCH}'")
    
    # MODIFIKASI: Catat waktu mulai
    start_time_bm = time.perf_counter()
    bm_results = bm.bm_search(cv_text_pm, KEYWORD_TO_SEARCH)
    # MODIFIKASI: Catat waktu selesai
    end_time_bm = time.perf_counter()
    duration_bm_ms = (end_time_bm - start_time_bm) * 1000
    
    print(f"Hasil: Ditemukan {len(bm_results)} kali.")
    # MODIFIKASI: Tampilkan waktu eksekusi
    print(f"Waktu eksekusi Boyer-Moore: {duration_bm_ms:.4f} ms")
    print("-" * 40)

    # --- Pengujian Algoritma Levenshtein Distance ---
    print("\n" + "-" * 40)
    print("--- PENGUJIAN ALGORITMA LEVENSHTEIN DISTANCE ---")
    distance = levenshtein.levenshtein_distance(WORD_1, WORD_2)
    print(f"Jarak Levenshtein antara '{WORD_1}' dan '{WORD_2}' adalah {distance}.")
    print("-" * 40)

    # --- Pengujian Modul Regex Extractor ---
    print("\n" + "-" * 40)
    print("--- PENGUJIAN REGEX EXTRACTOR ---")
    
    print("\n-- HASIL EKSTRAKSI SKILLS --")
    skills = regex_extractor.extract_skills(cv_text_regex)
    print(skills if skills else "[INFO] Bagian Skills tidak ditemukan.")
    
    print("\n-- HASIL EKSTRAKSI EXPERIENCE --")
    experience = regex_extractor.extract_experience(cv_text_regex)
    print_formatted_experience(experience)

    print("\n-- HASIL EKSTRAKSI EDUCATION --")
    education = regex_extractor.extract_education(cv_text_regex)
    print(education if education else "[INFO] Bagian Education tidak ditemukan.")
    print("-" * 40)
    
    print("\n" + "="*40)
    print("PENGUJIAN SELESAI")
    print("="*40)


if __name__ == "__main__":
    run_tests()