# Wechat-push
[![Build Status](https://travis-ci.org/gwy15/wechat-push.svg?branch=master)](https://travis-ci.org/gwy15/wechat-push)

Wechat-push is a service that allows you push message to your smart phone using the Wechat MP platform.
Wechat-push uses python/aiohttp as backend and Vue as frontend.

Wechat-push 可以利用微信服务号向手机推送消息，如服务器报警等。
Wechat-push 使用 python 作为后端，Vue 作为前端界面。

## Usage 使用方法

Wechat-push provides RESTful API. Wechat-push 提供 RESTful API。

### Send a message 发送消息
```
POST https://domain.com/message
data: {
    receiver: receiver open ID,
    title: message title,
    body (optional): message body (Markdown format),
    templateID (optional): template id to use,
    url (optional): url on the buttom of page. 
}
return:
    400 HTTPBadRequest for parameter errors
    200 OK: {
        errcode: Wechat errcode, 0 for success,
        errmsg: Wechat error message,
    }
```

### Receive a message 接受消息

Visit `https://domain.com/` for open ID. 访问 `https://domain.com/` 扫码关注获取你的 open ID。

Pick up your phone and open Wechat. 手机打开微信。

## Deployment | 部署

Download [releases](https://github.com/gwy15/wechat-push/releases)

下载 [分发](https://github.com/gwy15/wechat-push/releases)

### Environment Setup | 环境设置
To deploy, users must setup their .env files.

部署前，需要设置一些环境变量。

```
# edit server/.env
APP_ID = XXXXXXXXXX # your wechat MP account app ID 微信服务号的APP ID
APP_SECRET = XXXXX  # your wechat MP account app Secret 微信服务号的 APP SECRET
WECHAT_TOKEN = XXXX # your self defined wechat token 微信服务号的 token

SQL_DB_URL = sqlite:///messages.sqlite3
REDIS_URL = redis://@localhost:1234/0

# root url for front end page 前端根 url
VUE_APP_ROOT_URL = https://your.domain.com/
SERVER_API_ROOT = /
```

For nginx setup, see `config/your-site.conf`

Nginx 设置参见 `config/your-site.conf`

### Get Things Running | 把服务跑起来！

```
./wechat_py*.pex --port 1235
```

## TODOS

- [x] Redis
- [x] Account Bind
- [x] Scan QR Page
- [ ] Threshold For IP And Receiver
