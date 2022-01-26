import aioredis

from configs import RedisConfig
from common.err import HTTPException


class Redis(object):
    host = RedisConfig.host
    password = RedisConfig.password

    @classmethod
    async def set_dict(cls, key, name, values):
        try:
            redis_db = await aioredis.create_redis(address=cls.host, password=cls.password, encoding='utf-8')

            set_ = await redis_db.hmset_dict(key, {name: values})
            redis_db.close()
            return set_

        except Exception as err:
            print(err)
            raise HTTPException(status=100001, message='Redis缓存异常', data=err)

    @classmethod
    async def set_list(cls, key, values):
        try:
            redis_db = await aioredis.create_redis(address=cls.host, password=cls.password, encoding='utf-8')

            set_ = await redis_db.lpush(key, values)
            redis_db.close()
            return set_

        except Exception as err:
            print(err)
            raise HTTPException(status=100001, message='Redis缓存异常', data=err)

    @classmethod
    async def get_dict(cls, key, name):
        try:
            redis_db = await aioredis.create_redis(address=cls.host, password=cls.password, encoding='utf-8')

            resilt = await redis_db.hmget(key, name)
            print(resilt)
            await redis_db.closed
            return resilt

        except Exception as err:
            raise HTTPException(status=100001, message='Redis缓存异常')
