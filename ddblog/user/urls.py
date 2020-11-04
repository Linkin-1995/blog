from django.urls import path
from . import views

urlpatterns = [
    # http://127.0.0.1:8000/v1/users/sms
    path('sms', views.sms_view),
    # http://127.0.0.1:8000/v1/users/tedu
    path('<str:username>', views.UsersView.as_view()),
    # 上传用户头像的路由
    path('<str:username>/avatar', views.user_avatar)
]
