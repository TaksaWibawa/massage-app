from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from .models import Role, Employee, Service, Assignment


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
            raise ValidationError("Invalid username or password")
        self.user = user
        return self.cleaned_data


class EmployeeForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'name'}))
    phone = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'phone'}))
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'address'}))
    age = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'age'}))
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password'}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control', 'id': 'image-upload'}))

    class Meta:
        model = Employee
        fields = ["image", "name", "phone",
                  "address", "age", "username", "password"]

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        image = cleaned_data.get('image')

        if image is None:
            raise ValidationError("Please upload an image")

        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already exists")

        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            password=self.cleaned_data.get('password'),
        )
        user.save()
        self.instance.user = user
        return super(EmployeeForm, self).save(commit=commit)


class ServiceForm(forms.ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'name'}))
    price = forms.FloatField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'price'}))
    duration = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'duration'}))
    image = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control', 'id': 'image-upload'}))

    class Meta:
        model = Service
        fields = ["name", "price", "duration", "image"]

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        duration = cleaned_data.get('duration')
        image = cleaned_data.get('image')

        if price and duration:
            if price == 0 and duration > 0:
                raise ValidationError("Price must be greater than 0 if duration is greater than 0")
            if price > 0 and duration == 0:
                raise ValidationError("Duration must be greater than 0 if price is greater than 0")
        
        if image is None:
            raise ValidationError("Please upload an image")
        return cleaned_data

    def save(self, commit=True):
        return super(ServiceForm, self).save(commit=commit)


class AssignmentForm(forms.ModelForm):
    service = forms.ModelChoiceField(queryset=Service.objects.all(), empty_label='', initial=None, required=True,
                                     widget=forms.Select(attrs={'class': 'form-control form-select', 'id': 'service'}))
    employee = forms.ModelChoiceField(queryset=Employee.objects.all(), empty_label='', initial=None, required=True,
                                      widget=forms.Select(attrs={'class': 'form-control form-select', 'id': 'employee'}))
    chair = forms.ChoiceField(
        choices=[('', '')] + [(x, x) for x in range(1, 5)],
        required=True,
        widget=forms.Select(
            attrs={'class': 'form-control form-select', 'id': 'chair'})
    )
    customer = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'customer'}))
    phone = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'phone'}))
    start_date = forms.SplitDateTimeField(
        required=True,
        initial=timezone.now,
        widget=forms.SplitDateTimeWidget(
            date_format='%Y-%m-%d',
            time_format='%H:%M',
            date_attrs={'type': 'date', 'class': 'form-control'},
            time_attrs={'type': 'time', 'class': 'form-control'}
        )
    )

    class Meta:
        model = Assignment
        fields = ['service', 'employee', 'chair',
                  'customer', 'phone', 'start_date']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        service = cleaned_data.get('service')
        chair = cleaned_data.get('chair')
        employee = cleaned_data.get('employee')

        if start_date and service:
            end_date = start_date + timezone.timedelta(minutes=service.duration)

            # Check if the employee is occupied
            overlapping_assignments_employee = Assignment.objects.filter(
                Q(start_date__range=(start_date, end_date)) |
                Q(start_date__lte=start_date, end_date__gt=start_date) |
                Q(start_date__lt=end_date, end_date__gte=end_date),
                employee=employee
            )

            # Check if the chair is occupied by a different employee
            overlapping_assignments_chair = Assignment.objects.filter(
                Q(start_date__range=(start_date, end_date)) |
                Q(start_date__lte=start_date, end_date__gt=start_date) |
                Q(start_date__lt=end_date, end_date__gte=end_date),
                chair=chair
            ).exclude(employee=employee)

            if overlapping_assignments_employee.exists():
                raise ValidationError(
                    "The selected employee is already occupied in the selected date and time range.")

            if overlapping_assignments_chair.exists():
                raise ValidationError(
                    "The selected chair is already occupied by a different employee in the selected date and time range.")

        return cleaned_data

    def save(self, commit=True):
        return super(AssignmentForm, self).save(commit=commit)
