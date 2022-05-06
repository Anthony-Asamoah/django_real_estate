# Generated by Django 4.0.2 on 2022-05-02 15:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('listing', models.CharField(max_length=200)),
                ('listing_id', models.IntegerField()),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=15)),
                ('email', models.CharField(max_length=100)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(default=datetime.datetime(2022, 5, 2, 15, 0, 48, 735112))),
                ('user_id', models.IntegerField()),
            ],
        ),
    ]
