from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path

from user import views

urlpatterns = [
    # http://127.0.0.1:8000/v1/users
    re_path(r'^$', views.users),

    # http://127.0.0.1:8000/v1/users/<username>
    re_path(r'^/(?P<username>\w{1,11})$', views.users),

    # http://127.0.0.1:8000/v1/users/<username>/avatar
    re_path(r'^/(?P<username>\w{1,11})/avatar$', views.users_avatar)

]

