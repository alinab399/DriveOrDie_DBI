from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi_restful.cbv import cbv

from database import get_db
from models import DBScore, DBUser


class ScoreSchema(BaseModel):
    points: int
    user_id: int


router = APIRouter(
    prefix="/scores",
    tags=["Scores"]
)


@cbv(router)
class ScoreAPI:
    db: Session = Depends(get_db)

    @router.get("/")
    def get_all_scores(self):
        return self.db.query(DBScore).all()

    @router.post("/")
    def create_score(self, score: ScoreSchema):
        new_score = DBScore(
            points=score.points,
            user_id=score.user_id
        )

        self.db.add(new_score)
        self.db.commit()
        self.db.refresh(new_score)

        return new_score

    @router.get("/leaderboard")
    def get_leaderboard(self):
        result = (
            self.db.query(
                DBUser.username.label("username"),
                func.sum(DBScore.points).label("totalPoints")
            )
            .join(
                DBScore,
                DBUser.user_id == DBScore.user_id
            )
            .group_by(DBUser.user_id)
            .order_by(
                func.sum(DBScore.points).desc()
            )
            .all()
        )

        return [
            {
                "username": row.username,
                "totalPoints": row.totalPoints
            }
            for row in result
        ]