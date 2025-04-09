from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth.views import LoginView

from django.urls import path
from . import views

urlpatterns = [
   
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('dept', views.department, name='dept'),
    path('doc', views.doctor, name='doc'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),



    path('admindashboard', views.admin_dashboard_view, name='admindashboard'),

    path('doctorclick', views.doctorclick_view,name='doctorclick'),
    path('patientclick', views.patientclick_view,name='patientclick'),

    
    path('doctorsignup', views.doctor_signup_view,name='doctorsignup'),
    path('patientsignup', views.patient_signup_view),

    
    path('adminlogin/', views.admin_login_view, name='adminlogin'),
    path('afterlogin/', views.afterlogin_view, name='afterlogin'),
    path('doctorlogin/', 
         LoginView.as_view(template_name='doctorlogin.html', redirect_authenticated_user=True, next_page='/afterlogin'), 
         name='doctor_login'),
    path('patientlogin', LoginView.as_view(template_name='patientlogin.html'),name='patientlogin'), 
    

    path('admin-doctor', views.admin_doctor_view,name='admin-doctor'),
    path('admin-view-doctor', views.admin_view_doctor_view,name='admin-view-doctor'),
    path('delete-doctor-from-hospital/<int:pk>', views.delete_doctor_from_hospital_view,name='delete-doctor-from-hospital'),
    path('update-doctor/<int:pk>', views.update_doctor_view,name='update-doctor'),
    path('admin-add-doctor', views.admin_add_doctor_view,name='admin-add-doctor'),
    path('admin-approve-doctor', views.admin_approve_doctor_view,name='admin-approve-doctor'),
    path('approve-doctor/<int:pk>', views.approve_doctor_view,name='approve-doctor'),
    path('reject-doctor/<int:pk>', views.reject_doctor_view,name='reject-doctor'),
    path('admin-view-doctor-specialisation',views.admin_view_doctor_specialisation_view,name='admin-view-doctor-specialisation'),


    path('admin-patient', views.admin_patient_view,name='admin-patient'),
    path('admin-view-patient', views.admin_view_patient_view,name='admin-view-patient'),
    path('delete-patient-from-hospital/<int:pk>', views.delete_patient_from_hospital_view,name='delete-patient-from-hospital'),
    path('update-patient/<int:pk>', views.update_patient_view,name='update-patient'),
    path('admin-add-patient', views.admin_add_patient_view,name='admin-add-patient'),
    path('admin-approve-patient', views.admin_approve_patient_view,name='admin-approve-patient'),
    path('approve-patient/<int:pk>', views.approve_patient_view,name='approve-patient'),
    path('reject-patient/<int:pk>', views.reject_patient_view,name='reject-patient'),
    path('admin-discharge-patient', views.admin_discharge_patient_view,name='admin-discharge-patient'),
    path('discharge-patient/<int:pk>', views.discharge_patient_view,name='discharge-patient'),
    path('download-pdf/<int:pk>', views.download_pdf_view,name='download-pdf'),

    path('create-razorpay-order/<int:pk>/', views.create_razorpay_order, name='create-razorpay-order'),
    # Handle payment success (redirected after Razorpay checkout)
    path('payment-success/', views.payment_success, name='payment-success'),

    
    path('admin-appointment', views.admin_appointment_view,name='admin-appointment'),
    path('admin-view-appointment', views.admin_view_appointment_view,name='admin-view-appointment'),
    path('admin-add-appointment', views.admin_add_appointment_view,name='admin-add-appointment'),
    path('admin-approve-appointment', views.admin_approve_appointment_view,name='admin-approve-appointment'),
    path('approve-appointment/<int:pk>', views.approve_appointment_view,name='approve-appointment'),
    path('reject-appointment/<int:pk>', views.reject_appointment_view,name='reject-appointment'),


#---------FOR DOCTOR RELATED URLS-------------------------------------

    path('doctor-dashboard/', views.doctor_dashboard_view, name='doctor-dashboard'),
    path('search', views.search_view,name='search'),

    path('doctor-patient', views.doctor_patient_view,name='doctor-patient'),
    path('doctor-view-patient', views.doctor_view_patient_view,name='doctor-view-patient'),
    path('doctor-view-discharge-patient',views.doctor_view_discharge_patient_view,name='doctor-view-discharge-patient'),
    path('doctor-approve-patient', views.doctor_approve_patient_view,name='doctor-approve-patient'),
    path('doc-approve-patient/<int:pk>', views.doc_approve_patient,name='doc-approve-patient'),
    path('doc-reject-patient/<int:pk>', views.doc_reject_patient,name='doc-reject-patient'),


    path('doctor-appointment', views.doctor_appointment_view,name='doctor-appointment'),
    path('doctor-view-appointment', views.doctor_view_appointment_view,name='doctor-view-appointment'),
    path('doctor-delete-appointment',views.doctor_delete_appointment_view,name='doctor-delete-appointment'),
    path('doctor-approve-appointment',views.doctor_approve_appointment_view,name='doctor-approve-appointment'),
    path('doc-approve-appointment/<int:pk>', views.doc_approve_appointment,name='doc-approve-appointment'),
    path('delete-appointment/<int:pk>', views.delete_appointment_view,name='delete-appointment'),

    path('approve-discharge/<int:pk>/', views.approve_discharge_view, name="approve-discharge"),



    path('doctor-approve-discharge/', views.doctor_approve_discharge_view, name='doctor-approve-discharge'),
    path('approve-discharge/<int:pk>/', views.approve_discharge_view, name='approve-discharge'),




#---------FOR PATIENT RELATED URLS-------------------------------------


    path('patient-dashboard', views.patient_dashboard_view,name='patient-dashboard'),
    path('patient-appointment', views.patient_appointment_view,name='patient-appointment'),
    path('patient-book-appointment', views.patient_book_appointment_view,name='patient-book-appointment'),
    path('patient-view-appointment', views.patient_view_appointment_view,name='patient-view-appointment'),
    path('patient-view-doctor', views.patient_view_doctor_view,name='patient-view-doctor'),
    path('searchdoctor', views.search_doctor_view,name='searchdoctor'),
    path('patient-discharge', views.patient_discharge_view,name='patient-discharge'),
    path('patient-payment-history', views.patient_payment_history,name='patient-payment-history'),




    path('chat/', views.chat_view, name="chat-view"),
    path('chat/messages/<int:receiver_id>/', views.chat_messages_view, name="chat_messages"),
    path('chat/send/', views.send_message, name="send_message"),

     path('book-room/', views.book_room, name='book-room'),
    path('book-room/success/', views.room_booking_success, name='room-booking-success'),
    path('bookings/', views.room_booking_list, name='room-booking-list'),
    path('booking/<int:booking_id>/', views.room_booking_detail, name='room-booking-detail'),
    path('add-room/', views.add_room, name='add-room'),
    path('room/', views.room, name='room'),


    path('rooms/', views.room_list, name='room-list'),
    path('patient-rooms/', views.room_view, name='patient-rooms'),
    path('bookings/delete/<int:booking_id>/', views.delete_booking, name='delete-booking'),
    path('rooms/<int:room_id>/occupied/', views.occupied_details, name='occupied-details'),



    path('emergency-alert/', views.emergency_alert_view, name='emergency-alert'),
    path('view-emergency-alerts/', views.view_emergency_alerts, name='view-emergency-alerts'),
    path('resolve-alert/<int:alert_id>/', views.resolve_alert, name='resolve-alert'),
    
    path('request-ambulance/', views.request_ambulance, name='request_ambulance'),
    path('ambulance/', views.ambulance, name='ambulance'),

    path('ambulance-status/', views.ambulance_status, name='ambulance_status'),
    path('manage-ambulance/', views.manage_ambulance_requests, name='manage_ambulance_requests'),
    path('update-ambulance/<int:booking_id>/<str:status>/', views.update_ambulance_status, name='update_ambulance_status'),

    path('labtest/', views.labtest, name='labtest'),
    path('book-lab-test/', views.book_lab_test, name='book_lab_test'),
    path('view-booked-tests/', views.view_booked_tests, name='view_booked_tests'),
    path('upload-lab-report/<int:test_id>/', views.upload_lab_report, name='upload_lab_report'),
    path('lab-report/<int:patientId>/', views.view_lab_report, name='view-lab-report'),
    path('patient-lab-tests/', views.patient_lab_tests_view, name='patient_lab_tests'),


    path('doctor-appointment-management/', views.doctor_appointment_management, name='doctor-appointment-management'),




]