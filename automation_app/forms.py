# automation_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='First name')
    last_name = forms.CharField(max_length=30, required=True, help_text='Last name')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2', 'role']


class UserProfileForm(UserChangeForm):
    password = None  # Exclude password field from the form

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

class UserPasswordForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']