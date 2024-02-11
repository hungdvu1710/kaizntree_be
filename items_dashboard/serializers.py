from rest_framework import serializers
from .models import Item, Tags


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    tags = TagsSerializer(many=True, slug_field="name", read_only=True)

    class Meta:
        model = Item
        fields = "__all__"
