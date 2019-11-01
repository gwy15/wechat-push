from wechat.core import BaseRequest


class WechatQRCodeClient(BaseRequest):
    async def getTempQRCode(self, scene_id, expireSeconds=5*60):
        url = 'https://api.weixin.qq.com/cgi-bin/qrcode/create'
        data = {
            'expire_seconds': expireSeconds,
            'action_name': 'QR_SCENE',
            'action_info': {
                'scene': {
                    'scene_id': scene_id
                }
            }
        }
        return await self.postRequest(url, data)
