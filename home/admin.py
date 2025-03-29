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
from .models import ChatMessage, Room, RoomBooking

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



@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'is_available')
    list_filter = ('room_type', 'is_available')
    search_fields = ('room_number',)

@admin.register(RoomBooking)
class RoomBookingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'room', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('patient__user__first_name', 'room__room_number')
