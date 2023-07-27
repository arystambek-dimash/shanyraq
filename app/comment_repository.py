from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import update,delete,func
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .models import Comment


class CommentRequest(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    content: str
    created_at: Optional[datetime]
    author_id: int


class CommentRepository:
    @staticmethod
    def create_comment(db: Session, user_id, announcement_id, comment: CommentRequest):
        db_comment = Comment(content=comment.content, user_id=user_id, announcement_id=announcement_id)
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def get_comment_by_announcement_id(db:Session,announcement_id):
        return db.query(Comment).filter(Comment.announcement_id == announcement_id).all()

    @staticmethod
    def get_comment_by_announcement_id_with_comment_id(db: Session, announcement_id,comment_id):
        return db.query(Comment).filter(Comment.announcement_id == announcement_id and Comment.id == comment_id).first()

    @staticmethod
    def update_comment(db: Session, announcement_id,comment_id,user_id,comment:CommentRequest):
        updating_comment = update(Comment).filter(Comment.id == comment_id and Comment.announcement_id == announcement_id  and Comment.user_id == user_id).values(content = comment.content)
        db.execute(updating_comment)
        db.commit()
        updated_comment = db.query(Comment).get(comment_id)
        if updated_comment:
            return updated_comment
        raise HTTPException(status_code=404,detail="The comment not found")

    @staticmethod
    def delete_comment(db: Session, announcement_id, comment_id,user_id):
        deleting_comment = delete(Comment).filter(Comment.id == comment_id and Comment.announcement_id == announcement_id and Comment.user_id == user_id)
        db.execute(deleting_comment)
        db.commit()
        return True

    @staticmethod
    def get_length_comment(db:Session,announcement_id):
        comments = db.query(Comment).filter(Comment.announcement_id == announcement_id).all()
        return len(comments)
