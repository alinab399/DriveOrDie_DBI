from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import DBAnswer


class AnswerSchema(BaseModel):
    answer_text: str
    is_correct: bool
    question_id: int


router = APIRouter(
    prefix="/answers",
    tags=["Answers"]
)


@cbv(router)
class AnswerAPI:
    db: Session = Depends(get_db)

    @router.get("/")
    def get_all_answers(self):
        return self.db.query(DBAnswer).all()

    @router.post("/")
    def create_answer(self, answer: AnswerSchema):
        new_answer = DBAnswer(
            answer_text=answer.answer_text,
            is_correct=answer.is_correct,
            question_id=answer.question_id
        )

        self.db.add(new_answer)
        self.db.commit()
        self.db.refresh(new_answer)

        return new_answer