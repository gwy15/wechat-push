import asyncio
import aiohttp
import logging
logger = logging.getLogger(__name__)

from wechat.core.credential import AccessToken, TokenManager
from wechat.exceptions import WechatRequestError


class BaseRequest():
    def __init__(self, tokenManager: TokenManager):
        self.tokenManager = tokenManager

    async def _wrapUrlWithAccessToken(self, url):
        if '?access_token=' not in url:
            url += '?access_token={}'.format(
                await self.tokenManager.getAccessToken())
        return url

    @classmethod
    def _handleResponseJson(cls, data):
        errCode = data.get('errcode', None)
        if errCode is not None and errCode != 0:
            raise WechatRequestError(data['errmsg'], errCode)
        else:
            return data

    # APIs

    async def postRequest(self, url, data):
        logger.debug('{} POST {}, data={}'.format(
            self.__class__.__name__, url, data))
        url = await self._wrapUrlWithAccessToken(url)
        async with aiohttp.request('POST', url, json=data) as response:
            return self._handleResponseJson(await response.json())

    def postRequestSync(self, url, data):
        return asyncio.run(self.postRequest(url, data))

    async def getRequest(self, url, params=None):
        logger.debug('{} GET {}, params={}'.format(
            self.__class__.__name__, url, params))
        url = await self._wrapUrlWithAccessToken(url)
        async with aiohttp.request('GET', url, params=params) as response:
            return self._handleResponseJson(await response.json())

    def getRequestSync(self, url, params=None):
        return asyncio.run(self.getRequest(url, params=params))
