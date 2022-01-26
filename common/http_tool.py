from aiohttp import ClientSession
from typing import Any
from common.err import HTTPException
from json import loads


async def request(method: str, url: str, **kwargs: Any):
    method = method.lower()
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "Host": "api.weixin.qq.com",
    }
    try:
        async with ClientSession() as client:
            async with client.request(method, url, headers=headers, **kwargs) as resp:
                resp_text = await resp.text()
                return loads(resp_text)
    except Exception as err:
        print(err)
        raise HTTPException(status=-99, message="请求异常", data=err)
