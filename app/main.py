from fastapi import FastAPI, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordBearer
from . import database
from sqlalchemy.orm import Session
from jose import jwt
from fastapi.responses import Response
from .users_repository import UserRepostitory, UserRequest, UserResponse, UserUpdate
from .announcements_repository import AnnouncementRequest, AnnouncementResponse, AnnouncementRepository
from .comment_repository import CommentRequest, CommentRepository, CommentResponse

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/users/login")

user_repo = UserRepostitory()
announcement_repo = AnnouncementRepository()
comment_repo = CommentRepository()


def encode_to_jwt(user_id):
    body = {"user_id": user_id}
    return jwt.encode(body, "shanyraq", algorithm="HS256")


def decode_access_token(token):
    data = jwt.decode(token, "shanyraq", algorithms=["HS256"])
    return data["user_id"]


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    user = user_repo.get_user_by_id(db, int(decode_access_token(token)))
    if not user:
        raise HTTPException(status_code=404, detail="Not user such username")
    return user


@app.post("/auth/users/", tags=["Register"])
async def auth(user: UserRequest, db: Session = Depends(get_db)):
    existing_user = user_repo.get_user_by_username(db, user.username)
    if not existing_user or (
            existing_user.email == user.email or existing_user.username == user.username or existing_user.phone == user.phone):
        raise HTTPException(status_code=400, detail="The phone number or email or username is already taken")
    user_repo.create_user(db, user)
    return {"message": "Successful Authorized"}


@app.post("/auth/users/login", tags=["Login"])
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = user_repo.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="The user not found")
    if user.password != password:
        raise HTTPException(status_code=404, detail="The password is inccorect")
    access_token = encode_to_jwt(user.id)
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
    announcements = announcement_repo.get_all(db)
    for i in announcements:
        if comment_repo.get_comment_by_announcement_id(db, i.id):
            i.total_comments = comment_repo.get_length_comment(db, i.id)
    return announcements


@app.post("/shanyraks/", tags=["Announcements"])
async def create_announcements(announcement: AnnouncementRequest,
                               current_user: UserResponse = Depends(get_current_user),
                               db: Session = Depends(get_db)):
    announcement.user_id = current_user.id
    return {"id": announcement_repo.create_announcement(db, announcement).id}


@app.get("/shanyraks/{id_announcement}", tags=["Announcements"], response_model=AnnouncementResponse)
async def get_announcement(id_announcement: int, db: Session = Depends(get_db)):
    announcement = announcement_repo.get_announcement_by_id(db, id_announcement)
    if not announcement:
        raise HTTPException(status_code=404, detail="The announcement not found")
    announcement.total_comments = comment_repo.get_length_comment(db, id_announcement)
    return announcement


@app.patch("/shanyraks/{id_announcement}", tags=["Announcements"])
async def update_announcement(id_announcement: int,
                              announcement: AnnouncementRequest,
                              current_user: UserResponse = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    updating_announcement = announcement_repo.get_announcement_by_id(db, id_announcement)
    if not updating_announcement:
        raise HTTPException(status_code=404, detail="The announcement not found")
    if updating_announcement.user == current_user.id:
        announcement_repo.update_announcement(db, id_announcement, announcement)
        return {"message": "Successful updated"}
    raise HTTPException(status_code=404, detail="The flower ID is incorrect or you are not"
                                                "the user who placed the announcement")


@app.delete("/shanyraks/{id_announcement}", tags=["Announcements"])
async def delete_announcement(id_announcement: int,
                              current_user: UserResponse = Depends(get_current_user),
                              db: Session = Depends(get_db)):
    db_announcement = announcement_repo.get_announcement_by_id(db, id_announcement)
    if not db_announcement:
        raise HTTPException(status_code=404, detail="The announcement not found")
    if db_announcement.user != current_user.id or current_user.is_superuser != True:
        raise HTTPException(status_code=404, detail="The flower ID is incorrect or you are not"
                                                    "the user who placed the announcement")
    announcement_repo.delete_announcement(db, id_announcement)
    return {"message": "Successful Deleted"}


@app.get("/shanyraks/{id_announcement}/comments", tags=["Comments"])
async def get_comment(id_announcement: int,
                      db: Session = Depends(get_db)):
    if id_announcement and announcement_repo.get_announcement_by_id(db, id_announcement):
        return comment_repo.get_comment_by_announcement_id(db, id_announcement)
    raise HTTPException(status_code=404, detail="The announcement not found")


@app.post("/shanyraks/{id_announcement}/comments", tags=["Comments"])
async def create_comment(id_announcement: int, comment: CommentRequest,
                         current_user: UserResponse = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    if id_announcement and announcement_repo.get_announcement_by_id(db, id_announcement):
        comment_repo.create_comment(db, current_user.id, id_announcement, comment)
        return {"message": "Comment was public"}
    raise HTTPException(status_code=404, detail="The announcement not found")


@app.patch("/shanyraks/{id_announcement}/comments/{comment_id}", tags=["Comments"])
async def update_comment(id_announcement: int, comment_id: int, comment: CommentRequest,
                         current_user: UserResponse = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    db_comment = comment_repo.get_comment_by_announcement_id_with_comment_id(db, id_announcement, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="The comment not found or Ur not user which created the comment")
    if db_comment.user_id == current_user.id and db_comment:
        comment_repo.update_comment(db, announcement_id=id_announcement, user_id=current_user.id, comment_id=comment_id,
                                    comment=comment)
        return Response(status_code=200, content={"message": "Comment was successful updated"})
    raise HTTPException(status_code=404, detail="The comment not found or Ur not user which created the comment")


@app.delete("/shanyraks/{id_announcement}/comments/{comment_id}", tags=["Comments"])
async def delete_comment(id_announcement: int, comment_id: int,
                         current_user: UserResponse = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    db_comment = comment_repo.get_comment_by_announcement_id_with_comment_id(db, id_announcement, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="The comment not found")
    if db_comment.user_id == current_user.id or current_user.is_superuser:
        comment_repo.delete_comment(db, announcement_id=id_announcement, user_id=current_user.id, comment_id=comment_id)
        return {"message": "Comment was successful deleted"}
    raise HTTPException(status_code=404, detail="The comment not found or ur not the creater")


@app.get("/auth/users/get_users", tags=["Superuser"])
def get_all_users_only_super_user_can(current_user: UserResponse = Depends(get_current_user),
                                      db: Session = Depends(get_db)):
    if current_user.is_superuser:
        return user_repo.get_all(db)
    raise HTTPException(status_code=400, detail="Ur are not superuser")


@app.post("/auth/users/appoint_as_admin", tags=["Superuser"])
def appoint_as_super_user(user_id: int, current_user: UserResponse = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    if current_user.is_superuser and user_repo.get_user_by_id(db, user_id) is not None:
        user_repo.appoint_as_superuser(db, user_id)
        return {"message": "The user was superuser"}
    raise HTTPException(status_code=400, detail="Ur are not superuser or the user not in database")


@app.delete("/auth/users/delete_user", tags=["Superuser"])
def delete_user(user_id: int, current_user: UserResponse = Depends(get_current_user),
                db: Session = Depends(get_db)):
    if current_user.is_superuser and user_repo.get_user_by_id(db, user_id) is not None:
        user_repo.delete_user(db, user_id)
        return {"message": "The user was deleted"}
    raise HTTPException(status_code=400, detail="Ur are not superuser or the user not in database")
