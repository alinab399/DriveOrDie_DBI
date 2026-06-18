from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import DBScore, DBUser


class ScoreSchema(BaseModel):
    points: int
    user_id: int


router = APIRouter(prefix="/scores", tags=["Scores"])


@cbv(router)
class ScoreAPI:
    db: Session = Depends(get_db)

    # Alle Punkte bekommen
    @router.get("/")
    def get_all_scores(self):
        return self.db.query(DBScore).all()

    # Einen Punktestand für einen User erstellen
    @router.post("/")
    def create_score(self, score: ScoreSchema):
        new_score = DBScore(points=score.points, user_id=score.user_id)

        self.db.add(new_score)
        self.db.commit()
        self.db.refresh(new_score)

        return new_score

    # Alle Daten für das Leaderboard bekommen
    @router.get("/leaderboard", response_model=list[dict])
    def get_leaderboard(self):
        leaderboard = (
            self.db.query(
                DBUser.user_id,
                DBUser.username,
                func.sum(DBScore.points).label("total_points")
            )
            .join(DBScore, DBUser.user_id == DBScore.user_id)
            .group_by(DBUser.user_id, DBUser.username)
            .order_by(func.sum(DBScore.points).desc())
            .limit(10)
            .all()
        )
        return [
            {"user_id": item.user_id, "username": item.username, "total_points": item.total_points, }
            for item in leaderboard
        ]