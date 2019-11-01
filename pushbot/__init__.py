from aiohttp import web

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
        web.post(urlRoot + 'callback', views.Callback.post),
    ]


def createApp():
    import os
    import dotenv
    from urllib.parse import urlparse
    from wechat.core import TokenManager

    # load env
    dotenv.load_dotenv(dotenv.find_dotenv())
    appID = os.environ['appID']
    appSecret = os.environ['appSecret']
    urlRoot = os.environ.get('urlRoot', '/')
    if not (urlRoot.startswith('/') and urlRoot.endswith('/')):
        raise ValueError('urlRoot must starts and ends with a slash (/).')
    wechatMessageViewUrl = os.environ.get('wechatMessageViewUrl', None)
    if wechatMessageViewUrl is None:
        raise ValueError(
            'wechatMessageViewUrl must be set to enable detail page.')
    parseResult = urlparse(wechatMessageViewUrl)
    allowedDomains = '{}://{}'.format(
        parseResult.scheme, parseResult.netloc)

    # create app
    app = web.Application()
    app.add_routes(routes(urlRoot))
    # initiate token manager
    manager = TokenManager(appID, appSecret)
    session = models.initDB(os.environ['dbUrl'])
    app['config'] = {
        'appID': appID,
        'wechatMessageViewUrl': wechatMessageViewUrl,
        'tokenManager': manager,
        'session': session,
        'allowedDomains': allowedDomains
    }
    return app


async def asyncApp():
    return createApp()
