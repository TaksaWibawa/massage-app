import calendar
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from django import forms
from datetime import time
from .utils import get_global_setting
from .models import Role, Employee, Service, Assignment


class UserAdminForm(UserCreationForm):
    role = forms.ModelChoiceField(queryset=Role.objects.all())

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('role',)


class LoginForm(AuthenticationForm):
    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'username'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'password'}))

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            self.add_error('username', 'Invalid username or password')
            self.add_error('password', 'Invalid username or password')
        self.user = user
        return self.cleaned_data


class CreateUserForm(forms.ModelForm):
    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'username'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'password'}))

    class Meta:
        model = User
        fields = ["username", "password"]

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            self.add_error('username', 'Username already exists')

        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            password=self.cleaned_data.get('password'),
        )
        user.save()
        return user


class ChangePasswordForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'username', 'readonly': 'readonly'}))
    new_password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'new_password'}))
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'confirm_password'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['username'].initial = self.user.username

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data.get('new_password'))
        if commit:
            self.user.save()
        return self.user


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
    image = forms.ImageField(widget=forms.FileInput(
        attrs={'class': 'form-control', 'id': 'image-upload'}))

    class Meta:
        model = Employee
        fields = ["image", "color", "name", "phone", "address", "age"]

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        user = cleaned_data.get('user')

        if image is None:
            self.add_error('image', 'Please upload an image')

        if user and Employee.objects.filter(user=user).exists():
            raise forms.ValidationError("A user with this ID already exists.")

        return cleaned_data

    def save(self, commit=True):
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
        fields = ["image", "name", "price", "duration"]

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        duration = cleaned_data.get('duration')
        image = cleaned_data.get('image')

        if price and duration:
            if price == 0 and duration > 0:
                self.add_error(
                    'price', 'Price must be greater than 0 if duration is greater than 0')
            if price > 0 and duration == 0:
                self.add_error(
                    'duration', 'Duration must be greater than 0 if price is greater than 0')

        if image is None:
            self.add_error('image', 'Please upload an image')
        return cleaned_data

    def save(self, commit=True):
        return super(ServiceForm, self).save(commit=commit)


class AssignmentForm(forms.ModelForm):
    def default_start_date():
        return timezone.localtime(timezone.now()).replace(hour=18, minute=0, second=0, microsecond=0)

    def validate_time_range(value):
        if not (time(18, 0) <= value.time() <= time(22, 0)):
            raise ValidationError("Time must be between 18:00 and 22:00.")

    service = forms.ModelChoiceField(queryset=Service.objects.filter(is_active=True), empty_label='', initial=None, required=True,
                                     widget=forms.Select(attrs={'class': 'form-control form-select', 'id': 'service'}))
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(
            is_active=True, role__name__iexact='employee'),
        empty_label='Unassigned',
        initial=None,
        required=False,
        widget=forms.Select(
            attrs={'class': 'form-control form-select', 'id': 'employee'})
    )
    chair = forms.ChoiceField(
        required=True,
        widget=forms.Select(
            attrs={'class': 'form-control form-select', 'id': 'chair'})
    )
    customer = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'customer'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'phone'}))
    start_date = forms.SplitDateTimeField(
        required=True,
        initial=default_start_date,
        validators=[validate_time_range],
        widget=forms.SplitDateTimeWidget(
            date_format='%Y-%m-%d',
            time_format='%H:%M',
            date_attrs={'type': 'date', 'class': 'form-control',
                        'min': timezone.now().date().isoformat()},
            time_attrs={'type': 'time', 'class': 'form-control'}
        ),
    )

    def calculate_end_time(self, start_date=None, service=None):
        if start_date and service:
            end_date = start_date + \
                timezone.timedelta(minutes=service.duration)
            return end_date

    def get_available_chairs(self, start_date, end_date, assignment_id=None):
        max_chairs = get_global_setting('max chairs')
        all_chairs = range(1, max_chairs + 1)

        occupied_chairs_query = Assignment.objects.filter(
            start_date__lt=end_date,
            end_date__gt=start_date,
        ).exclude(id=assignment_id)

        occupied_chairs = occupied_chairs_query.values_list('chair', flat=True)

        return [chair for chair in all_chairs if chair not in occupied_chairs]

    class Meta:
        model = Assignment
        fields = ['start_date', 'service', 'chair',
                  'employee', 'customer', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['chair'].choices = [(i, str(i)) for i in range(
            1, get_global_setting('max chairs') + 1)]

    def check_overlapping_assignments(self, start_date, end_date, employee=None, chair=None):
        overlapping_assignments_query = Assignment.objects.exclude(id=self.instance.id).filter(
            start_date__lt=end_date,
            end_date__gt=start_date,
        )

        overlapping_chair_assignment = overlapping_assignments_query.filter(
            chair=chair).first()

        if overlapping_chair_assignment:
            start_date_str = timezone.localtime(
                overlapping_chair_assignment.start_date).strftime('%H:%M')
            end_date = timezone.localtime(
                overlapping_chair_assignment.end_date)
            end_date_str = end_date.strftime('%H:%M')
            self.add_error(
                'chair', f'Chair taken from {start_date_str} to {end_date_str}.')
            self.add_error(
                'start_date', f'Time slot taken from {start_date_str} to {end_date_str}.')

        if employee:
            overlapping_employee_assignment = overlapping_assignments_query.filter(
                employee=employee).exclude(is_done=True).first()

            if overlapping_employee_assignment:
                start_date_str = timezone.localtime(
                    overlapping_employee_assignment.start_date).strftime('%H:%M')
                end_date = timezone.localtime(
                    overlapping_employee_assignment.end_date)
                end_date_str = end_date.strftime('%H:%M')
                self.add_error(
                    'employee', f'Employee booked from {start_date_str} to {end_date_str}.')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        service = cleaned_data.get('service')
        chair = cleaned_data.get('chair')
        employee = cleaned_data.get('employee')

        if start_date is not None and start_date.date() < timezone.localdate():
            self.add_error('start_date', 'Cannot backdate assignment.')

        end_date = self.calculate_end_time(start_date, service)
        if end_date and end_date.time() > time(22, 0):
            self.add_error(
                'start_date', 'Exceeds working hours (18:00 - 22:00).')

        self.check_overlapping_assignments(
            start_date, end_date, employee, chair)

        available_chairs = self.get_available_chairs(
            start_date, end_date, self.instance.id)
        if chair and int(chair) not in available_chairs:
            self.add_error('chair', 'Chair not available at this time.')

        return cleaned_data

    def save(self, commit=True):
        return super().save(commit=commit)


class ServiceChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        formatted_price = f'{round(obj.price/1000)}k' if obj.price >= 1000 else obj.price
        return f'{obj.name} ({formatted_price})'


class AdditionalTreatmentForm(forms.Form):
    additional_service = ServiceChoiceField(
        queryset=Service.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control form-select'}),
        label=''
    )


AdditionalServicesFormset = forms.formset_factory(
    AdditionalTreatmentForm,
    extra=0,
    max_num=3
)


class EmployeeStatusFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', '-----'),
        (True, 'Active'),
        (False, 'Inactive'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, widget=forms.Select(
        attrs={'class': 'form-control form-select', 'id': 'status'}))

    def __init__(self, *args, **kwargs):
        super(EmployeeStatusFilterForm, self).__init__(*args, **kwargs)


class ServiceStatusFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', '-----'),
        (True, 'Active'),
        (False, 'Inactive'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, widget=forms.Select(
        attrs={'class': 'form-control form-select', 'id': 'status'}))

    def __init__(self, *args, **kwargs):
        super(ServiceStatusFilterForm, self).__init__(*args, **kwargs)


class MonthFilterForm(forms.Form):
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]
    month = forms.ChoiceField(choices=MONTH_CHOICES, required=False, widget=forms.Select(
        attrs={'class': 'form-control form-select', 'id': 'month'}))

    def __init__(self, *args, **kwargs):
        super(MonthFilterForm, self).__init__(*args, **kwargs)


class EmployeeFilterForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=None, required=False,
                                      widget=forms.Select(attrs={'class': 'form-control form-select', 'id': 'employee'}))
    date = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control', 'type': 'date', 'id': 'date'}))

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(EmployeeFilterForm, self).__init__(*args, **kwargs)

        if request and request.user.groups.filter(name__iexact='employee').exists():
            self.fields['employee'].queryset = Employee.objects.filter(
                user=request.user, is_active=True, role__name__iexact='employee')
        else:
            self.fields['employee'].queryset = Employee.objects.filter(
                is_active=True, role__name__iexact='employee')


class RecapHistoryFilterForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=None, required=False,
                                      widget=forms.Select(attrs={'class': 'form-control form-select', 'id': 'employee'}))
    start_date = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control', 'type': 'date', 'id': 'start_date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(
        attrs={'class': 'form-control', 'type': 'date', 'id': 'end_date'}))

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(RecapHistoryFilterForm, self).__init__(*args, **kwargs)

        if request and request.user.groups.filter(name__iexact='employee').exists():
            self.fields['employee'].queryset = Employee.objects.filter(
                user=request.user, is_active=True, role__name__iexact='employee')
        else:
            self.fields['employee'].queryset = Employee.objects.filter(
                is_active=True, role__name__iexact='employee')


class RecapPaySelectedForm(forms.Form):
    assignment_ids = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'assignment-ids'}))
    total_fee = forms.DecimalField(
        widget=forms.HiddenInput(attrs={'id': 'total-fee'}))
    fee_percentage = forms.DecimalField(
        widget=forms.HiddenInput(attrs={'id': 'fee-percentage'}))
    total_payment = forms.DecimalField(widget=forms.NumberInput(
        attrs={'class': 'form-control', 'id': 'total-payment'}))
    total_payment.widget.attrs['min'] = 0
    total_payment.widget.attrs['step'] = 1000
    total_payment.widget.attrs['required'] = True

    def clean(self):
        cleaned_data = super().clean()
        total_payment = cleaned_data.get('total_payment')
        total_fee = cleaned_data.get('total_fee')

        if total_payment < total_fee:
            self.add_error(
                'total_payment', 'Total payment must be greater than or equal to total fee')

        return cleaned_data
