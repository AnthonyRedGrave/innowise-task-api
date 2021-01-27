from django.urls import path, include
from .views import *
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

# router = DefaultRouter()
# router.register(r'api/offices', OfficeViewSet)
# router.register(r'api/rooms', RoomViewSet)

urlpatterns = [
    path('', index, name = 'index'),
    path('login/', LoginView.as_view(), name = 'login'),
    path('logout/', LogoutView.as_view(next_page = '/'), name = 'logout'),
    path('registration/', RegisterView.as_view(), name = 'registration'),
    path('search/', get_offices, name = 'search_address'),
    path('free_places/', get_free_places, name = 'free_places'),
    path('occupied_places', get_occupied_places, name = 'occupied_places'),
    path('occupied_places/<int:year>/<int:month>/<int:day>/', get_occupied_places_on_date, name = 'date_places'),
    path('office/<int:pk>/', office_detail, name = 'office_detail'),
    path('office/<int:pk>/room/<int:id>/', room_detail, name = 'room_detail'),
    path('office/<int:pk>/room/<int:id>/place/<int:num>/occupation/', OccupyPlace.as_view(), name = 'place_occupation'),
    path('office/<int:pk>/room/<int:id>/place/<int:num>/release/', ReleasePlace.as_view(), name = 'place_release'),

    path('api/office/', OfficeListApiView.as_view(), name = 'office_list'),
    path('api/office/<int:pk>/', OfficeDetailApiView.as_view(), name = 'office_detail_api'),
    path('api/room/', RoomListApiView.as_view(), name = 'room_list'),
    path('api/office/<int:pk>/room', OfficeRoomListApi.as_view(), name = 'office_room_list'),
    path('api/room/<int:pk>/', RoomDetailApiView.as_view(), name = 'room_detail'),
    path('api/room/<int:pk>/place/', RoomPlaceApiView.as_view(), name = 'room_place_list'),
    path('api/users/', api_user_list, name = 'user_list'),
    path('api/place/', PlaceListView.as_view(), name = 'place_list'),
    path('api/place/occupied/', PlaceListOccupiedApiView.as_view(), name = 'place_list_occupied'),
    path('api/place/free/', PlaceListFreeApiView.as_view(), name = 'place_list_free'),
    path('api/place/<int:pk>/', PlaceDetailView.as_view(), name = 'place_detail'),
    path('api/previous/<str:client>/', user_previous_place_list, name = 'user_previous_place'),

]
