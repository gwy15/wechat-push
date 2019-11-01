# Wechat-push

Wechat-push is a service that allows you push message to your smart phone using the Wechat MP platform.
Wechat-push uses python/aiohttp as backend and Vue as frontend.

Wechat-push 可以利用微信服务号向手机推送消息，如服务器报警等。
Wechat-push 使用 python 作为后端，Vue 作为前端界面。

## Usage 使用方法

Wechat-push provides RESTful API. Wechat-push 提供 RESTful API。

### Send a message 发送消息
```
POST https://domain.com/path/message
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


## Python Environment Setup | Python 环境搭建
```
$ virtualenv venv

# For *nix users 
$ source ./venv/bin/activate
# For powershell (Windows) users
PS > . .\venv\Scripts\activate.ps1
# for cmd (Windows) users
> venv\Scripts\activate

(venv) $ pip install -r requirement.txt
```

## Environment Variables Setup | 环境变量设置
To deploy, users must setup their .env files.

部署前，需要设置一些环境变量。

```
# edit .env
APP_ID = XXXXXXXXXX # your wechat MP account app ID 微信服务号的APP ID
appSecret = XXXXX  # your wechat MP account app Secret 微信服务号的 APP SECRET
# the database url (compatible with sqlalchemy) 数据库URL（sqlalchemy 格式）
SQL_DB_URL = sqlite:///messages.sqlite3
# url for front end page 前端 url
wechatMessageViewUrl = https://wxpush.domain.com/detail
# optional below
urlRoot = / # set if you'd like to deploy the service under a url. e.g., https://domain.com/wechat/message
```

For front end page, view detail-page/README.md

## Deploy
First deploy python service

For *nix users, nginx + gunicorn is recommended. But you're free to deploy using the same way under Windows as mentioned later.
```
$ gunicorn app:asyncApp --worker-class aiohttp.GunicornWebWorker --bind /tmp/wechat-push.sock
```

Setup nginx: see config/your-site.conf

For Windows users, since gunicorn isn't available under Windows, run app.py directly instead.
```
$ python app.py --help
```

## TODOS

[ ] Redis
[ ] Account Bind
[ ] Threshold For IP And Receiver
[ ] Scan QR Page
