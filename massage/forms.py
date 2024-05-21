from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from .models import Role, Employee

class UserAdminForm(UserCreationForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all())

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('role',)

class LoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            print("Invalid username or password")
            raise ValidationError("Invalid username or password")
        self.user = user
        return self.cleaned_data
        
class EmployeeForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Employee
        fields = ["image", "name", "phone", "address", "age", "username", "password"]
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Username already exists")
        return username

    def save(self, commit=True):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = User.objects.create(username=username, password=make_password(password))
        self.instance.user = user
        return super(EmployeeForm, self).save(commit=commit)