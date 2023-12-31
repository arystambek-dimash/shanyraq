from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, DECIMAL, TIMESTAMP, ForeignKey, JSON
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String(32),unique=True,index=True)
    phone = Column(String(32),unique=True,index=True)
    password = Column(String(32))
    name = Column(String(30))
    city = Column(String(15))
    created_at = Column(TIMESTAMP, default=datetime.now().replace(second=0,microsecond=0))
    updated_at = Column(TIMESTAMP, default=datetime.now().replace(second=0,microsecond=0))
    is_superuser = Column(Boolean, default=False)


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    type_announcement = Column(String)
    price = Column(Float)
    address = Column(String)
    area = Column(Float)
    rooms_count = Column(Integer)
    description = Column(String)
    announcement_at = Column(TIMESTAMP, default=datetime.now().replace(second=0,microsecond=0))
    updated_at = Column(TIMESTAMP, default=datetime.now().replace(second=0,microsecond=0))

    total_comments = Column(Integer)

    user = Column(ForeignKey('users.id'))


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    announcement_id = Column(Integer, ForeignKey("announcements.id"))

    created_at = Column(TIMESTAMP,default=datetime.now().replace(second=0,microsecond=0))
