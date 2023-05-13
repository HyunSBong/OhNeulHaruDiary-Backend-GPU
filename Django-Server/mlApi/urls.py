from django.urls import include, path
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register('mlapi', views.MLItemViewSet) # host url/mlapi

urlpatterns = [
    # path('', include(router.urls)),
    path('test/', views.TestPostMessageKafkaView.as_view()),
    path('summaryDiary/', views.SummaryDiaryView.as_view()),
    path('summaryDialogue/', views.SummaryDialogueView.as_view()),
    path('generateImage/create', views.GenerateImageCreateView.as_view()),
    path('generateImage/update', views.GenerateImageUpdateView.as_view()),
]