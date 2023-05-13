from django.conf import settings
from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView ,DestroyAPIView
from rest_framework.response import Response

from .serializers import MLItemSerializer
from .models import MLItem

from . import kafka_connector
from . import promptist
from . import text_summarization as summ
from . import text_recognition as recog
from . import diffusion

import uuid
import boto3

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
        consumer = kafka_connector.KafkaProducer(kafka_topic, data)
        for message in consumer:
            print("[Kafka]")
            print("Topic: %s, Partition: %d, Offset: %d, Key: %s, Value: %s" % (
                message.topic, message.partition, message.offset, message.key, message.value
            ))

        serializer.save(
            full_diary = full_diary,
            full_dialog=full_dialog,
            prompt = prompt,
            url = url,
            thumbnail_url = thumbnail_url
        )

class SummaryDiaryView(CreateAPIView):
    model = MLItem
    serializer_class = MLItemSerializer

    def perform_create(self, serializer):
        full_diary = self.request.data.get("full_diary", None) # 얘는 꼭 필요
        full_dialog = self.request.data.get("full_dialog", None)
        prompt = self.request.data.get("prompt", None)
        url = self.request.data.get("url", None)
        thumbnail_url = self.request.data.get("thumbnail_url", None)

        summarize = summ.inference_diary(full_diary) # input: String type
        # print(summarize)
        # summarize = "친구와 역에서 만났다."
        optimized_prompt = promptist.promptist_manual(summarize)

        if serializer.is_valid():
            serializer.save(
                full_diary = full_diary,
                full_dialog = full_dialog,
                prompt = optimized_prompt,
                url = url,
                thumbnail_url = thumbnail_url
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SummaryDialogueView(CreateAPIView):
    model = MLItem
    serializer_class = MLItemSerializer

    def perform_create(self, serializer):
        full_diary = self.request.data.get("full_diary", None)
        full_dialog = self.request.data.get("full_dialog", None) 
        prompt = self.request.data.get("prompt", None)
        url = self.request.data.get("url", None)
        thumbnail_url = self.request.data.get("thumbnail_url", None)
        req_files = self.request.FILES.getlist('req_files') # 얘는 꼭 필요 -> 이미지에서 가져와야함.
        

        optimized_prompt = ''
        dialogues = []
        file_urls = []
        for file in req_files:
            # full_dialog = recog. ## 이미지에서 대화추출 로직 output: List type
            # summarize = summ.inference_dialogue(full_dialog) # input: List type
            # dialogues.append(summarize)
            # S3 upload
            AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID', 'AWS_ACCESS_KEY_ID')
            AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', 'AWS_SECRET_ACCESS_KEY')
            AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'AWS_STORAGE_BUCKET_NAME')
            AWS_S3_CUSTOM_DOMAIN = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'AWS_S3_CUSTOM_DOMAIN')
            try :
                s3r = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                file._set_name(str(uuid.uuid4()))
                s3r.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(Body=file)

                file_urls.append(AWS_S3_CUSTOM_DOMAIN+"%s"%(file))
            except:
                return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # optimized_prompt = promptist.promptist_manual(dialogues)
        optimized_prompt = 'test'

        if serializer.is_valid():
            serializer.save(
                full_diary = full_diary,
                full_dialog = full_dialog,
                prompt = optimized_prompt,
                url = file_urls,
                thumbnail_url = thumbnail_url
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GenerateImageCreateView(CreateAPIView):
    model = MLItem
    serializer_class = MLItemSerializer

    def perform_create(self, serializer):
        full_diary = self.request.data.get("full_diary", None) # 얘는 꼭 필요
        full_dialog = self.request.data.get("full_dialog", None)
        prompt = self.request.data.get("prompt", None)
        url = self.request.data.get("url", None)
        thumbnail_url = self.request.data.get("thumbnail_url", None)

        files = []
        img = diffusion.generate_one(prompt)
        files.append(img)
        
        # S3 upload
        file_urls = []
        AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID', 'AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', 'AWS_SECRET_ACCESS_KEY')
        AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'AWS_STORAGE_BUCKET_NAME')
        AWS_S3_CUSTOM_DOMAIN = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'AWS_S3_CUSTOM_DOMAIN')
        try :
            s3r = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

            for file in files :
                file._set_name(str(uuid.uuid4()))
                s3r.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(Body=file)
                file_urls.append(AWS_S3_CUSTOM_DOMAIN+"%s"%(file))

            if serializer.is_valid():
                serializer.save(
                    full_diary = full_diary,
                    full_dialog = full_dialog,
                    prompt = prompt,
                    url = file_urls,
                    thumbnail_url = thumbnail_url
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        except:
            return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class GenerateImageUpdateView(UpdateAPIView):
    queryset = MLItem.objects.all()
    serializer_class = MLItemSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()

        # 이미지 생성
        files = []
        img = diffusion.generate_one(instance.prompt)
        files.append(img)

        # S3 upload
        AWS_ACCESS_KEY_ID = getattr(settings, 'AWS_ACCESS_KEY_ID', 'AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = getattr(settings, 'AWS_SECRET_ACCESS_KEY', 'AWS_SECRET_ACCESS_KEY')
        AWS_STORAGE_BUCKET_NAME = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'AWS_STORAGE_BUCKET_NAME')
        AWS_S3_CUSTOM_DOMAIN = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'AWS_S3_CUSTOM_DOMAIN')
        try :
            s3r = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

            for file in files :
                file._set_name(str(uuid.uuid4()))
                s3r.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(Body=file)

            data = {'url' : AWS_S3_CUSTOM_DOMAIN+"%s"%(file)}
            serializer = self.get_serializer(instance, data=data, partial=partial)

            if serializer.is_valid():
                self.perform_update(serializer)
                return Response(serializer.data, status=status.HTTP_200_OK) 
            return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class DeleteView(DestroyAPIView):
#     queryset = MLItem.objects.all()
#     serializer_class = MLItemSerializer
#     lookup_field = 'pk'