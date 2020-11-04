from django.db import models
from topic.models import Topic
from user.models import UserProfile

# Create your models here.
class Message(models.Model):
    # 评论
    #文章对象
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    #评论的人对象
    user_profile = models.ForeignKey(UserProfile,
                                     on_delete=models.CASCADE)
    content = models.CharField(max_length=50)
    created_time = models.DateTimeField(auto_now_add=True)
    #回复
    parent_message = models.IntegerField(default=0)