from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from datetime import time
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
    color = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'id': 'color', 'type': 'color', 'value': '#48D75F'}))
    name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'name'}))
    phone = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'phone'}))
    address = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'address'}))
    age = forms.IntegerField(required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'id': 'age'}))
    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'username'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'password'}))
    image = forms.ImageField(widget=forms.FileInput(
        attrs={'class': 'form-control', 'id': 'image-upload'}))

    class Meta:
        model = Employee
        fields = ["image", "name", "phone",
                  "address", "age", "username", "password", "color"]

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
    name = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'name'}))
    price = forms.FloatField(required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'id': 'price'}))
    duration = forms.IntegerField(required=True, widget=forms.NumberInput(
        attrs={'class': 'form-control', 'id': 'duration'}))
    image = forms.ImageField(widget=forms.FileInput(
        attrs={'class': 'form-control', 'id': 'image-upload'}))

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
                raise ValidationError(
                    "Price must be greater than 0 if duration is greater than 0")
            if price > 0 and duration == 0:
                raise ValidationError(
                    "Duration must be greater than 0 if price is greater than 0")

        if image is None:
            raise ValidationError("Please upload an image")
        return cleaned_data

    def save(self, commit=True):
        return super(ServiceForm, self).save(commit=commit)


class AssignmentForm(forms.ModelForm):
    def default_start_date():
        now = timezone.localtime(timezone.now())
        return now.replace(hour=18, minute=0, second=0, microsecond=0)

    def validate_time_range(value):
        start_time = time(18, 0)
        end_time = time(22, 0)

        if not (start_time <= value.time() <= end_time):
            raise ValidationError("Time must be between 18:00 and 22:00.")

    def calculate_end_time(self):
        start_date = self.cleaned_data.get('start_date')
        service = self.cleaned_data.get('service')

        if start_date and service:
            end_date = start_date + \
                timezone.timedelta(minutes=service.duration)

            if end_date.time() > time(22, 0):
                raise forms.ValidationError(
                    'The selected service exceeds the working hours (18:00 - 22:00).')

            return end_date

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
        initial=default_start_date,
        validators=[validate_time_range],
        widget=forms.SplitDateTimeWidget(
            date_format='%Y-%m-%d',
            time_format='%H:%M',
            date_attrs={'type': 'date', 'class': 'form-control'},
            time_attrs={'type': 'time', 'class': 'form-control'},
        ),
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
            end_date = self.calculate_end_time()

            # Check if the employee is occupied
            overlapping_assignments = Assignment.objects.filter(
                employee=employee,
                start_date__lt=end_date,
                end_date__gt=start_date,
                is_done=False
            )

            if self.instance.pk:
                overlapping_assignments = overlapping_assignments.exclude(
                    pk=self.instance.pk)

            if overlapping_assignments.exists():
                raise forms.ValidationError(
                    'The selected employee is already occupied in the selected date and time range.')

            # Check if the chair is occupied
            overlapping_assignments_chair = Assignment.objects.filter(
                chair=chair,
                start_date__lt=end_date,
                end_date__gt=start_date,
                is_done=False
            ).exclude(employee=employee)

            if overlapping_assignments_chair.exists():
                raise forms.ValidationError(
                    'The selected chair is already occupied in the selected date and time range.')

        return cleaned_data

    def save(self, commit=True):
        return super(AssignmentForm, self).save(commit=commit)


class ServiceChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        formatted_price = f'{round(obj.price/1000)}k' if obj.price >= 1000 else obj.price
        return f'{obj.name} ({formatted_price})'


class AdditionalTreatmentForm(forms.Form):
    additional_service = ServiceChoiceField(
        queryset=Service.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control form-select'}),
        label=''
    )


AdditionalServicesFormset = forms.formset_factory(
    AdditionalTreatmentForm,
    extra=0,
    max_num=3
)
