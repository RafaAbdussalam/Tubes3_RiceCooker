import fitz  # PyMuPDF
import re
import os
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_absolute_path(relative_path: str) -> str:
    """
    Mengkonversi path relatif menjadi path absolut.
    """
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        absolute_path = os.path.join(root_dir, relative_path)
        if not os.path.exists(absolute_path):
            logger.error(f"File tidak ditemukan: {absolute_path}")
            return ""
        return absolute_path
    except Exception as e:
        logger.error(f"Error dalam get_absolute_path: {str(e)}")
        return ""

def extract_text_for_regex(pdf_path: str) -> str:
    """
    Mengekstrak teks dari PDF dengan mempertahankan format asli (case dan newlines).
    Cocok untuk digunakan dengan Regular Expressions.

    Args:
        pdf_path: Path menuju file PDF.

    Returns:
        String teks dengan format asli.
    """
    try:
        absolute_path = get_absolute_path(pdf_path)
        if not absolute_path:
            return ""
            
        doc = fitz.open(absolute_path)
        full_text = ""
        for page in doc:
            # Menggunakan get_text("text") adalah default dan mempertahankan format
            full_text += page.get_text("text")
        doc.close()
        return full_text
    except Exception as e:
        logger.error(f"Error reading PDF for Regex {pdf_path}: {str(e)}")
        return ""

def extract_text_for_pattern_matching(pdf_path: str) -> str:
    """
    Mengekstrak teks dari PDF dan mengubahnya menjadi format 'flat' dan lowercase.
    Cocok untuk digunakan dengan algoritma KMP dan Boyer-Moore.

    Args:
        pdf_path: Path menuju file PDF.

    Returns:
        String teks dalam format lowercase dan spasi tunggal.
    """
    try:
        # Kita bisa menggunakan fungsi pertama sebagai dasar
        raw_text = extract_text_for_regex(pdf_path)
        if not raw_text:
            logger.warning(f"Tidak ada teks yang diekstrak dari {pdf_path}")
            return ""
        
        # 1. Ubah ke huruf kecil (lowercase)
        text = raw_text.lower()
        
        # 2. Ganti semua karakter whitespace (spasi, tab, newline) dengan satu spasi
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    except Exception as e:
        logger.error(f"Error dalam extract_text_for_pattern_matching untuk {pdf_path}: {str(e)}")
        return ""


# if __name__ == '__main__':
#     # Ganti dengan path CV yang valid dari folder data Anda
#     sample_cv_path = 'data/ACCOUNTANT/10554236.pdf' 

#     # --- Proses untuk Regex ---
#     print(f"Mengekstrak teks dari {sample_cv_path} untuk Regex...")
#     text_for_regex = extract_text_for_regex(sample_cv_path)
#     if text_for_regex:
#         # Menyimpan output ke file txt untuk perbandingan
#         with open('hasil_ekstraksi_regex.txt', 'w', encoding='utf-8') as f:
#             f.write(text_for_regex)
#         print("Ekstraksi untuk Regex berhasil. Output disimpan di 'hasil_ekstraksi_regex.txt'")
#     else:
#         print("Ekstraksi untuk Regex gagal.")

#     print("-" * 30)

#     # --- Proses untuk Pattern Matching ---
#     print(f"Mengekstrak teks dari {sample_cv_path} untuk Pattern Matching...")
#     text_for_pm = extract_text_for_pattern_matching(sample_cv_path)
#     if text_for_pm:
#         # Menyimpan output ke file txt untuk perbandingan
#         with open('hasil_ekstraksi_pattern_matching.txt', 'w', encoding='utf-8') as f:
#             f.write(text_for_pm)
#         print("Ekstraksi untuk Pattern Matching berhasil. Output disimpan di 'hasil_ekstraksi_pattern_matching.txt'")
#     else:
#         print("Ekstraksi untuk Pattern Matching gagal.")