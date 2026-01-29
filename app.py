import requests
from flask import Flask, request, jsonify, json
import time
import hmac
import hashlib
import base64
import urllib.parse

app = Flask(__name__)


# 处理GET请求和POST请求,群晖的包应该就是从请求头发出的，多余的也可以删掉。
@app.route('/recevice_data', methods=['GET', 'POST'])
def recevice_data():
    access_token = None
    text = None
    secret = None

    # 尝试从GET请求中获取参数
    if request.args:
        access_token = request.args.get('access_token')
        text = request.args.get('text')
        secret = request.args.get('secret')

    # 如果仍未找到参数，尝试从POST请求中获取参数
    if not access_token and request.method == 'POST':
        data = request.get_json()
        if data:
            access_token = data.get('access_token')
            text = data.get('text')
            secret = data.get('secret')

    # 如果仍未找到参数，尝试从请求头中获取参数
    if not access_token:
        access_token = request.headers.get('access_token')
    if not text:
        text = request.headers.get('text')
    if not secret:
        secret = request.headers.get('secret')

    text: str = text.replace(r"\n", "\n")
    if not secret or not access_token:
        print("钉钉机器人 服务的 SECRET 或者 TOKEN 未设置!!\n取消推送")
        return jsonify({"errcode": 1, "errmsg": "secret or access_token missing"}), 400
    print("钉钉机器人 服务启动")
    # sign生成算法
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    title = "[ 群晖通知 ]"

    url = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}&timestamp={timestamp}&sign={sign}'
    headers = {"Content-Type": "application/json;charset=utf-8"}
    data = {"msgtype": "text", "text": {"content": f"{title}\n{text}"}}
    dd_response = requests.post(
        url=url, data=json.dumps(data), headers=headers, timeout=30
    ).json()

    if not dd_response["errcode"]:
        print("钉钉机器人 推送成功！")
    else:
        print("钉钉机器人 推送失败！")

    response = {
        "errcode": "0",
        "errmsg": "ok"
    }
    return jsonify(response), 200


@app.route('/feishu', methods=['GET', 'POST'])
def feishu():
    access_token = None
    text = None
    secret = None

    # 尝试从GET请求中获取参数
    if request.args:
        access_token = request.args.get('access_token')
        text = request.args.get('text')
        secret = request.args.get('secret')

    # 如果仍未找到参数，尝试从POST请求中获取参数
    if not access_token and request.method == 'POST':
        data = request.get_json()
        if data:
            access_token = data.get('access_token')
            text = data.get('text')
            secret = data.get('secret')

    # 如果仍未找到参数，尝试从请求头中获取参数
    if not access_token:
        access_token = request.headers.get('access_token')
    if not text:
        text = request.headers.get('text')
    if not secret:
        secret = request.headers.get('secret')

    if text:
        text: str = text.replace(r"\n", "\n")
    
    if not access_token:
        print("飞书机器人 TOKEN 未设置!!\n取消推送")
        return jsonify({"errcode": 1, "errmsg": "access_token missing"}), 400

    print("飞书机器人 服务启动")
    
    timestamp = str(round(time.time()))
    sign = None
    
    if secret:
        # sign生成算法
        timestamp = str(int(time.time()))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        
        # 飞书签名校验：使用 HmacSHA256 算法计算签名
        # 根据飞书官方文档和社区实践，签名的计算方式比较特殊：
        # 将 "timestamp + \n + secret" 作为 Key，Message 为空字符串 (b"")
        # 参考：https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot
        
        # 1. 拼接签名字符串
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        
        # 2. 计算 HMAC-SHA256
        # 注意：Key 是 string_to_sign，Msg 是 b""
        hmac_code = hmac.new(string_to_sign_enc, b"", digestmod=hashlib.sha256).digest()
        
        # 3. Base64 编码
        sign = base64.b64encode(hmac_code).decode('utf-8')

        print(f"[Debug] Feishu Sign Info:")
        print(f"Timestamp: {timestamp} (Current system time)")
        print(f"Secret: {secret}")
        print(f"String to sign: {string_to_sign}")
        print(f"Generated Sign: {sign}")
        
        # 提示：如果仍然报错 "timestamp is not within one hour"，请检查运行此代码的服务器系统时间是否准确
        current_sys_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))
        print(f"System Time Formatted: {current_sys_time}")

    title = "[ 群晖通知 ]"
    
    url = f'https://open.feishu.cn/open-apis/bot/v2/hook/{access_token}'
    headers = {"Content-Type": "application/json;charset=utf-8"}
    
    data = {
        "msg_type": "text",
        "content": {
            "text": f"{title}\n{text}"
        }
    }
    
    if sign:
        data["timestamp"] = timestamp
        data["sign"] = sign

    feishu_response = requests.post(
        url=url, data=json.dumps(data), headers=headers, timeout=30
    ).json()

    if feishu_response.get("code") == 0 or feishu_response.get("StatusCode") == 0:
        print("飞书机器人 推送成功！")
    else:
        print(f"飞书机器人 推送失败！错误信息: {feishu_response}")

    response = {
        "errcode": "0",
        "errmsg": "ok",
        "feishu_response": feishu_response
    }
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
