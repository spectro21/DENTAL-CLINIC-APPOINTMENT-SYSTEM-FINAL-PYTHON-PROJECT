# ===================== USER CLASS =====================
class User:
    def __init__(self, name, contact, doctor, service, date):
        self.name = name
        self.contact = contact
        self.doctor = doctor
        self.service = service
        self.date = date

    def to_dict(self):
        return {
            "name": self.name,
            "contact": self.contact,
            "doctor": self.doctor,
            "service": self.service,
            "date": self.date
        }