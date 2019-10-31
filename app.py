import os
import argparse
from typing import Optional

import dotenv
from aiohttp import web

from wechat.core import TokenManager
from wechat.messages import WechatTemplateMessageClient
from wechat.exceptions import WechatRequestError


async def messageHandler(request):
    config = request.app['config']
    manager = config['tokenManager']

    data = await request.post()
    # get template ID
    templateID = data.get('templateID', None)
    if templateID is None:  # get default template ID
        templateID = config.get('defaultTemplateID', None)
        if templateID is None:  # default template ID not set
            templateID = await getDefaultTemplateID(manager)
            if templateID is None:  # still fails
                raise ValueError('No template id param was found.')
            config['defaultTemplateID'] = templateID
    # parse arguments
    receiver = data.get('receiver', None)
    if receiver is None:
        raise web.HTTPBadRequest(reason='must provide receiver')
    title = data.get('title', None)
    if title is None:
        raise web.HTTPBadRequest(reason='must provide title')
    body = data.get('body', '')
    url = data.get('url', None)
    # build post data
    postData = {
        'title': {'value': title},
        'body': {'body': body}
    }

    try:
        client = WechatTemplateMessageClient(manager)
        response = await client.sendTemplateMessage(receiver, templateID, postData, url)
    except WechatRequestError as ex:
        response = {
            'errcode': ex.errCode,
            'errmsg': str(ex)
        }

    return web.json_response(response)


async def getDefaultTemplateID(tokenManager: TokenManager) -> Optional[str]:
    client = WechatTemplateMessageClient(tokenManager)
    templateList = await client.getTemplateList()
    if len(templateList) != 1:
        return None
    else:
        return templateList[0]['template_id']


def createApp():
    # load env
    dotenv.load_dotenv(dotenv.find_dotenv())
    appID = os.environ['appID']
    appSecret = os.environ['appSecret']
    urlRoot = os.environ.get('urlRoot', '/')
    if not (urlRoot.startswith('/') and urlRoot.endswith('/')):
        raise ValueError('urlRoot must starts and ends with a slash (/).')

    # create app
    app = web.Application()
    app.add_routes([web.post(urlRoot + 'message', messageHandler)])
    # initiate token manager
    manager = TokenManager(appID, appSecret)
    app['config'] = {'tokenManager': manager}
    return app


def runDirectly():
    parser = argparse.ArgumentParser(description="Wechat message pusher")
    parser.add_argument(
        '--host', help='host to listen, default as 127.0.0.1', default='127.0.0.1')
    parser.add_argument(
        '--port', help='port to listen, default as 8080', default=8080)
    args = parser.parse_args()

    app = createApp()
    web.run_app(app, host=args.host, port=args.port)


if __name__ == "__main__":
    runDirectly()
