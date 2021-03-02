from django.urls import re_path

from wtoken import views

urlpatterns = [
    re_path(r'^$', views.tokens)

]