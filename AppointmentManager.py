from uuid import uuid4
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional


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
    booked_at: datetime = field(default_factory=datetime.now)


class AppointmentManager:
    def __init__(self):
        self.appointments: Dict[str, Appointment] = {}
        self.dentists = ["Dr. Smith", "Dr. Johnson", "Dr. Lee"]
        self.services = ["Cleaning", "Filling", "Tooth Extraction", "Check-up"]

    def reserve(self, patient: Patient, date: str, time: str, dentist: str) -> Optional[Appointment]:
        """Create new appointment unless duplicate"""
        for appt in self.appointments.values():
            if appt.patient.email == patient.email and appt.date == date and appt.time == time:
                return None  # duplicate
        appt_id = str(uuid4())[:8]
        appointment = Appointment(appt_id, patient, date, time, dentist)
        self.appointments[appt_id] = appointment
        return appointment

    def cancel(self, appt_id: str) -> bool:
        """Cancel by appointment ID"""
        return self.appointments.pop(appt_id, None) is not None

    def cancel_by_email(self, email: str) -> bool:
        """Cancel the first appointment found with this email"""
        for appt_id, appt in list(self.appointments.items()):
            if appt.patient.email == email:
                del self.appointments[appt_id]
                return True
        return False

    def all_appointments(self) -> List[Appointment]:
        """Return all appointments"""
        return list(self.appointments.values())

    def rebook(self, email: str, new_date: str, new_time: str, dentist: str) -> Optional[Appointment]:
        """Cancel old appointment by email and book a new one"""
        self.cancel_by_email(email)
        # Create dummy patient since cancel removed old one
        patient = Patient(name="Rebooked User", email=email)
        return self.reserve(patient, new_date, new_time, dentist)

def cancel_by_email(self, email: str) -> bool:
    """Cancel the first appointment found for a given email."""
    for appt_id, appt in list(self.appointments.items()):
        if appt.patient.email == email:
            del self.appointments[appt_id]
            return True
    return False