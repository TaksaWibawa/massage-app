from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import uuid

# Model for audit fields
class Auditable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='created_%(class)s_set', null=True, blank=True, on_delete=models.SET_NULL)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, related_name='updated_%(class)s_set', null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True

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

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_created_by', default=default_admin)
    last_updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='employee_last_updated_by', default=default_admin)

    def __str__(self):
        return self.user.username