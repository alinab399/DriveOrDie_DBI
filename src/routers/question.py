from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import get_db
from models import DBQuestion


class QuestionSchema(BaseModel):
    question_text: str
    question_type: str
    image_path: str | None = None


class QuestionAPI:
    def __init__(self):
        self.router = APIRouter(
            prefix="/questions",
            tags=["Questions"]
        )

        self.register_routes()

    def register_routes(self):
        self.router.add_api_route(
            "/", self.get_all_questions, methods=["GET"]
        )

        self.router.add_api_route(
            "/", self.create_question, methods=["POST"]
        )

        self.router.add_api_route(
            "/{question_id}", self.get_question, methods=["GET"]
        )

        self.router.add_api_route(
            "/{question_id}", self.delete_question, methods=["DELETE"]
        )

    def get_all_questions(self, db: Session = Depends(get_db)):
        return db.query(DBQuestion).all()

    def create_question(
        self,
        question: QuestionSchema,
        db: Session = Depends(get_db)
    ):
        new_question = DBQuestion(
            question_text=question.question_text,
            question_type=question.question_type,
            image_path=question.image_path
        )

        db.add(new_question)
        db.commit()
        db.refresh(new_question)

        return new_question

    def get_question(
        self,
        question_id: int,
        db: Session = Depends(get_db)
    ):
        question = db.query(DBQuestion).filter(
            DBQuestion.question_id == question_id
        ).first()

        if not question:
            raise HTTPException(
                status_code=404,
                detail="Frage nicht gefunden"
            )

        return question

    def delete_question(
        self,
        question_id: int,
        db: Session = Depends(get_db)
    ):
        question = db.query(DBQuestion).filter(
            DBQuestion.question_id == question_id
        ).first()

        if not question:
            raise HTTPException(
                status_code=404,
                detail="Frage nicht gefunden"
            )

        db.delete(question)
        db.commit()

        return {"message": "Frage gelöscht"}


question_api = QuestionAPI()
router = question_api.router