import time
from typing import Optional, Union
import uuid
import random
from xml.etree import ElementTree

from aiohttp import web

from pushbot.utils import getIPFromRequest
from wechat.messages import WechatTemplateMessageClient
from wechat.accounts import WechatQRCodeClient
from pushbot import utils
from pushbot import models


class Message:
    @staticmethod
    @utils.catchWechatError
    async def post(request: web.Request):
        """
        Send a message to user.
        Args:
            request: aiohttp request.

        Returns:
            web.JsonResponse
        """
        config = request.app['config']
        manager = config['tokenManager']

        data = await request.post()
        # get template ID
        templateID: Optional[str]
        templateID = data.get('templateID', default=None)
        if templateID is None:  # get default template ID
            templateID = config.get('defaultTemplateID', None)
            if templateID is None:  # default template ID not set
                templateID = await utils.getDefaultTemplateID(manager)
                if templateID is None:  # still fails
                    raise web.HTTPBadRequest(
                        reason='No template id param was found.')
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
        client = WechatTemplateMessageClient(manager)
        responseData = await client.sendTemplateMessage(receiver, templateID, postData, detailUrl)
        responseData['token'] = token
        response = {
            'success': True,
            'msg': None,
            'data': responseData
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
            errcode=responseData['errcode'],
            msgid=responseData.get('msgid', 0),
            title=title,
            body=body,
            url=url
        )
        session = config['session']
        session.add(message)
        session.commit()

        # return response
        return web.json_response(response)

    @staticmethod
    @utils.allowCORS
    async def get(request: web.Request):
        config = request.app['config']
        token = request.match_info['token']
        message: models.Message
        message = config['session'].query(
            models.Message).filter_by(id=token).one_or_none()
        if message is None:
            raise web.HTTPNotFound(
                reason='No records were found for this token.')
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
        return web.json_response(response, headers=headers)


class Scene:
    @staticmethod
    @utils.catchWechatError
    async def post(request: web.Request):
        """Get a new scene ID

        Args:
            request (web.Request): web request
        """
        scene_id = random.randint(1, 2**31 - 1)
        QRClient = WechatQRCodeClient(request.app['config']['tokenManager'])
        data = await QRClient.getTempQRCode(scene_id, expireSeconds=5*60)
        ticket = data['ticket']
        QRUrl = 'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={}'.format(
            ticket)

        return web.json_response({
            'success': True,
            'msg': '',
            'data': {
                'scene_id': scene_id,
                'ticket': ticket,
                'expire_at': time.time() + data['expire_seconds'],
                'QRUrl': QRUrl,
            }
        })

    @staticmethod
    async def get(request: web.Request):
        """Get open id for a scene ID

        Args:
            request (web.Request): web request
        """
        pass
        # TODO:


class Callback:
    @staticmethod
    @utils.verifyFromWechatCallback
    async def get(request: web.Request):
        return web.Response(text=request.rel_url.query['echostr'])

    @staticmethod
    @utils.verifyFromWechatCallback
    async def post(request: web.Request):
        """Callback from wechat

        Args:
            request (web.Request): [description]
        """
        body = await request.read()
        tree = ElementTree.fromstring(body.decode())
        afunc = {
            'event': Callback.handleEvent
        }.get(tree.find('MsgType').text.strip(), Callback.defaultHandler)
        response = await afunc(tree)

        return web.Response(text='')

    @staticmethod
    async def defaultHandler(tree: ElementTree.Element):
        pass

    @staticmethod
    async def handleEvent(tree: ElementTree.Element):
        openID = tree.find('FromUserName').text.strip()
        eventName = tree.find('Event').text.strip().lower()
        if eventName == 'subscribe':
            eventKey = tree.find('EventKey')
            if eventKey is None:
                return
            scene_id = int(eventKey.text.strip()[len('qrscene_'):])
            # add to redis
        elif eventName == 'scan':
            scene_id = int(tree.find('EventKey').text.strip())
            # add to redis
        elif eventName == 'unsubscribe':
            # remove from redis
            pass
