import logging
import random
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import localtime, now
from django.utils.crypto import get_random_string
from .forms import LoginForm, PasswordResetForm, LifeCertificateForm
from .models import Pensioner
from .models import OTP
from django.utils.timezone import now, localtime
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from .models import OTP
import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import GrievanceForm
from .models import Grievance, Pensioner
from django.contrib.auth.decorators import login_required
from .models import LifeCertificate
from django.shortcuts import render, get_object_or_404
from .models import Pensioner

@login_required
def life_certificate_history(request):
    pensioner = get_object_or_404(Pensioner, user=request.user)
    certificates = LifeCertificate.objects.filter(pensioner=pensioner).order_by('-submitted_at')
    return render(request, 'life_certificate_history.html', {'certificates': certificates})

logger = logging.getLogger(__name__)
User = get_user_model()

def is_valid_aadhaar(aadhaar_number):
    return aadhaar_number.isdigit() and len(aadhaar_number) >= 12

def home(request):
    return render(request, 'home.html')

# --------------------- SIGNUP -------------------------
def signup_view(request):
    if request.method == "POST":
        if request.POST.get("accept_invite") == "1":
            aadhaar_number = request.session.get('signup_aadhaar')
            user_id = request.session.get('signup_user_id')

            try:
                user = User.objects.get(id=user_id)
                pensioner = Pensioner.objects.get(user=user)

                preset_password = User.objects.make_random_password()
                user.set_password(preset_password)
                user.force_password_reset = True
                user.signup_email_sent = True
                user.save()

                pensioner.pension_status = "Active"
                pensioner.save()

                subject = "One Pension One ID - Your Login Credentials"
                email_message = f"""
Dear {user.username},

Welcome to the One Pension One ID portal. Your account has been successfully created.

Here are your login credentials:

    Username: {user.username}
    Password: {preset_password}

🛡️ Security Instructions:
- Please log in immediately and change your password.
- Do not share your login credentials with anyone.
- If you suspect any unauthorized access, contact support immediately.

📌 Note:
You will be prompted to reset your password on your first login for security purposes.

Thank you for being a valued pensioner.

Warm regards,  
One Pension One ID Team
                """.strip()

                send_mail(subject, email_message, settings.EMAIL_HOST_USER, ['1062000k@gmail.com'], fail_silently=False)

                request.session.pop('signup_aadhaar', None)
                request.session.pop('signup_user_id', None)

                messages.success(request, "Login credentials have been sent to your email.")
                return redirect('login')

            except Exception as e:
                logger.exception("Error sending invite email.")
                return render(request, 'signup.html', {
                    'modal': {
                        'title': 'Error',
                        'message': 'Something went wrong while creating your account. Please try again.',
                        'type': 'error'
                    }
                })

        aadhaar_number = request.POST.get("aadhaar_number", "").strip()

        if not is_valid_aadhaar(aadhaar_number):
            return render(request, 'signup.html', {
                'modal': {
                    'title': 'Invalid Aadhaar',
                    'message': 'Please enter a valid 12-digit Aadhaar number.',
                    'type': 'error'
                }
            })

        try:
            pensioner = Pensioner.objects.get(aadhaar_number=aadhaar_number)
            user = pensioner.user

            if user.signup_email_sent:
                return render(request, 'signup.html', {
                    'modal': {
                        'title': 'Already Registered',
                        'message': 'Signup email has already been sent. Please login.',
                        'type': 'error'
                    }
                })

            if not user.email:
                return render(request, 'signup.html', {
                    'modal': {
                        'title': 'Missing Email',
                        'message': 'No email is linked to this Aadhaar. Please contact support.',
                        'type': 'error'
                    }
                })

            request.session['signup_aadhaar'] = aadhaar_number
            request.session['signup_user_id'] = user.id

            return render(request, 'signup.html', {
                'modal': {
                    'title': 'You are Invited!',
                    'message': f"{user.username}, you are eligible to join. Would you like to receive your login credentials via email?",
                    'type': 'invite'
                }
            })

        except Pensioner.DoesNotExist:
            return render(request, 'signup.html', {
                'modal': {
                    'title': 'Not Found',
                    'message': 'No pensioner found with that Aadhaar number.',
                    'type': 'error'
                }
            })

    return render(request, 'signup.html')

# ---------------------- LOGIN ------------------------
def login_view(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f"User {user.username} logged in successfully.")

            login_time = localtime(now()).strftime("%Y-%m-%d %H:%M:%S")
            user_ip = request.META.get('REMOTE_ADDR', 'Unknown')

            subject = f"One Pension One ID - Login Alert for {user.username}"
            email_message = f"""
User {user.username} has logged in to the portal.

🕒 Time: {login_time}
🌐 IP Address: {user_ip}

📌 If this login was not performed by the pensioner, please take immediate action by resetting the password or contacting support.

Best regards,  
One Pension One ID Security Team
            """.strip()
            send_mail(subject, email_message, settings.EMAIL_HOST_USER, ['1062000k@gmail.com'], fail_silently=False)

            if user.force_password_reset:
                messages.info(request, "Please reset your password before continuing.")
                return redirect('password_reset')
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")

