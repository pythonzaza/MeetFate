from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
import aioredis

from configs import engine, async_engine, REDIS_CONFIG
from common.err import HTTPException


class BaseDB(object):
    # @classmethod
    # async def get_async_db(cls):
    #     db = AsyncSession(async_engine)
    #     try:
    #         yield db
    #     # except Exception as err:
    #     #     raise HTTPException(status=-100, message='网络繁忙请稍后重试', data=err)
    #     #     # raise HTTPException(status_code=200, detail={"status": 1001, "msg": "网络繁忙请稍后重试"})
    #     finally:
    #         await db.close()

    @classmethod
    async def get_async_db(cls) -> AsyncSession:
        return AsyncSession(async_engine)
        # except Exception as err:
        #     raise HTTPException(status=-100, message='网络繁忙请稍后重试', data=err)
        #     # raise HTTPException(status_code=200, detail={"status": 1001, "msg": "网络繁忙请稍后重试"})

    # @classmethod
    # def get_db(cls) -> Session:
    #     db = Session(engine)
    #     try:
    #         yield db
    #     finally:
    #         db.close()


class RedisDB(object):

    @classmethod
    async def get_async_redis(cls):
        redis_db = None
        try:
            redis_db = await aioredis.create_redis(**REDIS_CONFIG)
            yield redis_db
        finally:
            if redis_db:
                redis_db.close()

    @classmethod
    async def get_async_redis_(cls):
        try:
            redis_db = await aioredis.create_redis(**REDIS_CONFIG)
            return redis_db
        except Exception as err:
            print(err)
            raise HTTPException(message='系统繁忙请稍后重试', status=-1000)


def now():
    time = datetime.now()
    return time.strftime("%Y-%m-%d %H:%M:%S")
