from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import get_db
from models import DBQuestion, DBAnswer
import random


class AnswerInQuestionSchema(BaseModel):
    answer_text: str
    is_correct: bool

class QuestionSchema(BaseModel):
    question_text: str
    question_type: str  # "THEORY" oder "CAR" / "SEQUENCE"
    image_path: str | None = None
    answers: list[AnswerInQuestionSchema] = []



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


        # KI anfang
        question = random.choice(questions)

        if question.question_type == "theorie":
            # Für Single Choice: Antworten mischen, damit nicht immer die richtige oben steht
            formatted_answers = [
                {
                    "answer_id": ans.answer_id,
                    "answer_text": ans.answer_text,
                    "is_correct": ans.is_correct
                }
                for ans in question.answers
            ]
            random.shuffle(formatted_answers)  # Importiert aus random

            return {
                "question_id": question.question_id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "image_path": question.image_path,
                "answers": formatted_answers
            }
        elif question.question_type == "praxis":
            # Für die Auto-Reihenfolge: Nach answer_id sortieren (Reihenfolge des Einfügens)
            sorted_steps = sorted(question.answers, key=lambda x: x.answer_id)

            return {
                "question_id": question.question_id,
                "question_text": question.question_text,
                "question_type": question.question_type,
                "image_path": question.image_path,
                "actions": [
                    {
                        "id": ans.answer_id,
                        "text": ans.answer_text,
                        "correctOrder": idx + 1  # 1, 2, 3... basierend auf der ID-Sortierung
                    }
                    for idx, ans in enumerate(sorted_steps)
                ]
            }
        # KI ende



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

        for ans in question.answers:
            self.db.add(
                DBAnswer(
                    question_id=new_question.question_id,
                    answer_text=ans.answer_text,
                    is_correct=ans.is_correct
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