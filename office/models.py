from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, ValidationError
import datetime
from django.utils import timezone

class Office(models.Model):
    address = models.CharField("Адрес офиса", max_length=150)

    def __str__(self):
        return "Офис, находящийся по адресу {}".format(self.address)

    class Meta:
        verbose_name = 'Офис'
        verbose_name_plural = 'Офисы'
        ordering = ['address']



class Room(models.Model):
    number = models.CharField("Номер кабинета", max_length=5)
    count_of_places = models.IntegerField("Кол-во мест", validators=[MinValueValidator(0), MaxValueValidator(50)])
    count_of_occupied_places = models.IntegerField("Кол-во занятых мест",
                                                   validators=[MinValueValidator(0),
                                                               MaxValueValidator(count_of_places)],
                                                   editable=False, null=True, blank=True)
    count_of_free_places = models.IntegerField("Кол-во свободных мест", editable=False, null=True, blank=True)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='room', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.count_of_free_places == None and self.count_of_occupied_places == None:
            self.count_of_free_places, self.count_of_occupied_places = self.count_of_places, 0
            super().save(*args, **kwargs)
            for _ in range(self.count_of_places):
                curr_room = Room.objects.get(number = self.number, office = self.office)
                place = Place(room = curr_room)
                place.save()
        super().save(*args, **kwargs)

    def reset_places(self, *args, **kwargs):
        self.count_of_free_places, self.count_of_occupied_places = self.count_of_places, 0
        super().save(*args, **kwargs)

    def __str__(self):
        return "Кабинет №{}, находящийся в офисе по адресу {}".format(self.number, self.office.address)

    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"
        ordering = ['number']


class Place(models.Model):
    view = models.CharField("Место", max_length=100, editable=False, null=True, blank=True)
    client = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_date = models.DateField("Первая дата", null=True, blank=True, editable=False)
    data = models.DateField("Зарезервированная дата", auto_now = False, default = datetime.date.today() + datetime.timedelta(days=1), null=True, blank=True)

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='place', null=True, blank=True)

    occupied = models.BooleanField('Занято ли', default=False)

    def release_place(self, *args, **kwargs):
        if self.data:
            now_date = datetime.date.today()
            return now_date > self.data
        else:
            return False




    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.release_place():
            print("неправильная дата")
            self.occupied = False
            self.save()
        else:
            if self.occupied and self.client and self.data: #если есть галочка и все данные заполнены
                print("заполнено верно")
                self.view = "Место №{} (занято)".format(self.id)
                self.first_date = datetime.date.today()
                if self.room.count_of_places > self.room.count_of_occupied_places and 0 < self.room.count_of_free_places:
                    print("попал")
                    Room.objects.filter(number=self.room.number, office = self.room.office).update(count_of_occupied_places = models.F("count_of_occupied_places")+1)
                    Room.objects.filter(number=self.room.number, office = self.room.office).update(count_of_free_places = models.F("count_of_free_places")-1)

            elif self.occupied == False: # если нет галочки
                print("галочка не поставлена")
                self.view = "Место №{} (свободно)".format(self.id)
                self.client = None
                self.data = None
                self.first_date = None
                self.client = None

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):#не должны удаляться экземпляры модели
        if self.room:
            if self.room.count_of_places > self.room.count_of_free_places and 0 < self.room.count_of_occupied_places:
                Room.objects.filter(number=self.room.number, office = self.room.office).update(
                    count_of_occupied_places=models.F("count_of_occupied_places") - 1)
                Room.objects.filter(number=self.room.number, office = self.room.office).update(
                    count_of_free_places=models.F("count_of_free_places") + 1)
            self.occupied = False
            self.save()
        else:
            super().delete(*args, **kwargs)

    def reset_fields(self, *args, **kwargs):
        self.first_date = None
        self.occupied = False
        self.data = None
        self.client = None
        self.view = "Место №{} (свободно)".format(self.id)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.occupied:
            return "Место №{} (занято)".format(self.id)
        else:
            return "Место №{} (свободно)".format(self.id)


    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"
        ordering = ['room']

