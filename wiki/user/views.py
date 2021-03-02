import datetime
import hashlib
import json
import time

import jwt
from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.
from tools.login_check import login_check
from user.models import UserProfile
from wtoken.views import make_token

@login_check('PUT')
def users(request, username=None):
    if request.method == 'GET':

        if username:
            user = UserProfile.objects.filter(username=username)
            user = user[0]
            # 拿用户具体数据
            # 有查询字符串[?nickname=allen]
            if request.GET.keys():
                # 查询字符串
                data = {}
                for k in request.GET.keys():
                    if k == 'password':
                        continue
                    if hasattr(user, k):
                        v = getattr(user, k) # hasattr / getattr的使用
                        data[k] = v
                result = {'code':200,'username':username,'data':data}

            # 没查询字符串
            else:
                if user:
                    result = {'code':200, 'username':user.username, 'data':{'nickname':user.nickname,'sign':user.sign,'info':user.info,'avatar':str(user.avatar)}}
                else:
                    result = {'code':208}
            return JsonResponse(result)
        else:
            # 拿数据
            all_users = UserProfile.objects.all()
            users_data = []
            for user in all_users:
                dic = {}
                dic['nickname'] = user.nickname
                dic['username'] = user.username
                dic['sign'] = user.sign
                dic['info'] = user.info

                users_data.append(dic)
            result = {'code':200,'data':users_data}
            return JsonResponse(result)

    elif request.method == 'POST':
        # 创建用户

        json_str = request.body
        if not json_str:
            result = {'code': '10102','error': 'Please complete info'}
            return result
        json_obj = json.loads(json_str)
        username = json_obj.get('username')
        email = json_obj.get('email')
        if not username:
            result = {'code': '10101', 'error': 'Please write a username'}
            return JsonResponse(result)

        # TODO 检查json dict中的key是否存在
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        if password_1 != password_2:
            result = {'code': '10103', 'error': 'The password is error!'}
            return JsonResponse(result)
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result = {'code': 10104,'error': 'The username is already existed'}
            return JsonResponse(result)
        # 生成散列密码
        pm = hashlib.md5()
        pm.update(password_1.encode())

        # 创建用户
        try:
            UserProfile.objects.create(username=username, password=pm.hexdigest(), nickname=username, email=email)
        except Exception as e:
            print('----error----')
            print(e)
            result = {'code': 10105, 'error': 'The username is already existed!!'}
            return JsonResponse(result)

        # 生成token
        now_datetime = datetime.datetime.now()
        token = make_token(username, 3600*24, now_datetime)
        result = {'code': 200, 'data': {'token': token}, 'username':username}
        return JsonResponse(result)


    elif request.method == 'PUT':
        # 更新 http://127.0.0.1:8000/v1/users/username
        if not username:
            result = {'code':10107,'error':'Must give me username!!'}
            return JsonResponse(result)
        json_str = request.body
        # TODO 空body判断
        json_obj = json.loads(json_str)
        nickname = json_obj['nickname']
        sign = json_obj.get('sign')
        info = json_obj.get('info')
        # 更新
        # user = UserProfile.objects.filter(username=username)
        # user = user[0]
        user = request.user
        # 当前请求,token用户,修改自己的数据
        if user.username != username:
            result = {'code':10109, 'error':'The username is error!'}
            return JsonResponse(result)
        to_update = False
        if user.nickname != nickname: to_update=True
        if user.sign != sign: to_update=True
        if user.info != info: to_update=True
        if to_update:
            # 做更新
            user.nickname = nickname
            user.sign = sign
            user.info = info
            user.save()
        return JsonResponse({'code':200,'username':username})

    return JsonResponse({'code': 200})

@login_check('POST')
def users_avatar(request, username):
    # 处理头像上传
    if request.method != 'POST':
        result = {'code':10110, 'error':'Please use POST'}
        return JsonResponse(result)
    user = request.user
    if user.username != username:
        result = {'code':10109, 'error':'The username is eroor!'}
        return JsonResponse(result)
    user.avatar = request.FILES['avatar']
    user.save()
    return JsonResponse({'code':200, 'username':username})


