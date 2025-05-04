# serializers.py
from rest_framework import serializers
from .models import DataTable
import pandas as pd

import json
from rest_framework import serializers


class DataTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataTable
        fields = (
            "category",
            "project",
            "gender",
            "age",
            "date",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Convert demography JSON field to individual fields
        demography = json.loads(instance.demography) if instance.demography else {}
        for key, value in demography.items():
            if pd.isna(value):
                value = 0
            representation[key] = int(value)

        # Convert received_items JSON field to individual fields
        received_items = (
            json.loads(instance.received_items) if instance.received_items else {}
        )
        for key, value in received_items.items():
            if key == "benef" or key == "unit":
                if pd.isna(value):
                    value = 0
                value = int(value)
            representation[key] = value

        representation["benef"] = int(demography["benef"])
        representation["category_name"] = instance.category.name
        representation["project_name"] = instance.project.name
        representation["oblast"] = instance.place.oblast
        representation["rayon"] = instance.place.rayon
        representation["gromada"] = instance.place.gromada
        representation["settlement"] = instance.place.settlement

        return representation
