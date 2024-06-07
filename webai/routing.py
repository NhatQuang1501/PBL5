from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/ai/predict/$', consumers.PredictConsumer.as_asgi()),
]   