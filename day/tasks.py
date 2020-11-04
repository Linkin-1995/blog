#测试celery
from celery import Celery

#创建celery对象
app=Celery('tedu',broker='redis://@127.0.0.1:6379/1')

#创建任务函数
@app.task
def task_test():
    print('task is running')


