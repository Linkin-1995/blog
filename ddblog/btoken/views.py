from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from user.models import UserProfile
import json
import hashlib
from user.views import make_token


# Create your views here.
class TokenView(View):
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        username = json_obj['username']
        password = json_obj['password']
        try:
            user = UserProfile.objects.get(username=username)
        except Exception as e:
            print('-login error %s-' % e)
            result = {'code': 10200, 'error': 'username or password is wrong'}
            return JsonResponse(result)
        md5 = hashlib.md5()
        md5.update(password.encode())
        if md5.hexdigest() != user.password:
            result = {'code': 10201, 'error': 'username or password is wrong'}
            return JsonResponse(result)
        # 登录成功后,签发token
        token = make_token(username)
        result = {'code': 200, 'username': username,
                  'data': {'token': token.decode()}}
        return JsonResponse(result)
