from datetime import datetime, timedelta, date
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as logouts
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.db.models import Q, Sum
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.timezone import now
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
import razorpay
from django.views.decorators.csrf import csrf_exempt
from home.models import Patient, PatientDischargeDetails
from .forms import PatientForm, PatientUserForm, DoctorUserForm, DoctorForm
@login_required
def admin_dashboard_view(request):
    doctors = Doctor.objects.all().order_by('-id')
    patients = Patient.objects.all().order_by('-id')

    doctorcount = Doctor.objects.filter(status=True).count()
    pendingdoctorcount = Doctor.objects.filter(status=False).count()
    patientcount = Patient.objects.filter(status=True).count()
    pendingpatientcount = Patient.objects.filter(status=False, payment_done=False).count()

    appointmentcount = Appointment.objects.filter(status=True).exclude(description__startswith="Appointment booked during signup").count()
    pendingappointmentcount = Appointment.objects.filter(status=False).exclude(description__startswith="Appointment booked during signup").count()

    context = {
        'doctors': doctors,
        'patients': patients,
        'doctorcount': doctorcount,
        'pendingdoctorcount': pendingdoctorcount,
        'patientcount': patientcount,
        'pendingpatientcount': pendingpatientcount,
        'appointmentcount': appointmentcount,
        'pendingappointmentcount': pendingappointmentcount,
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def admin_doctor_view(request):
    return render(request, 'admin_doctor.html')  # Replace with your actual template


@login_required
def admin_patient_view(request):
    return render(request, 'admin_patient.html')  # Replace with your actual template

@login_required
def admin_appointment_view(request):
    return render(request, 'admin_appointment.html')  # Replace with your actual template

@login_required
def admin_doctor_view(request):
    return render(request, "admin_doctor.html")  # Replace with your actual template


@login_required
def admin_patient_view(request):
    return render(request, "admin_patient.html")  # Replace with your actual template

@login_required
def admin_appointment_view(request):
    return render(request, "admin_appointment.html")  # Replace with your actual template

def logout(request):
    logouts(request)
    return redirect('index')

# Create your views here.
def index(request):
    return render(request, "index.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def department(request):
    return render(request, "treatment.html")

def doctor(request):
    return render(request, "doctors.html")

# Rename your login view to avoid conflict
def login(request):
    return render(request, 'login_as.html')


def admin_login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if the user is a superuser
            if user.is_superuser:
                # Log in the user
                auth_login(request, user)
                return redirect('admindashboard')  # Redirect to the admin dashboard
            else:
                # Not a superuser, show generic error
                messages.error(request, "Incorrect username or password.")
        else:
            # Authentication failed, show generic error
            messages.error(request, "Incorrect username or password.")

    return render(request, "adminlogin.html")



#for showing signup/login button for doctor(by sumit)
def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'doctorclick.html')


#for showing signup/login button for patient(by sumit)
def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'patientclick.html')


def doctor_signup_view(request):
    form_submitted = False  # Track whether the form is submitted
    if request.method == 'POST':
        form_submitted = True
        user_form = DoctorUserForm(request.POST)
        doctor_form = DoctorForm(request.POST, request.FILES)
        if user_form.is_valid() and doctor_form.is_valid():
            # Save the user
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            
            # Save the doctor
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            
            # Add to doctor group
            my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group[0].user_set.add(user)

            messages.success(request, 'Account created successfully!')
            return redirect('doctor_login')  # Redirect to login page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = DoctorUserForm()
        doctor_form = DoctorForm()

    return render(request, 'doctorsignup.html', {
        'user_form': user_form,
        'doctor_form': doctor_form,
        'form_submitted': form_submitted
    })

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import Group
from django.utils.timezone import now
from . import forms, models

def patient_signup_view(request):
    user_form = forms.PatientUserForm()
    patient_form = forms.PatientForm()
    context = {'userForm': user_form, 'patientForm': patient_form}

    if request.method == 'POST':
        user_form = forms.PatientUserForm(request.POST)
        patient_form = forms.PatientForm(request.POST, request.FILES)
        
        if user_form.is_valid() and patient_form.is_valid():
            # Save user
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            # Save patient
            patient = patient_form.save(commit=False)
            patient.user = user

            # Validate doctor selection
            doctor = patient_form.cleaned_data['assignedDoctorId']
            appointmentDate = patient_form.cleaned_data['appointmentDate']
            time_slot = patient_form.cleaned_data['time_slot']

            # Ensure selected time slot is not already booked
            if models.Appointment.objects.filter(doctorId=doctor.id, appointmentDate=appointmentDate, time_slot=time_slot).exists():
                messages.error(request, "This time slot is already booked. Please choose another one.")
                return render(request, 'patientsignup.html', context)

            patient.assignedDoctorId = doctor.id
            patient.save()

            # Save appointment
            appointment = models.Appointment.objects.create(
                patientId=patient.id,
                doctorId=doctor.id,
                patientName=user.first_name,
                doctorName=doctor.user.first_name,
                appointmentDate=appointmentDate,
                time_slot=time_slot,
                description=f"Appointment booked during signup for {user.first_name}",
                status=True
            )

            # Add user to patient group
            patient_group, _ = Group.objects.get_or_create(name='PATIENT')
            patient_group.user_set.add(user)

            messages.success(request, "Registration successful! Your appointment has been booked.")
            return redirect('patientlogin')

    return render(request, 'patientsignup.html', context)



def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()
def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists() and Doctor.objects.filter(user=user).exists()
  

from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Doctor, Patient  # Adjust according to your models
def afterlogin_view(request):
    if request.user.is_authenticated:  # Ensure the user is logged in before checking roles
        if is_doctor(request.user):
            accountapproval = Doctor.objects.filter(user_id=request.user.id, status=True)
            if accountapproval.exists():
                return redirect('doctor-dashboard')
            else:
                return render(request, 'doctor_wait_for_approval.html')

        elif is_patient(request.user):
            patient = Patient.objects.filter(user_id=request.user.id).first()
            
            if patient:
                if patient.status:  # ✅ If patient is active (admitted)
                    return redirect('patient-dashboard')

                elif patient.payment_done:  # ✅ If patient is discharged and has paid the bill
                    return redirect('patient-dashboard')

            return render(request, 'patient_wait_for_approval.html')

    # If the user is not authenticated, show an error message
    messages.error(request, "Incorrect username or password.")
    return redirect('login')  # Redirect back to the login page



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient = get_object_or_404(models.Patient, user_id=request.user.id)

    doctor = None
    if patient.assignedDoctorId:
        try:
            doctor = models.Doctor.objects.get(id=patient.assignedDoctorId)  # Use 'id' instead of 'user_id'
        except models.Doctor.DoesNotExist:
            doctor = None

    mydict = {
        'patient': patient,
        'doctorName': doctor.get_name if doctor else "Not Assigned",
        'doctorMobile': doctor.mobile if doctor else "N/A",
        'doctorAddress': doctor.address if doctor else "N/A",
        'symptoms': patient.symptoms,
        'doctorDepartment': doctor.department if doctor else "N/A",
        'admitDate': patient.admitDate,
    }
    return render(request, 'patient_dashboard.html', mydict)




