import pymysql
import bcrypt
from datetime import datetime
from config import DATABASE_CONFIG

class DatabaseManager:
    def __init__(self):
        self.config = DATABASE_CONFIG
        self.connection = None

    def connect(self):
        try:
            self.connection = pymysql.connect(**self.config)
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor
        except Exception as e:
            print(f"Query execution error: {e}")
            self.connection.rollback()
            return None

    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        return cursor.fetchone() if cursor else None

    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params)
        return cursor.fetchall() if cursor else []

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def verify_password(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf-8'), hashed)

    def create_database(self):
        try:
            # Connect without database
            temp_config = self.config.copy()
            del temp_config['database']
            temp_connection = pymysql.connect(**temp_config)
            cursor = temp_connection.cursor()

            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
            temp_connection.commit()
            temp_connection.close()

            # Connect to the new database
            self.connect()
            self.create_tables()
            return True
        except Exception as e:
            print(f"Database creation error: {e}")
            return False

    def create_tables(self):
        tables = [
            # Doctor table
            '''CREATE TABLE IF NOT EXISTS doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                clinic_name VARCHAR(200) NOT NULL,
                doctor_name VARCHAR(100) NOT NULL,
                specialization VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                phone VARCHAR(15),
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash BINARY(60) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',

            # Patients table
            '''CREATE TABLE IF NOT EXISTS patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                gender ENUM('Male', 'Female', 'Other') NOT NULL,
                dob DATE NOT NULL,
                age INT NOT NULL,
                address TEXT,
                phone VARCHAR(15),
                email VARCHAR(100),
                medical_history TEXT,
                allergies TEXT,
                photo_path VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )''',

            # Appointments table
            '''CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id VARCHAR(20) NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
            )''',

            # Medicines table
            '''CREATE TABLE IF NOT EXISTS medicines (
                id INT AUTO_INCREMENT PRIMARY KEY,
                medicine_id VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50),
                manufacturer VARCHAR(100),
                batch_no VARCHAR(50),
                expiry_date DATE,
                stock_quantity INT DEFAULT 0,
                price DECIMAL(10,2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )''',

            # Prescriptions table
            '''CREATE TABLE IF NOT EXISTS prescriptions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                prescription_id VARCHAR(20) UNIQUE NOT NULL,
                patient_id VARCHAR(20) NOT NULL,
                appointment_id INT,
                prescription_date DATE NOT NULL,
                diagnosis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL
            )''',

            # Prescription items table
            '''CREATE TABLE IF NOT EXISTS prescription_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                prescription_id VARCHAR(20) NOT NULL,
                medicine_name VARCHAR(100) NOT NULL,
                dosage VARCHAR(100) NOT NULL,
                duration VARCHAR(50) NOT NULL,
                remarks TEXT,
                FOREIGN KEY (prescription_id) REFERENCES prescriptions(prescription_id) ON DELETE CASCADE
            )''',

            # Bills table
            '''CREATE TABLE IF NOT EXISTS bills (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bill_id VARCHAR(20) UNIQUE NOT NULL,
                patient_id VARCHAR(20) NOT NULL,
                appointment_id INT,
                consultation_fee DECIMAL(10,2) DEFAULT 0.00,
                medicine_charges DECIMAL(10,2) DEFAULT 0.00,
                lab_charges DECIMAL(10,2) DEFAULT 0.00,
                other_charges DECIMAL(10,2) DEFAULT 0.00,
                discount DECIMAL(10,2) DEFAULT 0.00,
                tax_amount DECIMAL(10,2) DEFAULT 0.00,
                tax_rate DECIMAL(5,2) DEFAULT 18.00,
                total_amount DECIMAL(10,2) NOT NULL,
                payment_method VARCHAR(50),
                bill_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL
            )'''
        ]

        for table_sql in tables:
            self.execute_query(table_sql)

        print("✓ All tables created successfully")

    def generate_id(self, prefix, table, column):
        # Get the last ID
        query = f"SELECT MAX(CAST(SUBSTRING({column}, {len(prefix)+1}) AS UNSIGNED)) as max_id FROM {table} WHERE {column} LIKE '{prefix}%%'"
        result = self.fetch_one(query)

        if result and result['max_id']:
            next_id = result['max_id'] + 1
        else:
            next_id = 1

        return f"{prefix}{next_id:04d}"
