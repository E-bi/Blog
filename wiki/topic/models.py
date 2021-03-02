from time import time

from django.db import models


# Create your models here.
from user.models import UserProfile


class Topic(models.Model):
    title = models.CharField('文章名称', max_length=50)
    # 技术类文章tec or 非技术类文章no-tec
    category = models.CharField('文章种类', max_length=20)
    # public or private
    limit = models.CharField('权限', max_length=10)
    introduce = models.CharField('简介', max_length=30)
    content = models.CharField('内容', max_length=90)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    update_time = models.DateTimeField('修改时间', auto_now=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    class Meta:
        db_table = 'topic'
