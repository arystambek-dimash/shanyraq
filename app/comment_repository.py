from datetime import datetime
from typing import Optional

from sqlalchemy import update,delete
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
        return db.query(Comment).filter(Comment.announcement_id == announcement_id)

    @staticmethod
    def update_comment(db: Session, announcement_id,comment_id,comment:CommentRequest):
        updating_comment = update(Comment).where(Comment.announcement_id == announcement_id and Comment.id == comment_id).values(content = comment.content)
        db.execute(updating_comment)
        db.commit()
        updated_comment = db.query(Comment).get(comment_id)
        return updated_comment

    @staticmethod
    def delete_comment(db: Session, announcement_id, comment_id):
        deleting_comment = update(Comment).where(Comment.announcement_id == announcement_id and Comment.id == comment_id)
        db.execute(deleting_comment)
        db.commit()
        return True

