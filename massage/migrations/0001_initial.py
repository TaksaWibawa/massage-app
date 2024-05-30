# Generated by Django 4.2 on 2024-05-29 19:11

import colorfield.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import massage.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('customer', models.CharField(default='Customer', max_length=100)),
                ('chair', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)])),
                ('phone', models.CharField(default='0', max_length=20)),
                ('start_date', models.DateTimeField(default=massage.models.Assignment.default_start_date)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('is_done', models.BooleanField(default=False, verbose_name='Finished')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GlobalSettings',
            fields=[
                ('name', models.CharField(default='Max Chairs', editable=False, max_length=255, primary_key=True, serialize=False, unique=True)),
                ('type', models.CharField(choices=[('number', 'Number'), ('percentage', 'Percentage (0-100)'), ('text', 'Text')], default='number', max_length=10)),
                ('value', models.TextField(default='8')),
            ],
            options={
                'verbose_name_plural': 'Global Settings',
            },
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.CharField(default='EMS-01012024-0001', editable=False, max_length=100, primary_key=True, serialize=False, unique=True)),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='massage.assignment')),
                ('cashier', models.ForeignKey(default=massage.models.default_user, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('last_updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image', models.ImageField(default='static/massage/images/woman-relaxing-spa 1.png', upload_to='static/massage/images/services/')),
                ('name', models.CharField(default='Service', max_length=100)),
                ('price', models.IntegerField(default=0)),
                ('duration', models.IntegerField(default=0)),
                ('discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('last_updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReceiptService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('last_updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='massage.receipt')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='massage.service')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='receipt',
            name='services',
            field=models.ManyToManyField(through='massage.ReceiptService', to='massage.service'),
        ),
        migrations.CreateModel(
            name='EmployeePayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('fee_percentage', models.DecimalField(decimal_places=2, max_digits=5)),
                ('total', models.DecimalField(decimal_places=2, max_digits=9)),
                ('is_paid', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('last_updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('receipt', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='massage.receipt')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(default='Employee', max_length=100)),
                ('image', models.ImageField(default='static/massage/images/profile-placeholder.svg', upload_to='static/massage/images/employees/')),
                ('phone', models.CharField(default='0', max_length=20)),
                ('address', models.TextField(default='Address')),
                ('age', models.IntegerField(default=0)),
                ('color', colorfield.fields.ColorField(default='#48D75F', image_field=None, max_length=25, samples=None)),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('last_updated_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to=settings.AUTH_USER_MODEL)),
                ('role', models.ForeignKey(default=massage.models.default_role, on_delete=django.db.models.deletion.CASCADE, to='massage.role')),
                ('user', models.OneToOneField(default=massage.models.default_user, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='assignment',
            name='employee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='massage.employee'),
        ),
        migrations.AddField(
            model_name='assignment',
            name='last_updated_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='assignment',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='massage.service'),
        ),
    ]
