from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import get_db
from models import DBAnswer


class AnswerSchema(BaseModel):
    answer_text: str
    is_correct: bool
    question_id: int


class AnswerAPI:
    def __init__(self):
        self.router = APIRouter(
            prefix="/answers",
            tags=["Answers"]
        )

        self.register_routes()

    def register_routes(self):
        self.router.add_api_route(
            "/", self.get_all_answers, methods=["GET"]
        )

        self.router.add_api_route(
            "/", self.create_answer, methods=["POST"]
        )

    def get_all_answers(self, db: Session = Depends(get_db)):
        return db.query(DBAnswer).all()

    def create_answer(
        self,
        answer: AnswerSchema,
        db: Session = Depends(get_db)
    ):
        new_answer = DBAnswer(
            answer_text=answer.answer_text,
            is_correct=answer.is_correct,
            question_id=answer.question_id
        )

        db.add(new_answer)
        db.commit()
        db.refresh(new_answer)

        return new_answer


answer_api = AnswerAPI()
router = answer_api.router