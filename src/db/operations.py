import configparser
import traceback
import time
import os
import logging

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from db.database_manager import DatabaseManager
from mysql.connector import Error

from core.pdf_parser import extract_text_for_pattern_matching, extract_text_for_regex
from core.kmp import kmp_search
from core.bm import bm_search
from core.levenshtein import levenshtein_distance
# from core.regex_extractor import extract_skills, extract_experience, extract_education, extract_all_sections
from core.regex_extractor import extract_all_sections
from core.aho_corasick import AhoCorasick

_db_manager_instance = None

def _get_db_manager():
    """Menginisialisasi dan mengembalikan instance tunggal DatabaseManager."""
    global _db_manager_instance
    if _db_manager_instance is None:
        try:
            config = configparser.ConfigParser()
            # Menggunakan path absolut dari root direktori
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(root_dir, 'src', 'config.ini')
            
            if not config.read(config_path):
                raise FileNotFoundError(f"FATAL: File '{config_path}' tidak ditemukan.")

            db_config = dict(config['database'])
            _db_manager_instance = DatabaseManager(db_config)
            
        except Exception as e:
            print("--- [ERROR KRITIS SAAT SETUP DATABASE] ---")
            traceback.print_exc()
            return None
            
    return _db_manager_instance

def fetch_dataset_by_category(categories: list[str], limit_per_category: int = 20):
    """
    FUNGSI BARU: Mengambil dataset dari DB sesuai spesifikasi tugas.
    Mengambil data sejumlah `limit_per_category` dari setiap kategori yang diberikan,
    diurutkan secara leksikografis berdasarkan path CV.
    """
    db_manager = _get_db_manager()
    if not db_manager or not db_manager.get_connection():
        print("[ERROR] Gagal mendapatkan koneksi database saat fetch dataset.")
        return []

    conn = db_manager.get_connection()
    # cursor = conn.cursor(dictionary=True)
    cursor = conn.cursor(buffered=True, dictionary=True)
    full_dataset = []
    
    print("Mulai mengambil dataset berdasarkan kategori...")
    for category in categories:
        query = """
        SELECT 
            p.applicant_id as id, 
            p.first_name,
            p.last_name, 
            d.cv_path
        FROM ApplicantProfile p
        JOIN ApplicationDetail d ON p.applicant_id = d.applicant_id
        WHERE d.cv_path LIKE %s
        ORDER BY d.cv_path ASC
        LIMIT %s
        """
        try:
            category_pattern = f"%/{category}/%"
            cursor.execute(query, (category_pattern, limit_per_category))
            results = cursor.fetchall()
            full_dataset.extend(results)
            # print(f"Mengambil {len(results)} CV dari kategori: {category}") # Uncomment untuk debug
        except Exception as e:
            print(f"Error fetching data untuk kategori {category}: {e}")

    if cursor:
        cursor.close()
        
    for candidate in full_dataset:
        candidate['name'] = f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip()

    print(f"Total dataset yang diambil: {len(full_dataset)} CV.")
    return full_dataset

