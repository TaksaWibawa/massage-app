import uuid
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from colorfield.fields import ColorField

def default_user():
    if User.objects.filter(username='admin').exists():
        return User.objects.get(username='admin')
    return User.objects.create(username='admin', password=make_password('admin'))

def default_role():
    if Role.objects.filter(name='employee').exists():
        return Role.objects.get(name='employee')
    return Role.objects.create(name='employee')

class Auditable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(User, related_name='created_%(class)s_set', null=True, blank=True, on_delete=models.SET_NULL, editable=False)
    last_updated_at = models.DateTimeField(auto_now=True, editable=False)
    last_updated_by = models.ForeignKey(User, related_name='updated_%(class)s_set', null=True, blank=True, on_delete=models.SET_NULL, editable=False)

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        if self._state.adding:
            if self.created_by is None:
                self.created_by = User.objects.get(username='admin')
            if self.last_updated_by is None:
                self.last_updated_by = User.objects.get(username='admin')

        else:
            if self.last_updated_by is None:
                self.last_updated_by = User.objects.get(username='admin')
        super().save(*args, **kwargs)

class GlobalSettings(models.Model):
    TYPE_CHOICES = [
        ('number', 'Number'),
        ('percentage', 'Percentage (0-100)'),
        ('text', 'Text'),
    ]

    name = models.CharField(max_length=255, unique=True, primary_key=True, default='Max Chairs', editable=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='number')
    value = models.TextField(default='8')

    class Meta:
        verbose_name_plural = "Global Settings"
    
    def __str__(self):
        return self.name
    
    def clean(self):
        if self.type == 'number' and not self.value.isdigit():
            raise ValidationError(_('Value must be a number for type Number'))
        elif self.type == 'percentage' and (not self.value.isdigit() or not 0 <= int(self.value) <= 100):
            raise ValidationError(_('Value must be a percentage (0-100) for type Percentage'))
        elif self.type == 'text' and not isinstance(self.value, str):
            raise ValidationError(_('Value must be a text for type Text'))

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Employee(Auditable):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default='Employee')
    image = models.ImageField(upload_to='static/massage/images/employees/', default='static/massage/images/profile-placeholder.svg')
    phone = models.CharField(max_length=20, default='0')
    address = models.TextField(default='Address')
    age = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=default_user)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, default=default_role)
    color = ColorField(default='#48D75F')
    is_active = models.BooleanField(default=True, verbose_name='Active')

    def __str__(self):
        return self.name
    
class Service(Auditable):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='static/massage/images/services/', default='static/massage/images/woman-relaxing-spa 1.png')
    name = models.CharField(max_length=100, default='Service')
    price = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True, verbose_name='Active')

    def __str__(self):
        return self.name
    
class Assignment(Auditable):
    def default_start_date():
        now = timezone.now()
        return now.replace(hour=18, minute=0, second=0, microsecond=0)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    customer = models.CharField(max_length=100, default='Customer')
    chair = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(8)])
    phone = models.CharField(max_length=20, default='0')
    start_date = models.DateTimeField(default=default_start_date)
    end_date = models.DateTimeField(null=True, blank=True)
    is_done = models.BooleanField(default=False, verbose_name='Finished')

    def save(self, *args, **kwargs):
        self.end_date = self.start_date + timezone.timedelta(minutes=self.service.duration)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.customer

class Receipt(Auditable):
    id = models.CharField(max_length=100, default='EMS-01012024-0001', unique=True, primary_key=True, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    cashier = models.ForeignKey(User, on_delete=models.CASCADE, default=default_user)
    services = models.ManyToManyField(Service, through='ReceiptService')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.id

class ReceiptService(Auditable):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_additional = models.BooleanField(default=False, verbose_name='Additional Service')

    def save(self, *args, **kwargs):
        self.price = self.service.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.service.name
    
class EmployeePayment(Auditable):
    receipt = models.OneToOneField(Receipt, on_delete=models.CASCADE)
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    total_fee = models.DecimalField(max_digits=9, decimal_places=2)
    is_paid = models.BooleanField(default=False, verbose_name='Paid Off')

    def calculate_total_prices(self):
        total = 0
        for service in self.receipt.services.all():
            total += service.price
        return total

    def save(self, *args, **kwargs):
        from .utils import get_global_setting
        self.fee_percentage = get_global_setting('Service Fee')
        total = self.calculate_total_prices()
        self.total_fee = total * self.fee_percentage / 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receipt.assignment.employee.name} - {self.receipt.assignment.customer}"