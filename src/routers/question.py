from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import get_db
from models import DBQuestion, DBActionStep
import random


class ActionStepSchema(BaseModel):
    text: str
    correct_order: int

class QuestionSchema(BaseModel):
    question_text: str
    question_type: str
    image_path: str | None = None

    action_steps: list[ActionStepSchema] = []


router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)


@cbv(router)
class QuestionAPI:
    db: Session = Depends(get_db)

    @router.get("/")
    def get_all_questions(self):
        return self.db.query(DBQuestion).all()

    @router.get("/random")
    def get_random_question(self):
        questions = self.db.query(DBQuestion).all()

        if not questions:
            raise HTTPException(
                status_code=404,
                detail="Keine Fragen vorhanden"
            )

        question = random.choice(questions)

        return {
            "question_id": question.question_id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "image_path": question.image_path,

            "actions": [
                {
                    "id": step.actionstep_id,
                    "text": step.text,
                    "correctOrder": step.correct_order
                }
                for step in sorted(
                    question.action_steps,
                    key=lambda x: x.correct_order
                )
            ]
        }

    @router.post("/", status_code=201)
    def create_question(self, question: QuestionSchema):

        new_question = DBQuestion(
            question_text=question.question_text,
            question_type=question.question_type,
            image_path=question.image_path
        )

        self.db.add(new_question)
        self.db.commit()
        self.db.refresh(new_question)

        for step in question.action_steps:
            self.db.add(
                DBActionStep(
                    question_id=new_question.question_id,
                    text=step.text,
                    correct_order=step.correct_order
                )
            )

        self.db.commit()

        return new_question

    @router.get("/{question_id}")
    def get_question_by_id(self, question_id: int):
        question = self.db.query(DBQuestion).filter(
            DBQuestion.question_id == question_id
        ).first()

        if not question:
            raise HTTPException(
                status_code=404,
                detail="Frage nicht gefunden"
            )

        return question

    @router.delete("/{question_id}")
    def delete_question(self, question_id: int):
        question = self.db.query(DBQuestion).filter(
            DBQuestion.question_id == question_id
        ).first()

        if not question:
            raise HTTPException(
                status_code=404,
                detail="Frage nicht gefunden"
            )

        self.db.delete(question)
        self.db.commit()

        return {"message": "Frage gelöscht"}