from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Grievance, LifeCertificate
from django.contrib.auth.forms import PasswordChangeForm
from django import forms


from django import forms
from .models import LifeCertificate

class LifeCertificateForm(forms.ModelForm):
    class Meta:
        model = LifeCertificate
        fields = ['certificate']


class GrievanceForm(forms.ModelForm):
    class Meta:
        model = Grievance
        fields = ['subject', 'description']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
class UserIDForm(forms.Form):
    username = forms.CharField(label='User ID', max_length=150)

class OTPForm(forms.Form):
    otp = forms.CharField(label='Enter OTP', max_length=6)

class NewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label='New Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
            raise forms.ValidationError("Passwords do not match.")


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

class LoginForm(AuthenticationForm):
    pass



class PasswordResetForm(PasswordChangeForm):
    class Meta:
        fields = ['old_password', 'new_password1', 'new_password2']
