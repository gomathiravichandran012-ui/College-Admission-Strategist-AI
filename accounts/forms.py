
from django import forms
from django.contrib.auth.models import User
from students.models import StudentProfile


class StudentRegistrationForm(forms.Form):

    full_name = forms.CharField(
        max_length=100,
        label="Full Name"
    )

    username = forms.CharField(
        max_length=150,
        label="Username"
    )

    email = forms.EmailField(
        label="Email Address"
    )

    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="Password"
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data


class StudentProfileForm(forms.ModelForm):

    class Meta:
        model = StudentProfile

        fields = [
            'full_name',
            'date_of_birth',
            'phone_number',
            'state',
            'education_stream',
            'percentage',
        ]

        widgets = {
            'full_name': forms.TextInput(
                attrs={'placeholder': 'Enter your full name'}
            ),
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'phone_number': forms.TextInput(
                attrs={'placeholder': 'Enter phone number'}
            ),
            'state': forms.TextInput(
                attrs={'placeholder': 'Enter your state'}
            ),
            'percentage': forms.NumberInput(
                attrs={
                    'placeholder': 'Enter percentage',
                    'step': '0.01',
                    'min': '0',
                    'max': '100'
                }
            ),
        }
