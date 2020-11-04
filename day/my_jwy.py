import base64
import json
import hmac
import time
import copy


class JWT:
    def __init__(self):
        pass

    @staticmethod
    def encode(payload, key, exp=300):
        # 1. 生成header
        # 1.1 map
        header = {'alg': 'HS256', 'typ': 'JWT'}
        # 1.2 map-->json
        # separators参数是一个元组.元组第一项表示元素之间用的分隔符;第二项表示键值之间的分隔符
        # sort_keys=True保证序列化时key的有序性
        header_json = json.dumps(header, separators=(',', ':'), sort_keys=True)
        # 1.3    json-->base64   参数和返回值都要求字节串
        # header_bs = base64.urlsafe_b64encode(header_json.encode())
        header_bs = JWT.b64encode(header_json.encode())

        # 2 payload
        # 保证在endoce函数内部不会修改传递的实参payload
        payload_data = copy.deepcopy(payload)
        # 过期时间
        payload_data['exp'] = time.time()+int(exp)
        # map-->json
        payload_json = json.dumps(
            payload_data, separators=(',', ':'), sort_keys=True)
        # json-->base64
        # payload_bs=base64.urlsafe_b64encode(payload_json.encode())
        payload_bs = JWT.b64encode(payload_json.encode())

        # 3 sign
        # 生成hmac对象    参数类型字节串
        hm = hmac.new(key.encode(), header_bs+b'.' +
                      payload_bs, digestmod='SHA256')
        # 获取最终结果
        hm = hm.digest()
        # 编码
        # hm_bs=base64.urlsafe_b64encode(hm)
        hm_bs = JWT.b64encode(hm)
        return header_bs+b'.'+payload_bs+b'.'+hm_bs

    @staticmethod
    # 去字节串中的=
    def b64encode(j_s):
        return base64.urlsafe_b64encode(j_s).replace(b'=', b'')

    @staticmethod
    # 补字节串中的=
    # 规则:4个字节一组(3个字符),不足4个补=
    def b64decode(b_s):
        rem = len(b_s) % 4
        if rem > 0:
            b_s += b'='*(4-rem)
        return base64.urlsafe_b64decode(b_s)

    @staticmethod
    # 解码验证
    def decode(token, key):
        # 对令牌分割
        header_bs, payload_bs, sign = token.split(b'.')
        # 重新再生成签名
        hm = hmac.new(key.encode(), header_bs+b'.' +
                      payload_bs, digestmod='SHA256')
        hm = hm.digest()
        hm_bs = JWT.b64encode(hm)
        # 两次签名比较
        if hm_bs != sign:
            raise
        # bs-->json
        payload_json = JWT.b64decode(payload_bs)
        # json-->字典
        payload = json.loads(payload_json)
        # 验证token是否过期
        # 过期时间
        exp = payload['exp']
        # 当前时间
        now = time.time()
        if now > exp:
            # 过期
            raise
        # 最终可以拿到payload数据
        return payload


if __name__ == "__main__":
    token = JWT.encode({'name': 'zjl'}, '123456')
    print(token)
    payload=JWT.decode(token,'123456')
    print(payload)
