from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from tools.login_dec import login_check
from django.utils.decorators import method_decorator
import json
from .models import Topic
from user.models import UserProfile
from tools.login_dec import get_user_by_request

from django.views.decorators.cache import cache_page
from tools.cache_dec import topic_cache
from django.core.cache import cache
from message.models import Message

# Create your views here.
class TopicViews(View):

    def make_topics_res(self, author, author_topics):
        topics_res = []
        for topic in author_topics:
            d = {}
            d['id'] = topic.id
            d['title'] = topic.title
            d['category'] = topic.category
            d['introduce'] = topic.introduce
            d['created_time'] = topic.created_time
            d['author'] = author.nickname
            topics_res.append(d)
        res = {'code': 200, 'data': {}}
        res['data']['topics'] = topics_res
        res['data']['nickname'] = author.nickname
        return res

    def make_topic_res(self, author, author_topic, is_self):

        if is_self:
            next_topic = Topic.objects.filter(id__gt=author_topic.id,
                                              user_profile_id=author.username).first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id,
                                              user_profile_id=author.username).last()
        else:
            next_topic = Topic.objects.filter(id__gt=author_topic.id,
                                              user_profile_id=author.username,
                                              limit='public').first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id,
                                              user_profile_id=author.username,
                                              limit='public').last()
        if next_topic:
            next_id = next_topic.id
            next_title = next_topic.title
        else:
            next_id = None
            next_title = None

        if last_topic:
            last_id = last_topic.id
            last_title = last_topic.title
        else:
            last_id = None
            last_title = None

        #获取某一文章的所有评论
        all_message=Message.objects.filter(topic=author_topic).order_by('-created_time')
        msg_list=[]
        r_dict={}
        #统计评论时不包含回复
        msg_count=0
        for msg in all_message:
            if msg.parent_message:
                #回复(队员)
                r_dict.setdefault(msg.parent_message,[])
                r_dict[msg.parent_message].append({
                'id':msg.id,
                'content':msg.content,
                'publisher':msg.user_profile.nickname,
                'publisher_avatar':str(msg.user_profile.avatar),
                'created_time':msg.created_time.strftime('%Y-%m-%d %H-%M-%S')
                })
            else:
                #评论(队长)
                msg_count+=1
                msg_list.append({
                'id':msg.id,
                'content':msg.content,
                'publisher':msg.user_profile.nickname,
                'publisher_avatar':str(msg.user_profile.avatar),
                'created_time':msg.created_time.strftime('%Y-%m-%d %H-%M-%S'),
                'reply':[]
                })
        for m in msg_list:
            if m['id'] in r_dict:
                m['reply']=r_dict[m['id']]


        result = {'code': 200, 'data': {}}
        result['data']['nickname'] = author.nickname
        result['data']['title'] = author_topic.title
        result['data']['category'] = author_topic.category
        result['data']['content'] = author_topic.content
        result['data']['introduce'] = author_topic.introduce
        result['data']['author'] = author.nickname
        result['data']['created_time'] = \
            author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        result['data']['last_id'] = last_id
        result['data']['last_title'] = last_title
        result['data']['next_id'] = next_id
        result['data']['next_title'] = next_title

        result['data']['messages'] = msg_list
        result['data']['messages_count'] = msg_count
        return result

    def clear_topic_cache(self, request):
        # url: /v1/topic/tedu
        # 前缀: topic_cache_self_ / topic_cache_
        # 后缀: ?category=tec / ?category=no-tec
        all_path = request.get_full_path()
        all_key_p = ['topic_cache_self_', 'topic_cache_']
        all_keys = []
        for key_p in all_key_p:
            for key_h in ['', '?category=tec', '?category=no-tec']:
                all_keys.append(key_p + all_path + key_h)
        print(all_keys)
        cache.delete_many(all_keys)

    @method_decorator(login_check)
    def post(self, request, author_id):
        # 获取前端数据,添加到数据库中
        author = request.myuser
        json_str = request.body
        json_obj = json.loads(json_str)
        content = json_obj['content']

        content_text = json_obj['content_text']
        introduce = content_text[:30]

        title = json_obj['title']

        limit = json_obj['limit']
        if limit not in ['public', 'private']:
            result = {'code': 10300, 'error': 'the limit is wrong~'}
            return JsonResponse(result)

        category = json_obj['category']
        if category not in ['tec', 'no-tec']:
            result = {'code': 10301, 'error': 'the category is wrong~'}
            return JsonResponse(result)
        Topic.objects.create(title=title, content=content,
                             limit=limit, category=category,
                             introduce=introduce, user_profile=author)

        # 清除缓存
        self.clear_topic_cache(request)

        return JsonResponse({'code': 200, 'username': author.username})

    @method_decorator(topic_cache(300))
    def get(self, request, author_id):
        print('----topic view in-------')
        try:
            author = UserProfile.objects.get(username=author_id)
        except Exception as e:
            result = {'code': 10305, 'error': 'the author is error'}
            return JsonResponse(result)
        visit_username = get_user_by_request(request)

        # 根据查询字符串是否有t_id,判断是文章列表还是文章详情
        t_id = request.GET.get('t_id')
        is_self = False
        if t_id:
            # 详情
            if visit_username == author_id:
                is_self = True
                try:
                    author_topic = Topic.objects.get(id=t_id, user_profile_id=author_id)
                except Exception as e:
                    result = {'code': 10103, 'error': 'the topic is error'}
                    return JsonResponse(result)
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id,
                                                     user_profile_id=author_id,
                                                     limit='public')
                except Exception as e:
                    result = {'code': 10103, 'error': 'the topic is error'}
                    return JsonResponse(result)
            res = self.make_topic_res(author, author_topic, is_self)
            return JsonResponse(res)
        else:
            # 列表
            is_category = False
            # 1.根据查询字符串获取分类category
            # 判断category的值是否在['tec','no-tec']
            # 如果有分类,并且值是正确的is_category=True
            category = request.GET.get('category')
            if category in ['tec', 'no-tec']:
                is_category = True

            if visit_username == author_id:
                # 2.1 如果有分类,添加分类的过滤
                if is_category:
                    author_topics = Topic.objects.filter(user_profile_id=author_id,
                                                         category=category)
                else:
                    author_topics = Topic.objects.filter(user_profile_id=author_id)
            else:
                # 2.2 如果有分类,添加分类的过滤
                if is_category:

                    author_topics = Topic.objects.filter(user_profile_id=author_id,
                                                         limit='public', category=category)
                else:
                    author_topics = Topic.objects.filter(user_profile_id=author_id,
                                                         limit='public')

            # 将查询结果集封装成json格式的数据
            result = self.make_topics_res(author, author_topics)
            return JsonResponse(result)
