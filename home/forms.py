# forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Doctor,Patient
from . import models
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Doctor
import re
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io
# Forms
class DoctorUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="Password must be at least 8 characters long and include both letters and numbers."
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Exclude current user when checking email uniqueness
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Email address is already registered.')
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError('Password must contain at least one letter.')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one digit.')
        return password


class DoctorForm(forms.ModelForm):
    mobile = forms.CharField(
        help_text="Mobile number must be exactly 10 digits."
    )

    class Meta:
        model = Doctor
        fields = ['profile_pic', 'address', 'mobile', 'status','department', 'experience']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError('Password must contain at least one letter.')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one digit.')
        return password

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not re.match(r'^\d{10}$', mobile):
            raise ValidationError('Mobile number must be exactly 10 digits.')
        return mobile

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address.strip():
            raise ValidationError('Address cannot be empty.')
        return address

from django import forms
from django.contrib.auth.models import User
from .models import Patient, Doctor, Appointment
from django.core.exceptions import ValidationError
import re
from PIL import Image
from django.utils.timezone import now

TIME_SLOTS = [
    ('09:00 AM - 10:00 AM', '09:00 AM - 10:00 AM'),
    ('10:00 AM - 11:00 AM', '10:00 AM - 11:00 AM'),
    ('11:00 AM - 12:00 PM', '11:00 AM - 12:00 PM'),
    ('02:00 PM - 03:00 PM', '02:00 PM - 03:00 PM'),
    ('03:00 PM - 04:00 PM', '03:00 PM - 04:00 PM'),
    ('04:00 PM - 05:00 PM', '04:00 PM - 05:00 PM'),
]

class PatientUserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        help_text="Password must be at least 8 characters long and include both letters and numbers."
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError("Password must contain at least one letter.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit.")
        return password

class PatientForm(forms.ModelForm):
    assignedDoctorId = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(status=True),
        empty_label="Select Doctor",
        widget=forms.Select(attrs={'class': 'form-control'}),
        to_field_name="id"
    )
    appointmentDate = forms.DateField(widget=forms.SelectDateWidget(), required=True)
    time_slot = forms.ChoiceField(choices=TIME_SLOTS, required=True)

    class Meta:
        model = Patient
        fields = ['address', 'mobile', 'status', 'symptoms', 'profile_pic', 'appointmentDate', 'time_slot']
        widgets = {
            'address': forms.Textarea(attrs={'required': True}),
            'mobile': forms.TextInput(attrs={'required': True}),
            'symptoms': forms.Textarea(attrs={'required': True}),
        }

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        if not re.match(r'^\d{10}$', mobile):
            raise ValidationError("Mobile number must contain exactly 10 digits.")
        return mobile

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address.strip():
            raise ValidationError("Address cannot be empty.")
        return address

    def clean_symptoms(self):
        symptoms = self.cleaned_data.get('symptoms')
        if not symptoms.strip():
            raise ValidationError("Symptoms field cannot be empty.")
        return symptoms

    def clean_profile_pic(self):
        profile_pic = self.cleaned_data.get('profile_pic')
        if profile_pic:
            try:
                img = Image.open(profile_pic)
                img.verify()
            except Exception:
                raise ValidationError("Profile picture must be a valid image file.")
        return profile_pic
    # def clean_assignedDoctorId(self):
    #     doctor = self.cleaned_data.get("assignedDoctorId")
    #     if doctor:
    #         return doctor.id  # Ensure doctor ID is stored as an integer
    #     return None

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("assignedDoctorId")
        appointmentDate = cleaned_data.get("appointmentDate")
        time_slot = cleaned_data.get("time_slot")

        if appointmentDate and appointmentDate < now().date():
            self.add_error("appointmentDate", "You cannot select a past date.")

        if doctor and appointmentDate and time_slot:
            if Appointment.objects.filter(doctorId=doctor.id, appointmentDate=appointmentDate, time_slot=time_slot).exists():
                self.add_error("time_slot", "This time slot is already booked. Please choose another one.")

        return cleaned_data

