import hashlib
import Crypto.Cipher.DES3
import base64
import json
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Union

from configs import EncryptConfig, oauth2_scheme, TOKEN_CONFIG
from common.err import HTTPException


class Encrypt(object):
    @staticmethod
    async def encrypt_password(password: str):
        """
        获取加密后的密码
        :param password: 原始密码
        :return:
        """
        sha256 = hashlib.sha256()
        sha256.update((password + EncryptConfig.password_key).encode())
        return sha256.hexdigest()

    async def verify_password(self, password: str, hash_password: str) -> bool:
        __hash_password = self.encrypt_password(password)
        if __hash_password == hash_password:
            return True
        else:
            return False

    @classmethod
    async def encrypt_token(cls, user_info: dict, key: str = EncryptConfig.token_key) -> str:
        """

        :param user_info: 待加密信息
        :param key: 加密key
        :return: token
        """
        key = await cls.check_key(key)
        user_info = await cls.check_data(json.dumps(user_info))
        crypto = Crypto.Cipher.DES3.new(key, Crypto.Cipher.DES3.MODE_ECB)
        token = base64.encodebytes(crypto.encrypt(user_info)).decode()

        return token

    @classmethod
    async def decrypt_token(cls, token: str, key) -> dict:
        """

        :param token:
        :param key:
        :return:
        """
        key = await cls.check_key(key)
        crypto = Crypto.Cipher.DES3.new(key, Crypto.Cipher.DES3.MODE_ECB)
        user_info_ = crypto.decrypt(base64.decodebytes(token.encode()))
        user_info: dict = json.loads(user_info_)
        return user_info

    @staticmethod
    async def check_key(key: str) -> bytes:
        long = len(key)

        if long > 24:
            raise Exception("Key不能超出24位")
        if 8 < long < 24:
            key += ' ' * (8 - long % 8)
        return key.encode()

    @staticmethod
    async def check_data(key: str) -> bytes:
        long = len(key)
        key += ' ' * (8 - long % 8)
        return key.encode()

    @staticmethod
    async def create_token(token: str, user_id: Union[str, int], wx_name: str, platform,
                           expires_delta: int = TOKEN_CONFIG.get('TOKEN_VALIDITY')):
        """
        创建token
        """
        to_encode = {
            "token": token,
            "user_id": user_id,
            "wx_name": wx_name,
            "platform": platform,
        }
        expire = datetime.utcnow() + timedelta(seconds=expires_delta)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, EncryptConfig.SECRET_KEY, algorithm=EncryptConfig.ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def parse_token(token: str):
        # async def parse_token(token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status=401,
            message='token错误'
        )
        try:
            payload = jwt.decode(token, EncryptConfig.SECRET_KEY, algorithms=[EncryptConfig.ALGORITHM],
                                 options={"require_exp": True})
            user_id: str = payload.get("user_id")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        # user = get_user(fake_users_db, username=token_data.username)
        user = payload
        if user is None:
            raise credentials_exception
        return user


if __name__ == '__main__':
    import asyncio

    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbiI6IndMYVNFMGJPVUlDTXlucG9rWVFSbDd1WHZzdEtESnhoIiwidXNlcl9pZCI6NSwid3hfbmFtZSI6Ilx1NGViYVx1NTE0MyIsImV4cCI6MTYzMTE3NDY5NH0.ofpGQmn5F390MtuGiTFIjAn8YyT1PKZuYnfODk1lohY'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Encrypt.parse_token(token))
