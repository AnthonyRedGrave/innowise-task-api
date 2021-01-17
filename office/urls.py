from django.urls import path, include
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', index, name = 'index'),
    path('login/', LoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(next_page = '/'), name = 'logout'),
    path('registration/', RegisterView.as_view(), name = 'registration'),

    path('search/', get_offices, name = 'search_address'),
    path('free_places/', get_free_places, name = 'free_places'),
    path('occupied_places', get_occupied_places, name = 'occupied_places'),
    path('date/<int:year>/<int:month>/<int:day>/', get_occupied_places_on_date, name = 'date_places'),
    path('office_<int:pk>/', office_detail, name = 'office_detail'),
    path('office_<int:pk>/room_<int:id>/', room_detail, name = 'room_detail'),
    path('office_<int:pk>/room_<int:id>/place_<int:num>/occupation/', OccupyPlace.as_view(), name = 'place_occupation'),
    path('office_<int:pk>/room_<int:id>/place_<int:num>/release/', ReleasePlace.as_view(), name = 'place_release'),
]

