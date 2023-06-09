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
    json_data = json.loads(data.text.encode('utf8'))

    bbox_ls = []
    images_ls = json_data.get('images')
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
    participant_ls = []
    participant_box_y = 0
    participant_search_status = False
    for idx, row in enumerate(bbox_ls):
        # exception
        if participant_search_status:
            break
        # 대화 상태 y좌표 구분 (좌표값이 110 이하안 경우 아이폰 카카오톡에서 투명하게 보이는 대화 내용이 감지되는 예외 처리)
        if row[1] < 110:
            continue
        # 대화 상대 인식
        if isHangul(row[-1]) == True:
            if len(participant_ls) >= 1:
                # '명지대 홍길동' 등 이름이 띄어쓰기로 긴 경우 대화 상대인지 y좌표로 판별
                box_y = row[1] - participant_box_y
                if box_y > 20:
                    bbox_ls = bbox_ls[idx:]
                    participant_search_status = True
                    break
            participant_ls.append(row[-1])
            participant_box_y = row[1]

            # bbox_ls = bbox_ls[idx+1:]
        # exception
        if isHangul(row[-1]) == False and len(participant_ls) >= 1:
            break

    participant = ' '.join(participant_ls) 
    print(participant)

    # 날짜 판별 "11:34"
    time_pattern = re.compile(r'^\d{1,2}:\d{2}$')
    check_time_format = lambda time_str: bool(time_pattern.match(time_str))

    new_bbox_ls = []
    dialogue = []
    for idx, row in enumerate(bbox_ls):
        if len(dialogue) > 1 and ' '.join(dialogue) == participant:
            dialogue = dialogue[len(dialogue):]
        if row[-1] == participant:
            continue
        elif check_time_format(row[-1]):
            new_bbox_ls.append(dialogue)
            dialogue = []
            continue
        elif row[-1] == 'PM' or row[-1] == 'AM':
            new_bbox_ls.append(dialogue)
            dialogue = []
            continue
        elif row[-1] == '오전' or row[-1] == '오후':
            new_bbox_ls.append(dialogue)
            dialogue = []
            continue
        elif row[-1] in ':':
            continue
        
        if isHangul(row[-1]):
            dialogue.append(row[-1])
            
    result = []
    if len(new_bbox_ls) > 2:
        for idx, content in enumerate(new_bbox_ls):
            if len(content) != 0:
                result.append(' '.join(content))
    print(result)
    return result


def clova_ocr(idx, image_url, return_dict):
    print(image_url)

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
    print(response)
    # 대화 추출
    res = get_dialogue(response)

    return_dict[idx] = res
