# dsm-webhook-dingding

# Webhook 转发服务

## 简介

本项目提供了一个用于转发群晖 Webhook 请求的 Flask 服务，以解决群晖无法直接处理钉钉机器人 API 中需要进行签名验证的问题。

## 逻辑概述

1. 群晖配置 Webhook 时，无法直接处理钉钉机器人 API 中的 `sign` 参数，该参数需要通过时间戳和 secret 进行计算。
2. 为解决这一问题，我们使用 Flask 编写了一个 Webhook 转发服务。
3. 当群晖触发 Webhook 请求时，请求将被发送到我们的转发服务。
4. 转发服务将接收到的请求进行处理，包括计算 `sign` 参数，并将带有正确签名的请求转发给钉钉机器人 API。

## 使用方法

1、将本项目部署至你的服务器环境中。

    ```
    # 安装依赖
    pip install -r requirements.txt
    
    #启动webhook中转服务
    nohup python webhook.py > webhook.log 2>&1 &
    
    ```



2、在群晖 Webhook 配置中，将 Webhook 请求的目标地址设置为部署的转发服务地址。

```
http://ip:port/recevice_data?access_token=xxx&text=%40%40TEXT%40%40&secret=xxx
```



POST请求，参考钉钉机器人[API设置](https://open.dingtalk.com/document/orgapp/custom-bot-send-message-type)

```
{
    "at": {
        "isAtAll": true
    },
    "msgtype":"text",
    "text": {
        "content": "@@TEXT@@"
    }
}
```



3、当群晖触发 Webhook 请求时，转发服务将会处理请求并将正确签名的请求发送给钉钉机器人 API。

## 注意事项

- 请妥善保管转发服务的 secret，避免泄露导致安全问题。
- 确保转发服务能够正常访问并转发请求至钉钉机器人 API。

## 为什么一定要用钉钉机器人的通知？

是啊！为什么？邮箱不就不用折腾了？？？wtf...



加了飞书的Notify ，消息速度好像比钉钉快