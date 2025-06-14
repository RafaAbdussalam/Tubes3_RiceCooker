import configparser
import traceback
from db.database_manager import DatabaseManager
from mysql.connector import Error

_db_manager_instance = None

def _get_db_manager():
    global _db_manager_instance
    if _db_manager_instance is None:
        try:
            config = configparser.ConfigParser()
            
            # program dijalankan di dir src 
            config_path = 'config.ini'
            read_files = config.read(config_path)
            
            if not read_files:
                raise FileNotFoundError(
                    f"FATAL: File '{config_path}' tidak ditemukan. "
                    f"Pastikan Anda menjalankan program dari dalam folder 'src' "
                    f"dan file 'config.ini' ada di dalam folder 'src' juga."
                )

            db_config = dict(config['database'])
            _db_manager_instance = DatabaseManager(db_config)
            
        except Exception as e:
            print(f"--- [ERROR KRITIS SAAT SETUP DATABASE] ---")
            # Mencetak error lengkap untuk diagnosis
            traceback.print_exc()
            return None
            
    return _db_manager_instance

def fetch_candidates():
    """Mengambil semua kandidat dari database."""
    db_manager = _get_db_manager()
    if not db_manager or not db_manager.get_connection():
        print("[ERROR] Gagal mendapatkan koneksi database saat fetch.")
        return []

    conn = db_manager.get_connection()
    cursor = conn.cursor(dictionary=True)
    candidates = []
    
    query = """
    SELECT 
        p.applicant_id as id, 
        CONCAT(p.first_name, ' ', p.last_name) as name, 
        d.cv_path
    FROM ApplicantProfile p
    JOIN ApplicationDetail d ON p.applicant_id = d.applicant_id
    """
    try:
        cursor.execute(query)
        candidates = cursor.fetchall()
    except Error as e:
        print(f"Error fetching candidates: {e}")
    finally:
        if cursor:
            cursor.close()
    return candidates

def save_candidate_profile(profile_data):
    """Menyimpan profil kandidat baru ke database."""
    db_manager = _get_db_manager()
    if not db_manager or not db_manager.get_connection():
        print("Cannot save profile, no database connection.")
        return None
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    name_parts = profile_data.get('name', '').split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    try:
        conn.start_transaction()
        sql_profile = "INSERT INTO ApplicantProfile (first_name, last_name, phone_number) VALUES (%s, %s, %s)"
        cursor.execute(sql_profile, (first_name, last_name, profile_data.get('phone')))
        applicant_id = cursor.lastrowid
        sql_detail = "INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) VALUES (%s, %s, %s)"
        cursor.execute(sql_detail, (applicant_id, 'General Applicant', profile_data.get('cv_path')))
        conn.commit()
        print(f"Successfully saved profile for {profile_data.get('name')} with ID {applicant_id}.")
        return applicant_id
    except Error as e:
        conn.rollback()
        print(f"Error saving profile: {e}")
        if e.errno == 1062: 
            print("This profile may already exist.")
        return None
    finally:
        if cursor:
            cursor.close()

def close_db_connection():
    """Menutup koneksi database saat aplikasi keluar."""
    db_manager = _get_db_manager()
    if db_manager:
        db_manager.close()