from django import forms
from .models import Appointment, Doctor, Patient, TIME_SLOTS
from django import forms
from django.utils.timezone import now
from .models import Appointment, Doctor, Patient

class AppointmentForm(forms.ModelForm):
    doctorId = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(status=True),
        empty_label="Select Doctor",
        widget=forms.Select(attrs={'class': 'form-control'}),
        to_field_name="id"
    )
    patientId = forms.ModelChoiceField(
        queryset=Patient.objects.filter(status=True),
        empty_label="Select Patient",
        widget=forms.Select(attrs={'class': 'form-control'}),
        to_field_name="id"
    )
    appointmentDate = forms.DateField(widget=forms.SelectDateWidget())
    time_slot = forms.ChoiceField(choices=TIME_SLOTS)

    class Meta:
        model = Appointment
        fields = ['appointmentDate', 'time_slot', 'description', 'status']

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get("doctorId")
        appointmentDate = cleaned_data.get("appointmentDate")
        time_slot = cleaned_data.get("time_slot")

        if appointmentDate and appointmentDate < now().date():
            self.add_error("appointmentDate", "You cannot book an appointment for a past date.")

        if doctor and appointmentDate and time_slot:
            if Appointment.objects.filter(doctorId=doctor.id, appointmentDate=appointmentDate, time_slot=time_slot).exists():
                self.add_error("time_slot", "This time slot is already booked. Please choose another one.")

        return cleaned_data

from django import forms
from .models import Appointment, Doctor
from django.utils.timezone import now

from django import forms
from .models import Appointment, Doctor
from django.utils.timezone import now

TIME_SLOTS = [
    ('09:00 AM - 10:00 AM', '09:00 AM - 10:00 AM'),
    ('10:00 AM - 11:00 AM', '10:00 AM - 11:00 AM'),
    ('11:00 AM - 12:00 PM', '11:00 AM - 12:00 PM'),
    ('02:00 PM - 03:00 PM', '02:00 PM - 03:00 PM'),
    ('03:00 PM - 04:00 PM', '03:00 PM - 04:00 PM'),
    ('04:00 PM - 05:00 PM', '04:00 PM - 05:00 PM'),
]

class PatientAppointmentForm(forms.ModelForm):
    doctorId = forms.ModelChoiceField(
        queryset=Doctor.objects.all(),  # Ensure it's fetching Doctor objects
        empty_label="Select Doctor",
        widget=forms.Select(attrs={'class': 'form-control'})
    )


    appointmentDate = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )
    time_slot = forms.ChoiceField(
        choices=TIME_SLOTS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Appointment
        fields = ['description', 'appointmentDate', 'time_slot']

#for contact us page
class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))

from django import forms
from .models import ChatMessage,  RoomBooking

from django import forms
from .models import ChatMessage

from django import forms
from .models import ChatMessage

# class ChatMessageForm(forms.ModelForm):
#     class Meta:
#         model = ChatMessage
#         fields = ['receiver', 'message']
#         widgets = {
#             'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Type your message...'}),
#         }

from django import forms
from .models import ChatMessage
from .models import Doctor, Patient

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Type your message...'}),
        }

from django import forms
from .models import PatientDischargeDetails

from django import forms
import json
from .models import PatientDischargeDetails

from django import forms
import json
from .models import PatientDischargeDetails
from django import forms
import json
from .models import PatientDischargeDetails
from django import forms
import json
from .models import PatientDischargeDetails

class PrescriptionForm(forms.ModelForm):
    medicines_json = forms.CharField(
        widget=forms.HiddenInput(), required=False
    )

    class Meta:
        model = PatientDischargeDetails
        fields = ['medicineCost']

    def clean_medicines_json(self):
        """ Validate and parse medicine data """
        try:
            medicines = json.loads(self.cleaned_data['medicines_json'])
            return json.dumps(medicines)
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid medicine data format.")

# 🏥 Room Booking Form
class RoomBookingForm(forms.ModelForm):
    class Meta:
        model = RoomBooking
        fields = ['room', 'start_date', 'end_date']
