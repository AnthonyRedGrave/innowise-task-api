from django.shortcuts import render
from .models import *
from django.views import generic
from django.db.models import Q
from .forms import *
from django.shortcuts import reverse, redirect

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
                curr_user_occup_places = Place.objects.exclude(id = num)
                if curr_user_occup_places:
                    print(curr_user_occup_places)
                    for pl in curr_user_occup_places:
                        if request.user == pl.client and pl != place:
                            pl.delete()
                            place = form.save()
                            place.client = request.user
                            place.save()

                else:
                    place = form.save()
                    place.client = request.user
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