@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    return render(request,'doctor_appointment.html',{'doctor':doctor})



# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
def admin_doctor_view(request):
    return render(request,'admin_doctor.html')



@login_required(login_url='adminlogin')
def admin_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'admin_view_doctor.html',{'doctors':doctors})




@login_required(login_url='adminlogin')
def delete_doctor_from_hospital_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')


@login_required(login_url='adminlogin')
def update_doctor_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)

    if request.method == 'POST':
        userForm = forms.DoctorUserForm(request.POST, instance=user)
        doctorForm = forms.DoctorForm(request.POST, request.FILES, instance=doctor)

        if userForm.is_valid() and doctorForm.is_valid():
            user = userForm.save(commit=False)

            # Ensure password isn't changed unless explicitly updated
            if 'password' in userForm.cleaned_data and userForm.cleaned_data['password']:
                user.set_password(userForm.cleaned_data['password'])

            user.save()

            doctor = doctorForm.save(commit=False)

            # Handle profile picture removal
            if 'remove_profile_pic' in request.POST:
                doctor.profile_pic.delete(save=False)
                doctor.profile_pic = None

            doctor.status = True  # Keep doctor active
            doctor.save()

            messages.success(request, '')
            return redirect('admin-view-doctor')

        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        userForm = forms.DoctorUserForm(instance=user)
        doctorForm = forms.DoctorForm(instance=doctor)

    return render(request, 'admin_update_doctor.html', {
        'userForm': userForm,
        'doctorForm': doctorForm
    })


@login_required(login_url='adminlogin')
def admin_add_doctor_view(request):
    form_submitted = False  # Track whether the form is submitted

    # Initialize forms outside the POST block to avoid UnboundLocalError
    user_frm = DoctorUserForm()
    doctor_form = DoctorForm()

    if request.method == 'POST':
        form_submitted = True
        user_frm = DoctorUserForm(request.POST)
        doctor_form = DoctorForm(request.POST, request.FILES)
        
        if user_frm.is_valid() and doctor_form.is_valid():
            # Save the user
            user = user_frm.save(commit=False)
            user.set_password(user_frm.cleaned_data['password'])
            user.save()
            
            # Save the doctor
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            
            # Add to doctor group
            my_doctor_group, created = Group.objects.get_or_create(name='DOCTOR')
            my_doctor_group.user_set.add(user)

            return HttpResponseRedirect('admin-view-doctor')

    return render(request, 'admin_add_doctor.html', {
        'user_form': user_frm,
        'doctor_form': doctor_form,
        'form_submitted': form_submitted
    })






@login_required(login_url='adminlogin')
def admin_approve_doctor_view(request):
    #those whose approval are needed
    doctors=models.Doctor.objects.all().filter(status=False)
    return render(request,'admin_approve_doctor.html',{'doctors':doctors})

@login_required(login_url='adminlogin')
def approve_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    doctor.status=True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))

@login_required(login_url='adminlogin')
def reject_doctor_view(request,pk):
    doctor=models.Doctor.objects.get(id=pk)
    user=models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')


@login_required(login_url='adminlogin')
def admin_view_doctor_specialisation_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    return render(request,'admin_view_doctor_specialisation.html',{'doctors':doctors})





from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from . import models
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from . import models

@login_required(login_url='adminlogin')
def admin_view_patient_view(request):
    # Fetch all patients along with their latest appointment details
    patients = models.Patient.objects.filter(status=True)

    for patient in patients:
        appointment = models.Appointment.objects.filter(patientId=patient.id).order_by('-appointmentDate').first()

        # Attach appointment details to the patient object dynamically
        patient.appointmentDate = appointment.appointmentDate if appointment else "No Appointment"
        patient.time_slot = appointment.time_slot if appointment else "No Time Slot"

    return render(request, 'admin_view_patient.html', {'patients': patients})



@login_required(login_url='adminlogin')
def admin_add_patient_view(request):
    user_form = forms.PatientUserForm()
    patient_form = forms.PatientForm()
    
    if request.method == 'POST':
        user_form = forms.PatientUserForm(request.POST)
        patient_form = forms.PatientForm(request.POST, request.FILES)
        
        if user_form.is_valid() and patient_form.is_valid():
            # Save user
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            # Save patient
            patient = patient_form.save(commit=False)
            patient.user = user

            # Validate doctor selection
            doctor = patient_form.cleaned_data['assignedDoctorId']
            appointmentDate = patient_form.cleaned_data['appointmentDate']
            time_slot = patient_form.cleaned_data['time_slot']

            # Ensure selected time slot is not already booked
            if models.Appointment.objects.filter(doctorId=doctor.id, appointmentDate=appointmentDate, time_slot=time_slot).exists():
                messages.error(request, "This time slot is already booked. Please choose another one.")
                return render(request, 'admin_add_patient.html', {'userForm': user_form, 'patientForm': patient_form})

            patient.assignedDoctorId = doctor.id
            patient.save()

            # Save appointment
            appointment = models.Appointment.objects.create(
                patientId=patient.id,
                doctorId=doctor.id,
                patientName=user.first_name,
                doctorName=doctor.user.first_name,
                appointmentDate=appointmentDate,
                time_slot=time_slot,
                description=f"Appointment booked during signup for {user.first_name}",
                status=True
            )

            # Add user to patient group
            patient_group, _ = Group.objects.get_or_create(name='PATIENT')
            patient_group.user_set.add(user)

            messages.success(request, "Registration successful! Your appointment has been booked.")
            return redirect('admin-view-patient')

        else:
            # Show form validation errors on the same page
            messages.error(request, "")

    return render(request, 'admin_add_patient.html', {'userForm': user_form, 'patientForm': patient_form})



@login_required(login_url='adminlogin')
def delete_patient_from_hospital_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from . import models, forms
from django.contrib import messages
from django.core.exceptions import ValidationError
import re
from PIL import Image
from django.utils.timezone import now
from .models import Doctor, Appointment

