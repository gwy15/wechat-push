import unittest
import time
import tempfile

from wechat.tests.utils import async_test

from wechat.core.credential import AccessToken
from wechat.core.credential import TokenManager
from wechat.exceptions import WechatRequestError


class AccessTokenTest(unittest.TestCase):
    def testConstructor(self):
        AccessToken('test token', 123)
        AccessToken('test token', 123.123)

        for token in (None, 123, dict(), []):
            with self.assertRaises(TypeError):
                AccessToken(token, 123)
        for expiresAt in (None, dict(), []):
            with self.assertRaises(TypeError):
                AccessToken('test', expiresAt)

    def testExpire(self):
        token = AccessToken('test token', 123)
        self.assertTrue(token.expired())
        token = AccessToken('test token', time.time() + 2)
        self.assertFalse(token.expired())

    def testLoad(self):
        token = AccessToken.fromJsonObject({'token': 'test', 'expiresAt': 123})
        self.assertEqual(token, 'test')
        self.assertTrue(token.expired())
        with self.assertRaises(KeyError):
            AccessToken.fromJsonObject({})

    def testDump(self):
        data = {'token': 'test', 'expiresAt': 123}
        token = AccessToken.fromJsonObject(data)
        self.assertEqual(token.toJsonObject(), data)


class TokenManagerTest(unittest.TestCase):
    def testConstructor(self):
        TokenManager('id', 'secret')
        TokenManager('id', 'secret', None)

    def testLoad(self):
        with tempfile.TemporaryDirectory() as dir:
            man = TokenManager('id', 'secret', dir)
            man._loadToken()
            self.assertIsNone(man.token)
            man._dumpToken()

    @async_test
    async def testGetAccessToken(self):
        with tempfile.TemporaryDirectory() as dir:
            man = TokenManager('id', 'secret', dir)
            with self.assertRaises(WechatRequestError):
                await man.getAccessToken()


if __name__ == "__main__":
    unittest.main()
