from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import DBLogging


class LoggingSchema(BaseModel):
    action: str
    user_id: int


router = APIRouter(
    prefix="/logs",
    tags=["Logging"]
)


@cbv(router)
class LoggingAPI:
    db: Session = Depends(get_db)

    # Alle Logging Einträge bekommen
    @router.get("/")
    def get_all_logs(self):
        return self.db.query(DBLogging).all()

    # Einen Log Eintrag erstellen
    @router.post("/")
    def create_log(self, log: LoggingSchema):
        new_log = DBLogging(
            action=log.action,
            timestamp=datetime.now(),
            user_id=log.user_id
        )

        self.db.add(new_log)
        self.db.commit()
        self.db.refresh(new_log)

        return new_log