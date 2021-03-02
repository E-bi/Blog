import random

from django.db import models
from django.db.models import DateTimeField


def default_sign():
    signs = ['低调的家伙', '人类诞生', '大学士']
    return random.choice(signs)


# Create your models here.
class UserProfile(models.Model):
    username = models.CharField('用户名', max_length=11, primary_key=True)
    nickname = models.CharField('昵称', max_length=30)
    email = models.EmailField('邮箱')
    password = models.CharField('密码', max_length=32)
    sign = models.CharField('个人签名', max_length=50, default=default_sign)
    info = models.CharField('个人描述', max_length=150, default='')
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)
    # upload_to 指定存储位置 MEDIA_ROOT + upload_to的值
    # wiki/media/avatar
    avatar = models.ImageField('头像', upload_to='avatar', default='')
    login_time = models.DateTimeField('登录时间', null=True)

    class Meta:
        db_table = 'user_profile'
