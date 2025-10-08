import mysql.connector
from mysql.connector import Error


def create_database():
    """Create database and tables - Run this once"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )

        cursor = connection.cursor()

        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS dental_clinic")
        cursor.execute("USE dental_clinic")

        # Create patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                gender VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create appointments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INT AUTO_INCREMENT PRIMARY KEY,
                appointment_uuid VARCHAR(10) UNIQUE NOT NULL,
                patient_id INT NOT NULL,
                appointment_date VARCHAR(20) NOT NULL,
                appointment_time VARCHAR(20) NOT NULL,
                dentist VARCHAR(100) NOT NULL,
                status VARCHAR(20) DEFAULT 'Pending',
                reason_for_visit TEXT,
                booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
                INDEX idx_date_dentist (appointment_date, dentist),
                INDEX idx_patient (patient_id)
            )
        """)

        connection.commit()
        print("✓ Database and tables created successfully!")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


class DatabaseManager:
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "dental_clinic"

    def get_connection(self):
        """Get database connection"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return connection
        except Error as e:
            print(f"Connection Error: {e}")
            return None

    def add_patient(self, name, email, gender):
        """Add new patient to database"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            insert_query = "INSERT INTO patients (name, email, gender) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (name, email, gender))
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding patient: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_patient_by_email(self, email):
        """Get patient ID from email"""
        connection = self.get_connection()
        if not connection:
            return None

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT patient_id, name FROM patients WHERE email = %s", (email,))
            result = cursor.fetchone()
            return result
        except Error as e:
            print(f"Error fetching patient: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def add_appointment(self, patient_id, appointment_uuid, date, time, dentist, reason):
        """Add new appointment to database"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            insert_query = """
                INSERT INTO appointments 
                (patient_id, appointment_uuid, appointment_date, appointment_time, dentist, status, reason_for_visit)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query,
                           (patient_id, appointment_uuid, date, time, dentist, "Pending", reason))
            connection.commit()
            return True
        except Error as e:
            print(f"Error adding appointment: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_all_appointments(self):
        """Retrieve all appointments"""
        connection = self.get_connection()
        if not connection:
            return []

        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT a.appointment_uuid, p.name, p.email, a.appointment_date, 
                       a.appointment_time, a.dentist, a.status, a.reason_for_visit
                FROM appointments a
                JOIN patients p ON a.patient_id = p.patient_id
                ORDER BY a.appointment_date DESC
            """)
            results = cursor.fetchall()
            return results
        except Error as e:
            print(f"Error fetching appointments: {e}")
            return []
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def check_slot_available(self, dentist, date, time):
        """Check if time slot is available"""
        connection = self.get_connection()
        if not connection:
            return True

        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM appointments 
                WHERE dentist = %s AND appointment_date = %s 
                AND appointment_time = %s AND status IN ('Pending', 'Confirmed')
            """, (dentist, date, time))
            result = cursor.fetchone()
            return result[0] == 0
        except Error as e:
            print(f"Error checking slot: {e}")
            return True
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def update_appointment_status(self, appointment_uuid, status):
        """Update appointment status"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE appointments SET status = %s 
                WHERE appointment_uuid = %s
            """, (status, appointment_uuid))
            connection.commit()
            return True
        except Error as e:
            print(f"Error updating status: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def delete_appointment_by_email(self, email):
        """Delete patient's appointment by email"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT patient_id FROM patients WHERE email = %s", (email,))
            result = cursor.fetchone()

            if not result:
                return False

            patient_id = result[0]
            cursor.execute("""
                DELETE FROM appointments WHERE patient_id = %s
            """, (patient_id,))
            connection.commit()
            return True
        except Error as e:
            print(f"Error deleting appointment: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def delete_appointment_by_uuid(self, appointment_uuid):
        """Delete specific appointment by UUID"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            cursor.execute("""
                DELETE FROM appointments WHERE appointment_uuid = %s
            """, (appointment_uuid,))
            connection.commit()
            return True
        except Error as e:
            print(f"Error deleting appointment: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()