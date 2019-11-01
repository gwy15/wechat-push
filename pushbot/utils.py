from typing import Optional

from wechat.core import TokenManager
from wechat.messages import WechatTemplateMessageClient


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
