from fastapi_restful.cbv import cbv
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models import DBQuestion, DBAnswer, DBActionStep

from database import get_db
from models import DBQuestion, DBAnswer
import random


class AnswerInQuestionSchema(BaseModel):
    answer_text: str
    is_correct: bool

class ActionStepSchema(BaseModel):
    text: str
    correct_order: int

class QuestionSchema(BaseModel):
    question_text: str
    question_type: str
    image_path: str | None = None

    answers: list[AnswerInQuestionSchema] = []
    action_steps: list[ActionStepSchema] = []



router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)


@cbv(router)
class QuestionAPI:
    db: Session = Depends(get_db)

    # Alle Fragen (Theorie & Praxis) werden zurückgegeben
    @router.get("/")
    def get_all_questions(self):
        return self.db.query(DBQuestion).all()

    # Eine zufällige Frage bekommen
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

        response_data = {
            "question_id": question.question_id,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "image_path": question.image_path,
            "answers": [],
            "actions": []
        }

        # Wenn es eine Theoriefrage ist, packen wir die Antworten dazu
        if question.question_type == "theorie":
            response_data["answers"] = [
                {
                    "answer_id": ans.answer_id,
                    "answer_text": ans.answer_text,
                    "is_correct": ans.is_correct
                } for ans in question.answers
            ]
        elif question.question_type == "praxis":


            # Für die Auto-Reihenfolge: Nach answer_id sortieren (Reihenfolge des Einfügens)
            sorted_steps = sorted(question.action_steps, key=lambda x: x.correct_order)

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
                    for step in sorted_steps
                ]
            }
        return response_data

        # KI ende


    # Eine Frage mit Antwortmöglichkeiten erstellen
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

    # Eine bestimmte Frage bekommen
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

    # Eine bestimmte Frage löschen
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