def search_cvs(keywords: list[str], algorithm: str, top_n: int):
    """
    Fungsi utama untuk orkestrasi pencarian, menggabungkan Exact dan Fuzzy Match.
    """
    CATEGORIES = [
        'ACCOUNTANT', 'ADVOCATE', 'AGRICULTURE', 'APPAREL', 'ARTS', 'AUTOMOBILE',
        'AVIATION', 'BANKING', 'BPO', 'BUSINESS-DEVELOPMENT', 'CHEF', 'CONSTRUCTION',
        'CONSULTANT', 'DESIGNER', 'DIGITAL-MEDIA', 'ENGINEERING', 'FINANCE',
        'FITNESS', 'HEALTHCARE', 'HR', 'INFORMATION-TECHNOLOGY', 'PUBLIC-RELATIONS',
        'SALES', 'TEACHER'
    ]
    
    all_candidates = fetch_dataset_by_category(CATEGORIES, limit_per_category=20)
    
    if not all_candidates:
        return {'data': [], 'execution_time_exact': 0, 'execution_time_fuzzy': 0, 'total_scanned': 0}

    results = {}
    lower_keywords = [kw.strip().lower() for kw in keywords if kw.strip()]
    total_scanned = len(all_candidates)
    failed_files = []

    # Bangun automaton Aho-Corasick sekali saja jika dipilih
    ac_automaton = None
    if algorithm.upper() == 'AHO-CORASICK':
        ac_automaton = AhoCorasick()
        for keyword in lower_keywords:
            ac_automaton.add_keyword(keyword)
        ac_automaton.build_failure_links()

    # --- Tahap 1: Exact Matching ---
    start_time_exact = time.time()
    for candidate in all_candidates:
        cv_path = candidate['cv_path']
        cv_text = extract_text_for_pattern_matching(cv_path)
        if not cv_text:
            continue

        if algorithm.upper() in ['KMP', 'BM']:
            for keyword in lower_keywords:
                search_func = kmp_search if algorithm.upper() == 'KMP' else bm_search
                indices = search_func(cv_text, keyword)
                if indices:
                    # (logika KMP/BM tetap sama)
                    candidate_id = candidate['id']
                    if candidate_id not in results:
                        results[candidate_id] = { 'id': candidate_id, 'name': candidate['name'], 'cv_path': cv_path, 'matched_keywords': {}, 'match_count': 0 }
                    results[candidate_id]['matched_keywords'][keyword] = len(indices)
        
        elif algorithm.upper() == 'AHO-CORASICK':
            # Cari semua keyword sekaligus
            found_matches = ac_automaton.search(cv_text)
            if found_matches:
                candidate_id = candidate['id']
                if candidate_id not in results:
                    results[candidate_id] = { 'id': candidate_id, 'name': candidate['name'], 'cv_path': cv_path, 'matched_keywords': {}, 'match_count': 0 }
                
                # Salin hasil dari Aho-Corasick
                for keyword, indices in found_matches.items():
                    results[candidate_id]['matched_keywords'][keyword] = len(indices)


    for res in results.values():
        res['match_count'] = len(res['matched_keywords'])
    exact_match_duration = time.time() - start_time_exact

    # --- Tahap 2: Fuzzy Matching (Lengkap) ---
    start_time_fuzzy = time.time()
    found_keywords_exact = {kw for res in results.values() for kw in res['matched_keywords']}
    unmatched_keywords = [kw for kw in lower_keywords if kw not in found_keywords_exact]
    
    fuzzy_match_duration = 0
    if unmatched_keywords:
        THRESHOLD = 2  # Jarak Levenshtein <= 2 dianggap mirip
        
        for candidate in all_candidates:
            if candidate['cv_path'] in failed_files:
                continue
                
            try:
                cv_text = extract_text_for_pattern_matching(candidate['cv_path'])
                if not cv_text:
                    continue
                
                cv_words = set(cv_text.split())
                for keyword in unmatched_keywords:
                    for word in cv_words:
                        if abs(len(keyword) - len(word)) <= THRESHOLD:
                            dist = levenshtein_distance(keyword, word)
                            if dist <= THRESHOLD and dist > 0:
                                candidate_id = candidate['id']
                                if candidate_id not in results:
                                    results[candidate_id] = {
                                        'id': candidate_id, 'name': candidate['name'], 'cv_path': candidate['cv_path'],
                                        'matched_keywords': {}, 'match_count': 0
                                    }
                                
                                fuzzy_key = f"{keyword} (similar: {word})"
                                results[candidate_id]['matched_keywords'][fuzzy_key] = results[candidate_id]['matched_keywords'].get(fuzzy_key, 0) + 1
                                break
            except Exception as e:
                logger.error(f"Error dalam fuzzy matching untuk {candidate['cv_path']}: {str(e)}")
                continue
        
        for res in results.values():
            res['match_count'] = len(res['matched_keywords'])
        
        fuzzy_match_duration = time.time() - start_time_fuzzy

    # --- Tahap 3: Finalisasi Hasil ---
    sorted_results = sorted(results.values(), key=lambda x: x['match_count'], reverse=True)
    
    if failed_files:
        logger.warning(f"Gagal memproses {len(failed_files)} file: {', '.join(failed_files)}")
    
    return {
        'data': sorted_results[:top_n],
        'execution_time_exact': exact_match_duration,
        'execution_time_fuzzy': fuzzy_match_duration,
        'total_scanned': total_scanned,
        'failed_files': failed_files
    }

# def get_applicant_summary(applicant_id: int, cv_path: str):
#     """
#     Mengambil profil dari DB dan mengekstrak info dari CV untuk halaman ringkasan.
#     Fungsi ini sekarang menerima cv_path secara langsung untuk memastikan konsistensi.
#     """
#     db_manager = _get_db_manager()
#     conn = db_manager.get_connection()
#     cursor = conn.cursor(buffered=True, dictionary=True)
    
#     # Query sekarang hanya untuk mengambil data profil, bukan path lagi
#     cursor.execute("SELECT * FROM ApplicantProfile WHERE applicant_id = %s", (applicant_id,))
#     profile_data = cursor.fetchone()

#     if not profile_data:
#         cursor.close()
#         return None

#     # Gunakan cv_path yang diberikan langsung, tidak lagi dari hasil query
#     cv_text_for_regex = extract_text_for_regex(cv_path)
#     if not cv_text_for_regex:
#         print(f"Gagal memproses file untuk regex: {cv_path}")

#     extracted_sections = extract_all_sections(cv_text_for_regex)

#     summary_data = {
#         'profile': profile_data,
#         'summary': extracted_sections.get('summary', 'Tidak ditemukan ringkasan.'),
#         'skills': extracted_sections.get('skills', 'Tidak ditemukan keahlian.'),
#         'experience': extracted_sections.get('experience', 'Tidak ditemukan pengalaman kerja.'),
#         'education': extracted_sections.get('education', 'Tidak ditemukan riwayat pendidikan.')
#     }
    
#     cursor.close()
#     return summary_data

def get_applicant_summary(applicant_id: int, cv_path: str):
    """
    Versi ini disesuaikan untuk bekerja dengan regex_extractor yang baru.
    """
    db_manager = _get_db_manager()
    conn = db_manager.get_connection()
    cursor = conn.cursor(buffered=True, dictionary=True)
    
    cursor.execute("SELECT * FROM ApplicantProfile WHERE applicant_id = %s", (applicant_id,))
    profile_data = cursor.fetchone()

    if not profile_data:
        cursor.close()
        return None

    cv_text_for_regex = extract_text_for_regex(cv_path)
    
    # Panggil fungsi ekstraksi utama SATU KALI saja
    extracted_sections = extract_all_sections(cv_text_for_regex)

    # Ambil hasilnya dari dictionary yang sudah jadi
    summary_data = {
        'profile': profile_data,
        'summary': extracted_sections.get('summary'),
        'skills': extracted_sections.get('skills'),
        'experience': extracted_sections.get('experience'),
        'education': extracted_sections.get('education')
    }
    
    cursor.close()
    return summary_data

def close_db_connection():
    """Menutup koneksi database saat aplikasi keluar."""
    db_manager = _get_db_manager()
    if db_manager:
        db_manager.close()
        print("Koneksi database berhasil ditutup.")