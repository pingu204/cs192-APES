from django import forms
from django.contrib.auth.forms import BaseUserCreationForm
from django.contrib.auth.models import User
from session.models import Student

class UserRegisterForm(BaseUserCreationForm):
    username = forms.CharField(max_length=20)
    email = forms.EmailField()
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Re-type Password",widget=forms.PasswordInput)

    class Meta:
        model = Student
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]
    # not needed bc set email as unique
    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if email and self._meta.model.objects.filter(email__iexact=email).exists():
    #         raise forms.ValidationError("Email already exists in database") 
    #     return email
    # # reference:
    # # Antheiz. Stack Overflow.
    # # Last accessed: 02/06/2025
    # # https://stackoverflow.com/questions/60110304/how-to-raise-validationerror-in-django-model-if-email-exist

    def clean_password1(self, *args, **kwargs):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise forms.ValidationError("Must contain at least 8 alphanumeric characters")
        return password1
    
    def clean_password2(self, *args, **kwargs):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Must match previously-typed password")
        return password2
