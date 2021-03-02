from django.urls import re_path

from message import views

urlpatterns = [
    re_path(r'^/(?P<topic_id>\d+)$', views.messages)
]