import jwt
from django.http import JsonResponse
from user.models import UserProfile

TOKEN_KEY = '1234567ab'
def login_check(*methods):
    def _login_check(func):
        def wrapper(request, *args, **kwargs):
            # 逻辑判断
            # 1.取出token
            # 2.判断当前请求是否需要校验
            # 3.如果需要检验token,如何校验
            if not methods:
                return func(request, *args, **kwargs)
            else:
                if request.method not in methods:
                    return func(request,*args,**kwargs)
            # 取出token
            token = request.META.get('HTTP_AUTHORIZATION')
            if not token:
                result = {'code':10201}
                return JsonResponse(result)
            try:
                result = jwt.decode(token,TOKEN_KEY,algorithms='HS256')
            except Exception as e:
                result = {'code':20105,'error':'Please login'}
                return JsonResponse(result)
            username = result['username']

            # 取出token里的login_time
            login_time = result.get('login_time')
            user = UserProfile.objects.get(username=username)
            if login_time:
                if login_time != str(user.login_time):
                    result = {'code': 20106, 'error': 'Other guys have login!Please login again!!'}
                    return JsonResponse(result)
            request.user = user

            return func(request,*args,**kwargs)
        return wrapper
    return _login_check

def get_user_by_request(request):
    # 尝试获取用户身份
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        # 用户没登录
        return None
    try:
        res = jwt.decode(token,TOKEN_KEY,algorithms='HS256')
    except Exception as e:
        return None
    username = res['username']
    user = UserProfile.objects.filter(username=username)
    if not user:
        return None
    return user[0]

