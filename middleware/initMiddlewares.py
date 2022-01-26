import asyncio
from fastapi import Request, Depends
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from common.common_init import RedisDB, BaseDB


class InitMiddleware(BaseHTTPMiddleware):
    """
    获取数据库连接中间件
    """

    def __init__(self, app: ASGIApp, dispatch: DispatchFunction = None) -> None:
        super().__init__(app, dispatch)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # request.state.db = await BaseDB.get_async_db()
        # request.state.redis = await RedisDB.get_async_redis_()
        tasks = [BaseDB.get_async_db(), RedisDB.get_async_redis_()]
        request.state.db, request.state.redis = await asyncio.gather(*tasks)

        response = await call_next(request)
        request.state.redis.close()
        return response
