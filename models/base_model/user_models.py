from sqlalchemy import Column, Integer, String, DateTime

from common.base import Base


class BaseUser(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    account = Column(String)
    phone = Column(String, unique=True)
    email = Column(String, unique=True)
    name = Column(String)
    password = Column(String)
    sex = Column(Integer, default=0)
    wx_open_id = Column(String, unique=True)
    wx_head = Column(String)
    wx_name = Column(String)
    # wx_account = Column(String)
    wx_session_key = Column(String)
    wx_fate_union_id = Column(String)
    token = Column(String)
    country = Column(String)
    province = Column(String)
    city = Column(String)
    register_time = Column(DateTime)
    last_login_time = Column(DateTime)
    is_authentication = Column(Integer, default=0)


class BaseUserInfo(Base):
    __tablename__ = 'user_info'
    id = Column(Integer, primary_key=True)