@login_required(login_url='adminlogin')
def update_patient_view(request, pk):
    patient = get_object_or_404(models.Patient, id=pk)
    user = get_object_or_404(User, id=patient.user_id)

    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST, instance=user)
        patientForm = forms.PatientForm(request.POST, request.FILES, instance=patient)

        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save(commit=False)

            if 'password' in userForm.cleaned_data and userForm.cleaned_data['password']:
                user.set_password(userForm.cleaned_data['password'])

            user.save()

            patient = patientForm.save(commit=False)

            if 'remove_profile_pic' in request.POST:
                patient.profile_pic.delete(save=False)
                patient.profile_pic = None

            patient.status = True
            patient.save()

            messages.success(request, 'Patient details updated successfully!')
            return redirect('admin-view-patient')
        else:
            messages.error(request, 'Please correct the errors below.')
            print("User Form Errors:", userForm.errors)
            print("Patient Form Errors:", patientForm.errors)

    else:
        userForm = forms.PatientUserForm(instance=user)
        patientForm = forms.PatientForm(instance=patient) # Ensure instance is passed here

    return render(request, 'admin_update_patient.html', {
        'userForm': userForm,
        'patientForm': patientForm
    })
@login_required(login_url='adminlogin')
def admin_approve_patient_view(request):
    #those whose approval are needed
    patients=models.Patient.objects.all().filter(status=False)
    return render(request,'admin_approve_patient.html',{'patients':patients})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Doctor, Patient, PatientDischargeDetails

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    """ Show only fully discharged patients under the logged-in doctor """
    
    doctor = Doctor.objects.get(user_id=request.user.id)

    # ✅ Get fully discharged patients under this doctor
    discharged_patients = Patient.objects.filter(
        assignedDoctorId=doctor.id,
        discharge_status=False,  # ✅ Discharge approved
        payment_done=True,  # ✅ Payment completed
        status=True  # ✅ Fully discharged (not active)
    )

    # ✅ Fetch discharge details for each patient
    discharge_details = {d.patientId: d for d in PatientDischargeDetails.objects.filter(
        patientId__in=discharged_patients.values_list('id', flat=True)
    )}

    # ✅ Attach discharge details dynamically
    for patient in discharged_patients:
        discharge_info = discharge_details.get(patient.id)
        if discharge_info:
            patient.releaseDate = discharge_info.releaseDate
            patient.patientName = discharge_info.patientName  # Ensure correct name display
        else:
            patient.releaseDate = "Not Available"
            patient.patientName = patient.get_name

    return render(request, 'doctor_view_discharge_patient.html', {
        'dischargedpatients': discharged_patients, 
        'doctor': doctor
    })


@login_required(login_url='adminlogin')
def admin_view_appointment_view(request):
    appointments = models.Appointment.objects.filter(status=True).exclude(description__startswith="Appointment booked during signup")
    return render(request, 'appointment.html', {'appointments': appointments})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from . import models, forms
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from . import models, forms

from django.utils.timezone import now
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from . import forms, models

@login_required(login_url='adminlogin')
def admin_add_appointment_view(request):
    appointmentForm = forms.AppointmentForm()

    if request.method == 'POST':
        appointmentForm = forms.AppointmentForm(request.POST)
        if appointmentForm.is_valid():
            appointment = appointmentForm.save(commit=False)

            # Fetch doctor and patient objects
            doctor = appointmentForm.cleaned_data['doctorId']
            patient = appointmentForm.cleaned_data['patientId']
            appointmentDate = appointmentForm.cleaned_data['appointmentDate']
            time_slot = appointmentForm.cleaned_data['time_slot']

            # Ensure only future dates are allowed
            if appointmentDate < now().date():
                messages.error(request, "You cannot book an appointment for a past date.")
            elif models.Appointment.objects.filter(doctorId=doctor.id, appointmentDate=appointmentDate, time_slot=time_slot).exists():
                messages.error(request, "This time slot is already booked. Please choose another one.")
            else:
                # Assign correct values
                appointment.doctorId = doctor.id  # Store the doctor’s ID
                appointment.patientId = patient.id  # Store the patient’s ID
                appointment.doctorName = doctor.user.first_name
                appointment.patientName = patient.user.first_name
                appointment.status = True
                appointment.save()
                messages.success(request, "Appointment successfully booked!")
                return redirect('admin-view-appointment')

    return render(request, 'admin_add_appointment.html', {'appointmentForm': appointmentForm})

@login_required(login_url='adminlogin')
def admin_approve_appointment_view(request):
    #those whose approval are needed
    appointments=models.Appointment.objects.all().filter(status=False)
    return render(request,'admin_approve_appointment.html',{'appointments':appointments})




@login_required(login_url='adminlogin')
def approve_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('admin-approve-patient'))



@login_required(login_url='adminlogin')
def reject_patient_view(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-approve-patient')




@login_required(login_url='adminlogin')
def approve_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))



@login_required(login_url='adminlogin')
def reject_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')

from datetime import date
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Patient, Appointment

logger = logging.getLogger(__name__)

@login_required(login_url='adminlogin')
def admin_discharge_patient_view(request):
    """ Show patients who need to be discharged, including those who were discharged before and now have a new appointment. """

    # Step 1: Patients pending payment for their first discharge
    first_time_discharge = Patient.objects.filter(
        discharge_status=True,  # ✅ Approved for discharge
        payment_done=False,  # ✅ Payment NOT done yet
        status=True  # ✅ Discharged (not currently active)
    )

    # Step 2: Patients who were discharged before, re-admitted, and need discharge again
    re_discharge_patients = Patient.objects.filter(
        status=True,  # ✅ Currently admitted again (re-admitted)
        re_admit=True,  # ✅ Previously discharged, now readmitted
        assignedDoctorId__in=Appointment.objects.values_list('doctorId', flat=True)  # ✅ Has an active appointment
    )

    # Combine both sets of patients
    patients_to_discharge = first_time_discharge | re_discharge_patients

    logger.debug(f"Admin View: Patients Awaiting Payment or Re-Discharge: {patients_to_discharge.count()}")

    return render(request, 'admin_discharge_patient.html', {'patients': patients_to_discharge})


# @login_required(login_url='adminlogin')
# def discharge_patient_view(request, pk):
#     patient = get_object_or_404(models.Patient, id=pk)

#     # Retrieve assigned doctor correctly
#     assigned_doctor = models.Doctor.objects.filter(id=patient.assignedDoctorId).first()
#     assigned_doctor_name = assigned_doctor.get_name if assigned_doctor else "Doctor Not Assigned"

#     days_spent = (date.today() - patient.admitDate).days

#     patient_data = {
#         'patientId': pk,
#         'name': patient.get_name,
#         'mobile': patient.mobile,
#         'address': patient.address,
#         'symptoms': patient.symptoms,
#         'admitDate': patient.admitDate,
#         'todayDate': date.today(),
#         'day': days_spent,
#         'assignedDoctorName': assigned_doctor_name,  # Corrected doctor name retrieval
#     }

