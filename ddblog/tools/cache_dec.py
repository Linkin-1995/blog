from django.core.cache import cache
from .login_dec import get_user_by_request


def topic_cache(expire):
    def _topic_cache(func):
        def wrapper(request, *args, **kwargs):
            # 如果是文章详情页,暂时先不考虑缓存
            if 't_id' in request.GET.keys():
                # 文章详情,回头大家自己处理
                return func(request, *args, **kwargs)
            # 文章列表(组合得到所有的缓存key)
            visitor_username = get_user_by_request(request)
            author_username = kwargs['author_id']
            if visitor_username == author_username:
                cache_key = 'topic_cache_self_%s' % (request.get_full_path())
            else:
                cache_key = 'topic_cache_%s' % (request.get_full_path())
            print('-cache key is %s-' % cache_key)
            # 缓存思想
            res = cache.get(cache_key)
            if res:
                print('--cache in--')
                return res
            res = func(request, *args, **kwargs)
            cache.set(cache_key, res, expire)
            return res

        return wrapper

    return _topic_cache
