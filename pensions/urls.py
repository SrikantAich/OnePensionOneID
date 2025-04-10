from django.urls import path
from . import views
from .views import (
    signup_view, login_view, logout_view, home,
    password_reset_view, forgot_password_view,
    otp_verify_view, otp_reset_password_view,
    submit_grievance, grievance_list
)
from django.views.generic import TemplateView

urlpatterns = [
    path('', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('home/', home, name='home'),
    path('logout/', logout_view, name='logout'),


    # Password + OTP
    path('reset-password/', password_reset_view, name='password_reset'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('otp-verify/', otp_verify_view, name='otp_verify'),
    path('reset-via-otp/', otp_reset_password_view, name='otp_reset_password'),

    # Grievance
    # path('dashboard/', dashboard_view, name='dashboard'),
    path('submit/', submit_grievance, name='submit_grievance'),
    path('list/', grievance_list, name='grievance_list'),

    path('transactions/', views.pension_transactions, name='pension_transactions'),
    path('life-certificate/', views.upload_life_certificate, name='life_certificate'),
    path('life-certificate/success/', TemplateView.as_view(template_name='life_certificate_success.html'), name='life_certificate_success'),
    path('life-certificate/history/', views.life_certificate_history, name='life_certificate_history'),



]
