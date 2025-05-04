import json
from rest_framework import serializers
from activity_map.models import Marker, Place
from reports.models import Category, Project
from data_tables.models import DataTable, RegionStatistic


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name", "donors")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "icon", "color")


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ("id", "oblast", "rayon", "gromada", "settlement")


class DataTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataTable
        fields = (
            "photo",
            "category",
            "project",
            "gender",
            "age",
            "date",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["category_name"] = instance.category.name
        representation["project_name"] = instance.project.name
        representation["oblast"] = instance.place.oblast
        representation["rayon"] = instance.place.rayon
        representation["gromada"] = instance.place.gromada
        representation["settlement"] = instance.place.settlement
        received_items = (
            json.loads(instance.received_items) if instance.received_items else {}
        )
        representation["received_items"] = received_items

        return representation


class MarkerSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    category = CategorySerializer()
    place = PlaceSerializer()
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()

    class Meta:
        model = Marker
        fields = (
            "id",
            "category",
            "project",
            "place",
            "lat",
            "lng",
        )

    def get_lat(self, obj):
        return obj.location.y

    def get_lng(self, obj):
        return obj.location.x


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name",)


class RegionStatisticSerializer(serializers.Serializer):
    name = serializers.CharField()
    oblast = serializers.CharField()
    total_benef = serializers.IntegerField()
    activities = serializers.SerializerMethodField()

    def get_activities(self, instance):
        region = RegionStatistic.objects.filter(
            name=instance["name"], oblast=instance["oblast"]
        ).first()
        if region:
            return list(
                region.project.categories.values_list("name", flat=True).distinct()
            )
        return []

    def to_representation(self, instance):
        return {
            "name": instance["name"],
            "oblast": instance["oblast"],
            "total_benef": instance["total_benef"],
            "activities": self.get_activities(instance),
        }
