from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from alipay import AliPay
from django.views import View
from django.conf import settings

import json

# Create your views here.

app_private_key_string = open(
    settings.ALIPAY_KEY_DIR + 'app_private_key.pem').read()
alipay_public_key_string = open(
    settings.ALIPAY_KEY_DIR + 'alipay_public_key.pem').read()

# 一般该状态在数据库中
ORDER_STATUS = 1  # 1 待付款 2 已付款 3 付款失败


# 基类(创建AliPay对象,封装api)
class MyAliPay(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.alipay = AliPay(
            appid=settings.ALIPAY_APP_ID,
            # 当前app的私钥(对请求签名)
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥
            alipay_public_key_string=alipay_public_key_string,
            # 签名算法(RSA SHA2)
            sign_type='RSA2',
            # 指明是测试模式
            debug=True,
            app_notify_url=None
        )

    def get_trade_url(self, order_id, amount):
        base_url = 'https://openapi.alipaydev.com/gateway.do'
        order_string = self.alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=amount,
            # 订单标题
            subject=order_id,
            return_url=settings.ALIPAY_RETURN_URL,
            notify_url=settings.ALIPAY_NOTIFY_URL
        )
        return base_url + '?' + order_string

    def get_verify_result(self, data, sign):
        # True:验签通过  False:失败
        return self.alipay.verify(data, sign)

    def get_trade_result(self, order_id):
        result = self.alipay.api_alipay_trade_query(out_trade_no=order_id)
        if result.get('trade_status') == 'TRADE_SUCCESS':
            return True
        return False

class JumpView(MyAliPay):

    def get(self, request):
        return render(request, 'ajax_alipay.html')

    def post(self, request):
        json_obj = json.loads(request.body)
        order_id = json_obj['order_id']
        pay_url = self.get_trade_url(order_id, 99)
        return JsonResponse({'pay_url': pay_url})

class ResultView(MyAliPay):
    def get(self, request):
        # return HttpResponse('一夜暴富')
        request_data = {k: request.GET[k] for k in request.GET.keys()}
        print(request_data)
        order_id = request_data['out_trade_no']
        if ORDER_STATUS == 2:
            return HttpResponse('成功')
        # 订单状态没有变，需要主动查询
        elif ORDER_STATUS == 1:
            result = self.get_trade_result(order_id)
            if result:
                return HttpResponse('主动查询成功')
            else:
                return HttpResponse('失败')

    def post(self, request):
        # 支付成功后，支付宝主动发送post请求,告知支付结果
        # 拿到支付结果，若成功，修改订单状态为已付款
        # 否则，设置订单状态为失败
        request_data = {k: request.POST[k] for k in request.POST.keys()}
        # 从字典格式的数据中取出签名
        sign = request_data.pop('sign')
        is_verify = self.get_verify_result(request_data, sign)
        if is_verify:
            trade_status = request_data['trade_status']
            if trade_status == 'TRADS_SUCCESS':
                # 在数据库中将订单表状态由待支付改为已付款
                # ORDER_STATUS = 2
                return HttpResponse('ok')
            else:
                # 在数据库中将订单表状态由待支付改为支付失败
                # ORDER_STATUS = 3
                return HttpResponse('ok')
        else:
            return HttpResponse('非法访问')
