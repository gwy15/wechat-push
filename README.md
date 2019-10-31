# Wechat-push

## Project setup
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

## Setup environment variables
To deploy, users must setup their .env files.

```
# edit .env
appID = XXXXXXXXXX # your wechat MP account app ID
appSecret = XXXXX  # your wechat MP account app Secret
dbUrl = sqlite:///messages.sqlite3 # the database url (compatible with sqlalchemy)
wechatMessageViewUrl = https://wxpush.domain.com/detail # url for front end page
# optional below
urlRoot = / # set if you'd like to deploy the service under a url
```

For front end page, view detail-page/README.md

## Deploy
First deploy python service

For *nix users, nginx + gunicorn is recommended. But you're free to deploy using the same way under Windows as mentioned later.
```
$ gunicorn app:app --worker-class aiohttp.GunicornWebWorker --bind /tmp/wechat-push.sock
```

Setup nginx: see config/your-site.conf

For Windows users, since gunicorn isn't available under Windows, run app.py directly instead.
```
$ python app.py --help
```
