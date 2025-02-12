from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from session.models import Student
import re

class UserRegisterForm(UserCreationForm):
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
        'no_value': ("No inputted password."),
        'no_number': ("Password must contain at least one number."),
        'no_capital': ("Password must contain at least one capital letter."),
    }
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
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
            
        elif password1 is None or password2 is None:
            raise forms.ValidationError(self.error_messages['no_value'], code= 'no_value')
        
        elif not re.search(r'\d', password1):
            raise forms.ValidationError('no_number', code="no_number")

        # Check for both capital and small letters
        elif not re.search(r'[A-Z]', password1) or not re.search(r'[a-z]', password1):
            raise forms.ValidationError('no_capital', code='no_capital')
        
        else:
            return password2

        
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


# UserAuthenticationForm class to override AuthenticationForm since logins are allowed for BOTH username and email
# not just username/email alone (which is already supported by AuthenticationForm)
class UserAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        max_length = 40,
        label = "Username | Email Address",
        widget = forms.TextInput(
            attrs = {
                "placeholder" : "Username or Email Address",
                "class" : "form-control"
            }
        ))

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs = {
                "placeholder" : "Password",
                "class" : "form-control"
            }
        )
    )

    def clean(self):
        User = get_user_model()
        username_or_email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        # if user either fails to fill up username/email field or password field, error is raised    
        if not username_or_email or not password:
            raise ValidationError("Both fields are required.") 
            
        # find user by either username or email since logging in permits both as preferred by the user (given that its valid ofc)    
        user = User.objects.filter(email=username_or_email).first() or User.objects.filter(username=username_or_email).first()
        
        # if invalid inputted email/username
        if not user:
            # TEST: print("The account does not exist. Please sign up.")
            raise ValidationError("The account does not exist. Please sign up.")
        
        # TEST: print(user, user.username)


        # authenticate using user.email since we set USERNAME_FIELD = "email" in models.py
        authenticated_user = authenticate(username=user.email, password=password)

        # if valid user email/username but password is wrong, raise error
        if not authenticated_user:
            # TEST: print("The password you've entered is incorrect. Please try again.")
            raise ValidationError("The password you've entered is incorrect. Please try again.")
                    
        self.cleaned_data["username"] = user.email

        return self.cleaned_data
    
    def get_user(self):
        return self.user_cache