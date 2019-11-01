from typing import Optional
import functools
import hashlib

from aiohttp import web

from wechat.core import TokenManager
from wechat.messages import WechatTemplateMessageClient
from wechat.exceptions import WechatRequestError


def getIPFromRequest(request):
    """
    Get IP from aiohttp request
    Args:
        request:

    Returns:

    """
    ip = request.headers.get('X-Real-IP', None) or \
        request.headers.get('X-Forwarded-For', None)
    if ip is None:
        peername = request.transport.get_extra_info('peername')
        if peername is not None:
            ip, _ = peername
        else:
            ip = ''
    return ip


async def getDefaultTemplateID(tokenManager: TokenManager) -> Optional[str]:
    client = WechatTemplateMessageClient(tokenManager)
    templateList = await client.getTemplateList()
    if len(templateList) != 1:
        return None
    else:
        return templateList[0]['template_id']

async def verifyRequest(request: web.Request):
    signature = request.rel_url.query.get('signature', None)
    timestamp = request.rel_url.query.get('timestamp', None)
    nonce = request.rel_url.query.get('nonce', None)
    if not (signature and timestamp and nonce):
        raise web.HTTPUnauthorized(reason='must be signatured.')
    token = request.app['config']['WECHAT_TOKEN']
    raw = ''.join(sorted([token, timestamp, nonce])).encode()
    if signature != hashlib.sha1(raw).hexdigest():
        raise web.HTTPUnauthorized(reason='bad signature.')

# wrappers
def catchWechatError(afunc):
    @functools.wraps(afunc)
    async def wrapper(*args, **kws):
        try:
            response = await afunc(*args, **kws)
            return response
        except WechatRequestError as ex:
            data = {
                'success': False,
                'msg': 'WechatRequestError: ' + str(ex)
            }
            return web.json_response(data)

        return res
    return wrapper

def allowCORS(afunc):
    @functools.wraps(afunc)
    async def wrapper(request, *args, **kws):
        config = request.app['config']
        response = await afunc(request, *args, **kws)
        response.headers['Access-Control-Allow-Origin'] = config['allowedDomains']
        return response
    return wrapper

def verifyFromWechatCallback(afunc):
    @functools.wraps(afunc)
    async def wrapper(request):
        await verifyRequest(request)
        return await afunc(request)
    return wrapper
