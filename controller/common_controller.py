from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from aioredis import Redis
from fastapi.requests import Request

from common.err import HTTPException
from models.init_models.user_models import UserRegister, UserOut, UserLogin, UserInfo
from models.init_models.wx_models import WxLogin, WxToken
from common.common_init import BaseDB, RedisDB
from servers.user_servers import UserServers

common_router = APIRouter()


# @common_router.post("/register", response_model=UserOut)
# async def register(user: UserRegister, db: AsyncSession = Depends(BaseDB.get_async_db)):
#     user_server = UserServers(db)
#     await user_server.check_account(user.account)
#     new_user = await user_server.create_account(user)
#
#     return UserOut(data=new_user)
#
#
# @common_router.post("/login")
# async def login(user: UserLogin, db: AsyncSession = Depends(BaseDB.get_async_db),
#                 redis_db: Redis = Depends(RedisDB.get_async_redis)):
#     if not user.code:
#         pass
#     user_server = UserServers(db=db)
#     login_user = await user_server.verify_account(user)
#     token = await user_server.create_token(login_user)

def get_db_session() -> int:
    import random
    try:
        yield random.randint(1, 100)
    except Exception as err:
        print(err)
    finally:
        print('finally')


@common_router.post("/wx/login", response_model=UserOut, response_model_exclude={"data.city"})
async def test(requests: Request, wx_login: WxLogin):
    db: AsyncSession = requests.state.db
    redis_db: Redis = requests.state.redis

    print(requests.state.db)
    user_server = UserServers(db=db, redis=redis_db)
    # wx_token = await user_server.wx_login(wx_login.code)
    wx_token = WxToken(**{'session_key': '2l89PN5/6Ite+LJ0m15WPg==', 'openid': 'oqMg_5YPfLP9kR0I2cKRJv_rmmi8'})
    user_out = await user_server.from_wx_login(wx_login, wx_token)
    print(user_out.json())
    user = UserOut(data=user_out)
    return user
