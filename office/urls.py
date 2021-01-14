from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index, name = 'index'),
    path('search/', get_offices, name = 'search_address'),
    path('office_<int:pk>/', office_detail, name = 'office_detail'),
    path('office_<int:pk>/room_<int:id>/', room_detail, name = 'room_detail'),
    path('office_<int:pk>/room_<int:id>/place_<int:num>/occupation/', OccupyPlace.as_view(), name = 'place_occupation'),
    path('office_<int:pk>/room_<int:id>/place_<int:num>/release/', ReleasePlace.as_view(), name = 'place_release'),
]

