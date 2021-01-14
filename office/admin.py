from django.core.exceptions import PermissionDenied
from django.contrib import admin
from django.contrib.admin.actions import delete_selected as delete_selected_
from .models import *

def reset_places(self, request, queryset):
    for ob in queryset:
        ob.reset_places()
        for place in ob.place.all():
            place.reset_fields()

class OfficeAdmin(admin.ModelAdmin):
    list_display = ['address',]
    list_display_links = ['address',]
    #readonly_fields = ['address',]


def delete_queryset(self, request, queryset):
    for ob in queryset:
        ob.delete()

class PlaceAdmin(admin.ModelAdmin):
    list_display = ['view', 'client', 'data', 'room']
    actions = [delete_queryset]

class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'count_of_places', 'count_of_occupied_places', 'count_of_free_places', 'office']
    list_display_links = ['number', 'office', 'count_of_occupied_places', 'count_of_free_places']
    readonly_fields = ['count_of_occupied_places', 'count_of_free_places']
    actions = [reset_places]





admin.site.register(Office, OfficeAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Place, PlaceAdmin)