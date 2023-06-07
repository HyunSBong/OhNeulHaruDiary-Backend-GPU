from rest_framework import status
from rest_framework.response import Response

import os

from . import promptist
from . import text_summarization as summ
from . import text_recognition as recog
from . import diffusion

from . import kafka_connector

# k_producer = kafka_connector.KafkaConnector()
k_producer = kafka_connector.KafkaConnector()
k_consumer = kafka_connector.KafkaConnector()

kafka_topic = ('inference_prompt', 'image')

def to_kafka_summm_infer_diary(topic, diary_id, full_diary):
    summarize = summ.inference_diary(full_diary) # input: String type
    optimized_prompt = promptist.promptist_manual(summarize)

    data = {
        'diary_id': diary_id,
        'prompt': optimized_prompt
    }
    
    k_producer.Kafka_Producer(topic, data)
    
    return optimized_prompt

def to_kafka_summm_infer_dialogue(topic, diary_id, sum_dialogue):
    summarize = summ.inference_dialogue(sum_dialogue) # input: List type
    optimized_prompt = promptist.promptist_manual(summarize)

    data = {
        'diary_id': diary_id,
        'prompt': optimized_prompt
    }

    k_producer.Kafka_Producer(topic, data)
    
    return optimized_prompt

def to_kafka_diffusion(topic, v):
    k_producer.Kafka_Producer(topic, v)

def from_kafka_summm_infer_diary():
    consumer = k_consumer.kafka_Consumer(kafka_topic[0])
    for msg in consumer:
        print("Topic: %s, Partition: %d, Offset: %d, Key: %s, Value: %s" % (
            msg.topic, msg.partition, msg.offset, msg.key, msg.value))
        
        full_diary = msg.value['full_diary']
        full_dialog = msg.value['full_dialog']
        prompt = msg.value['prompt']
        url = msg.value['url']
        thumbnail_url = msg.value['thumbnail_url']
        serializer = msg.value['serializer']

        summarize = summ.inference_diary(full_diary) # input: String type
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

def from_kafka_summm_infer_dialogue():
    consumer = k_consumer.kafka_Consumer(kafka_topic[0])
    for msg in consumer:
        print("Topic: %s, Partition: %d, Offset: %d, Key: %s, Value: %s" % (
            msg.topic, msg.partition, msg.offset, msg.key, msg.value))
        
        req_urls = msg.value['value']
        serializer = msg.value['serializer']

        sum_dialogue = []
        for url in req_urls:
            dialogue = recog.clova_ocr(url) # url은 s3 url로 받아야함.
            print(dialogue)
            for content in dialogue:
                for raw in content:
                    sum_dialogue.append(raw)

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

def from_kafka_diffusion():
    consumer = k_consumer.kafka_Consumer(kafka_topic[0])
    for msg in consumer:
        print("Topic: %s, Partition: %d, Offset: %d, Key: %s, Value: %s" % (
            msg.topic, msg.partition, msg.offset, msg.key, msg.value))
        
        full_diary = msg.value['full_diary']
        full_dialog = msg.value['full_dialog']
        prompt = msg.value['prompt']
        url = msg.value['url']
        thumbnail_url = msg.value['thumbnail_url']
        serializer = msg.value['serializer']

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
    