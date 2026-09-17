from database.db_manager import DatabaseManager
from datetime import datetime, date
import os
from collections import defaultdict

class DoctorModel:
    def __init__(self):
        self.db = DatabaseManager()

    def register_doctor(self, clinic_name, doctor_name, specialization, email, phone, username, password):
        if not self.db.connect():
            return False, "Database connection failed"

        try:
            # Check if username already exists
            existing = self.db.fetch_one("SELECT id FROM doctors WHERE username = %s", (username,))
            if existing:
                return False, "Username already exists"

            # Hash password
            password_hash = self.db.hash_password(password)

            # Insert doctor
            query = '''INSERT INTO doctors (clinic_name, doctor_name, specialization, email, phone, username, password_hash)
                      VALUES (%s, %s, %s, %s, %s, %s, %s)'''

            cursor = self.db.execute_query(query, (clinic_name, doctor_name, specialization, email, phone, username, password_hash))

            if cursor:
                return True, "Doctor registered successfully"
            else:
                return False, "Registration failed"

        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.db.disconnect()

    def authenticate_doctor(self, username, password):
        if not self.db.connect():
            return False, None

        try:
            doctor = self.db.fetch_one("SELECT * FROM doctors WHERE username = %s", (username,))

            if doctor and self.db.verify_password(password, doctor['password_hash']):
                return True, doctor
            else:
                return False, None

        except Exception as e:
            print(f"Authentication error: {e}")
            return False, None
        finally:
            self.db.disconnect()

    def get_doctor_info(self):
        if not self.db.connect():
            return None

        try:
            return self.db.fetch_one("SELECT * FROM doctors LIMIT 1")
        except Exception as e:
            print(f"Error getting doctor info: {e}")
            return None
        finally:
            self.db.disconnect()

