# Generated by Django 4.2 on 2024-05-24 06:55

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('massage', '0009_rename_date_assignment_start_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='color',
            field=colorfield.fields.ColorField(default='#48D75F', image_field=None, max_length=25, samples=None),
        ),
    ]