#     if request.method == 'POST':
#         try:
#             room_charge = int(request.POST.get('roomCharge', 0)) * days_spent
#             doctor_fee = int(request.POST.get('doctorFee', 0))
#             medicine_cost = int(request.POST.get('medicineCost', 0))
#             other_charge = int(request.POST.get('OtherCharge', 0))
#             total_amount = room_charge + doctor_fee + medicine_cost + other_charge

#             bill_details = {
#                 'roomCharge': room_charge,
#                 'doctorFee': doctor_fee,
#                 'medicineCost': medicine_cost,
#                 'OtherCharge': other_charge,
#                 'total': total_amount,
#             }

#             patient_data.update(bill_details)

#             discharge_details = models.PatientDischargeDetails(
#                 patientId=pk,
#                 patientName=patient.get_name,
#                 assignedDoctorName=assigned_doctor_name,
#                 address=patient.address,
#                 mobile=patient.mobile,
#                 symptoms=patient.symptoms,
#                 admitDate=patient.admitDate,
#                 releaseDate=date.today(),
#                 daySpent=days_spent,
#                 medicineCost=medicine_cost,
#                 roomCharge=room_charge,
#                 doctorFee=doctor_fee,
#                 OtherCharge=other_charge,
#                 total=total_amount
#             )
#             discharge_details.save()

#             return render(request, 'patient_final_bill.html', context=patient_data)
#         except ValueError:
#             patient_data['error'] = "Invalid input. Please enter valid numbers."
#             return render(request, 'patient_generate_bill.html', context=patient_data)

#     return render(request, 'patient_generate_bill.html', context=patient_data)


@login_required(login_url='adminlogin')
def discharge_patient_view(request, pk):
    patient = get_object_or_404(models.Patient, id=pk)
    assigned_doctor = models.Doctor.objects.filter(id=patient.assignedDoctorId).first()
    assigned_doctor_name = assigned_doctor.get_name if assigned_doctor else "Doctor Not Assigned"

    days_spent = (date.today() - patient.admitDate).days

    # Fetch previous discharge details if available
    discharge_details = models.PatientDischargeDetails.objects.filter(patientId=pk).first()
    prescribed_medicines = json.loads(discharge_details.prescribed_medicines) if discharge_details and discharge_details.prescribed_medicines else []

    patient_data = {
        'patientId': pk,
        'name': patient.get_name,
        'mobile': patient.mobile,
        'address': patient.address,
        'symptoms': patient.symptoms,
        'admitDate': patient.admitDate,
        'todayDate': date.today(),
        'day': days_spent,
        'assignedDoctorName': assigned_doctor_name,
        'prescribed_medicines': prescribed_medicines  # Include prescribed medicines
    }

    if request.method == 'POST':
        try:
            room_charge = int(request.POST.get('roomCharge', 0)) * days_spent
            doctor_fee = int(request.POST.get('doctorFee', 0))
            medicine_cost = int(request.POST.get('medicineCost', 0))
            other_charge = int(request.POST.get('OtherCharge', 0))
            total_amount = room_charge + doctor_fee + medicine_cost + other_charge

            bill_details = {
                'roomCharge': room_charge,
                'doctorFee': doctor_fee,
                'medicineCost': medicine_cost,
                'OtherCharge': other_charge,
                'total': total_amount,
            }

            patient_data.update(bill_details)

            # Save discharge details with medicine information
            discharge_details = models.PatientDischargeDetails(
                patientId=pk,
                patientName=patient.get_name,
                assignedDoctorName=assigned_doctor_name,
                address=patient.address,
                mobile=patient.mobile,
                symptoms=patient.symptoms,
                admitDate=patient.admitDate,
                releaseDate=date.today(),
                daySpent=days_spent,
                medicineCost=medicine_cost,
                roomCharge=room_charge,
                doctorFee=doctor_fee,
                OtherCharge=other_charge,
                total=total_amount,
                prescribed_medicines=json.dumps(prescribed_medicines)  # Save as JSON
            )
            discharge_details.save()

            return render(request, 'patient_final_bill.html', context=patient_data)
        except ValueError:
            patient_data['error'] = "Invalid input. Please enter valid numbers."
            return render(request, 'patient_generate_bill.html', context=patient_data)

    return render(request, 'patient_generate_bill.html', context=patient_data)

import io
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return



def download_pdf_view(request, pk):
    dischargeDetails = models.PatientDischargeDetails.objects.filter(patientId=pk).order_by('-id')[:1]

    if not dischargeDetails:
        return HttpResponse("No discharge details found.", content_type="text/plain")

    context = {
        'patientName': dischargeDetails[0].patientName,
        'assignedDoctorName': dischargeDetails[0].assignedDoctorName,
        'address': dischargeDetails[0].address,
        'mobile': dischargeDetails[0].mobile,
        'symptoms': dischargeDetails[0].symptoms,
        'admitDate': dischargeDetails[0].admitDate,
        'releaseDate': dischargeDetails[0].releaseDate,
        'daySpent': dischargeDetails[0].daySpent,
        'medicineCost': dischargeDetails[0].medicineCost,
        'roomCharge': dischargeDetails[0].roomCharge,
        'doctorFee': dischargeDetails[0].doctorFee,
        'OtherCharge': dischargeDetails[0].OtherCharge,
        'total': dischargeDetails[0].total,
    }

    # Correcting the template file path
    template_path = r'C:\Users\VISHN\Desktop\main pro\hospital\home\templates\download_bill.html'
    
    return render_to_pdf(template_path, context)

#--------------------------------------admin end ----------------------------------------------------------------------#
#--------------------------------------doctor stat---------------------------------------------------------------------#


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    """ Doctor Dashboard View """

    doctor = models.Doctor.objects.get(user_id=request.user.id)  

    # ✅ Get count of active (non-discharged) patients assigned to this doctor
    patientcount = models.Patient.objects.filter(
        status=True, assignedDoctorId=doctor.id, discharge_status=False
    ).count()

    # ✅ Get count of approved (active) appointments for this doctor
    appointmentcount = models.Appointment.objects.filter(status=True, doctorId=doctor.id).count()

    # ✅ Get count of fully discharged patients (paid & marked as discharged)
    patientdischarged = models.Patient.objects.filter(
        assignedDoctorId=doctor.id,
        discharge_status=True,  # ✅ Approved for discharge
        payment_done=True  # ✅ Payment completed
    ).count()

    # ✅ Get appointments & related patients for doctor's dashboard table
    appointments = models.Appointment.objects.filter(status=True, doctorId=doctor.id).order_by('-id')
    patientid = [a.patientId for a in appointments]
    patients = models.Patient.objects.filter(status=True, id__in=patientid).order_by('-id')
    appointments = zip(appointments, patients)

    mydict = {
        'patientcount': patientcount,
        'appointmentcount': appointmentcount,
        'patientdischarged': patientdischarged,  # ✅ Corrected discharged patient count
        'appointments': appointments,
        'doctor': doctor,  # ✅ Profile picture support
    }

    return render(request, 'doctor_dashboard.html', context=mydict)

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict={
    'doctor':models.Doctor.objects.get(user_id=request.user.id), #for profile picture of doctor in sidebar
    }
    return render(request,'doctor_patient.html',context=mydict)

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)

    # ✅ Exclude discharged patients
    patients = models.Patient.objects.filter(status=True, payment_done=False,assignedDoctorId=doctor.id, discharge_status=False)

    for patient in patients:
        appointment = models.Appointment.objects.filter(patientId=patient.id, doctorId=doctor.id).first()
        if appointment:
            patient.appointmentDate = appointment.appointmentDate
            patient.time_slot = appointment.time_slot
        else:
            patient.appointmentDate = "Not Scheduled"
            patient.time_slot = "Not Scheduled"

    return render(request, 'doctor_view_patient.html', {'patients': patients, 'doctor': doctor})

