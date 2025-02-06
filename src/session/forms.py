from django import forms
from django.contrib.auth.forms import BaseUserCreationForm
from django.contrib.auth.models import User

""" class UserRegisterForm(BaseUserCreationForm):
    username = forms.CharField()
    email = forms.EmailField()
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Re-type Password",widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]
    
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
 """