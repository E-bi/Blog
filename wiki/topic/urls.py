from django.urls import re_path

from topic import views

urlpatterns = [
    re_path(r'^/(?P<author_id>\w{1,11})$', views.topics),
]