# ------------------ PASSWORD RESET --------------------
@login_required
def password_reset_view(request):
    if request.method == "POST":
        form = PasswordResetForm(request.user, request.POST)
        if form.is_valid():
            try:
                user = form.save()
                user.force_password_reset = False
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password has been reset successfully.")
                logger.info(f"User {user.username} reset password successfully.")

                reset_time = localtime(now()).strftime("%Y-%m-%d %H:%M:%S")
                subject = f"One Pension One ID - Password Reset Notification"
                email_message = f"""
User {user.username} has successfully reset their password.

🕒 Time: {reset_time}
📌 If this action was not initiated by the pensioner, please secure the account immediately.

Security Tips:
- Do not reuse old passwords.
- Never share your password with anyone.
- Use strong and unique passwords for each site.

Sincerely,  
One Pension One ID Security Team
                """.strip()
                send_mail(subject, email_message, settings.EMAIL_HOST_USER, ['1062000k@gmail.com'], fail_silently=False)

                return redirect('home')

            except Exception as e:
                logger.exception(f"Error during password reset for {request.user.username}")
                messages.error(request, "An error occurred during password reset. Please try again.")
    else:
        form = PasswordResetForm(request.user)
    return render(request, 'password_reset.html', {'form': form})

# ------------------ FORGOT PASSWORD (OTP - Model Based) ---------------------
def forgot_password_view(request):
    show_modal = False
    if request.method == "POST":
        username = request.POST.get("username")
        try:
            user = User.objects.get(username=username)

            # Expire previous OTPs
            OTP.objects.filter(user=user, is_used=False).update(is_used=True)

            # Generate and store new OTP
            otp_code = random.randint(100000, 999999)
            OTP.objects.create(user=user, code=otp_code)

            # Send email
            subject = "One Pension One ID - OTP for Password Reset"
            email_message = f"""
Dear {user.username},

You have requested to reset your password.

🔐 OTP: {otp_code}

This OTP is valid for one-time use and expires shortly.
If you did not request this, please contact support immediately.

🕒 Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
🌐 IP Address: {get_client_ip(request)}

Sincerely,  
One Pension One ID Team
            """.strip()

            send_mail(subject, email_message, settings.EMAIL_HOST_USER, ['1062000k@gmail.com'])

            request.session['otp_user_id'] = user.id
            messages.success(request, "An OTP has been sent to your email. Click OK to proceed.")
            show_modal = True

        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return render(request, 'forgot_password.html', {'show_modal': show_modal})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')
def otp_verify_view(request):
    user_id = request.session.get("otp_user_id")
    if not user_id:
        return redirect("forgot_password")

    show_modal = False

    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        try:
            user = User.objects.get(id=user_id)
            otp_entry = OTP.objects.filter(user=user, is_used=False).latest("created_at")

            if str(otp_entry.code) == entered_otp:
                otp_entry.is_used = True
                otp_entry.save()
                return redirect("otp_reset_password")
            else:
                messages.error(request, "Invalid OTP.")
                show_modal = True

        except (User.DoesNotExist, OTP.DoesNotExist):
            messages.error(request, "OTP session expired or invalid.")
            show_modal = True

    return render(request, "otp_verify.html", {"show_modal": show_modal})




def is_strong_password(password):
    """Validates password strength."""
    return (
        len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'\d', password) and
        re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    )

