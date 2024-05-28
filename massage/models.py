from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from colorfield.fields import ColorField
import uuid

# Model for audit fields
class Auditable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_%(class)s_set', null=True, blank=True, on_delete=models.SET_NULL)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, related_name='updated_%(class)s_set', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True

class GlobalSettings(models.Model):
    name = models.CharField(max_length=255, unique=True, primary_key=True, default='Max Chairs')
    type = models.CharField(max_length=255, default='number')
    value = models.TextField(default='8')

    class Meta:
        verbose_name_plural = "Global Settings"
    
    def __str__(self):
        return self.name

# Model for role management
class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Model for employee management
class Employee(Auditable):
    # Default values
    def default_admin():
        if User.objects.filter(username__iexact='admin').exists():
            return User.objects.get(username__iexact='admin').id
        else:
            user = User.objects.create(username='admin', password=make_password('admin'))
            user.save()
            return user.id

    def default_user():
        if User.objects.filter(username__iexact='employee').exists():
            return User.objects.get(username__iexact='employee').id
        else:
            user = User.objects.create(username='employee', password=make_password('employee'))
            user.save()
            return user.id

    def default_role():
        if Role.objects.filter(name__iexact='Employee').exists():
            return Role.objects.get(name__iexact='Employee').id
        else:
            role = Role.objects.create(name='Employee')
            role.save()
            return role.id

    # Main fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, default='Employee')
    image = models.ImageField(upload_to='static/massage/images/employees/', default='static/massage/images/profile-placeholder.svg')
    phone = models.CharField(max_length=20, default='0')
    address = models.TextField(default='Address')
    age = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=default_user)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, default=default_role)
    color = ColorField(default='#48D75F')  

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_created_by', default=default_admin)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_last_updated_by', default=default_admin)

    def __str__(self):
        return self.name
    
# Model for service management
class Service(Auditable):
    # Default values
    def default_admin():
        if User.objects.filter(username__iexact='admin').exists():
            return User.objects.get(username__iexact='admin').id
        else:
            user = User.objects.create(username='admin', password=make_password('admin'))
            user.save()
            return user.id

    # Main fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='static/massage/images/services/', default='static/massage/images/woman-relaxing-spa 1.png')
    name = models.CharField(max_length=100, default='Service')
    price = models.IntegerField(default=0)
    duration = models.IntegerField(default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_created_by', default=default_admin)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_last_updated_by', default=default_admin)

    def __str__(self):
        return self.name
    
# Model for assignment management
class Assignment(Auditable):
    # Default values
    def default_admin():
        if User.objects.filter(username__iexact='admin').exists():
            return User.objects.get(username__iexact='admin').id
        else:
            user = User.objects.create(username='admin', password=make_password('admin'))
            user.save()
            return user.id
    def default_start_date():
        now = timezone.now()
        return now.replace(hour=18, minute=0, second=0, microsecond=0)

    # Main fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    customer = models.CharField(max_length=100, default='Customer')
    chair = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    phone = models.CharField(max_length=20, default='0')
    start_date = models.DateTimeField(default=default_start_date)
    end_date = models.DateTimeField(null=True, blank=True)
    is_done = models.BooleanField(default=False)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_created_by', default=default_admin)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_last_updated_by', default=default_admin)

    def save(self, *args, **kwargs):
        self.end_date = self.start_date + timezone.timedelta(minutes=self.service.duration)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.customer

# Model for receipt
class Receipt(Auditable):
    # Default values
    def default_admin():
        if User.objects.filter(username__iexact='admin').exists():
            return User.objects.get(username__iexact='admin').id
        else:
            user = User.objects.create(username='admin', password=make_password('admin'))
            user.save()
            return user.id

    # Main fields
    id = models.CharField(max_length=100, default='EMS-01012024-0001', unique=True, primary_key=True, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    cashier = models.ForeignKey(User, on_delete=models.CASCADE, default=default_admin)
    services = models.ManyToManyField(Service, through='ReceiptService')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receipt_created_by', default=default_admin)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receipt_last_updated_by', default=default_admin)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.assignment.customer

# Model for receipt service
class ReceiptService(Auditable):
    # Default values
    def default_admin():
        if User.objects.filter(username__iexact='admin').exists():
            return User.objects.get(username__iexact='admin').id
        else:
            user = User.objects.create(username='admin', password=make_password('admin'))
            user.save()
            return user.id

    # Main fields
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receipt_service_created_by', default=default_admin)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receipt_service_last_updated_by', default=default_admin)

    def save(self, *args, **kwargs):
        self.price = self.service.price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.service.name