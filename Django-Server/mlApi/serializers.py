from rest_framework import serializers
from .models import MLItem

class MLItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = MLItem
        fields = ("__all__")
        # fields = ["full_diary", "full_dialog", "prompt", "url", 'thumbnail_url']