from sqlalchemy import Column, String, Integer
from .db import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    city_name = Column(String)
    searched = Column(Integer)


class UserSearch(Base):
    __tablename__ = "usersearches"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_host = Column(String)
    user_request = Column(String)
