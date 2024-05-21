# Generated by Django 4.2 on 2024-05-21 02:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import massage.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('massage', '0004_alter_employee_role_alter_employee_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='employee',
            old_name='updated_at',
            new_name='last_updated_at',
        ),
        migrations.AddField(
            model_name='employee',
            name='created_by',
            field=models.ForeignKey(default=massage.models.Employee.default_admin, on_delete=django.db.models.deletion.CASCADE, related_name='employee_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='employee',
            name='last_updated_by',
            field=models.ForeignKey(default=massage.models.Employee.default_admin, on_delete=django.db.models.deletion.CASCADE, related_name='employee_last_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
