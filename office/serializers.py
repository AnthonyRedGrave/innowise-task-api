from task_office.office.models import *
from rest_framework import serializers

class OfficeSerializer(serializers.HyperlinkedModelSerializer):
    #room = serializers.StringRelatedField(many=True)
    class Meta:
        model = Office
        fields = ['id', 'address']

# class RoomSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Room
#         fields = ['id', 'number', 'count_of_places', 'count_of_occupied_places', 'count_of_free_places']
#