class PatientModel:
    def __init__(self):
        self.db = DatabaseManager()

    def add_patient(self, name, gender, dob, address, phone, email, medical_history, allergies, photo_path=None):
        if not self.db.connect():
            return False, "Database connection failed"

        try:
            # Calculate age
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

            # Generate patient ID
            patient_id = self.db.generate_id("PAT", "patients", "patient_id")


            query = '''INSERT INTO patients (patient_id, name, gender, dob, age, address, phone, email, medical_history, allergies, photo_path)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

            cursor = self.db.execute_query(query, (patient_id, name, gender, dob, age, address, phone, email, medical_history, allergies, photo_path))

            if cursor:
                return True, patient_id
            else:
                return False, "Failed to add patient"

        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.db.disconnect()

    def get_all_patients(self):
        if not self.db.connect():
            return []

        try:
            return self.db.fetch_all("SELECT * FROM patients ORDER BY created_at DESC")
        except Exception as e:
            print(f"Error getting patients: {e}")
            return []
        finally:
            self.db.disconnect()

    def search_patients(self, search_term):
        if not self.db.connect():
            return []

        try:
            query = '''SELECT * FROM patients 
                      WHERE name LIKE %s OR patient_id LIKE %s OR phone LIKE %s 
                      ORDER BY created_at DESC'''
            term = f"%{search_term}%"
            return self.db.fetch_all(query, (term, term, term))
        except Exception as e:
            print(f"Error searching patients: {e}")
            return []
        finally:
            self.db.disconnect()

    def get_patient_by_id(self, patient_id):
        if not self.db.connect():
            return None

        try:
            return self.db.fetch_one("SELECT * FROM patients WHERE patient_id = %s", (patient_id,))
        except Exception as e:
            print(f"Error getting patient: {e}")
            return None
        finally:
            self.db.disconnect()

    def update_patient(self, patient_id, name, gender, dob, address, phone, email, medical_history, allergies, photo_path=None):
        if not self.db.connect():
            return False, "Database connection failed"

        try:
            # Calculate age
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

            query = '''UPDATE patients SET name=%s, gender=%s, dob=%s, age=%s, address=%s, phone=%s, email=%s, 
                      medical_history=%s, allergies=%s, photo_path=%s WHERE patient_id=%s'''

            cursor = self.db.execute_query(query, (name, gender, dob, age, address, phone, email, medical_history, allergies, photo_path, patient_id))

            if cursor:
                return True, "Patient updated successfully"
            else:
                return False, "Failed to update patient"

        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.db.disconnect()

    def delete_patient(self, patient_id):
        if not self.db.connect():
            return False, "Database connection failed"
        try:
            # Delete patient record by patient_id
            query = "DELETE FROM patients WHERE patient_id = %s"
            cursor = self.db.execute_query(query, (patient_id,))
            if cursor:
                return True, "Patient deleted successfully"
            else:
                return False, "Failed to delete patient"
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.db.disconnect()

    def get_patient_counts_grouped_by_date(self, start_date, end_date):
        if not self.db.connect():
            return {}

        try:
            query = """
                SELECT DATE(created_at) AS reg_date, COUNT(*) AS count
                FROM patients
                WHERE DATE(created_at) BETWEEN %s AND %s
                GROUP BY reg_date
                ORDER BY reg_date
            """
            rows = self.db.fetch_all(query, (start_date, end_date))
            return {row['reg_date']: row['count'] for row in rows}
        except Exception as e:
            print(f"Error fetching patient counts: {e}")
            return {}
        finally:
            self.db.disconnect()


class AppointmentModel:
    def __init__(self):
        self.db = DatabaseManager()

    def book_appointment(self, patient_id, appointment_date, appointment_time, notes=""):
        if not self.db.connect():
            return False, "Database connection failed"

        try:
            query = '''INSERT INTO appointments (patient_id, appointment_date, appointment_time, notes)
                      VALUES (%s, %s, %s, %s)'''

            cursor = self.db.execute_query(query, (patient_id, appointment_date, appointment_time, notes))

            if cursor:
                return True, "Appointment booked successfully"
            else:
                return False, "Failed to book appointment"

        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.db.disconnect()

    def get_appointments_by_date(self, appointment_date):
        if not self.db.connect():
            return []

        try:
            query = '''SELECT a.*, p.name as patient_name FROM appointments a
                      JOIN patients p ON a.patient_id = p.patient_id
                      WHERE a.appointment_date = %s
                      ORDER BY a.appointment_time'''

            return self.db.fetch_all(query, (appointment_date,))
        except Exception as e:
            print(f"Error getting appointments: {e}")
            return []
        finally:
            self.db.disconnect()

    def get_today_appointments(self):
        today = date.today()
        return self.get_appointments_by_date(today)

    def update_appointment_status(self, appointment_id, status):
        if not self.db.connect():
            return False

        try:
            cursor = self.db.execute_query("UPDATE appointments SET status = %s WHERE id = %s", (status, appointment_id))
            return cursor is not None
        except Exception as e:
            print(f"Error updating appointment: {e}")
            return False
        finally:
            self.db.disconnect()

    def get_appointments_by_date_range(self, start_date, end_date):
        if not self.db.connect():
            return []
        try:
            query = """
                SELECT a.*, p.name AS patient_name, d.doctor_name AS doctor_name
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.patient_id
                LEFT JOIN doctors d ON a.id = d.id
                WHERE a.appointment_date BETWEEN %s AND %s
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
            """
            return self.db.fetch_all(query, (start_date, end_date))
        except Exception as e:
            print(f"Error fetching appointments by date range: {e}")
            return []
        finally:
            self.db.disconnect()

    def get_appointment_stats(self, start_date, end_date):
        """
        Returns:
            appointments_per_day: dict {date: count}
            status_counts: dict {Scheduled/Completed/Cancelled: count}
        """
        if not self.db.connect():
            return {}, {}

        try:
            query = """
                SELECT appointment_date, status
                FROM appointments
                WHERE appointment_date BETWEEN %s AND %s
            """
            rows = self.db.fetch_all(query, (start_date, end_date))

            appointments_per_day = defaultdict(int)
            status_counts = {"Scheduled": 0, "Completed": 0, "Cancelled": 0}

            for row in rows:
                apt_date = row['appointment_date']
                status = row['status']

                appointments_per_day[apt_date] += 1
                if status in status_counts:
                    status_counts[status] += 1

            return dict(appointments_per_day), status_counts

        except Exception as e:
            print(f"Error fetching appointment stats: {e}")
            return {}, {}
        finally:
            self.db.disconnect()


class MedicineModel:
    def __init__(self):
        self.db = DatabaseManager()

    def add_medicine(self, name, category, manufacturer, batch_no, expiry_date, stock_quantity, price):
        if not self.db.connect():
            return False, "Database connection failed"

        try:
            medicine_id = self.db.generate_id("MED", "medicines", "medicine_id")

            query = '''INSERT INTO medicines (medicine_id, name, category, manufacturer, batch_no, expiry_date, stock_quantity, price)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''

            cursor = self.db.execute_query(query, (medicine_id, name, category, manufacturer, batch_no, expiry_date, stock_quantity, price))

            if cursor:
                return True, medicine_id
            else:
                return False, "Failed to add medicine"

        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.db.disconnect()

    def get_all_medicines(self):
        if not self.db.connect():
            return []

        try:
            return self.db.fetch_all("SELECT * FROM medicines ORDER BY name")
        except Exception as e:
            print(f"Error getting medicines: {e}")
            return []
        finally:
            self.db.disconnect()

    def get_low_stock_medicines(self, threshold=10):
        if not self.db.connect():
            return []

        try:
            return self.db.fetch_all("SELECT * FROM medicines WHERE stock_quantity <= %s ORDER BY stock_quantity", (threshold,))
        except Exception as e:
            print(f"Error getting low stock medicines: {e}")
            return []
        finally:
            self.db.disconnect()

    def update_stock(self, medicine_id, new_quantity):
        if not self.db.connect():
            return False

        try:
            cursor = self.db.execute_query("UPDATE medicines SET stock_quantity = %s WHERE medicine_id = %s", (new_quantity, medicine_id))
            return cursor is not None
        except Exception as e:
            print(f"Error updating stock: {e}")
            return False
        finally:
            self.db.disconnect()

    def update_medicine(self, medicine_id, name, category, manufacturer, batch_no, expiry_date, stock_quantity, price):
        if not self.db.connect():
            return False, "Database connection failed"
        try:
            query = '''
                UPDATE medicines
                SET name=%s, category=%s, manufacturer=%s, batch_no=%s, expiry_date=%s,
                    stock_quantity=%s, price=%s
                WHERE medicine_id=%s
            '''
            cursor = self.db.execute_query(query, (
                name, category, manufacturer, batch_no, expiry_date,
                stock_quantity, price, medicine_id
            ))
            if cursor:
                return True, "Medicine updated successfully"
            else:
                return False, "Failed to update medicine"
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.db.disconnect()

    def get_medicine_id_by_name(self, medicine_name):
        if not self.db.connect():
            return None

        try:
            query = "SELECT medicine_id FROM medicines WHERE name = %s"
            row = self.db.fetch_one(query, (medicine_name,))
            if row:
                # If row is dict, use row['medicine_id'], else row[0]
                return row.get('medicine_id') if isinstance(row, dict) else row[0]
            return None
        except Exception as e:
            print(f"Error getting medicine id by name: {e}")
            return None
        finally:
            self.db.disconnect()



    def get_expiry_medicines(self, days=30):
        if not self.db.connect():
            return []
        try:
            query = """
            SELECT * FROM medicines
            WHERE expiry_date <= DATE_ADD(CURDATE(), INTERVAL %s DAY)
            ORDER BY expiry_date
            """
            cursor = self.db.execute_query(query, (days,))
            if cursor:
                return cursor.fetchall()
            else:
                return []
        except Exception as e:
            print("Error getting expiry medicines", e)
            return []
        finally:
            self.db.disconnect()


