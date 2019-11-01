from aiohttp import web
import redis

from pushbot import models
from pushbot import views
from pushbot import log

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
    APP_SECRET = os.environ['APP_SECRET']
    # load url root
    URL_ROOT = os.environ.get('URL_ROOT', '/')
    if not (URL_ROOT.startswith('/') and URL_ROOT.endswith('/')):
        raise ValueError('URL_ROOT must starts and ends with a slash (/).')
    # load wechat message view url
    DETAIL_BASE_URL = os.environ.get('DETAIL_BASE_URL', None)
    if DETAIL_BASE_URL is None:
        raise ValueError(
            'DETAIL_BASE_URL must be set to enable detail page.')
    parseResult = urlparse(DETAIL_BASE_URL)
    ALLOWED_DOMAINS = '{}://{}'.format(
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
    manager = TokenManager(APP_ID, APP_SECRET)

    # create app
    app = web.Application()
    app.add_routes(routes(URL_ROOT))
    app['config'] = {
        'tokenManager': manager,
        'session': session,
        'redis': r,
        'APP_ID': APP_ID,
        'WECHAT_TOKEN': WECHAT_TOKEN,
        'DETAIL_BASE_URL': DETAIL_BASE_URL,
        'ALLOWED_DOMAINS': ALLOWED_DOMAINS
    }
    return app


async def asyncApp():
    return createApp()
