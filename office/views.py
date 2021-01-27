from django.shortcuts import render
from django.views import generic
from rest_framework.response import Response
from .forms import *
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import *
from django.shortcuts import reverse, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .serializers import *
from .utils import *


def index(request):
    offices = Office.objects.all()
    context = {'offices':offices}
    return render(request, 'office/index.html', context)

def get_offices(request):
    query = request.GET.get('address')
    offices = Office.objects.filter(address__icontains = query)
    context = {'offices':offices, 'curr_address': query}
    return render(request, 'office/search.html', context)

def office_detail(request, pk):
    office = Office.objects.get(id = pk)
    rooms = Room.objects.filter(office = office)

    context = {'office': office, 'rooms': rooms}
    return render(request, 'office/detail.html', context)

def room_detail(request, pk, id):
    office = Office.objects.get(id = pk)
    room = Room.objects.get(id = id)
    places = Place.objects.filter(room = room)
    places = check_date(places)
    context = {'room': room, 'places': places, 'office': office}
    return render(request, 'room/detail.html', context)


class OccupyPlace(generic.View):
    def get(self, request, pk, id, num):
        office = Office.objects.get(id=pk)
        room = Room.objects.get(id=id)
        place = Place.objects.get(id = num)
        form = PlaceForm()
        context = {'form': form, 'office': office, 'room': room, 'place': place}

        return render(request, 'room/occupy.html', context)

    def post(self, request, pk, id, num):
        if request.user.is_authenticated:
            office = Office.objects.get(id=pk)
            room = Room.objects.get(id=id)
            place = Place.objects.get(id = num)
            form = PlaceForm(request.POST, instance=place)
            if form.is_valid():
                curr_user_occup_places = Place.objects.filter(client = request.user).exclude(id = num)
                if curr_user_occup_places:
                    print(curr_user_occup_places)
                    for pl in curr_user_occup_places:
                        if request.user == pl.client and pl != place:
                            pl.delete()
                            place = form.save(commit=False)
                            place.client = request.user
                            place.occupied = True
                            place.save()

                else:
                    print("таких мест нет")
                    place = form.save(commit=False)
                    place.client = request.user
                    place.occupied = True
                    place.save()

            else:
                print(form.is_valid())
                print(form.is_bound)
                print(form.errors)
            return redirect(reverse('room_detail', kwargs={'pk': pk, 'id': id}))

class ReleasePlace(generic.View):
    def get(self, request, pk, id, num):
        office = Office.objects.get(id=pk)
        room = Room.objects.get(id=id)
        place = Place.objects.get(id=num)
        return render(request, 'room/delete.html',
                      context={'office': office, 'room': room, 'place': place})

    def post(self, request, pk, id, num):
        office = Office.objects.get(id=pk)
        room = Room.objects.get(id=id)
        place = Place.objects.get(id=num)
        place.delete()
        return redirect(reverse('index'))


def get_free_places(request):
    offices = Office.objects.all()
    context = {'offices': offices}
    return render(request, 'room/free_places.html', context)

def get_occupied_places(request):
    occupied_places = Place.objects.filter(occupied = True)
    occupied_places = check_date(occupied_places)
    context = {'places': occupied_places}
    return render(request, 'room/occupied_places.html', context)

def get_occupied_places_on_date(request, year, month, day):
    curr_date = datetime.date(year, month, day)
    places = Place.objects.filter(data__gte = curr_date, first_date__lte = curr_date, occupied = True)
    free_places = Place.objects.filter(occupied = False)
    places = check_date(places)
    context = {'occupied_places': places, 'free_places':free_places, 'curr_date': curr_date,
               'count_occupied_places': len(places),
               'count_free_places': len(free_places)}
    return render(request, 'room/date_free.html', context)


class LoginView(generic.View):
    def get(self, request):
        login_form = LoginForm()
        context = {'login_form' : login_form}
        return render(request, 'auth/login.html', context)

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(username = username, password = password)
            if user:
                login(request, user)
                return redirect('index')

        return render(request, 'auth/login.html', context = {'login_form': login_form})

class RegisterView(generic.View):
    def get(self, request):
        register_form = RegisterForm()
        context = {'register_form': register_form}
        return render(request, 'auth/registration.html', context)

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            new_user = register_form.save(commit=False)
            new_user.username = register_form.cleaned_data['username']
            new_user.email = register_form.cleaned_data['email']
            new_user.save()
            new_user.set_password(register_form.cleaned_data['password'])
            new_user.save()
            user = authenticate(username = register_form.cleaned_data['username'],
                                password = register_form.cleaned_data['password'])
            login(request, user)
            return redirect('index')

        context = {'register_form': register_form}
        return render(request, 'auth/registration.html', context)

# -----------------------------REST API OFFICE---------------------------------------------


class OfficeListApiView(generics.ListCreateAPIView): #Список всех офисов
    serializer_class = OfficeSerializer
    permission_classes = [IsAuthenticated]
    queryset = Office.objects.all()


class OfficeDetailApiView(generics.RetrieveUpdateDestroyAPIView): #Информация о офисе
    serializer_class = OfficeSerializer
    permission_classes = [IsAuthenticated]
    queryset = Office.objects.all()


