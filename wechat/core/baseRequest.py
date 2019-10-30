import aiohttp
from wechat.core.credential import AccessToken, TokenManager
from wechat.exceptions import WechatRequestError


class BaseRequest():
    def __init__(self, tokenManager: TokenManager):
        self.tokenManager = tokenManager

    async def postRequest(self, url, data):
        if '?access_token=' not in url:
            url += '?access_token={}'.format(
                await self.tokenManager.getAccessToken())

        async with aiohttp.request('POST', url, json=data) as response:
            responseData = await response.json()

        errCode = responseData.get('errcode', None)
        if errCode is not None and errCode != 0:
            raise WechatRequestError(responseData['errmsg'], errCode)
        else:
            return responseData
