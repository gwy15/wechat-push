import asyncio
import aiohttp

from wechat.core import BaseRequest


class WechatTemplateMessageClient(BaseRequest):
    async def sendTemplateMessage(self, receiverOpenID, templateID, data, url=None):
        apiUrl = 'https://api.weixin.qq.com/cgi-bin/message/template/send'
        templateData = {
            'touser': receiverOpenID,
            'template_id': templateID,
            'data': data
        }
        if url:
            templateData['url'] = url
        response = await self.postRequest(apiUrl, templateData)
        return response
