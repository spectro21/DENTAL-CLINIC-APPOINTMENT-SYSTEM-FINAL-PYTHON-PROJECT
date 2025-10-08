# -------------------------
# Data models
# -------------------------
from uuid import uuid4
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from database_manager import DatabaseManager, create_database


@dataclass
class Patient:
    name: str
    email: str


@dataclass
class Appointment:
    id: str
    patient: Patient
    date: str
    time: str
    dentist: str
    status: str = "Pending"
    booked_at: datetime = field(default_factory=datetime.now)


# -------------------------
# Manager class
# -------------------------
class AppointmentManager:
    def __init__(self):
        self.appointments: Dict[str, Appointment] = {}
        self.db = DatabaseManager()
        # UNCOMMENT ONLY ON FIRST RUN TO CREATE DATABASE:
        # create_database()

        self.dentists = [
            "Dr. Jhunsoy Love Jun",
            "Dr. Jograd Ballesteros",
            "Dr. Beyoncé Calubaquib",
            "Dr. Estanislao Manansala",
            "Dr. Federico Liwanag VII",
            "Dr. Vergamino Antiporda",
            "Dr. Princess Payapa Pamplona"
        ]

        # Admin credentials
        self.admin_username = "admin"
        self.admin_password = "admin123"

        # Available time slots
        self.time_slots = [
            "08:00 AM", "08:30 AM", "09:00 AM", "09:30 AM",
            "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
            "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM",
            "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM",
            "05:00 PM", "05:30 PM"
        ]

    def verify_admin(self, username: str, password: str) -> bool:
        """Verify admin credentials"""
        return username == self.admin_username and password == self.admin_password

    def reserve(self, patient: Patient, date: str, time: str, dentist: str, reason: str = "") -> Optional[Appointment]:
        """Reserve appointment - checks database and saves to DB"""
        # Check database for availability
        if not self.db.check_slot_available(dentist, date, time):
            return None

        # Get or create patient in database
        patient_result = self.db.get_patient_by_email(patient.email)
        if patient_result:
            patient_id = patient_result[0]
        else:
            self.db.add_patient(patient.name, patient.email, "N/A")
            patient_result = self.db.get_patient_by_email(patient.email)
            patient_id = patient_result[0]

        # Create appointment
        appt_id = str(uuid4())[:8]
        appointment = Appointment(appt_id, patient, date, time, dentist, "Pending")

        # Save to database
        self.db.add_appointment(patient_id, appt_id, date, time, dentist, reason)

        # Keep in-memory copy too
        self.appointments[appt_id] = appointment
        return appointment

    def is_time_slot_available(self, dentist: str, date: str, time: str) -> bool:
        """Check if a time slot is available for a specific dentist and date"""
        return self.db.check_slot_available(dentist, date, time)

    def get_available_slots(self, dentist: str, date: str) -> List[str]:
        """Get all available time slots for a dentist on a specific date"""
        available = []
        for time_slot in self.time_slots:
            if self.is_time_slot_available(dentist, date, time_slot):
                available.append(time_slot)
        return available

    def cancel(self, appt_id: str) -> bool:
        """Cancel appointment by ID"""
        if appt_id in self.appointments:
            del self.appointments[appt_id]
            return self.db.delete_appointment_by_uuid(appt_id)
        return False

    def cancel_by_email(self, email: str) -> bool:
        """Cancel appointment by patient email"""
        if self.db.delete_appointment_by_email(email):
            for appt_id, appt in list(self.appointments.items()):
                if appt.patient.email == email:
                    del self.appointments[appt_id]
            return True
        return False

    def confirm_appointment(self, appt_id: str) -> bool:
        """Confirm an appointment"""
        if appt_id in self.appointments:
            self.appointments[appt_id].status = "Confirmed"
            self.db.update_appointment_status(appt_id, "Confirmed")
            return True
        return False

    def decline_appointment(self, appt_id: str) -> bool:
        """Decline an appointment"""
        if appt_id in self.appointments:
            self.appointments[appt_id].status = "Declined"
            self.db.update_appointment_status(appt_id, "Declined")
            return True
        return False

    def all_appointments(self) -> List[Appointment]:
        """Retrieve all appointments from database"""
        results = self.db.get_all_appointments()
        appointments = []
        for row in results:
            appt_id, name, email, date, time, dentist, status, reason = row
            patient = Patient(name, email)
            appt = Appointment(appt_id, patient, date, time, dentist, status)
            appointments.append(appt)
        return appointments

    def rebook(self, email: str, new_date: str, new_time: str, dentist: str, reason: str = "") -> Optional[Appointment]:
        """Cancel old appointment by email and book a new one"""
        # Get old patient info before canceling
        patient_result = self.db.get_patient_by_email(email)
        if not patient_result:
            return None

        name = patient_result[1]

        # Cancel old appointment
        self.cancel_by_email(email)

        # Create new appointment with same patient info
        patient = Patient(name=name, email=email)
        return self.reserve(patient, new_date, new_time, dentist, reason)