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
