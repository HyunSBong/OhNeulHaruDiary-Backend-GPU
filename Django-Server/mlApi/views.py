from django.shortcuts import render
from rest_framework import viewsets
from .serializers import MLItemSerializer
from .models import MLItem


class MLItemViewSet(viewsets.ModelViewSet):
    queryset = MLItem.objects.all()
    serializer_class = MLItemSerializer