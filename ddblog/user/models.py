from django.db import models
import random


def default_sign():
    signs = ['good luck', 'I am happy', 'very good']
    return random.choice(signs)


# Create your models here.
class UserProfile(models.Model):
    username = models.CharField(max_length=11, primary_key=True)
    nickname = models.CharField(max_length=30)
    email = models.EmailField()
    password = models.CharField(max_length=32)
    # default=函数名称,随机的返回默认签名
    sign = models.CharField(max_length=50, default=default_sign)
    info = models.CharField(max_length=150, default='')
    # 个人头像(upload_to,头像所在目录的子目录)
    avatar = models.ImageField(upload_to='avatar', null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=11, default='')

    class Meta:
        db_table = 'user_user_profile'

