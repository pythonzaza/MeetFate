import random
import string
from typing import Dict, Any, Optional
from sqlalchemy import select, insert, update, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from aioredis import Redis

from configs import WxConfig, TOKEN_CONFIG
from common.err import HTTPException
from common.common_init import now
from common.http_tool import request
from common.encrypt import Encrypt
from models.base_model.user_models import BaseUser
# from models.init_models.user_models import UserLogin
from models.init_models.wx_models import WxLogin, WxToken
from models.init_models.user_models import UserInfo


class UserServers(object):
    def __init__(self, db: AsyncSession, redis: Redis):
        self.db = db
        self.redis = redis

    async def create_token(self, login_user: BaseUser, user_id=None, platform='wx') -> Optional[str]:
        login_user.token = ''.join(random.sample(string.ascii_letters + string.digits, 32))
        print(login_user.token)
        login_user.last_login_time = now()
        try:
            async with self.db.begin():
                stmt = update(BaseUser).where(BaseUser.id == user_id). \
                    values(token=login_user.token, last_login_time=login_user.last_login_time)
                print(stmt)
                result = await self.db.execute(stmt)
                if result.rowcount != 1:
                    await self.db.rollback()
                    raise HTTPException(status=-10003, message='token创建失败')

                user_token = await Encrypt.create_token(login_user.token, user_id, login_user.wx_name, platform)

                await self.redis.set(key=f'user:token:{platform}:user{user_id}', value=user_token,
                                     expire=TOKEN_CONFIG.get('TOKEN_EXPIRE'))

                await self.db.commit()
                return user_token
        except Exception as err:
            print(err)
            raise HTTPException(status=-10003, message='token获取失败', data=err)

    async def create_account(self, userInfo: WxLogin, wx_token: WxToken):
        """
        :param userInfo: 新账号
        :param wx_token: 新账号
        """
        # user_dict = user.dict()
        user_dict: dict = {**userInfo.dict(), **wx_token.dict()}
        del user_dict['code']

        if user_dict.get("password"):
            hash_password = await Encrypt.encrypt_password(user_dict['password'])
            user_dict.update({"password": hash_password})

        user_dict.update({"register_time": now()})

        stmt = insert(BaseUser)
        result = await self.db.execute(stmt, user_dict)
        user_dict['id'] = result.lastrowid
        user = BaseUser(**user_dict)
        if result:
            await self.db.commit()
        else:
            await self.db.rollback()
            raise HTTPException(status=-10002, message='注册失败')

        return user

    # async def verify_account(self, user: UserLogin, ) -> BaseUser:
    #     user.password = await Encrypt.encrypt_password(user.password)
    #     async with self.db.begin():
    #         stmt = select(BaseUser).where(or_(
    #             and_(BaseUser.account == user.account, BaseUser.password == user.password),
    #             and_(BaseUser.email == user.email, BaseUser.password == user.password)
    #         ))
    #         result = await self.db.execute(stmt)
    #         login_user = result.scalars().first()
    #         if not login_user:
    #             raise HTTPException(status=10001, message="账号或密码错误")
    #         return login_user

    async def query_wx_account(self, wx_token: WxToken) -> Optional[BaseUser]:
        # 查重
        stmt = select(BaseUser).where(BaseUser.wx_open_id == wx_token.wx_open_id)
        # stmt = select(BaseUser).where(BaseUser.wx_open_id == wx_token.wx_open_id).options(selectinload(BaseUser.id))
        result = await self.db.execute(stmt)
        login_user = result.scalars().first()
        if login_user:
            return login_user

    async def get_wx_account(self, userInfo: WxLogin, wx_token: WxToken) -> [BaseUser, int]:
        try:
            async with self.db.begin():
                # 查重
                login_user = await self.query_wx_account(wx_token)
                # 不存在则创建
                if not login_user:
                    login_user = await self.create_account(userInfo, wx_token)
                print(login_user)
                user_out = UserInfo.from_orm(login_user)
                return user_out, login_user.id
        except Exception as err:
            raise HTTPException(status=-101, message='获取用户信息失败', data=err)

    @staticmethod
    async def wx_login(code: str):
        url = f'{WxConfig.wx_gateway}/sns/jscode2session'
        params = {
            "appid": WxConfig.app_id,
            "secret": WxConfig.secret,
            "js_code": code,
            "grant_type": "authorization_code",
        }
        resp = await request('get', url, params=params)
        if resp.get("errcode", 0) == 0:
            return WxToken(**resp)
        else:
            raise HTTPException(status=401, message='微信登录失败', data=resp)

    async def from_wx_login(self, userInfo: WxLogin, wx_token: WxToken):
        login_user, user_id = await self.get_wx_account(userInfo, wx_token)
        new_token = await self.create_token(login_user, user_id)
        login_user.token = new_token
        return login_user
