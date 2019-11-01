from aiohttp import web
import redis

from pushbot import models
from pushbot import views


def routes(urlRoot):
    return [
        # messages
        web.post(urlRoot + 'message', views.Message.post),
        web.get(urlRoot + 'message/{token}', views.Message.get),
        # scene (scan for receiver id)
        web.post(urlRoot + 'scene', views.Scene.post),
        web.get(urlRoot + 'scene/{scene_id}', views.Scene.get),
        # callback from wechat
        web.get(urlRoot + 'callback', views.Callback.get),
        web.post(urlRoot + 'callback', views.Callback.post),
    ]


def createApp():
    import os
    import dotenv
    from urllib.parse import urlparse
    from wechat.core import TokenManager

    # load env
    dotenv.load_dotenv(dotenv.find_dotenv())
    APP_ID = os.environ['APP_ID']
    appSecret = os.environ['appSecret']
    # load url root
    URL_ROOT = os.environ.get('URL_ROOT', '/')
    if not (URL_ROOT.startswith('/') and URL_ROOT.endswith('/')):
        raise ValueError('URL_ROOT must starts and ends with a slash (/).')
    # load wechat message view url
    wechatMessageViewUrl = os.environ.get('wechatMessageViewUrl', None)
    if wechatMessageViewUrl is None:
        raise ValueError(
            'wechatMessageViewUrl must be set to enable detail page.')
    parseResult = urlparse(wechatMessageViewUrl)
    allowedDomains = '{}://{}'.format(
        parseResult.scheme, parseResult.netloc)
    # load wechat token
    WECHAT_TOKEN = os.environ.get('WECHAT_TOKEN', None)
    if WECHAT_TOKEN is None:
        raise ValueError('WECHAT_TOKEN must be set to verify wechat callback.')
    # load redis db
    r = redis.Redis.from_url(os.environ['REDIS_URL'], decode_responses=True)
    # load SQL db
    session = models.initDB(os.environ['SQL_DB_URL'])
    # initiate token manager
    manager = TokenManager(APP_ID, appSecret)

    # create app
    app = web.Application()
    app.add_routes(routes(URL_ROOT))
    app['config'] = {
        'APP_ID': APP_ID,
        'WECHAT_TOKEN': WECHAT_TOKEN,
        'wechatMessageViewUrl': wechatMessageViewUrl,
        'tokenManager': manager,
        'session': session,
        'redis': r,
        'allowedDomains': allowedDomains
    }
    return app


async def asyncApp():
    return createApp()
