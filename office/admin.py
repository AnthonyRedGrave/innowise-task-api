from django import forms
from django.core.exceptions import PermissionDenied
from django.contrib import admin
from django.contrib.admin.actions import delete_selected as delete_selected_
from .models import *
from .utils import check_date


class OfficeAdmin(admin.ModelAdmin):
    list_display = ['address',]
    list_display_links = ['address',]
    #readonly_fields = ['address',]




def check_queryset(self, request, queryset):
    for place in queryset:
        if place.release_place(): # если дата бронирования неправильная
            print("Срок действия бронирования {} истек".format(place))
            place.delete()

class PlaceForm(forms.ModelForm):

    def clean(self):
        data = self.cleaned_data['data']
        now = datetime.date.today()
        if data < now:
            raise forms.ValidationError("Дата для бронирования места некорректна!")
        return self.cleaned_data

    class Meta:
        model = Place
        fields = ['data', 'client', 'room', 'occupied',]


def expired_places(self, request, queryset): #проверяет и стирает просроченные ли места
    for place in queryset:
        if place.release_place():
            print("{} освобождается!".format(place))
            place.reset_fields()
expired_places.short_description = "Проверить выбранные места на коректность даты бронирования"


def reset_places(self, request, queryset): #освобождает места
    for place in queryset:
        print("{} освобождается!".format(place))
        place.reset_fields()
reset_places.short_description = "Освободить выбранные места"


class PlaceAdmin(admin.ModelAdmin):
    list_display = ['view', 'client', 'first_date', 'data', 'room']
    readonly_fields = ['first_date']
    form = PlaceForm
    actions = [expired_places, reset_places]

    def get_queryset(self, request):
        queryset = super(PlaceAdmin, self).get_queryset(request)
        for place in queryset:
            if place.release_place():
                print("{} освобождается!".format(place))
                place.reset_fields()

            UsersPreviousPlace.objects.get_or_create(client = place.client, place = place.correct_name(),
                                                      first_date = place.first_date, last_date = place.data,
                                                      room = place.room.__str__(),
                                                      office = place.room.office.__str__())
        UsersPreviousPlace.objects.filter(client = None).delete()

        return queryset

def check_rooms(self, request, queryset):
    for room in queryset:
        count = Place.objects.filter(room = room, room__office = room.office).count()
        count_of_free_places = Place.objects.filter(room = room, room__office = room.office, occupied = False).count()
        count_of_occupied_places = Place.objects.filter(room = room, room__office = room.office, occupied = True).count()
        Room.objects.filter(id = room.id).update(count_of_places = count, count_of_free_places = count_of_free_places,
                                                 count_of_occupied_places = count_of_occupied_places)


check_rooms.short_description = "Проверить кабинеты"

class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'count_of_places', 'count_of_occupied_places', 'count_of_free_places', 'office']
    list_display_links = ['number', 'office', 'count_of_occupied_places', 'count_of_free_places']
    readonly_fields = ['count_of_occupied_places', 'count_of_free_places']
    actions = [check_rooms]

    def get_queryset(self, request):
        qs = super(RoomAdmin,self).get_queryset(request)
        for room in qs:
            room.place.all = check_date(room.place.all())
            count = Place.objects.filter(room=room, room__office=room.office).count()
            count_of_free_places = Place.objects.filter(room=room, room__office=room.office, occupied=False).count()
            count_of_occupied_places = Place.objects.filter(room=room, room__office=room.office, occupied=True).count()
            Room.objects.filter(id=room.id).update(count_of_places=count, count_of_free_places=count_of_free_places,
                                                   count_of_occupied_places=count_of_occupied_places)
        return qs

class UsersPreviousPlaceAdmin(admin.ModelAdmin):
    list_display = ['client', 'place', 'room', 'office', 'first_date', 'last_date',]

    def get_queryset(self, request):
        query_set = super(UsersPreviousPlaceAdmin, self).get_queryset(request)
        for place in query_set:
            if place.client == None:
                place.delete()
                print("удалено")
        return query_set



admin.site.register(UsersPreviousPlace, UsersPreviousPlaceAdmin)
admin.site.register(Office, OfficeAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Place, PlaceAdmin)