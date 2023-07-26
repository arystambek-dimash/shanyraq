from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordBearer
from .users_repository import UserRepostitory, UserRequest, UserResponse, UserUpdate
from .announcements_repository import AnnouncementRequest, AnnouncementResponse, AnnouncementRepository
from . import database
from sqlalchemy.orm import Session
from jose import jwt

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/users/login")

user_repo = UserRepostitory()
announcement_repo = AnnouncementRepository()


def encode_to_jwt(phone):
    body = {"phone": phone}
    return jwt.encode(body, "shanyraq", algorithm="HS256")


def decode_access_token(token):
    data = jwt.decode(token, "shanyraq", algorithms=["HS256"])
    return data["phone"]


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    user_phone = decode_access_token(token)
    user_phone = user_phone.replace("-", "")
    user = user_repo.get_user_by_phone(db, user_phone)
    if not user:
        raise HTTPException(status_code=404, detail="Not user such number")

    return user


@app.post("/auth/users/", tags=["Register"])
async def auth(user: UserRequest, db: Session = Depends(get_db)):
    existing_user = user_repo.get_user_by_phone(db, user.phone)
    if existing_user:
        return {"message": "The phone number or email is already taken"}
    user_repo.create_user(db, user)
    return {"message": "Successful Authorized"}


@app.post("/auth/users/login", tags=["Login"])
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = user_repo.get_user_by_phone(db, "tel:" + username)
    if user is None:
        raise HTTPException(status_code=404, detail="The user not found")
    if user.password != password:
        raise HTTPException(status_code=404, detail="The password is inccorect")
    access_token = encode_to_jwt(user.phone)
    return {"access_token": access_token}


@app.get("/auth/users/me/", response_model=UserResponse, tags=["Profile"])
async def profile(user: UserRequest = Depends(get_current_user)):
    return user


@app.patch("/auth/users/me/", tags=["Profile"])
async def profile_edit(user_update: UserUpdate,
                       user: UserRequest = Depends(get_current_user),
                       db: Session = Depends(get_db)):
    user_repo.update_user(db, user.email, user_update)
    return {"messages": "successful updated"}


@app.get("/shanyraks/all", tags=["Announcements"])
async def get_all_announcements(db: Session = Depends(get_db)):
    return announcement_repo.get_all(db)


@app.post("/shanyraks/", tags=["Announcements"])
async def create_announcements(announcement: AnnouncementRequest,
                               current_user: UserRequest = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    announcement.user_id = current_user.id
    announcement_repo.create_announcement(db, announcement)
    return {"message": "successful created"}


@app.get("/shanyraks/{id_announcement}",tags=["Announcements"])
async def get_announcement(id_announcement: int, db: Session = Depends(get_db)):
    return announcement_repo.get_announcement_by_id(db, id_announcement)


@app.patch("/shanyraks/{id_announcement}",tags=["Announcements"])
async def update_announcement(id_announcement: int,
                              announcement: AnnouncementRequest,
                              current_user: UserRequest = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    updating_announcement = announcement_repo.get_announcement_by_id(db, id_announcement)
    if updating_announcement.user == current_user.id:
        announcement_repo.update_announcement(db, id_announcement, announcement)
        return {"message": "Successful updated"}
    raise HTTPException(status_code=404, detail="The flower ID is incorrect or you are not"
                                                "the user who placed the announcement")


@app.delete("/shanyraks/{id_announcement}",tags=["Announcements"])
async def delete_announcement(id_announcement: int,
                              current_user: UserRequest = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    updating_announcement = announcement_repo.get_announcement_by_id(db, id_announcement)
    if updating_announcement.user == current_user.id:
        announcement_repo.delete_announcement(db, id_announcement)
        return {"message": "Successful Deleted"}
    raise HTTPException(status_code=404, detail="The flower ID is incorrect or you are not"
                                                "the user who placed the announcement")


@app.post("/shanyraks/{id_announcement}/comments")
async def type_comment(id_announcement:int,current_user:UserRequest = Depends(get_current_user),db:Session=Depends(get_db)):
    pass