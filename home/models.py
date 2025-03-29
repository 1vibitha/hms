from django.db import models
import json
# Create your models here.
# models.py

from django.db import models
from django.contrib.auth.models import User

# List of departments
departments = [
    ('Cardiologist', 'Cardiologist'),
    ('Dermatologists', 'Dermatologists'),
    ('Emergency Medicine Specialists', 'Emergency Medicine Specialists'),
    ('Allergists/Immunologists', 'Allergists/Immunologists'),
    ('Anesthesiologists', 'Anesthesiologists'),
    ('Colon and Rectal Surgeons', 'Colon and Rectal Surgeons'),
]

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/DoctorProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    department = models.CharField(max_length=50, choices=departments, default='Cardiologist')
    experience = models.IntegerField(default=0, help_text="Years of experience")
    status = models.BooleanField(default=False)

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return "{} ({})".format(self.user.first_name, self.department)


# TIME_SLOTS = [
#     ('09:00 AM - 10:00 AM', '09:00 AM - 10:00 AM'),
#     ('10:00 AM - 11:00 AM', '10:00 AM - 11:00 AM'),
#     ('11:00 AM - 12:00 PM', '11:00 AM - 12:00 PM'),
#     ('02:00 PM - 03:00 PM', '02:00 PM - 03:00 PM'),
#     ('03:00 PM - 04:00 PM', '03:00 PM - 04:00 PM'),
#     ('04:00 PM - 05:00 PM', '04:00 PM - 05:00 PM'),
# ]
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/PatientProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=False)
    symptoms = models.CharField(max_length=100, null=False)
    assignedDoctorId = models.PositiveIntegerField(null=True)
    admitDate = models.DateField(auto_now=True)
    signup_time = models.DateTimeField(auto_now_add=True)  # New field to store signup time
    discharge_status=models.BooleanField(default=False)
    payment_done=models.BooleanField(default=False)
    status = models.BooleanField(default=False)
    re_admit= models.BooleanField(default=False)

    @property
    def get_name(self):
        return self.user.first_name + " " + self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return self.user.first_name 



TIME_SLOTS = [
    ('09:00 AM - 10:00 AM', '09:00 AM - 10:00 AM'),
    ('10:00 AM - 11:00 AM', '10:00 AM - 11:00 AM'),
    ('11:00 AM - 12:00 PM', '11:00 AM - 12:00 PM'),
    ('02:00 PM - 03:00 PM', '02:00 PM - 03:00 PM'),
    ('03:00 PM - 04:00 PM', '03:00 PM - 04:00 PM'),
    ('04:00 PM - 05:00 PM', '04:00 PM - 05:00 PM'),
]

class Appointment(models.Model):
    patientId = models.PositiveIntegerField(null=True)
    doctorId = models.PositiveIntegerField(null=True)
    patientName = models.CharField(max_length=40, null=True)
    doctorName = models.CharField(max_length=40, null=True)
    appointmentDate = models.DateField()
    time_slot = models.CharField(max_length=20, choices=TIME_SLOTS)
    description = models.TextField(max_length=500)
    status = models.BooleanField(default=False)

    class Meta:
        unique_together = ('doctorId', 'appointmentDate', 'time_slot')

    def __str__(self):
        return f"{self.doctorName} - {self.appointmentDate} - {self.time_slot}"

class PatientDischargeDetails(models.Model):
    patientId=models.PositiveIntegerField(null=True)
    patientName=models.CharField(max_length=40)
    assignedDoctorName=models.CharField(max_length=40)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=True)
    symptoms = models.CharField(max_length=100,null=True)

    admitDate=models.DateField(null=False)
    releaseDate=models.DateField(null=False)
    daySpent=models.PositiveIntegerField(null=False)

    roomCharge=models.PositiveIntegerField(null=False)
    medicineCost=models.PositiveIntegerField(null=False)
    doctorFee=models.PositiveIntegerField(null=False)
    OtherCharge=models.PositiveIntegerField(null=False)
    total=models.PositiveIntegerField(null=False)
    prescribed_medicines = models.TextField(null=True, blank=True) 
    def get_prescribed_medicines(self):
        """ Convert stored JSON to dictionary format """
        try:
            return json.loads(self.prescribed_medicines)
        except json.JSONDecodeError:
            return []

from django.db import models
from django.contrib.auth.models import User

# class ChatMessage(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
#     message = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.sender} -> {self.receiver}: {self.message[:30]}"
from django.db import models
 # Import Doctor & Patient models

class ChatMessage(models.Model):
    sender_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True, related_name="sent_messages")
    sender_patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True, related_name="sent_messages")
    receiver_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, null=True, blank=True, related_name="received_messages")
    receiver_patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True, related_name="received_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = self.sender_doctor if self.sender_doctor else self.sender_patient
        receiver = self.receiver_doctor if self.receiver_doctor else self.receiver_patient
        return f"{sender} -> {receiver}: {self.message[:20]}"


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="prescriptions")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)  # e.g., "2 times a day"
    duration = models.CharField(max_length=100)  # e.g., "5 days"
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Medicine cost
    date_prescribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine_name} for {self.patient.get_name}"
    
class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50, choices=[
        ('General', 'General'),
        ('Private', 'Private'),
        ('ICU', 'ICU'),
    ])
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type}"

class RoomBooking(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.patient.get_name} booked {self.room.room_number} ({self.start_date} to {self.end_date if self.end_date else 'Ongoing'})"

    def save(self, *args, **kwargs):
        """ Automatically update room availability when booking changes """
        if self.is_active:
            self.room.is_available = False  # Mark room as occupied
        else:
            self.room.is_available = True  # Room becomes available again
        self.room.save()
        super().save(*args, **kwargs)
