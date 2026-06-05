from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
# Wichtig: DBUser muss importiert werden, da du es im Leaderboard benutzt!
from models import DBScore, DBUser


class ScoreSchema(BaseModel):
    points: int
    user_id: int


# 1. Router zuerst definieren
router = APIRouter(prefix="/scores", tags=["Scores"])


# 2. Die Klasse mit dem @cbv Decorator versehen
@cbv(router)
class ScoreAPI:
    # Damit steht `self.db` in JEDER Methode automatisch zur Verfügung
    db: Session = Depends(get_db)

    @router.get("/")
    def get_all_scores(self):
        return self.db.query(DBScore).all()

    @router.post("/")
    def create_score(self, score: ScoreSchema):
        new_score = DBScore(points=score.points, user_id=score.user_id)

        self.db.add(new_score)
        self.db.commit()
        self.db.refresh(new_score)

        return new_score

    @router.get("/leaderboard", response_model=list[dict])
    def get_leaderboard(self):
        # Aggregiere die Punkte pro Benutzer und sortiere absteigend
        leaderboard = (
            self.db.query(
                DBUser.username, func.sum(DBScore.points).label("total_points")
            )
            .join(DBScore, DBUser.user_id == DBScore.user_id)
            .group_by(DBUser.user_id, DBUser.username)
            .order_by(func.sum(DBScore.points).desc())
            .all()
        )

        return [
            {"username": item.username, "total_points": item.total_points}
            for item in leaderboard
        ]