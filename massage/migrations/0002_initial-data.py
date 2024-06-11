# Generated by Django 4.2 on 2024-05-29 02:43

from django.db import migrations
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

def add_global_settings(apps, schema_editor):
    GlobalSettings = apps.get_model('massage', 'GlobalSettings')
    settings = [
        {'name': 'Max Chairs', 'type': 'number', 'value': '8'},
        {'name': 'PPN', 'type': 'percentage', 'value': '10'},
        {'name': 'Service Fee', 'type': 'percentage', 'value': '40'},
    ]

    for setting in settings:
        if not GlobalSettings.objects.filter(name=setting['name']).exists():
            GlobalSettings.objects.create(**setting)

def add_roles(apps, schema_editor):
    Role = apps.get_model('massage', 'Role')
    roles = ['supervisor', 'accountant', 'employee']
    for role_name in roles:
        if not Role.objects.filter(name=role_name).exists():
            Role.objects.create(name=role_name)

def create_superuser(apps, schema_editor):
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create(username='admin', password=make_password('admin123'), is_superuser=True, is_staff=True)

def create_supervisor(apps, schema_editor):
    User = get_user_model()
    Employee = apps.get_model('massage', 'Employee')
    Role = apps.get_model('massage', 'Role')
    if not User.objects.filter(username='supervisor').exists():
        user = User.objects.create_user('supervisor', 'supervisor@example.com', 'supervisor123')
        role = Role.objects.get(name='supervisor')
        Employee.objects.create(user_id=user.id, role=role)

        group, _created = Group.objects.get_or_create(name='Supervisor')
        group.user_set.add(user)
    
def create_accountant(apps, schema_editor):
    User = get_user_model()
    Employee = apps.get_model('massage', 'Employee')
    Role = apps.get_model('massage', 'Role')
    if not User.objects.filter(username='accountant').exists():
        user = User.objects.create_user('accountant', 'accountant@example.com', 'accountant123')
        role = Role.objects.get(name='accountant')
        Employee.objects.create(user_id=user.id, role=role)

        group, _created = Group.objects.get_or_create(name='Accountant')
        group.user_set.add(user)

def create_employee(apps, schema_editor):
    User = get_user_model()
    Employee = apps.get_model('massage', 'Employee')
    Role = apps.get_model('massage', 'Role')

    if not User.objects.filter(username='employee').exists():
        user = User.objects.create_user('employee', 'employee@example.com', 'employee123')
        role = Role.objects.get(name='employee')
        Employee.objects.create(user_id=user.id, role=role)

        group, _created = Group.objects.get_or_create(name='Employee')
        group.user_set.add(user)

def remove_global_settings(apps, schema_editor):
    GlobalSettings = apps.get_model('massage', 'GlobalSettings')
    GlobalSettings.objects.all().delete()

def remove_all_users(apps, schema_editor):
    User = get_user_model()
    User.objects.all().delete()

def remove_roles(apps, schema_editor):
    Role = apps.get_model('massage', 'Role')
    Role.objects.all().delete()

def remove_employee(apps, schema_editor):
    User = get_user_model()
    Employee = apps.get_model('massage', 'Employee')
    User.objects.filter(username='employee').delete()
    Employee.objects.filter(user__username='employee').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('massage', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_all_users, remove_all_users),
        migrations.RunPython(create_superuser, remove_all_users),
        migrations.RunPython(add_global_settings, remove_global_settings),
        migrations.RunPython(add_roles, remove_roles),
        migrations.RunPython(create_supervisor, remove_employee),
        migrations.RunPython(create_accountant, remove_employee),
        migrations.RunPython(create_employee, remove_employee),
    ]

