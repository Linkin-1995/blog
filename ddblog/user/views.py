from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator

from user.models import UserProfile

from django.views import View
import json
import hashlib
import jwt
from django.conf import settings
import time
from tools.login_dec import login_check

import random
from tools.sms import YunTongXin
from django.core.cache import cache
from .tasks import send_sms

class UsersView(View):
    def get(self, request, username=None):
        if username:
            # 获取指定用户信息
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                print('get user error %s' % e)
                result = {'code': 10104, 'error': 'username is wrong!'}
                return JsonResponse(result)

            if request.GET.keys():
                data = {}
                for k in request.GET.keys():
                    if k == 'password':
                        continue
                    if hasattr(user, k):
                        data[k] = getattr(user, k)
                result = {'code': 200, 'username': username, 'data': data}
            else:
                result = {'code': 200,
                          'username': username,
                          'data': {'info': user.info, 'sign': user.sign,
                                   'nickname': user.nickname,
                                   'avatar': str(user.avatar)}}
            return JsonResponse(result)

        else:
            # 获取所有用户信息
            return HttpResponse('get all users')

    def post(self, request):
        # 表单的方式获取数据
        # print(request.POST)
        # ajax异步请求提交的json数据
        print(request.body)
        json_str = request.body
        json_obj = json.loads(json_str)
        username = json_obj['username']
        email = json_obj['email']
        phone = json_obj['phone']
        password_1 = json_obj['password_1']
        password_2 = json_obj['password_2']
        sms_num = json_obj['sms_num']

        # 校验验证码
        # 生成键
        cache_key = 'sms_%s' % phone
        old_code = cache.get(cache_key)
        if not old_code:
            result = {'code': 10113, 'error': 'code is wrong'}
            return JsonResponse(result)
        if int(sms_num) != old_code:
            result = {'code': 10113, 'error': 'code is wrong'}
            return JsonResponse(result)

        # 检查用户名长度
        if len(username) > 11:
            result = {'code': 10100, 'error': 'username is wrong!'}
            return JsonResponse(result)
        # 检查用户名是否可用
        old_user = UserProfile.objects.filter(username=username)
        if  old_user:
            result = {'code': 10101, 'error': 'username is alreay exists!'}
            return JsonResponse(result)
        # 密码检查
        if password_1 != password_2:
            result = {'code': 10102, 'error': 'password is wrong!'}
            return JsonResponse(result)
        md5 = hashlib.md5()
        md5.update(password_1.encode())
        # md5.digest(),返回字节串,通常用于中间值计算
        # md5.hexdigest(),返回16进制字符串,通常用于传输或保存
        password_h = md5.hexdigest()
        # 插入数据
        try:
            user = UserProfile.objects.create(username=username,
                                              password=password_h,
                                              email=email,
                                              nickname=username,
                                              phone=phone)
        except Exception as e:
            print('create error is %s' % e)
            result = {'code': 10101, 'error': 'username is alreay exists!'}
            return JsonResponse(result)
        # 签发token
        token = make_token(username)
        result = {'code': 200,
                  'username': username,
                  'data': {'token': token.decode()}}
        return JsonResponse(result)

    @method_decorator(login_check)
    def put(self, request, username):
        # 获取前端提交的数据
        json_str = request.body
        json_obj = json.loads(json_str)
        request.myuser.sign = json_obj['sign']
        request.myuser.nickname = json_obj['nickname']
        request.myuser.info = json_obj['info']
        request.myuser.save()
        result = {'code': 200, 'username': request.myuser.username}
        return JsonResponse(result)


def make_token(username, expire=3600 * 24):
    key = settings.JWT_TOKEN_KEY
    now = time.time()
    payload = {'username': username, 'exp': now + expire}
    return jwt.encode(payload, key, algorithm='HS256')


@login_check
def user_avatar(request, username):
    if request.method != 'POST':
        result = {'code': 10105, 'error': 'must be POST'}
        return JsonResponse(result)

    # 上传头像
    user = request.myuser
    user.avatar = request.FILES['avatar']
    user.save()

    result = {'code': 200, 'username': user.username}
    return JsonResponse(result)


def sms_view(request):
    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj['phone']

    # 生成键
    cache_key = 'sms_%s' % phone
    # 防止多次重复发送
    old_code = cache.get(cache_key)
    if old_code:
        result = {'code': 10112, 'error': '请稍后发送'}
        return JsonResponse(result)
    # 生成随机码
    code = random.randint(1000, 9999)
    # 在缓存中存储验证码
    cache.set(cache_key, code, 65)

    # # 同步发送
    # x = YunTongXin(settings.SMS_ACCOUNT_ID,
    #                settings.SMS_ACCOUNT_TOKEN,
    #                settings.SMS_APP_ID,
    #                settings.SMS_TEMPLATE_ID)
    # res = x.run(phone, code)
    # 异步发送
    send_sms.delay(phone, code)

    print('code is %s' % code)
    # print('send sms result is %s' % res)

    return JsonResponse({'code': 200})
