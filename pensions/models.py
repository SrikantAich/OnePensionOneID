from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_posted']  # latest first

    def __str__(self):
        return self.title

class OTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - OTP: {self.code} - Used: {self.is_used}"
# ✅ Custom User Model with Role
class User(AbstractUser):
    ROLE_CHOICES = [
        ('pensioner', 'Pensioner'),
        ('admin', 'Admin'),
        ('govt_official', 'Government Official')
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    force_password_reset = models.BooleanField(default=True)  # ✅ Enforce password reset on first login
    signup_email_sent = models.BooleanField(default=False)    # ✅ Track if signup email was sent

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",  # ✅ Fix for clash
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",  # ✅ Fix for clash
        blank=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


# ✅ Pensioner Model
class Pensioner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pension_id = models.CharField(max_length=20, unique=True)
    aadhaar_number = models.CharField(max_length=12, unique=True)
    pan_number = models.CharField(max_length=10, unique=True)
    date_of_birth = models.DateField()
    bank_account = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    pension_status = models.CharField(
        max_length=10,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive')]
    )

    def __str__(self):
        return f"{self.user.username} (Pension ID: {self.pension_id})"


# ✅ Pension Model
class Pension(models.Model):
    pensioner = models.OneToOneField(Pensioner, on_delete=models.CASCADE)
    pension_type = models.CharField(
        max_length=50,
        choices=[('Old Age', 'Old Age'), ('Disability', 'Disability'), ('Family', 'Family')]
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('Ongoing', 'Ongoing'), ('Completed', 'Completed')]
    )

    def __str__(self):
        return f"{self.pensioner.user.username} - {self.pension_type} ({self.status})"


# ✅ Pension Transactions Model
# models.py
class PensionTransaction(models.Model):
    pensioner = models.ForeignKey(Pensioner, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.CharField(max_length=20)  # e.g., "March 2025"
    status = models.CharField(
        max_length=20,
        choices=(('Credited', 'Credited'), ('Pending', 'Pending'))
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pensioner.user.username} - {self.month} - ₹{self.amount}"


from django.db import models
from django.utils import timezone

class LifeCertificate(models.Model):
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
    ]

    pensioner = models.ForeignKey(Pensioner, on_delete=models.CASCADE)
    certificate = models.FileField(upload_to='life_certificates/')
    live_photo = models.ImageField(upload_to='life_certificates/photos/', blank=True, null=True)  # 📸 New Field
    submitted_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Submitted')
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.pensioner.user.username} - {self.status} ({self.submitted_at.strftime('%Y-%m-%d')})"

# models.py

class Grievance(models.Model):
    SUBJECT_CHOICES = [
        ('Pension not credited', 'Pension not credited'),
        ('Incorrect pension amount', 'Incorrect pension amount'),
        ('Life certificate issue', 'Life certificate issue'),
        ('Bank detail update', 'Bank detail update'),
        ('Document verification delay', 'Document verification delay'),
        ('Other', 'Other'),
    ]

    pensioner = models.ForeignKey(Pensioner, on_delete=models.SET_NULL, null=True)
    subject = models.CharField(max_length=255, choices=SUBJECT_CHOICES)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Resolved', 'Resolved')],
        default='Open'
    )
    remarks = models.TextField(blank=True, null=True)  # ✅ New field for admins only
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Grievance by {self.pensioner.user.username} - {self.status}"

# ✅ OTP Model for Forgot Password Flow
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    def __str__(self):
        return f"OTP for {self.user.username} - {self.code} ({'Used' if self.is_used else 'Unused'})"
