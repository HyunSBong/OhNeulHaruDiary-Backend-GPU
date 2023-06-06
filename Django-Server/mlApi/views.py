from django.conf import settings
from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import status
from rest_framework.generics import CreateAPIView, UpdateAPIView ,DestroyAPIView
from rest_framework.response import Response

from .serializers import MLItemSerializer
from .models import MLItem

from . import kafka_connector
from . import kafka_network as kn
from . import promptist
from . import text_summarization as summ
from . import text_recognition as recog
from . import diffusion

import multiprocessing as mp

# class MLItemViewSet(viewsets.ModelViewSet):
#     queryset = MLItem.objects.all()
#     serializer_class = MLItemSerializer
kafka_topic = ('inference_diary', 'inference_dialogue', 'diffusion')

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

        # json_data = {
        #         'full_diary': full_diary,
        #         'full_dialog': full_dialog,
        #         'prompt' : prompt,
        #         'url' : url,
        #         'thumbnail_url' : thumbnail_url,
        #         'serializer' : serializer
        #     }
        # p_infer_diary = mp.Process(target=kn.to_kafka_summm_infer_diary, args=(kafka_topic[0], json_data))
        # p_infer_diary.start()

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
        req_urls = self.request.data.get('req_urls') # 얘는 꼭 필요 -> 이미지에서 가져와야함.

        # json_data = {
        #         'value' : req_urls,
        #         'serializer' : serializer
        #     }
        # p_infer_dialogue = mp.Process(target=kn.to_kafka_summm_infer_dialogue, args=(kafka_topic[1], json_data))
        # p_infer_dialogue.start()
        
        processes = []  
        manager = mp.Manager()
        return_dict = manager.dict()
        
        for idx, url in enumerate(req_urls):
            process = mp.Process(target=recog.clova_ocr, args=(idx, url, return_dict,))
            processes.append(process)
            process.start()
            
        for process in processes:
            process.join()
        
        sorted_return_dict = sorted(return_dict.items())
        get_values = lambda lst: [value for _, value in lst]
        sum_dialogue = get_values(sorted_return_dict)

        get_values = lambda lst: [value[0] for value in lst]
        sum_dialogue = get_values(sum_dialogue)
        print(sum_dialogue)
        
        summarize = summ.inference_dialogue(sum_dialogue) # input: List type
        optimized_prompt = promptist.promptist_manual(summarize)

        if serializer.is_valid():
            serializer.save(
                full_dialog = sum_dialogue,
                prompt = optimized_prompt,
                url = req_urls
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

        # json_data = {
        #         'full_diary': full_diary,
        #         'full_dialog': full_dialog,
        #         'prompt' : prompt,
        #         'url' : url,
        #         'thumbnail_url' : thumbnail_url,
        #         'serializer' : serializer
        #     }
        # p_diffusion = mp.Process(target=kn.to_kafka_diffusion, args=(kafka_topic[2], json_data))
        # p_diffusion.start()

        files = []
        img = diffusion.generate_one(prompt)
        files.append(img) # return 파일 이름 (temp/*)
        
        # S3 upload
        uploaded_urls = []
        try :
            for filename in files :
                url = diffusion.uploadS3(filename)
                uploaded_urls.append(url)

            if serializer.is_valid():
                serializer.save(
                    full_diary = full_diary,
                    full_dialog = full_dialog,
                    prompt = prompt,
                    url = uploaded_urls,
                    thumbnail_url = thumbnail_url
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        except:
            return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class GenerateImageUpdateView(UpdateAPIView):
#     queryset = MLItem.objects.all()
#     serializer_class = MLItemSerializer
#     lookup_field = 'pk'

#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', True)
#         instance = self.get_object()

#         # 이미지 생성
#         files = []
#         img = diffusion.generate_one(instance.prompt)
#         files.append(img)

#         # S3 upload
#         uploaded_urls = []
#         try :
#             for filename in files :
#                 url = diffusion.uploadS3(filename)
#                 uploaded_urls.append(url)

#             data = {'url' : AWS_S3_CUSTOM_DOMAIN+"%s"%(file)}
#             serializer = self.get_serializer(instance, data=data, partial=partial)

#             if serializer.is_valid():
#                 self.perform_update(serializer)
#                 return Response(serializer.data, status=status.HTTP_200_OK) 
#             return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         except:
#             return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class DeleteView(DestroyAPIView):
#     queryset = MLItem.objects.all()
#     serializer_class = MLItemSerializer
#     lookup_field = 'pk'