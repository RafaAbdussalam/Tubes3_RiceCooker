import configparser
from db.database_manager import DatabaseManager
from mysql.connector import Error

_db_manager_instance = None

def getDB_manager():
    global _db_manager_instance
    if _db_manager_instance is None:
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            db_config = dict(config['database'])
            _db_manager_instance = DatabaseManager(db_config)
        except Exception as e:
            print(f"Failed to read config or initialize DB Manager: {e}")
            return None
    return _db_manager_instance

def fetch_candidates():
    db_manager = getDB_manager()
    if not db_manager or not db_manager.get_connection():
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
        cursor.close()
        
    return candidates

def save_candidate_profile(profile_data):
    db_manager = getDB_manager()
    if not db_manager or not db_manager.get_connection():
        print("Cannot save profile, no database connection.")
        return None

    conn = db_manager.get_connection()
    cursor = conn.cursor()

    # split nama jadi dua komponen
    name_parts = profile_data.get('name', '').split(' ', 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ''
    
    try:
        conn.start_transaction()

        # insert data ke tabel aplicant profile
        sql_profile = """
        INSERT INTO ApplicantProfile (first_name, last_name, phone_number) 
        VALUES (%s, %s, %s)
        """
        cursor.execute(sql_profile, (first_name, last_name, profile_data.get('phone')))
        applicant_id = cursor.lastrowid

        # insert ke tabel aplicant detail
        sql_detail = """
        INSERT INTO ApplicationDetail (applicant_id, application_role, cv_path) 
        VALUES (%s, %s, %s)
        """
        # Using a default role as it's not specified in the UI
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
        cursor.close()

def close_db_connection():
    """Closes the main database connection when the app exits."""
    db_manager = getDB_manager()
    if db_manager:
        db_manager.close()