from test_celery.celery import app
import time

#创建任务函数
@app.task
def task_test():
    print("task begin....")
    time.sleep(10)
    print("task over....")