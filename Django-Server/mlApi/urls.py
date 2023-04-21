from django.urls import include, path
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register('mlapi', views.MLItemViewSet) # host url/mlapi

urlpatterns = [
    # path('', include(router.urls)),
    path('test/', views.TestPostMessageKafkaView.as_view()),
]