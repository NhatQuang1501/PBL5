from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("hello/", views.say_hello),
    path("",views.trangchu),
    path("trangchu/",views.trangchu),
    # path("down_audio/",views.downaudio),
    # path('run_prediction/', views.run_prediction, name='run_prediction')
    # path("get_predict/", views.get_predict)
]