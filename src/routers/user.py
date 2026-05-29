from typing import List

from fastapi_restful.cbv import cbv
from sqlalchemy import Null
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

router = APIRouter(
            prefix="/users",
            tags=["Users"])

@cbv(router)
class UserAPI:
    db: Session = Depends(get_db)

    @router.get("/", response_model=list[UserSchema])
    def get_all_users(self):
        return self.db.query(DBUser).all()

    @router.post("/", response_model=UserSchema, status_code=201)
    def create_user(self, user: UserSchema):
        existing_user = self.db.query(DBUser).filter(
            DBUser.username == user.username
        ).first()

        if existing_user is not None:
            raise HTTPException(
                status_code=409,
                detail="User existiert schon"
            )
        new_user = DBUser(
            username=user.username,
            password=user.password
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user

    @router.get("/{user_id}", response_model=UserSchema)
    def get_user_by_id(self, user_id: int):
        user = self.db.query(DBUser).filter(
            DBUser.user_id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User nicht gefunden"
            )

        return user

    @router.delete("/{user_id}")
    def delete_user(self, user_id: int):
        user = self.db.query(DBUser).filter(
            DBUser.user_id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User nicht gefunden"
            )

        self.db.delete(user)
        self.db.commit()

        return {"message": "User gelöscht"}

    @router.post("/login")
    def login_user(self, login: LoginSchema):

        user = self.db.query(DBUser).filter(
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


