# Generated by Django 4.0.2 on 2022-04-16 14:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('realtors', '0002_alter_realtor_hire_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realtor',
            name='hire_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 4, 16, 14, 10, 37, 978349)),
        ),
    ]