def otp_reset_password_view(request):
    user_id = request.session.get("otp_user_id")
    if not user_id:
        return redirect('forgot_password')

    try:
        user = User.objects.get(id=user_id)
        otp_entry = OTP.objects.filter(user=user, is_used=True).latest('created_at')
    except (User.DoesNotExist, OTP.DoesNotExist):
        messages.error(request, "Something went wrong. Please try again.")
        return redirect('forgot_password')

    # Check OTP expiration (15 minutes)
    otp_age = (now() - otp_entry.created_at).total_seconds()
    if otp_age > 900:  # 15 * 60 seconds
        messages.error(request, "Your OTP has expired. Please request a new one.")
        return redirect('forgot_password')

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif not is_strong_password(new_password):
            messages.error(request, "Password must be at least 8 characters long and include uppercase, lowercase, number, and symbol.")
        else:
            user.set_password(new_password)
            user.force_password_reset = False
            user.save()

            # Send security alert email
            user_ip = request.META.get('REMOTE_ADDR', 'Unknown')
            reset_time = localtime(now()).strftime("%Y-%m-%d %H:%M:%S")

            subject = "One Pension One ID - Password Reset Confirmation"
            email_message = f"""
Dear {user.username},

This is to inform you that the password for your account on the One Pension One ID portal has been successfully reset.

🔐 Account Details:
- Username: {user.username}
- Time of Reset: {reset_time}
- IP Address: {user_ip}

If this password reset was initiated by you, no further action is required.

---

⚠️ Important Security Advice:

- Never share your password or OTP with anyone — not even government officials.
- Use a strong and unique password combining uppercase, lowercase, numbers, and symbols.
- Do not reuse passwords from other platforms.
- Always log out after using public/shared devices.

If you did NOT initiate this password reset, please contact our support team immediately and change your password again as a precaution.

---

Thank you for using One Pension One ID.  
Your security is our top priority.

Warm regards,  
One Pension One ID Security Team  
Email: support@onepension.com 

""".strip()

            send_mail(subject, email_message, settings.EMAIL_HOST_USER, ['1062000k@gmail.com'], fail_silently=False)

            messages.success(request, "Your password has been reset successfully. You can now log in.")
            return redirect('login')

    return render(request, 'otp_reset_password.html')

 
 
    user_id = request.session.get("otp_user_id")
    if not user_id:
        return redirect('forgot_password')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('forgot_password')

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        if new_password and new_password == confirm_password:
            user.set_password(new_password)
            user.force_password_reset = False
            user.save()
            messages.success(request, "Your password has been reset successfully. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, 'otp_reset_password.html')



@login_required
def submit_grievance(request):
    try:
        pensioner = Pensioner.objects.get(user=request.user)
    except Pensioner.DoesNotExist:
        messages.error(request, "Only pensioners can file grievances.")
        return redirect('dashboard')  # or any fallback

    if request.method == 'POST':
        form = GrievanceForm(request.POST)
        if form.is_valid():
            grievance = form.save(commit=False)
            grievance.pensioner = pensioner
            grievance.save()
            messages.success(request, "Grievance submitted successfully!")
            return redirect('grievance_list')
    else:
        form = GrievanceForm()

    return render(request, 'submit_grievance.html', {'form': form})


@login_required
def grievance_list(request):
    try:
        pensioner = Pensioner.objects.get(user=request.user)
        grievances = Grievance.objects.filter(pensioner=pensioner).order_by('-created_at')
    except Pensioner.DoesNotExist:
        grievances = []

    return render(request, 'grievance_list.html', {'grievances': grievances})



from django.contrib.auth.decorators import login_required
from .models import PensionTransaction
from datetime import timedelta

@login_required
def pension_transactions(request):
    try:
        pensioner = Pensioner.objects.get(user=request.user)
        transactions = PensionTransaction.objects.filter(pensioner=pensioner).order_by('-created_at')

    except Pensioner.DoesNotExist:
        transactions = []

    return render(request, 'pension_transaction_history.html', {'transactions': transactions})

import base64
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404


@login_required
def upload_life_certificate(request):
    pensioner = get_object_or_404(Pensioner, user=request.user)

    if request.method == 'POST':
        form = LifeCertificateForm(request.POST, request.FILES)
        if form.is_valid():
            life_certificate = form.save(commit=False)
            life_certificate.pensioner = pensioner

            # Handle captured live photo
            data_url = request.POST.get('captured_photo')
            if data_url:
                format, imgstr = data_url.split(';base64,')  # format ~= data:image/X,
                ext = format.split('/')[-1]
                file_name = f"live_photo_{pensioner.id}.{ext}"
                life_certificate.live_photo = ContentFile(base64.b64decode(imgstr), name=file_name)

            life_certificate.save()
            return redirect('life_certificate_success')
    else:
        form = LifeCertificateForm()

    return render(request, 'upload_life_certificate.html', {'form': form})

from datetime import timedelta
from django.shortcuts import render
from .models import Pensioner, PensionTransaction, Grievance, LifeCertificate, Announcement

def home(request):
    user = request.user

    # Get Pensioner instance for the logged-in user
    pensioner = Pensioner.objects.get(user=user)

    # Last Pension Credit
    last_transaction = PensionTransaction.objects.filter(pensioner=pensioner).order_by('-month').first()

    # Pending Grievances
    pending_grievances = Grievance.objects.filter(pensioner=pensioner, status='Open').count()

    # Life Certificate Verification Pending
    pending_verifications = LifeCertificate.objects.filter(status='Submitted').count()

    # Last Submitted Life Certificate & Next Due Date
    last_life_certificate = LifeCertificate.objects.filter(pensioner=pensioner).order_by('-submitted_at').first()
    next_due_date = None
    if last_life_certificate:
        next_due_date = last_life_certificate.submitted_at + timedelta(days=335)


    announcements = Announcement.objects.all()[:5]
    context = {
        'last_transaction': last_transaction,
        'pending_grievances': pending_grievances,
        'pending_verifications': pending_verifications,
        'last_life_certificate': last_life_certificate,
        'next_due_date': next_due_date,
        'last_transaction_date': last_transaction.created_at if last_transaction else None,
        'announcements': announcements,
    }

    return render(request, 'home.html', context)
