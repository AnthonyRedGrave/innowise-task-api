# Generated by Django 3.1.5 on 2021-01-09 11:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('office', '0002_place'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='office',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='place', to='office.office'),
            preserve_default=False,
        ),
    ]
