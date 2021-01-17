from django.shortcuts import render
from .models import *
from django.views import generic
from django.db.models import Q
from .forms import *
from django.shortcuts import reverse, redirect
from django.contrib.auth import authenticate, login

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
    correct_places = []
    for place in places:
        if place.release_place():
            print("было освобождено {}".format(place))
            place.delete()
            correct_places.append(place)
        else:
            print("Все нормально")
            correct_places.append(place)

    context = {'room': room, 'places': correct_places, 'office': office}
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
                #print(form.cleaned_data)
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

    rooms = Room.objects.all()
    free_places = Place.objects.filter(occupied = False)
    context = {'offices': offices}
    return render(request, 'room/free_places.html', context)

def get_occupied_places(request):
    occupied_places = Place.objects.filter(occupied = True)
    correct_places = []
    for place in occupied_places:
        if place.release_place():
            print("было освобождено {}".format(place))
            place.delete()
            correct_places.append(place)
        else:
            print("Все нормально")
            correct_places.append(place)
    context = {'places': correct_places}
    return render(request, 'room/occupied_places.html', context)

def get_occupied_places_on_date(request, year, month, day):
    curr_date = datetime.date(year, month, day)
    places = Place.objects.filter(data__gte = curr_date, first_date__lte = curr_date, occupied = True)
    free_places = Place.objects.filter(occupied = False)
    occupied_places = []
    for place in places:
        if place.release_place():
            print("было освобождено {}".format(place))
            place.delete()
            occupied_places.append(place)
        else:
            print("Все нормально")
            occupied_places.append(place)


    print(curr_date)
    context = {'occupied_places': occupied_places, 'free_places':free_places, 'curr_date': curr_date,
               'count_occupied_places': len(occupied_places),
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
