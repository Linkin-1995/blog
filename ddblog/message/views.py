from django.shortcuts import render
from django.http import JsonResponse
from tools.login_dec import login_check
from .models import Message
import json
from topic.models import Topic

# Create your views here.
@login_check
def message_view(request,topic_id):
    if request.method!='POST':
        result={'code':10400,'error':'please use POST'}
        return JsonResponse(result)
    #1.获取登录用户
    user=request.myuser
    #2.通常在数据中根据topic_id,获取要评论的topic对象[验证]
    try:
        topic=Topic.objects.get(id=topic_id)
    except Exception as e:
        result={'code':10401,'error':'topic_id is wrong'}
        return JsonResponse(result)
    #3.从request.body获取前端提交的评论内容
    json_str=request.body
    json_obj=json.loads(json_str)
    content=json_obj['content']
    parent_id=json_obj.get('parent_id',0)
    #4.将评论数据添加到数据库中
    Message.objects.create(topic=topic,user_profile=user,parent_message=parent_id,
    content=content)

    return JsonResponse({'code':200})