import os
import sys
import django

# ✅ Ensure the project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

# ✅ Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "one_pension_one_id.settings")

# ✅ Initialize Django
django.setup()

from django.contrib.auth import get_user_model
from pensions.models import Pensioner
from datetime import date

User = get_user_model()

users_to_create = []
pensioners_to_create = []

for i in range(1, 50):
    username = f"testuser{i}"
    email = f"test{i}@example.com"
    password = "Pension@123"

    if not User.objects.filter(username=username).exists():
        user = User(username=username, email=email, role="pensioner")
        user.set_password(password)
        users_to_create.append(user)

User.objects.bulk_create(users_to_create)

for user in User.objects.filter(username__startswith="testuser"):
    pensioners_to_create.append(
        Pensioner(
            user=user,
            pension_id=f"100{user.id}",
            aadhaar_number=f"1234567890{user.id}",
            pan_number=f"ABCDE123{user.id}",
            date_of_birth=date(1960, 1, 1),
            bank_account=f"9876543210{user.id}",
            ifsc_code="SBIN0001234",
            pension_status="Inactive"
        )
    )

Pensioner.objects.bulk_create(pensioners_to_create)

print("✅ Testing Users with Pensioner Role Successfully Created!")
