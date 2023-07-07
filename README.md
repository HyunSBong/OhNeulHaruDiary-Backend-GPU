# SketchDay-Backend-ML
머신러닝 및 분산 처리 서버

## 프로젝트 개요
명지대학교 캡스톤디자인 프로젝트 - SketchDay (기록을 더 풍성하게, 그림 일기 서비스)
<img width="1080" alt="title" src="https://user-images.githubusercontent.com/69189272/233691909-1cab5b7e-ea80-42f3-84a8-e794a34a1350.png">
<img width="724" alt="content" src="https://github.com/MJU-capstone-2023/SketchDay-Backend-ML/assets/69189272/7fc248d4-3871-46c2-849d-d75828e3a81e">

## 주요기능
- 일기 내용을 기반으로 적절한 그림 생성
- 메신저 스크린샷만으로 그림 일기 생성
  - 메신저 스크린샷에서 대화 내용을 파악

## 프로젝트 인원
총 4명 (Front-End 1명, Back-End 3명, ML 1명)

# Environment

|분류|이름|버전|
|:---|:---|:---|
|OS|ubuntu|22.04|
|OS|MacOS|13.2|
||Docker|20.10.7|
||Docker-compose|3.2|
||Kafdrop|4.0.0|
|Language|Python|3.9.2|
||Scala|2.12|
|DB|MySQL|5.7|
|Distribute PipeLine|Kafka|2.8.0|
||Spark|3.1.2|
||Airflow|2.2.3|
||kafka-python|0.10.0|
|Web|django|4.2|
||mysqlclient|2.1.1|
||djangorestframework|3.14.0|
||django-storages|1.13.2|
||boto3|1.26.114|
|ML|torch|2.0.0|
||diffusers|0.15.0|
||transformers|4.28.1|
||accelerate|0.18.0|
||CUDA|11.2.2|
||cuDNN|8|
||Nvidia Driver|470.57.02|

# Directories
|디렉토리명|설명|
|:---|:---|
|Django-Server|장고 서버 관련 디렉토리|
|docker|도커 파일 관련 디렉토리|

## Service Architecture
<img width="1079" alt="workflow" src="https://user-images.githubusercontent.com/69189272/233691906-0b273fba-142c-4c27-aa65-67be3a693b1d.png">

## Contact
본 프로젝트는 NCP papago translation, email auth 등 실행 전에 설정해야할 부분이 많습니다. 관심있으신 분은 [email](sanseng@mju.ac.kr)로 연락주세요.
