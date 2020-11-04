"""ddblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from . import views
from user import views as user_views
from btoken import views as btoken_views
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    #
    path('test_cors', views.test_cors),
    path('test_cors_server', views.test_cors_server),
    # FBV-function based view
    # user应用下的视图模块的视图函数
    # path('v1/users', user_views.user_view)
    # CBV-class based view
    # url <-->UsersView
    # 请求方法GET<-->UsersView的方法 get
    # 请求方法POST<-->UsersView的方法 post
    # ...
    # 如果根据请求方法找不到对应的类的方法,返回405.
    path('v1/users', user_views.UsersView.as_view()),
    #  v1/users/<username>
    path('v1/users/', include('user.urls')),

    path('v1/tokens', btoken_views.TokenView.as_view()),
    #
    path('v1/topics/', include('topic.urls')),
    # v1/messages/
    path('v1/messages/', include('message.urls')),
]
urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
