from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, UpdateAPIView ,DestroyAPIView
from rest_framework.response import Response

from .serializers import MLItemSerializer
from .models import MLItem
from . import kafka_connector


# class MLItemViewSet(viewsets.ModelViewSet):
#     queryset = MLItem.objects.all()
#     serializer_class = MLItemSerializer

class TestPostMessageKafkaView(CreateAPIView):
    model = MLItem
    serializer_class = MLItemSerializer

    def perform_create(self, serializer):
        full_diary = self.request.data.get("full_diary", None)
        full_dialog = self.request.data.get("full_dialog", None)
        prompt = self.request.data.get("prompt", None)
        url = self.request.data.get("url", None)
        thumbnail_url = self.request.data.get("thumbnail_url", None)

        kafka_topic = "Diary"
        if full_diary == None:
            kafka_topic = "Dialog"
        
        print("REQ TEST : " + full_diary)

        data = {'message': '일기 원본 : ' + full_diary}
        consumer = kafka_connector.KafkaConsumer(kafka_topic, data)
        for message in consumer:
            print("[Kafka]")
            print("Topic: %s, Partition: %d, Offset: %d, Key: %s, Value: %s" % (
                message.topic, message.partition, message.offset, message.key, message.value
            ))

        # serializer.save(
        #     full_diary = full_diary,
        #     full_dialog=full_dialog,
        #     prompt = prompt,
        #     url = url,
        #     thumbnail_url = thumbnail_url
        # )

 