from django.contrib import admin
from .models import *

class OfficeAdmin(admin.ModelAdmin):
    list_display = ['address', 'count_of_occupied_places', 'count_of_free_places', 'count_of_places']
    list_display_links = ['address', 'count_of_occupied_places', 'count_of_free_places', 'count_of_places']



admin.site.register(Office, OfficeAdmin)
admin.site.register(Place)