# Generated by Django 3.1.5 on 2021-01-25 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('office', '0024_userspreviousplace_place'),
    ]

    operations = [
        migrations.AddField(
            model_name='userspreviousplace',
            name='office_name',
            field=models.CharField(default=None, editable=False, max_length=150, verbose_name='Офис'),
            preserve_default=False,
        ),
    ]
