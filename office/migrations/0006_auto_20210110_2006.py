# Generated by Django 3.1.5 on 2021-01-10 17:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('office', '0005_auto_20210110_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='data',
            field=models.DateField(default=datetime.date(2021, 1, 10), null=True, verbose_name='Дата для бронирования'),
        ),
    ]