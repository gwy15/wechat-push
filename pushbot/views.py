import time
from typing import Optional, Union

from aiohttp import web
import uuid

from aiohttp.web_request import FileField
from multidict import MultiDictProxy

from pushbot.utils import getIPFromRequest
from wechat.messages import WechatTemplateMessageClient
from wechat.exceptions import WechatRequestError
from pushbot import utils
from pushbot import models


class Message:
    @staticmethod
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
                    raise web.HTTPBadRequest(reason='No template id param was found.')
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

    @staticmethod
    async def get(request: web.Request):
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
