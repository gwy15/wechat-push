from typing import Optional

from wechat.core import BaseRequest


class WechatTemplateMessageClient(BaseRequest):
    async def sendTemplateMessage(
            self, receiverOpenID: str, templateID: str,
            data: str, url: Optional[str] = None):
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

    async def getTemplateList(self):
        url = 'https://api.weixin.qq.com/cgi-bin/' \
                'template/get_all_private_template'
        data = await self.getRequest(url)
        return data['template_list']
