from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import get_db
from models import DBUser


class UserSchema(BaseModel):
    username: str
    password: str


class LoginSchema(BaseModel):
    username: str
    password: str


class UserAPI:
    def __init__(self):
        self.router = APIRouter(
            prefix="/users",
            tags=["Users"]
        )

        self.register_routes()

    def register_routes(self):
        self.router.add_api_route(
            "/", self.get_all_users, methods=["GET"]
        )

        self.router.add_api_route(
            "/", self.create_user, methods=["POST"]
        )

        self.router.add_api_route(
            "/{user_id}", self.get_user, methods=["GET"]
        )

        self.router.add_api_route(
            "/{user_id}", self.delete_user, methods=["DELETE"]
        )

        self.router.add_api_route(
            "/login", self.login_user, methods=["POST"]
        )

    def get_all_users(self, db: Session = Depends(get_db)):
        return db.query(DBUser).all()

    def create_user(
        self,
        user: UserSchema,
        db: Session = Depends(get_db)
    ):
        new_user = DBUser(
            username=user.username,
            password=user.password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    def get_user(
        self,
        user_id: int,
        db: Session = Depends(get_db)
    ):
        user = db.query(DBUser).filter(
            DBUser.user_id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User nicht gefunden"
            )

        return user

    def delete_user(
        self,
        user_id: int,
        db: Session = Depends(get_db)
    ):
        user = db.query(DBUser).filter(
            DBUser.user_id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User nicht gefunden"
            )

        db.delete(user)
        db.commit()

        return {"message": "User gelöscht"}

    def login_user(
        self,
        login: LoginSchema,
        db: Session = Depends(get_db)
    ):

        user = db.query(DBUser).filter(
            DBUser.username == login.username,
            DBUser.password == login.password
        ).first()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Benutzername oder Passwort falsch"
            )

        return {
            "message": "Login erfolgreich",
            "user_id": user.user_id,
            "username": user.username
        }


user_api = UserAPI()
router = user_api.router