@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_discharge_patient_view(request):
    """ Show only fully discharged patients with discharge details under the logged-in doctor """

    doctor = models.Doctor.objects.get(user_id=request.user.id)

    # ✅ Fetch only patients who are fully discharged (discharge approved + payment completed)
    discharged_patient_ids = models.Patient.objects.filter(
        assignedDoctorId=doctor.id,
        discharge_status=False,
        status=True,  
        payment_done=True  
    ).values_list('id', flat=True)

    # ✅ Get discharge details only for those patients under the logged-in doctor
    discharged_details = models.PatientDischargeDetails.objects.filter(patientId__in=discharged_patient_ids)

    return render(request, 'doctor_view_discharge_patient.html', {
        'dischargedpatients': discharged_details,  # Pass discharge details instead of patient objects
        'doctor': doctor
    })


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(
        status=True, doctorId=doctor.id
    ).exclude(description__startswith="Appointment booked during signup")  

    return render(request, 'doctor_view_appointment.html', {
        'appointments': appointments,
        'doctor': doctor
    })


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(
        status=True, doctorId=doctor.id
    ).exclude(description__startswith="Appointment booked during signup")  

    return render(request, 'doctor_delete_appointment.html', {
        'appointments': appointments,
        'doctor': doctor
    })





@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def search_view(request):
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    # whatever user write in search box we get in query
    query = request.GET['query']
    patients=models.Patient.objects.all().filter(status=True,assignedDoctorId=doctor.id).filter(Q(symptoms__icontains=query)|Q(user__first_name__icontains=query))
    return render(request,'doctor_view_patient.html',{'patients':patients,'doctor':doctor})



@login_required(login_url='doctorlogin')  # Ensure only logged-in doctors can access
@user_passes_test(is_doctor)
def doctor_approve_patient_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)  # Get logged-in doctor
    
    # Get patients assigned to this doctor
    patients = models.Patient.objects.filter(status=False,payment_done=False, assignedDoctorId=doctor.id)
    
    return render(request, 'doctor_approve_patient.html', {'patients': patients,'doctor': doctor})



@login_required(login_url='adminlogin')
def doc_approve_patient(request,pk):
    patient=models.Patient.objects.get(id=pk)
    patient.status=True
    patient.save()
    return redirect(reverse('doctor-approve-patient'))

@login_required(login_url='adminlogin')
def doc_reject_patient(request,pk):
    patient=models.Patient.objects.get(id=pk)
    user=models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('doctor-approve-patient')




