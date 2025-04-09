from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Doctor, Patient,Appointment,PatientDischargeDetails

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'mobile', 'status']
    search_fields = ['user__first_name', 'user__last_name', 'department']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['user', 'mobile', 'address', 'status']
    search_fields = ['user__first_name', 'user__last_name']


class AppointmentAdmin(admin.ModelAdmin):
    pass
admin.site.register(Appointment, AppointmentAdmin)

class PatientDischargeDetailsAdmin(admin.ModelAdmin):
    pass
admin.site.register(PatientDischargeDetails, PatientDischargeDetailsAdmin)


from django.contrib import admin
from .models import ChatMessage

from django.contrib import admin
from .models import ChatMessage

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('get_sender', 'get_receiver', 'message', 'timestamp')

    def get_sender(self, obj):
        """ Show the sender whether it's a doctor or a patient """
        if obj.sender_doctor:
            return f"Doctor: {obj.sender_doctor.user.first_name} {obj.sender_doctor.user.last_name}"
        elif obj.sender_patient:
            return f"Patient: {obj.sender_patient.user.first_name} {obj.sender_patient.user.last_name}"
        return "Unknown"

    def get_receiver(self, obj):
        """ Show the receiver whether it's a doctor or a patient """
        if obj.receiver_doctor:
            return f"Doctor: {obj.receiver_doctor.user.first_name} {obj.receiver_doctor.user.last_name}"
        elif obj.receiver_patient:
            return f"Patient: {obj.receiver_patient.user.first_name} {obj.receiver_patient.user.last_name}"
        return "Unknown"

    get_sender.short_description = "Sender"
    get_receiver.short_description = "Receiver"

admin.site.register(ChatMessage, ChatMessageAdmin)

from django.contrib import admin
from .models import Room, RoomBooking, Patient,EmergencyAlert,Prescription,LabTestBooking,LabTestPrescription

admin.site.register(Room)
admin.site.register(RoomBooking)
admin.site.register(EmergencyAlert)
admin.site.register(Prescription)
from django.contrib import admin
from .models import AmbulanceBooking

@admin.register(AmbulanceBooking)
class AmbulanceBookingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'location', 'booking_time', 'status')
admin.site.register(LabTestBooking)
admin.site.register(LabTestPrescription)
