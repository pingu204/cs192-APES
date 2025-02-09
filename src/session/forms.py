from django import forms
from django.contrib.auth.forms import BaseUserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from session.models import Student

class UserRegisterForm(BaseUserCreationForm):
    username = forms.CharField(
        max_length = 20,
        widget = forms.TextInput(
            attrs = {
                "placeholder" : "Username",
                "class" : "form-control"
            }
        ))

    email = forms.EmailField(
        widget = forms.EmailInput(
            attrs = {
                "placeholder" : "juandelacruz@gmail.com",
                "class" : "form-control"
            }
        )
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs = {
                "placeholder" : "Password",
                "class" : "form-control"
            }
        )
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs = {
                "placeholder" : "Re-enter Password",
                "class" : "form-control"
            }
        )
    )
    
    agreement = forms.BooleanField(
        widget = forms.CheckboxInput(
            attrs = {
                "class" : "form-check-input",
                "id" : "agreement"
            }
        )
    )

    class Meta:
        model = Student
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'agreement',
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
    # commented out bc ff errors shown by javascript eventlisteners
    # def clean_password1(self, *args, **kwargs):
    #     password1 = self.cleaned_data.get('password1')
    #     if len(password1) < 8:
    #         raise forms.ValidationError("Must contain at least 8 alphanumeric characters")
    #     return password1
    
    # def clean_password2(self, *args, **kwargs):
    #     password1 = self.cleaned_data.get('password1')
    #     password2 = self.cleaned_data.get('password2')

    #     if password1 and password2 and password1 != password2:
    #         raise forms.ValidationError("Must match previously entered password")
    #     return password2



class UserAuthenticationForm(AuthenticationForm):
    def clean(self):
        User = get_user_model()
        username_or_email = self.cleaned_data.get("username")
        
        if username_or_email:
            user = User.objects.filter(email=username_or_email).first() or User.objects.filter(username=username_or_email).first()
            if user:
                self.cleaned_data["username"] = user.email # replace input with actual user email
        
        return super().clean()