import asyncio
import aiohttp

from wechat.core import BaseRequest


class WechatTemplateMessageClient(BaseRequest):
    async def sendTemplateMessage(self, receiverOpenID, templateID, data):
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send'
        templateData = {
            'touser': receiverOpenID,
            'template_id': templateID,
            'data': data
        }
        response = await self.postRequest(url, templateData)
        return response
