from datetime import datetime
from typing import Optional

from .models import User
from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from sqlalchemy.orm import Session
from sqlalchemy import update, delete


class UserRequest(BaseModel):
    email: EmailStr
    username: str
    phone: PhoneNumber = Field(max_length=32, min_length=10)
    password: str = Field(max_length=32, min_length=8)
    name: str = Field(max_length=30)
    city: str = Field(max_length=15)
    created_at: Optional[datetime] = datetime.utcnow()
    updated_at: Optional[datetime] = datetime.utcnow()

    class Config:
        json_schema_extra = {
            "example": {
                "email": "nfactorial@school.com",
                "username": "qwerty",
                "phone": "+77775551122",
                "password": "password123",
                "name": "Dalida",
                "city": "Almaty"
            },
        }


class UserLogin(BaseModel):
    username: str = Field(max_length=32, min_length=10)
    password: str = Field(max_length=32, min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "qwerty",
                "password": "password"
            }
        }


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: str
    name: str
    city: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    is_superuser: bool = False


class UserUpdate(BaseModel):
    username: str
    name: str
    city: str


class UserRepostitory:
    @staticmethod
    def get_user_by_username(db: Session, username):
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id):
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(db: Session, user: UserRequest):
        db_user = User(email=user.email, phone=user.phone, username=user.username, password=user.password,
                       name=user.name, city=user.city)

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def update_user(db: Session, user_email, user: UserUpdate):
        db_update = update(User).where(User.email == user_email).values(username=user.username, name=user.name,
                                                                        city=user.city,
                                                                        updated_at=datetime.now().replace(second=0,
                                                                                                          microsecond=0))
        db.execute(db_update)
        db.commit()
        updated_user = db.query(User).get(user_email)
        return updated_user

    @staticmethod
    def get_all(db: Session):
        return db.query(User).all()

    @staticmethod
    def appoint_as_superuser(db: Session, user_id):
        db.execute(update(User).where(User.id == user_id).values(is_superuser=True))
        db.commit()

    @staticmethod
    def delete_user(db:Session,user_id):
        db.execute(delete(User).where(User.id == user_id).first())
        db.commit()
