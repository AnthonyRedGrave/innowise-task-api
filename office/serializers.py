from .models import *
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
import datetime
from django.contrib.auth.models import User
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ValidationError

class UserPreviousPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersPreviousPlace
        fields = "__all__"


class PlaceSerializer(serializers.ModelSerializer):
    client = serializers.SlugRelatedField(slug_field="username", read_only=True)
    room_name = serializers.CharField(source='room', read_only = True)

    class Meta:
        model = Place
        fields = ['id', 'view', 'first_date', 'data', 'room', 'room_name', 'occupied', 'client']
        read_only_fields = ['first_date', 'client']

    def create(self, validated_data):
        print("placeSerializer create")
        client = None
        room = Room.objects.get(id = validated_data['room'])
        occupied = False
        data = None
        first_date = None
        place = Place.objects.create(data = data, first_date = first_date, occupied = occupied, client = client, room = room)
        place.view = "Место №{} (свободно)".format(place.id)
        place.save()
        return place

    def validate(self, data):
        if data['data']:
            if data['data'] < datetime.date.today():
                raise serializers.ValidationError({"data": "Wrong date!"})

        if data['room'] == None:
            raise serializers.ValidationError({"room": "This field is required!"})
        return data

    def update(self, instance, validated_data):
        print('update serializer')
        if instance.room.id != int(validated_data['room']):
            raise serializers.ValidationError({"room": "You can't change room!"})
        if validated_data['occupied']:
            print("True")
            instance.occupied = True
            instance.data = validated_data['data']
            instance.first_date = datetime.date.today()
            instance.view = "Место №{} (занято)".format(instance.id)
            instance.save()
        else:
            print("False")
            instance.occupied = False
            instance.data = None
            instance.first_date = None
            instance.client = None
            instance.view = "Место №{} (свободно)".format(instance.id)

        return instance


class RoomSerializer(serializers.ModelSerializer):
    office_name = serializers.CharField(source='office', read_only=True)
    place = PlaceSerializer(many = True, read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'number', 'count_of_places', 'count_of_occupied_places', 'count_of_free_places',
                        'office_name', 'office', 'place']
        read_only = ['place', 'office_name']

    def validate(self, data):
        if int(data['number']) < 0:
            raise serializers.ValidationError({"number": "Wrong room number!"})
        if data['office'] == None:
            raise serializers.ValidationError({"office": "This field is required!"})
        return data

    def create(self, validated_data):
        print(validated_data)
        number = validated_data['number']
        count_of_places = int(validated_data['count_of_places'])
        office = Office.objects.get(id = validated_data['office'])
        room = Room.objects.create(number = number, count_of_places = count_of_places, office = office)
        return room

    def update(self, instance, validated_data):
        print("roomSerialize update")
        if instance['office'] != validated_data['office']:
            raise serializers.ValidationError({"office": "You can't change office!"})

        count_of_all_places = validated_data['count_of_places']

        if int(instance.count_of_places) == 0 and int(instance.count_of_places) < int(count_of_all_places):
            print("если 0 либо указано больше")
            instance.count_of_places = count_of_all_places
            instance.count_of_occupied_places, instance.count_of_free_places = 0, instance.count_of_places

            for _ in range(int(instance.count_of_places)):
                place = Place(room = instance)
                place.save()

        elif int(instance.count_of_places) > int(count_of_all_places):
            print("если указано меньше")

            places = Place.objects.filter(room = instance, occupied = False)
            to_delete = int(instance.count_of_places) - int(count_of_all_places)

            places_to_del = places[0:to_delete]

            for p in places_to_del:
                p.delete()
            instance.count_of_places = count_of_all_places
            instance.count_of_occupied_places, instance.count_of_free_places = 0, instance.count_of_places

        elif int(instance.count_of_places) < int(count_of_all_places):
            print("если больше")
            for _ in range(int(count_of_all_places) - int(instance.count_of_places)):
                place = Place(room=instance)
                place.save()
        instance.count_of_places = int(count_of_all_places)
        instance.count_of_free_places = Place.objects.filter(room = instance, occupied = False).count()
        instance.count_of_occupied_places = Place.objects.filter(room=instance, occupied=True).count()
        return instance


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = ['id', 'address']


class UserSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(source='place', read_only=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'place_name']