# Generated by Django 3.1.5 on 2021-01-11 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('office', '0011_auto_20210111_1652'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='office',
            name='hide_count_of_free_places',
        ),
        migrations.RemoveField(
            model_name='office',
            name='hide_count_of_occupied_places',
        ),
        migrations.RemoveField(
            model_name='office',
            name='hide_count_of_places',
        ),
    ]
