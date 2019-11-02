import time
from typing import Optional, Union
import uuid
import random
from xml.etree import ElementTree
import redis
import logging

from aiohttp import web

from pushbot.utils import getIPFromRequest
from wechat.messages import WechatTemplateMessageClient
from wechat.accounts import WechatQRCodeClient
from pushbot import utils
from pushbot import models

logger = logging.getLogger(__name__)


class Message:
    EXPIRES_IN = 60*60

    @staticmethod
    def _token2RedisName(token):
        return 'wxpush:msg:{}'.format(token)

    @staticmethod
    def _simplifiedMessage(message: models.Message):
        return {
            'title': message.title,
            'body': message.body,
            'created_time': message.created_time,
            'url': message.url
        }

    @staticmethod
    def _save2Redis(r: redis.Redis, message: models.Message):
        redisName = Message._token2RedisName(message.id)
        mapping = Message._simplifiedMessage(message)
        r.hmset(redisName, mapping)
        r.expire(redisName, Message.EXPIRES_IN)  # expires

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
        templateID = data.get('templateID', None) or \
            config.get('defaultTemplateID', None)
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
        # optional
        body = data.get('body', '')
        url = data.get('url', '')
        created_time = time.time()
        # build post data
        postData = {
            'title': {'value': title},
            'body': {'value': body}
        }
        token = uuid.uuid4().hex
        detailUrl = config['VUE_APP_ROOT_URL'] + 'detail/' + token

        # send
        client = WechatTemplateMessageClient(manager)
        responseData = await client.sendTemplateMessage(
            receiver, templateID, postData, detailUrl)
        responseData['token'] = token
        response = {
            'success': True,
            'msg': None,
            'data': responseData
        }

        # insert into SQL db
        message = models.Message(
            id=token,
            app_id=config['APP_ID'],
            template_id=templateID,
            receiver_id=receiver,
            created_time=created_time,
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

        # insert into redis
        Message._save2Redis(config['redis'], message)

        # return response
        return web.json_response(response)

    @staticmethod
    @utils.allowCORS
    async def get(request: web.Request):
        config = request.app['config']
        token = request.match_info['token']
        logger.debug('GET /message/{}'.format(token))
        # query from redis
        r: redis.Redis = config['redis']
        redisName = Message._token2RedisName(token)
        try:
            data = r.hgetall(redisName)
        except redis.exceptions.RedisError as ex:
            logger.warning('Redis failed: {}'.format(ex))
            data = {}
        # if fails, retrieve from SQL db
        if len(data) == 0:
            message: models.Message
            message = config['session'].query(
                models.Message).filter_by(id=token).one_or_none()
            if message is None:
                raise web.HTTPNotFound(
                    reason='No records were found for this token.')
            # save to redis
            Message._save2Redis(config['redis'], message)
            data = Message._simplifiedMessage(message)
        # build reponse
        response = {
            'success': True,
            'msg': 'Success',
            'data': data
        }
        return web.json_response(response)


class Scene:
    EXPIRES_IN = 5*60

    @staticmethod
    @utils.allowCORS
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
                'decodedUrl': data['url']
            }
        })

    @staticmethod
    @utils.allowCORS
    async def get(request: web.Request):
        """Get open id for a scene ID

        Args:
            request (web.Request): web request
        """
        scene_id = request.match_info['scene_id']
        # query redis
        r: redis.Redis = request.app['config']['redis']
        try:
            openID = r.get(Scene._sceneID2RedisName(scene_id))
        except redis.exceptions.RedisError as ex:
            logger.warning('Redis error: {}'.format(ex))
            openID = None

        if openID is None:
            raise web.HTTPNotFound(reason='No such scene id.')
        return web.json_response({
            'success': True,
            'msg': '',
            'data': {
                'openID': openID
            }
        })

    @staticmethod
    def _sceneID2RedisName(scene_id):
        return 'wxpush:scene:{}'.format(scene_id)


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
        response = await afunc(tree, request.app['config']['redis'])

        return web.Response(text='')

    @staticmethod
    async def defaultHandler(tree: ElementTree.Element, r: redis.Redis):
        pass

    @staticmethod
    async def handleEvent(tree: ElementTree.Element, r: redis.Redis):
        openID = tree.find('FromUserName').text.strip()
        eventName = tree.find('Event').text.strip().lower()
        if eventName == 'subscribe':
            eventKey = tree.find('EventKey')
            if eventKey is None:
                return
            # scan to subscribe
            scene_id = int(eventKey.text.strip()[len('qrscene_'):])
            r.set(  # add to redis
                Scene._sceneID2RedisName(scene_id),
                openID, ex=Scene.EXPIRES_IN)
        elif eventName == 'scan':
            scene_id = int(tree.find('EventKey').text.strip())
            r.set(  # add to redis
                Scene._sceneID2RedisName(scene_id),
                openID, ex=Scene.EXPIRES_IN)
        elif eventName == 'unsubscribe':
            pass
