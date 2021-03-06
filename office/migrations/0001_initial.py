# Generated by Django 3.1.5 on 2021-01-09 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Office',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count_of_places', models.IntegerField(verbose_name='Кол-во мест')),
                ('count_of_occupied_places', models.IntegerField(verbose_name='Кол-во занятых мест')),
                ('count_of_free_places', models.IntegerField(verbose_name='Кол-во свободных мест')),
                ('address', models.CharField(max_length=150, verbose_name='Адрес офиса')),
            ],
            options={
                'verbose_name': 'Офис',
                'verbose_name_plural': 'Офисы',
            },
        ),
    ]
