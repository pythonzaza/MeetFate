import json
import time
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from aioredis import Redis

from models.init_models import user_models
from common.encrypt import Encrypt
from common.common import BaseDB, RedisDB
from common.err import HTTPException

router = APIRouter()


@router.post('/register')
async def register(user: user_models.UserRegister, db: AsyncSession = Depends(BaseDB.get_async_db),
                   redis_db: Redis = Depends(RedisDB.get_async_redis)):
    async with db.begin():
        smt = text("select * from `user` where account = :account limit 1")
        result = await db.execute(smt, {"account": user.account})
        user_ = result.first()
        if user_:
            raise HTTPException(status=-1, message='账户已存在')

        user.password = await Encrypt.encrypt_password(user.password)
        register_sql = text('insert into user (account,password,register_time) \
                            value (account=:account,password=:password,register_time=:register_time)')
        new_user = jsonable_encoder(user)
        result = await db.execute(register_sql,
                                  {"account": user.account, "password": user.password,
                                   "register_time": int(time.time())})
        if not result:
            raise HTTPException(status=-1, message='注册失败,请稍后重试')
        await db.commit()
    token = await Encrypt.encrypt_token(new_user, 'asdadfewvrasdw12d')
    new_user.update({"token": token})

    set_token = await redis_db.hmset(f'cp_test:user:token', token, json.dumps(new_user))
    if not set_token:
        raise HTTPException(status=-100, message='缓存异常')
    return new_user
