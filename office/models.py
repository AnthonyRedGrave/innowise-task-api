from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator, ValidationError
import datetime
from django.db import IntegrityError
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver


class Office(models.Model):
    address = models.CharField("Адрес офиса", max_length=150, null=True, blank=True)

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
        try:
            if self.count_of_free_places == 0 and self.count_of_occupied_places == 0 or self.count_of_free_places == None\
                    and self.count_of_occupied_places == None:
                self.count_of_free_places, self.count_of_occupied_places = self.count_of_places, 0
                super().save(*args, **kwargs)
                if self.office:
                    curr_room = Room.objects.get(number=self.number, office=self.office)
                    for _ in range(self.count_of_places):
                        place = Place(room=curr_room)
                        place.save()
            super().save(*args, **kwargs)
        except IntegrityError:
            pass

    def reset_places(self, *args, **kwargs):
        self.count_of_free_places, self.count_of_occupied_places = self.count_of_places, 0
        super().save(*args, **kwargs)

    def __str__(self):
        return "Кабинет №{}, находящийся в офисе по адресу {}".format(self.number, self.office.address)

    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"
        ordering = ['office']
        unique_together = ['number', 'office']


class Place(models.Model):
    view = models.CharField("Место", max_length=100, editable=False, null=True, blank=True)
    client = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='place')
    first_date = models.DateField("Первая дата", default=datetime.date.today(), null=True, blank=True, editable=False)
    data = models.DateField("Зарезервированная дата", auto_now=False,
                            default=datetime.date.today() + datetime.timedelta(days=1), null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='place', null=True, blank=True)
    occupied = models.BooleanField('Занято ли', default=False)

    def release_place(self, *args, **kwargs):
        if self.data:
            now_date = datetime.date.today()
            return now_date > self.data
        else:
            return False

    def correct_name(self):
        return "Место №{}".format(self.id)

    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
            count = 0
            count_places = 0
            if self.occupied and self.client and self.data:  # если есть галочка и все данные заполнены
                self.view = "Место №{} (занято)".format(self.id)
                self.first_date = datetime.date.today()
                count = Place.objects.filter(room=self.room, room__office=self.room.office, occupied=True).count()
                count_places = Place.objects.filter(room=self.room, room__office=self.room.office).count()
                for place in Place.objects.filter(room=self.room, room__office=self.room.office, occupied=True):
                    Room.objects.filter(number=self.room.number, office=self.room.office).update(
                        count_of_places=count_places)
                    Room.objects.filter(number=self.room.number, office=self.room.office).update(
                        count_of_occupied_places=count)
                    Room.objects.filter(number=self.room.number, office=self.room.office).update(
                        count_of_free_places=models.F("count_of_places") - count)

                previous_place = UsersPreviousPlace.objects.create(client=self.client, place = self.correct_name(),
                                                                   first_date=self.first_date, last_date=self.data,
                                                                   room=self.room.__str__(),
                                                                   office = self.room.office.__str__())

            elif self.occupied == False:  # если нет галочки
                print("сюда")
                self.view = "Место №{} (свободно)".format(self.id)
                self.data = None
                self.first_date = None
                self.client = None
                count = Place.objects.filter(room=self.room, room__office=self.room.office, occupied=True).count()
                count_places = Place.objects.filter(room=self.room, room__office=self.room.office).count()
                for place in Place.objects.filter(room=self.room, room__office=self.room.office, occupied=True):
                    Room.objects.filter(number=self.room.number, office=self.room.office).update(
                        count_of_places=count_places)
                    Room.objects.filter(number=self.room.number, office=self.room.office).update(
                        count_of_occupied_places=count)
                    Room.objects.filter(number=self.room.number, office=self.room.office).update(
                        count_of_free_places=models.F("count_of_places") - count)
            super().save(*args, **kwargs)
        except IntegrityError:
            pass

    def reset_fields(self, *args, **kwargs):
        print("Освобождаю место №{}".format(self.id))
        self.occupied = False
        self.save()

    def __str__(self):
        if self.occupied:
            return "Место №{} (занято)".format(self.id)
        else:
            return "Место №{} (свободно)".format(self.id)

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"
        ordering = ['room']


@receiver(post_delete, sender=Place)
def delete_place(sender, instance, *args, **kwargs):
    try:
        count_places = Place.objects.filter(room__id=instance.room.id).count()
        count_of_free_places = Place.objects.filter(room__id=instance.room.id, occupied=False).count()
        count_of_occupied_places = Place.objects.filter(room__id=instance.room.id, occupied=True).count()
        Room.objects.filter(id=instance.room.id).update(count_of_places=count_places,
                                                        count_of_free_places=count_of_free_places,
                                                        count_of_occupied_places=count_of_occupied_places)
    except ObjectDoesNotExist as v:
        print(v)


class UsersPreviousPlace(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_previous_place', editable=False, null=True, blank=True)
    place = models.CharField("Место", max_length=150, editable=False)
    first_date = models.DateField("Дата начала бронирования", auto_now=False, editable=False, null=True, blank=True)
    last_date = models.DateField("Дата окончания бронирования", auto_now=False, editable=False, null=True, blank=True)
    room = models.CharField("Кабинет", max_length=150, editable=False)
    office = models.CharField("Офис", max_length=150, editable=False)

    def __str__(self):
        return "Место, на котором пользователь {} сидел".format(self.client)

    class Meta:
        verbose_name = "Бывшее место пользователей"
        verbose_name_plural = "Бывшие места пользователей"