class PrescriptionModel:
    def __init__(self):
        self.db = DatabaseManager()

    def create_prescription(self, patient_id, diagnosis, prescription_items):
        if not self.db.connect():
            return False, "Database connection failed"

        try:
            prescription_id = self.db.generate_id("PRE", "prescriptions", "prescription_id")

            # Insert prescription
            query = '''INSERT INTO prescriptions (prescription_id, patient_id, prescription_date, diagnosis)
                      VALUES (%s, %s, %s, %s)'''

            cursor = self.db.execute_query(query, (prescription_id, patient_id, date.today(), diagnosis))

            if not cursor:
                return False, "Failed to create prescription"

            # Insert prescription items
            for item in prescription_items:
                item_query = '''INSERT INTO prescription_items (prescription_id, medicine_name, dosage, duration, remarks)
                               VALUES (%s, %s, %s, %s, %s)'''
                self.db.execute_query(item_query, (prescription_id, item['medicine'], item['dosage'], item['duration'], item['remarks']))

            return True, prescription_id

        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.db.disconnect()

    def get_prescription_by_id(self, prescription_id):
        if not self.db.connect():
            return None, []

        try:
            # Get prescription details
            prescription = self.db.fetch_one("SELECT * FROM prescriptions WHERE prescription_id = %s", (prescription_id,))

            # Get prescription items
            items = self.db.fetch_all("SELECT * FROM prescription_items WHERE prescription_id = %s", (prescription_id,))

            return prescription, items
        except Exception as e:
            print(f"Error getting prescription: {e}")
            return None, []
        finally:
            self.db.disconnect()

    def get_all_prescriptions(self):
        if not self.db.connect():
            return []
        try:
            rows = self.db.fetch_all("""
                SELECT p.prescription_id, p.diagnosis, p.prescription_date, pt.name AS patient_name
                FROM prescriptions p
                JOIN patients pt ON p.patient_id = pt.patient_id
                ORDER BY p.prescription_date DESC
            """)
            return rows
        except Exception as e:
            print("Error:", e)
            return []
        finally:
            self.db.disconnect()

    def search_prescriptions(self, keyword):
        if not self.db.connect():
            return []
        try:
            like_query = f"%{keyword}%"
            query = """
                SELECT p.prescription_id, p.diagnosis, p.prescription_date, pt.name AS patient_name
                FROM prescriptions p
                JOIN patients pt ON p.patient_id = pt.patient_id
                WHERE pt.name LIKE %s OR p.diagnosis LIKE %s
                ORDER BY p.prescription_date DESC
            """
            return self.db.fetch_all(query, (like_query, like_query))
        except Exception as e:
            print("Error searching:", e)
            return []
        finally:
            self.db.disconnect()

    def update_prescription(self, prescription_id, patient_id, diagnosis):
        if not self.db.connect():
            return False, "Database connection failed"
        try:
            update_query = '''
                UPDATE prescriptions
                SET patient_id=%s,
                    diagnosis=%s,
                    prescription_date=CURDATE()
                WHERE prescription_id=%s
            '''
            cursor = self.db.execute_query(update_query, (patient_id, diagnosis, prescription_id))
            if cursor:
                return True, "Prescription updated successfully"
            else:
                return False, "Failed to update prescription"
        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.db.disconnect()

    def delete_prescription_items(self, prescription_id):
        if not self.db.connect():
            return False
        try:
            delete_items_query = 'DELETE FROM prescription_items WHERE prescription_id = %s'
            cursor = self.db.execute_query(delete_items_query, (prescription_id,))
            return cursor is not None
        except Exception as e:
            print(f"Error deleting prescription items: {e}")
            return False
        # ❌ remove self.db.disconnect() here

    def add_prescription_item(self, prescription_id, medicine_name, dosage, duration, remarks):
        if not self.db.connect():
            return False
        try:
            insert_item_query = '''
                INSERT INTO prescription_items (prescription_id, medicine_name, dosage, duration, remarks)
                VALUES (%s, %s, %s, %s, %s)
            '''
            cursor = self.db.execute_query(insert_item_query,
                                           (prescription_id, medicine_name, dosage, duration, remarks))
            return cursor is not None
        except Exception as e:
            print(f"Error adding prescription item: {e}")
            return False
        finally:
            self.db.disconnect()

    def delete_prescription(self, prescription_id):
        if not self.db.connect():
            return False
        try:
            # Delete items first for referential integrity
            self.delete_prescription_items(prescription_id)
            query = "DELETE FROM prescriptions WHERE prescription_id = %s"
            cursor = self.db.execute_query(query, (prescription_id,))
            return cursor is not None
        except Exception as e:
            print(f"Error deleting prescription: {e}")
            return False
        finally:
            self.db.disconnect()


