from django.conf import settings

import requests
import uuid
import time
import json
import re
import sys

NCP_SECRET_KEY = getattr(settings, 'NCP_SECRET_KEY', 'NCP_SECRET_KEY')
NCP_APIGW_URL = getattr(settings, 'NCP_APIGW_URL', 'NCP_APIGW_URL')


# 한글인지 확인
def isHangul(text):
    #Check the Python Version
    pyVer3 =  sys.version_info >= (3, 0)

    if pyVer3 : # for Ver 3 or later
        encText = text
    else: # for Ver 2.x
        if type(text) is not unicode:
            encText = text.decode('utf-8')
        else:
            encText = text

    hanCount = len(re.findall(u'[\u3130-\u318F\uAC00-\uD7A3]+', encText))
    return hanCount > 0

def get_dialogue(data):
    # with open('json_sample.json', encoding='utf-8') as data:
    json_data = json.loads(data.text.encode('utf8'))
    # json_data = json.load(data)
    # json_data = data

    bbox_ls = []
    images_ls = json_data.get('images')
    print(images_ls)
    fields_ls = images_ls[0]['fields']

    for idx, field in enumerate(fields_ls):
        bbox_temp = []
        inferText = field['inferText']
        boundingPoly = field['boundingPoly']['vertices']
        
        # 왼쪽 위, 오른쪽 위, 오른쪽 아래,왼쪽 아래 로 저장
        for vertice in boundingPoly[0:]:
            x = vertice['x']
            y = vertice['y']
            bbox_temp.append(int(x))
            bbox_temp.append(int(y))
        
        bbox_temp.append(inferText)
        bbox_ls.append(bbox_temp)
    
    # 대화 추출
    participant = ''
    for idx, row in enumerate(bbox_ls):
        if isHangul(row[-1]) == True:
            participant = row[-1]
            bbox_ls = bbox_ls[idx+1:]
            break

    new_bbox_ls = []
    dialogue = []
    for idx, row in enumerate(bbox_ls):
        if row[-1] == participant:
            continue
        elif row[-1] == 'PM' or row[-1] == 'AM':
            new_bbox_ls.append(dialogue)
            dialogue = []
            continue
        elif row[-1] in ':':
            continue
        
        if isHangul(row[-1]):
            dialogue.append(row[-1])
    
    return new_bbox_ls


def clova_ocr(image_url):

    request_json = {
        'images': [
            {
                'format': 'png',
                'name': 'demo',
                'url': image_url
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    payload = json.dumps(request_json).encode('UTF-8')
    headers = {
    'X-OCR-SECRET': NCP_SECRET_KEY,
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", NCP_APIGW_URL, headers=headers, data = payload)
    # 대화 추출
    res = get_dialogue(response)

    return res