class OfficeRoomListApi(generics.ListCreateAPIView): #Список всех кабинетов в отдельном офисе
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Room.objects.filter(office__id = self.kwargs['pk'])


    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        for room in qs:
            room.place.all = check_date(room.place.all())
            count = Place.objects.filter(room=room, room__office=room.office).count()
            count_of_free_places = Place.objects.filter(room=room, room__office=room.office, occupied=False).count()
            count_of_occupied_places = Place.objects.filter(room=room, room__office=room.office, occupied=True).count()
            Room.objects.filter(id=room.id).update(count_of_places=count, count_of_free_places=count_of_free_places,
                                                   count_of_occupied_places=count_of_occupied_places)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


    def create(self, request, *args, **kwargs):
        print("create")
        serializer = RoomSerializer(data = request.data)
        if serializer.is_valid():
            serializer.create(request.data)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors)


class RoomListApiView(generics.ListCreateAPIView): # Список всех кабинетов
    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        for room in qs:
            room.place.all = check_date(room.place.all())
            count = Place.objects.filter(room=room, room__office=room.office).count()
            count_of_free_places = Place.objects.filter(room=room, room__office=room.office, occupied=False).count()
            count_of_occupied_places = Place.objects.filter(room=room, room__office=room.office, occupied=True).count()
            Room.objects.filter(id=room.id).update(count_of_places=count, count_of_free_places=count_of_free_places,
                                                   count_of_occupied_places=count_of_occupied_places)
        serializer = self.get_serializer(qs, many = True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print("create")
        serializer = RoomSerializer(data = request.data)
        if serializer.is_valid():
            serializer.create(request.data)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors)


class RoomDetailApiView(generics.RetrieveUpdateDestroyAPIView): # Информация об отдельном кабинете
    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format = None):
        room = self.get_object()
        room.place.all = check_date(room.place.all())
        count = Place.objects.filter(room=room, room__office=room.office).count()
        count_of_free_places = Place.objects.filter(room=room, room__office=room.office, occupied=False).count()
        count_of_occupied_places = Place.objects.filter(room=room, room__office=room.office, occupied=True).count()
        room.count_of_places=count
        room.count_of_free_places=count_of_free_places
        room.count_of_occupied_places=count_of_occupied_places
        serializer = RoomSerializer(room)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        room = self.get_object()

        serializer = RoomSerializer(room, request.data)
        if serializer.is_valid():
            serializer.update(room, request.data)
            return Response(serializer.data)
        return Response(serializer.errors)


class RoomPlaceApiView(generics.ListCreateAPIView): # Список всех мест отдельного кабинета
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Place.objects.filter(room__id = self.kwargs['pk'])

    def list(self, request, *args, **kwargs):
        qs = check_date(self.get_queryset())
        serializer = PlaceSerializer(qs, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print("create")
        serializer = PlaceSerializer(data = request.data)
        print(request.data['room'])

        if serializer.is_valid():
            serializer.create(request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


class PlaceListView(generics.ListCreateAPIView): # Список всех мест
    serializer_class = PlaceSerializer
    queryset = Place.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        qs = check_date(self.get_queryset())
        serializer = PlaceSerializer(qs, many = True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        print("create")
        serializer = PlaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


class PlaceDetailView(generics.RetrieveUpdateDestroyAPIView): # Информация об отдельном месте
    serializer_class = PlaceSerializer
    queryset = Place.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format = None):
        place = self.get_object()
        if place.release_place():
            place.reset_fields()
        serializer = PlaceSerializer(place)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        place = self.get_object()
        if place.client == request.user:#если клиент - это пользователь
            serializer = PlaceSerializer(place, data = request.data)
            if serializer.is_valid():
                serializer.update(place, request.data)
                return Response(serializer.data, status = status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif place.client == None:
            for p in Place.objects.filter(client = request.user).exclude(id = place.id): #если пользователь сидит на каком-то месте
                p.reset_fields()
            serializer = PlaceSerializer(place, data = request.data)
            if serializer.is_valid():
                place.client = request.user
                serializer.update(place, request.data)
                return Response(serializer.data, status = status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif place.client != request.user or request.user == None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        place = self.get_object()
        place.delete()
        return Response(status = status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def api_user_list(request):
    if request.method == 'GET':
        clients = User.objects.all()
        serializer = UserSerializer(clients, many=True)
        return Response(serializer.data)


class PlaceListOccupiedApiView(generics.ListCreateAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Place.objects.filter(occupied = True)

    def create(self, request, *args, **kwargs):
        print("create")
        serializer = PlaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


class PlaceListFreeApiView(generics.ListCreateAPIView):
    serializer_class = PlaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Place.objects.filter(occupied=False)

    def create(self, request, *args, **kwargs):
        print("create")
        serializer = PlaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(request.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_previous_place_list(request, client):
    if request.method == 'GET':
        user = User.objects.get(username = client)
        queryset = UsersPreviousPlace.objects.filter(client = user)
        serializer = UserPreviousPlaceSerializer(queryset, many = True)
        return Response(serializer.data)