@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def delete_appointment_view(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.delete()
    doctor=models.Doctor.objects.get(user_id=request.user.id) #for profile picture of doctor in sidebar
    appointments=models.Appointment.objects.all().filter(status=True,doctorId=request.user.id)
    patientid=[]
    for a in appointments:
        patientid.append(a.patientId)
    patients=models.Patient.objects.all().filter(status=True,user_id__in=patientid)
    appointments=zip(appointments,patients)
    return render(request,'doctor_delete_appointment.html',{'appointments':appointments,'doctor':doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_approve_appointment_view(request):
    try:
        # Get the logged-in doctor
        doctor = models.Doctor.objects.get(user=request.user)

        # Fetch appointments assigned to this doctor and exclude those booked during signup
        appointments = models.Appointment.objects.filter(
            status=False, doctorId=doctor.id
        ).exclude(description__startswith="Appointment booked during signup")

        # Fetch patients related to these appointments
        patient_ids = appointments.values_list('patientId', flat=True)
        patients = models.Patient.objects.filter(id__in=patient_ids)

        return render(request, 'doctor_approve_appointment.html', {
            'appointments': appointments,
            'patients': patients,
            'doctor': doctor
        })

    except models.Doctor.DoesNotExist:
        messages.error(request, "Doctor profile not found.")
        return redirect('doctor_dashboard')  # Redirect to a suitable page


@login_required(login_url='adminlogin')
def doc_approve_appointment(request,pk):
    appointment=models.Appointment.objects.get(id=pk)
    appointment.status=True
    appointment.save()
    return redirect(reverse('doctor-approve-appointment'))




#-----------------------------------------------------------------------------------------------------
# import logging
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required, user_passes_test
# from .models import Doctor, Patient, Appointment

# logger = logging.getLogger(__name__)

# @login_required(login_url='doctorlogin')
# @user_passes_test(lambda u: u.groups.filter(name='DOCTOR').exists())
# def doctor_approve_discharge_view(request):
#     doctor = Doctor.objects.filter(user_id=request.user.id).first()
#     if not doctor:
#         messages.error(request, "Doctor profile not found.")
#         return redirect('doctor-dashboard')

#     # Step 1: Fetch active patients (not discharged, not readmitted, and pending payment)
#     active_patients = Patient.objects.filter(
#         assignedDoctorId=doctor.id,
#         status=True,            # Currently admitted
#         discharge_status=False, # Not yet discharged
#         payment_done=False,     # Payment not yet done
#         re_admit=False          # Not marked for re-admission
#     )

#     # Step 2: Fetch re-admitted patients (previously discharged but admitted again)
#     readmitted_patients = Patient.objects.filter(
#         assignedDoctorId=doctor.id,
#         status=True,        # Admitted again
#         re_admit=True       # Marked for re-admission
#     )

#     # Combine both sets of patients
#     patients = active_patients | readmitted_patients

#     # Step 3: Fetch approved appointments for these patients
#     approved_appointments = Appointment.objects.filter(
#         patientId__in=patients.values_list('id', flat=True),
#         status=True  # Appointment approved
#     )

#     logger.debug(f"Doctor: {doctor.get_name}, Patients Found: {patients.count()}")

#     # Step 4: Attach appointment details dynamically to each patient
#     patient_appointments = {appt.patientId: appt for appt in approved_appointments}

#     for patient in patients:
#         appointment = patient_appointments.get(patient.id)
#         patient.appointmentDate = ap
# pointment.appointmentDate if appointment else "Not Scheduled"
#         patient.time_slot = appointment.time_slot if appointment else "Not Scheduled"

#     return render(request, 'doctor_approve_discharge.html', {'patients': patients, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(lambda u: u.groups.filter(name='DOCTOR').exists())
def doctor_approve_discharge_view(request):
    doctor = Doctor.objects.filter(user_id=request.user.id).first()
    if not doctor:
        messages.error(request, "Doctor profile not found.")
        return redirect('doctor-dashboard')

    # Step 1: Fetch active patients (newly admitted or awaiting discharge)
    active_patients = Patient.objects.filter(
        assignedDoctorId=doctor.id,
        status=True,            
        discharge_status=False,  # Not yet discharged
        payment_done=False,      # Payment not yet done
    )

    # Step 2: Fetch re-admitted patients (who have booked a new appointment after previous discharge)
    readmitted_patients = Patient.objects.filter(
        assignedDoctorId=doctor.id,
        status=True,      
        re_admit=True,  # Marked for re-admission
    )

    # Combine both sets of patients
    patients = active_patients | readmitted_patients

    # Step 3: Fetch future appointments
    future_appointments = Appointment.objects.filter(
        patientId__in=patients.values_list('id', flat=True),
        status=True,  # Appointment is approved
        appointmentDate__gte=now().date()  # Only future appointments
    )

    # Create a dictionary to map patients with their future appointments
    patient_future_appointments = {appt.patientId: appt for appt in future_appointments}

    for patient in patients:
        appointment = patient_future_appointments.get(patient.id)

        # Step 4: Allow discharge **only if no future appointments exist**
        patient.has_future_appointment = appointment is not None
        if appointment:
            patient.appointmentDate = appointment.appointmentDate
            patient.time_slot = appointment.time_slot
        else:
            patient.appointmentDate = "No Upcoming Appointment"
            patient.time_slot = "No Upcoming Slot"

    return render(request, 'doctor_approve_discharge.html', {'patients': patients, 'doctor': doctor})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import json
from .models import Patient, Doctor, PatientDischargeDetails
from .forms import PrescriptionForm
from django.utils.timezone import now
from datetime import timedelta

@login_required(login_url='doctorlogin')
def approve_discharge_view(request, pk):
    patient = get_object_or_404(Patient, id=pk)
    doctor = get_object_or_404(Doctor, user=request.user)

    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            medicines_data = request.POST.get('medicines_json', '[]')
            medicines_json = json.loads(medicines_data)

            discharge = form.save(commit=False)
            discharge.patientId = patient.id
            discharge.patientName = patient.get_name
            discharge.assignedDoctorName = doctor.get_name
            discharge.address = patient.address
            discharge.mobile = patient.mobile
            discharge.symptoms = patient.symptoms
            discharge.admitDate = patient.admitDate
            discharge.releaseDate = now().date()

            # ✅ Ensure daySpent is at least 1
            day_difference = (discharge.releaseDate - discharge.admitDate).days
            discharge.daySpent = max(1, day_difference)  # Ensures a minimum of 1 day

            discharge.roomCharge = discharge.daySpent * 2000  # Example room rate
            discharge.doctorFee = 5000
            discharge.OtherCharge = 1000
            discharge.total = discharge.roomCharge + discharge.doctorFee + discharge.medicineCost + discharge.OtherCharge

            discharge.prescribed_medicines = json.dumps(medicines_json)
            discharge.save()

            patient.discharge_status = True
            patient.status = True
            patient.save()

            return redirect('doctor-approve-discharge')

    else:
        form = PrescriptionForm()

    return render(request, 'approve_discharge.html', {'form': form, 'patient': patient})


# @login_required(login_url='doctorlogin')
# @user_passes_test(lambda u: u.groups.filter(name='DOCTOR').exists())
# def approve_discharge_view(request, pk):
#     """ Doctor approves discharge for a patient if they have no future appointments. """
    
#     patient = get_object_or_404(Patient, id=pk)

#     # Ensure the patient is assigned to the logged-in doctor
#     doctor = get_object_or_404(Doctor, user=request.user)
#     if patient.assignedDoctorId != doctor.id:
#         messages.error(request, "You are not authorized to approve this discharge.")
#         return redirect('doctor-approve-discharge')

#     # Check if the patient has any **future** appointments
#     future_appointments = Appointment.objects.filter(
#         patientId=patient.id,
#         appointmentDate__gte=now().date(),  # Future or today’s appointment
#         status=True  # Approved appointments only
#     )

#     if future_appointments.exists():
#         messages.warning(request, "Discharge cannot be approved because the patient has upcoming appointments.")
#         return redirect('doctor-approve-discharge')

#     # ✅ Allow re-admission after discharge
#     patient.discharge_status = True  # Mark as discharged
#     patient.re_admit = False  # Reset re-admit status
#     patient.status = True  # Allow them to log in and book new appointments
#     patient.payment_done = False  # Ensure new payment is required for the next discharge
#     patient.save()

#     messages.success(request, "Patient discharge approved successfully. They can now book new appointments.")
#     return redirect('doctor-approve-discharge')

#-----------------------------------------doctor end -------------------------------------------------------------------------#
#----------------------------------------- patient start -------------------------------------------------------------------------#


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'patient_appointment.html',{'patient':patient})
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from django.contrib import messages
from . import forms, models

# @login_required(login_url='patientlogin')
# @user_passes_test(is_patient)
# def patient_book_appointment_view(request):
#     appointmentForm = forms.PatientAppointmentForm()
#     patient = models.Patient.objects.get(user_id=request.user.id)

#     if request.method == 'POST':
#         appointmentForm = forms.PatientAppointmentForm(request.POST)
#         if appointmentForm.is_valid():
#             doctor = appointmentForm.cleaned_data['doctorId']  # Fetch doctor object
#             appointmentDate = appointmentForm.cleaned_data['appointmentDate']
#             time_slot = appointmentForm.cleaned_data['time_slot']

#             # Ensure only future appointments
#             if appointmentDate < now().date():
#                 messages.error(request, "You cannot book an appointment for a past date.")
#             elif models.Appointment.objects.filter(doctorId=doctor.id, appointmentDate=appointmentDate, time_slot=time_slot).exists():
#                 messages.error(request, "This time slot is already booked. Please choose another one.")
#             else:
#                 appointment = appointmentForm.save(commit=False)
#                 appointment.doctorId = doctor.id  # Store doctor ID as integer
#                 appointment.patientId = patient.id  # Fix: Store Patient model's ID
#                 appointment.doctorName = doctor.user.first_name  # Store doctor's name separately
#                 appointment.patientName = patient.user.first_name
#                 appointment.status = False  # Set status as pending
#                 appointment.save()

#                 messages.success(request, "Appointment request submitted successfully!")
#                 return HttpResponseRedirect('patient-view-appointment')

#     return render(request, 'patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient})

@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    appointmentForm = forms.PatientAppointmentForm()
    patient = models.Patient.objects.get(user_id=request.user.id)

    if request.method == 'POST':
        appointmentForm = forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            doctor = appointmentForm.cleaned_data['doctorId']  # Fetch doctor object
            appointmentDate = appointmentForm.cleaned_data['appointmentDate']
            time_slot = appointmentForm.cleaned_data['time_slot']

            # Ensure only future appointments
            if appointmentDate < now().date():
                messages.error(request, "You cannot book an appointment for a past date.")
            elif models.Appointment.objects.filter(doctorId=doctor.id, appointmentDate=appointmentDate, time_slot=time_slot).exists():
                messages.error(request, "This time slot is already booked. Please choose another one.")
            else:
                appointment = appointmentForm.save(commit=False)
                appointment.doctorId = doctor.id  # Store doctor ID as integer
                appointment.patientId = patient.id  # Store Patient model's ID
                appointment.doctorName = doctor.user.first_name  # Store doctor's name separately
                appointment.patientName = patient.user.first_name
                appointment.status = False  # Set status as pending
                appointment.save()

                # ✅ If patient was discharged earlier, mark them as re-admitted
                if patient.discharge_status:
                    patient.re_admit = True  # Mark for re-admission
                    patient.status = True  # Ensure they appear in active patient lists
                    patient.payment_done = False  # Ensure new payment required after next discharge
                    patient.save()

                messages.success(request, "Appointment request submitted successfully!")
                return HttpResponseRedirect('patient-view-appointment')

    return render(request, 'patient_book_appointment.html', {'appointmentForm': appointmentForm, 'patient': patient})


def patient_view_doctor_view(request):
    doctors=models.Doctor.objects.all().filter(status=True)
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    return render(request,'patient_view_doctor.html',{'patient':patient,'doctors':doctors})



def search_doctor_view(request):
    patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
    
    # whatever user write in search box we get in query
    query = request.GET['query']
    doctors=models.Doctor.objects.all().filter(status=True).filter(Q(department__icontains=query)| Q(user__first_name__icontains=query))
    return render(request,'patient_view_doctor.html',{'patient':patient,'doctors':doctors})


@login_required(login_url='patientlogin')
@user_passes_test(lambda u: u.groups.filter(name='PATIENT').exists())
def patient_view_appointment_view(request):
    patient = get_object_or_404(Patient, user_id=request.user.id)  # Ensure the patient exists
    
    appointments = Appointment.objects.filter(
        patientId=patient.id,  # Use patientId instead of patient
        status=True  # Only show approved appointments
    ).exclude(description__startswith="Appointment booked during signup")
    
    return render(request, 'patient_view_appointment.html', {'appointments': appointments, 'patient': patient})


# @login_required(login_url='patientlogin')
# @user_passes_test(is_patient)
# def patient_discharge_view(request):
#     patient=models.Patient.objects.get(user_id=request.user.id) #for profile picture of patient in sidebar
#     dischargeDetails=models.PatientDischargeDetails.objects.all().filter(patientId=patient.id).order_by('-id')[:1]
#     patientDict=None
#     if dischargeDetails:
#         patientDict ={
#         'is_discharged':True,
#         'patient':patient,
#         'patientId':patient.id,
#         'patientName':patient.get_name,
#         'assignedDoctorName':dischargeDetails[0].assignedDoctorName,
#         'address':patient.address,
#         'mobile':patient.mobile,
#         'symptoms':patient.symptoms,
#         'admitDate':patient.admitDate,
#         'releaseDate':dischargeDetails[0].releaseDate,
#         'daySpent':dischargeDetails[0].daySpent,
#         'medicineCost':dischargeDetails[0].medicineCost,
#         'roomCharge':dischargeDetails[0].roomCharge,
#         'doctorFee':dischargeDetails[0].doctorFee,
#         'OtherCharge':dischargeDetails[0].OtherCharge,
#         'total':dischargeDetails[0].total,
#         }
#         print(patientDict)
#     else:
#         patientDict={
#             'is_discharged':False,
#             'patient':patient,
#             'patientId':request.user.id,
#         }
#     return render(request,'patient_discharge.html',context=patientDict)
@login_required(login_url='patientlogin')
def patient_discharge_view(request):
    patient = get_object_or_404(Patient, user_id=request.user.id)
    dischargeDetails = PatientDischargeDetails.objects.filter(patientId=patient.id).order_by('-id')[:1]

    patientDict = {
        'is_discharged': bool(dischargeDetails),
        'patient': patient,
        'patientId': patient.id,
    }

    if dischargeDetails:
        details = dischargeDetails[0]
        prescribed_medicines = json.loads(details.prescribed_medicines) if details.prescribed_medicines else []

        patientDict.update({
            'patientName': details.patientName,
            'assignedDoctorName': details.assignedDoctorName,
            'address': details.address,
            'mobile': details.mobile,
            'symptoms': details.symptoms,
            'admitDate': details.admitDate,
            'releaseDate': details.releaseDate,
            'daySpent': details.daySpent,
            'medicineCost': details.medicineCost,
            'roomCharge': details.roomCharge,
            'doctorFee': details.doctorFee,
            'OtherCharge': details.OtherCharge,
            'total': details.total,
            'prescribed_medicines': prescribed_medicines,
        })

    return render(request, 'patient_discharge.html', context=patientDict)

#------------------------ PATIENT RELATED VIEWS END ------------------------------
#---------------------------------------------------------------------------------


# # Razorpay Payment Integration
# def create_razorpay_order(request, pk):
#     patient = get_object_or_404(Patient, id=pk)
#     discharge_details = PatientDischargeDetails.objects.filter(patientId=pk).first()
#     if not discharge_details:
#         messages.error(request, "No billing details found for this patient.")
#         return redirect("admin_discharge_patient_view")

#     client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
#     order_amount = discharge_details.total * 100
#     order_currency = "INR"

#     razorpay_order = client.order.create({
#         "amount": order_amount,
#         "currency": order_currency,
#         "payment_capture": "1",
#     })

#     request.session["razorpay_order_id"] = razorpay_order["id"]
#     request.session["razorpay_patient_id"] = pk

#     context = {
#         "razorpay_key": settings.RAZORPAY_KEY_ID,
#         "order_id": razorpay_order["id"],
#         "amount": order_amount,
#         "patient": patient,
#     }

#     return render(request, "razorpay_payment.html", context)

def create_razorpay_order(request, pk):
    patient = get_object_or_404(Patient, id=pk)

    # Fetch the latest discharge details (for multiple discharges)
    discharge_details = PatientDischargeDetails.objects.filter(patientId=pk).order_by('-releaseDate').first()
    
    if not discharge_details:
        messages.error(request, "No billing details found for this patient.")
        return redirect("admin_discharge_patient_view")

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order_amount = discharge_details.total * 100
    order_currency = "INR"

    razorpay_order = client.order.create({
        "amount": order_amount,
        "currency": order_currency,
        "payment_capture": "1",
    })

    request.session["razorpay_order_id"] = razorpay_order["id"]
    request.session["razorpay_patient_id"] = pk

    context = {
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "order_id": razorpay_order["id"],
        "amount": order_amount,
        "patient": patient,
    }

    return render(request, "razorpay_payment.html", context)


from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Patient, Appointment

@csrf_exempt
def payment_success(request):
    patient_id = request.session.get("razorpay_patient_id")
    if not patient_id:
        messages.error(request, "Payment successful but patient ID not found!")
        return redirect("admin-discharge-patient")

    try:
        patient = Patient.objects.get(id=patient_id)

        # Step 1: Mark payment as done
        patient.payment_done = True
        patient.discharge_status = False  # Allow re-signup and new appointments
        patient.save()

        # Step 2: Delete all **non-signup** appointments for this patient
        Appointment.objects.filter(
            patientId=patient.id
        ).exclude(description__startswith="Appointment booked during signup").delete()

        messages.success(request, "Payment successful! All pending appointments have been cleared.")
        return redirect("admin-discharge-patient")

    except Patient.DoesNotExist:
        messages.error(request, "Payment successful, but no matching patient found.")
        return redirect("admin-discharge-patient")



@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_payment_history(request):
    """ View all past payments made by a patient """
    patient = get_object_or_404(Patient, user=request.user)
    
    payment_history = PatientDischargeDetails.objects.filter(patientId=patient.id).order_by('-releaseDate')

    return render(request, "patient_payment_history.html", {
        "payment_history": payment_history,
        "patient": patient  # ✅ Ensure patient is passed to template
    })


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
# from .models import ChatMessage, Patient
# from .forms import ChatMessageForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ChatMessage
# from .forms import ChatMessageForm

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# from .models import ChatMessage, Doctor, Patient, User

# @login_required
# def chat_view(request):
#     user = request.user

#     if hasattr(user, 'patient'):
#         # If the user is a patient, show only doctors in the chat list
#         chat_users = User.objects.filter(doctor__isnull=False)
#     elif hasattr(user, 'doctor'):
#         # If the user is a doctor, show only their assigned patients in the chat list
#         chat_users = User.objects.filter(patient__assignedDoctorId=user.id)
#     else:
#         chat_users = User.objects.none()  # If the user is not a patient or doctor, show no one
    
#     messages = ChatMessage.objects.filter(sender=user) | ChatMessage.objects.filter(receiver=user)
#     messages = messages.order_by('timestamp')

#     return render(request, 'chat.html', {'chat_users': chat_users, 'messages': messages})


# # 💊 Medicine Prescription View
# @login_required
# def prescribe_medicine(request, patient_id):
#     if request.method == 'POST':
#         form = MedicinePrescriptionForm(request.POST)
#         if form.is_valid():
#             prescription = form.save(commit=False)
#             prescription.patient_id = patient_id
#             prescription.doctor = request.user.doctor
#             prescription.save()
#             return redirect('doctor-view-discharge-patient')
#     else:
#         form = MedicinePrescriptionForm()
#     return render(request, 'prescribe_medicine.html', {'form': form})

# # 🏥 Room Booking View
# @login_required
# def book_room(request):
#     if request.method == 'POST':
#         form = RoomBookingForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('room-booking-success')
#     else:
#         form = RoomBookingForm()
    
#     return render(request, 'book_room.html', {'form': form})
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatMessage
from .models import Doctor, Patient, Appointment  # Import Appointment model
import json

@login_required
def chat_view(request):
    """ Displays the chat page with filtered users """
    user = request.user
    chat_users = []

    if hasattr(user, 'patient'):
        chat_users = Doctor.objects.all()  # Patients can chat with all doctors
    elif hasattr(user, 'doctor'):
        doctor = user.doctor
        assigned_patients = Patient.objects.filter(assignedDoctorId=doctor.id)
        appointment_patients = Patient.objects.filter(id__in=Appointment.objects.filter(doctorId=doctor.id).values_list('patientId', flat=True))
        chat_users = assigned_patients.union(appointment_patients)  # Combine both patient groups

    return render(request, 'chat.html', {'chat_users': chat_users})

@login_required
def chat_messages_view(request, receiver_id):
    """ Fetch chat messages between logged-in user and selected user """
    user = request.user
    messages = []

    if hasattr(user, 'patient'):
        patient = user.patient
        doctor = get_object_or_404(Doctor, id=receiver_id)
        messages = ChatMessage.objects.filter(sender_patient=patient, receiver_doctor=doctor) | \
                   ChatMessage.objects.filter(sender_doctor=doctor, receiver_patient=patient)

    elif hasattr(user, 'doctor'):
        doctor = user.doctor
        patient = get_object_or_404(Patient, id=receiver_id)
        messages = ChatMessage.objects.filter(sender_doctor=doctor, receiver_patient=patient) | \
                   ChatMessage.objects.filter(sender_patient=patient, receiver_doctor=doctor)

    messages = messages.order_by('timestamp')
    return JsonResponse({'messages': list(messages.values('message', 'timestamp'))})

@csrf_exempt
@login_required
def send_message(request):
    """ Send a chat message with role-based restrictions """
    if request.method == "POST":
        data = json.loads(request.body)
        message_text = data['message']
        sender = request.user

        receiver_patient = Patient.objects.filter(id=data['receiver_id']).first()
        receiver_doctor = Doctor.objects.filter(id=data['receiver_id']).first()

        if hasattr(sender, 'patient'):
            sender_patient = sender.patient
            if receiver_doctor:
                ChatMessage.objects.create(sender_patient=sender_patient, receiver_doctor=receiver_doctor, message=message_text)
                return JsonResponse({"success": "Message sent successfully."})
            else:
                return JsonResponse({"error": "Invalid receiver. Patients can only chat with doctors."}, status=403)

        elif hasattr(sender, 'doctor'):
            sender_doctor = sender.doctor
            if receiver_patient and receiver_patient.assignedDoctorId == sender_doctor.id:
                ChatMessage.objects.create(sender_doctor=sender_doctor, receiver_patient=receiver_patient, message=message_text)
                return JsonResponse({"success": "Message sent successfully."})
            else:
                return JsonResponse({"error": "Doctors can only chat with their assigned patients."}, status=403)

    return JsonResponse({"error": "Invalid request."}, status=400)
