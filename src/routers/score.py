from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from database import get_db
from models import DBScore


class ScoreSchema(BaseModel):
    points: int
    user_id: int


class ScoreAPI:
    def __init__(self):
        self.router = APIRouter(
            prefix="/scores",
            tags=["Scores"]
        )

        self.register_routes()

    def register_routes(self):
        self.router.add_api_route(
            "/", self.get_all_scores, methods=["GET"]
        )

        self.router.add_api_route(
            "/", self.create_score, methods=["POST"]
        )

    def get_all_scores(self, db: Session = Depends(get_db)):
        return db.query(DBScore).all()

    def create_score(
        self,
        score: ScoreSchema,
        db: Session = Depends(get_db)
    ):
        new_score = DBScore(
            points=score.points,
            user_id=score.user_id
        )

        db.add(new_score)
        db.commit()
        db.refresh(new_score)

        return new_score


score_api = ScoreAPI()
router = score_api.router