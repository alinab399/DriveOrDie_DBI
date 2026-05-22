from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import DBLogging


class LoggingSchema(BaseModel):
    action: str
    user_id: int


class LoggingAPI:
    def __init__(self):
        self.router = APIRouter(
            prefix="/logs",
            tags=["Logging"]
        )

        self.register_routes()

    def register_routes(self):
        self.router.add_api_route(
            "/", self.get_all_logs, methods=["GET"]
        )

        self.router.add_api_route(
            "/", self.create_log, methods=["POST"]
        )

    def get_all_logs(self, db: Session = Depends(get_db)):
        return db.query(DBLogging).all()

    def create_log(
        self,
        log: LoggingSchema,
        db: Session = Depends(get_db)
    ):
        new_log = DBLogging(
            action=log.action,
            timestamp=datetime.now(),
            user_id=log.user_id
        )

        db.add(new_log)
        db.commit()
        db.refresh(new_log)

        return new_log


logging_api = LoggingAPI()
router = logging_api.router