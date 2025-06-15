import mysql.connector
from mysql.connector import Error

class DatabaseManager:
    def __init__(self, config):
        # print("test0")
        self.config = config
        self.connection = None
        try:
            conn_init = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                use_pure = True
            )
            # print("test1")
            cursor_init = conn_init.cursor()
            cursor_init.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            cursor_init.close()
            conn_init.close()
            print(f"Database '{self.config['database']}' is ready.")

            self.connection = mysql.connector.connect(**self.config, use_pure=True)
            if self.connection.is_connected():
                self._create_tables()

        except Error as e:
            print(f"Error inisiasi database: {e}")
            self.connection = None

    def _create_tables(self):
        if not self.connection:
            return
        
        cursor = self.connection.cursor()
        try:
            # tabel applicant profile
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ApplicantProfile (
                applicant_id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(50) DEFAULT NULL,
                last_name VARCHAR(50) DEFAULT NULL,
                date_of_birth DATE DEFAULT NULL,
                address VARCHAR(255) DEFAULT NULL,
                phone_number VARCHAR(20) DEFAULT NULL
            )
            """)

            # tabel application detail
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ApplicationDetail (
                detail_id INT AUTO_INCREMENT PRIMARY KEY,
                applicant_id INT NOT NULL,
                application_role VARCHAR(100) DEFAULT NULL,
                cv_path TEXT,
                FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) ON DELETE CASCADE
            )
            """)
            self.connection.commit()
            print("Tabel berhasil dibuat.")
        except Error as e:
            print(f"Error membuat tabel: {e}")
        finally:
            cursor.close()

    def get_connection(self):
        if not self.connection or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(**self.config, use_pure=True)
            except Error as e:
                print(f"Gagal connect ke database: {e}")
                return None
        return self.connection

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database closed.")