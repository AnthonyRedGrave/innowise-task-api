from django.db import models
from django.contrib.auth.models import User
import datetime

class Office(models.Model):
    count_of_places = models.IntegerField("Кол-во мест")
    count_of_occupied_places = models.IntegerField("Кол-во занятых мест")
    count_of_free_places = models.IntegerField("Кол-во свободных мест")
    address = models.CharField("Адрес офиса", max_length=150)

    def __str__(self):
        return "Офис, по адресу {}".format(self.address)

    class Meta:
        verbose_name = "Офис"
        verbose_name_plural = "Офисы"

class Place(models.Model):
    client = models.OneToOneField(User, on_delete=models.CASCADE)
    data = models.DateField("Дата для бронирования", auto_now = False, default = datetime.date.today())
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='place')

    def __str__(self):
        return "Место номер №{}".format(self.id)

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"


