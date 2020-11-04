from django.shortcuts import render
from django.http import HttpResponse
from .tasks import task_test
import datetime


def test_celery(request):
    task_test.delay()
    now = datetime.datetime.now()
    html = "return at %s" % (now.strftime('%H:%M:%S'))
    return HttpResponse(html)