class BillModel:
    def __init__(self):
        self.db = DatabaseManager()

    def create_bill(self, patient_id, consultation_fee, medicine_charges, lab_charges, other_charges, discount, tax_rate, payment_method):
        if not self.db.connect():
            return False, "Database connection failed"

        try:
            bill_id = self.db.generate_id("BILL", "bills", "bill_id")

            # Calculate totals
            subtotal = consultation_fee + medicine_charges + lab_charges + other_charges - discount
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal + tax_amount

            query = '''INSERT INTO bills (bill_id, patient_id, consultation_fee, medicine_charges, lab_charges, 
                      other_charges, discount, tax_amount,tax_rate, total_amount,payment_method, bill_date)
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

            cursor = self.db.execute_query(query, (bill_id, patient_id, consultation_fee, medicine_charges, 
                                                 lab_charges, other_charges, discount, tax_amount,tax_rate, total_amount,payment_method, date.today()))

            if cursor:
                return True, bill_id
            else:
                return False, "Failed to create bill"

        except Exception as e:
            return False, f"Error: {str(e)}"
        finally:
            self.db.disconnect()

    def get_revenue_summary(self, start_date, end_date):
        if not self.db.connect():
            return None

        try:
            query = '''SELECT 
                        COUNT(*) as total_bills,
                        SUM(total_amount) as total_revenue,
                        SUM(consultation_fee) as consultation_revenue,
                        SUM(medicine_charges) as medicine_revenue
                      FROM bills 
                      WHERE bill_date BETWEEN %s AND %s '''

            return self.db.fetch_one(query, (start_date, end_date))
        except Exception as e:
            print(f"Error getting revenue summary: {e}")
            return None
        finally:
            self.db.disconnect()

    def get_revenue_over_time(self, start_date, end_date):
        if not self.db.connect():
            return []

        try:
            query = '''SELECT 
                        bill_date,
                        SUM(total_amount) as total_revenue
                       FROM bills
                       WHERE bill_date BETWEEN %s AND %s
                       GROUP BY bill_date
                       ORDER BY bill_date'''
            return self.db.fetch_all(query, (start_date, end_date))
        except Exception as e:
            print(f"Error getting revenue over time: {e}")
            return []
        finally:
            self.db.disconnect()

    def get_bills(self, search=None, start_date=None, end_date=None):
        if not self.db.connect():
            return []

        try:
            query = """
                SELECT b.bill_id, p.name AS patient_name, b.bill_date, b.total_amount,
                       b.payment_method
                FROM bills b
                JOIN patients p ON b.patient_id = p.patient_id
                WHERE 1=1
            """
            params = []
            if search:
                query += " AND (p.name LIKE %s OR b.bill_id LIKE %s)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term])
            if start_date:
                query += " AND b.bill_date >= %s"
                params.append(start_date)
            if end_date:
                query += " AND b.bill_date <= %s"
                params.append(end_date)

            query += " ORDER BY b.bill_date DESC"
            return self.db.fetch_all(query, tuple(params))

        except Exception as e:
            print(f"Error fetching bills: {e}")
            return []
        finally:
            self.db.disconnect()

    def get_bill_by_id(self, bill_id):
        if not self.db.connect():
            return None

        try:
            query = """SELECT b.*, p.name as patient_name 
                       FROM bills b
                       JOIN patients p ON b.patient_id = p.patient_id
                       WHERE b.bill_id = %s"""
            return self.db.fetch_one(query, (bill_id,))
        except Exception as e:
            print(f"Error fetching bill by id: {e}")
            return None
        finally:
            self.db.disconnect()

    def update_bill(self, bill_id, patient_id, consultation_fee, medicine_charges,
                    lab_charges, other_charges, discount, tax_rate, payment_method):
        if not self.db.connect():
            return False
        try:
            subtotal = consultation_fee + medicine_charges + lab_charges + other_charges - discount
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal + tax_amount
            query = '''
                UPDATE bills SET patient_id=%s, consultation_fee=%s, medicine_charges=%s,
                lab_charges=%s, other_charges=%s, discount=%s, tax_amount=%s, tax_rate=%s,
                total_amount=%s, payment_method=%s WHERE bill_id=%s
            '''
            self.db.execute_query(query, (patient_id, consultation_fee, medicine_charges, lab_charges,
                                          other_charges, discount, tax_amount, tax_rate, total_amount,
                                          payment_method, bill_id))
            return True, "Bill updated"
        except Exception as e:
            print(f"Error updating bill: {e}")
            return False
        finally:
            self.db.disconnect()



