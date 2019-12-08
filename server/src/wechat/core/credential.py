import asyncio
import random
import string
import json
from pathlib import Path
from typing import Optional, Union
import time
import logging
import datetime

import aiohttp

from wechat.exceptions import WechatRequestError

logger = logging.getLogger(__name__)


class AccessToken(str):
    def __new__(cls, token: str, expiresAt: Union[int, float]):
        return str.__new__(cls, token)

    def __init__(self, token: str, expiresAt: Union[int, float]):
        """Init access token object

        Args:
            token (str): token.
            expiresAt (int, float): Unix timestamp for the token to expire.
        """
        if not isinstance(token, str):
            raise TypeError(
                'Param token must be str, not {}'.format(
                    type(token).__name__))
        if not isinstance(expiresAt, (int, float)):
            raise TypeError(
                'Param expiresAt must be int or float, not {}'.format(
                    type(expiresAt).__name__))

        self.expiresAt = expiresAt

    def expired(self):
        return time.time() > self.expiresAt

    @classmethod
    def fromJsonObject(cls, jsonObject):
        return cls(jsonObject['token'], jsonObject['expiresAt'])

    def toJsonObject(self):
        return {
            'token': str(self),
            'expiresAt': self.expiresAt
        }

    def __repr__(self):
        return '<AccessToken expiring @ {} in {:d} seconds>'.format(
            datetime.datetime.fromtimestamp(self.expiresAt)
            .strftime("%y-%m-%d %H:%M:%S"),
            int(self.expiresAt - time.time())
        )


class TokenManager():
    def __init__(self, appID: str, appSecret: str, path: Path = None):
        """Initiate token manager

        Args:
            appID (str): Wechat app ID
            appSecret (str): Wechat app secret
            path (Path, optional): Path to directory for storing tokens.
                Defaults to None, which will use ~/.config/wechat/.
        """

        self.appID = appID
        self.appSecret = appSecret

        if path is None:
            self.path = Path('~/.config/wechat').expanduser()
        else:
            if not isinstance(path, (Path, str)):
                raise ValueError(
                    'Param path must be pathlib.Path or str, not {}'.format(type(path).__name__))
            self.path = Path(path)

        self.path.mkdir(parents=True, exist_ok=True)
        self.tokenFile = self.path / 'credentials.json'

        self.token = self._loadToken()
        logger.debug('Token load: {}'.format(repr(self.token)))

    def _loadToken(self) -> Optional[AccessToken]:
        """Return a valid token or None

        Returns:
            Optional[AccessToken]: A valid token or None object.
        """
        if not self.tokenFile.exists():
            return None

        with self.tokenFile.open('r') as f:
            data = json.load(f)
        token = data.get(self.appID, None)

        if token is None:
            return None

        token = AccessToken.fromJsonObject(token)
        if token.expired():
            return None
        return token

    def _dumpToken(self):
        """Dump token to database. Return directly if no token available."""
        if self.token is None:
            return
        if not self.tokenFile.exists():
            data = {self.appID: self.token.toJsonObject()}
        else:
            with open(self.tokenFile, 'r') as f:
                data = json.load(f)
                data[self.appID] = self.token.toJsonObject()
        with open(self.tokenFile, 'w') as f:
            json.dump(data, f)

    async def getAccessToken(self) -> AccessToken:
        """Get a valid access token. Lazy refresh.

        Returns:
            AccessToken: token
        """
        if self.token is None:
            self.token = await self._getAccessToken()
            self._dumpToken()
        elif self.token.expired():
            self.token = await self._getAccessToken()
            self._dumpToken()
        return self.token

    async def _getAccessToken(self) -> AccessToken:
        """Get a new access token

        Raises:
            WechatRequestError: Wechat reject the request.

        Returns:
            AccessToken: A valid token
        """
        logger.debug('Get new access token.')
        url = 'https://api.weixin.qq.com/cgi-bin/token'
        params = {
            'grant_type': 'client_credential',
            'appid': self.appID,
            'secret': self.appSecret,
        }
        async with aiohttp.request('GET', url, params=params) as response:
            responseData = await response.json()
        errCode = responseData.get('errcode', None)
        if errCode is not None:
            raise WechatRequestError(responseData['errmsg'], errCode)
        else:
            expiresAt = int(responseData['expires_in'] + time.time())
            return AccessToken(responseData['access_token'], expiresAt)
