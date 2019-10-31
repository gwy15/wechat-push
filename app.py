import os
import argparse
from typing import Optional
import uuid
import time
from urllib.parse import urlparse

import dotenv
from aiohttp import web

from wechat.core import TokenManager
from wechat.messages import WechatTemplateMessageClient
from wechat.exceptions import WechatRequestError
import models


def getIPFromRequest(request):
    ip = request.headers.get('X-Real-IP', None) or \
        request.headers.get('X-Forwarded-For', None)
    if ip is None:
        peername = request.transport.get_extra_info('peername')
        if peername is not None:
            ip, _ = peername
        else:
            ip = ''
    return ip


async def postMessageHandler(request):
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
        'body': {'value': body}
    }
    token = uuid.uuid4().hex
    detailUrl = config['wechatMessageViewUrl'] + '?token=' + token

    # send
    try:
        client = WechatTemplateMessageClient(manager)
        response = await client.sendTemplateMessage(receiver, templateID, postData, detailUrl)
        response['token'] = token
    except WechatRequestError as ex:
        response = {
            'errcode': ex.errCode,
            'errmsg': str(ex)
        }

    # insert into db
    message = models.Message(
        id=token,
        app_id=config['appID'],
        template_id=templateID,
        receiver_id=receiver,
        created_time=time.time(),
        ip=getIPFromRequest(request),
        UA=request.headers.get('User-Agent', ''),
        errcode=response['errcode'],
        msgid=response.get('msgid', 0),
        title=title,
        body=body,
        url=url
    )
    session = config['session']
    session.add(message)
    session.commit()

    # return response
    return web.json_response(response)


async def getDefaultTemplateID(tokenManager: TokenManager) -> Optional[str]:
    client = WechatTemplateMessageClient(tokenManager)
    templateList = await client.getTemplateList()
    if len(templateList) != 1:
        return None
    else:
        return templateList[0]['template_id']


async def getMessageDetailHandler(request):
    config = request.app['config']
    token = request.match_info['token']
    message: models.Message
    message = config['session'].query(
        models.Message).filter_by(id=token).one_or_none()
    if message is None:
        response = {
            'success': False,
            'msg': 'No records were found for this token.'
        }
    else:
        response = {
            'success': True,
            'msg': 'Success',
            'data': {
                'title': message.title,
                'body': message.body,
                'created_time': message.created_time,
                'url': message.url
            }
        }
    headers = {
        'Access-Control-Allow-Origin': config['allowedDomains']
    }
    return web.json_response(response, headers=headers)


def createApp():
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
    app.add_routes([
        web.post(urlRoot + 'message', postMessageHandler),
        web.get(urlRoot + 'message/{token}', getMessageDetailHandler),
    ])
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
