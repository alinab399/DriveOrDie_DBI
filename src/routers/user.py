from fastapi import APIRouter, Depends, HTTPException
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session
import bcrypt
from database import get_db
from models import DBUser, DBScore


class UserSchema(BaseModel):
    user_id: int | None = None
    username: str
    password: str
    is_admin: bool | None = False


class LoginSchema(BaseModel):
    username: str
    password: str


class PointsSchema(BaseModel):
    points: int


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@cbv(router)
class UserAPI:
    db: Session = Depends(get_db)

    # Admin bekommt alle User mit Score schon im richtigen Format
    @router.get("/all")
    def get_all_users_admin(self):

        result = (
            self.db.query(
                DBUser.user_id,
                DBUser.username,
                DBUser.is_admin,
                func.coalesce(
                    func.sum(DBScore.points),
                    0
                ).label("score")
            )
            .outerjoin(
                DBScore,
                DBUser.user_id == DBScore.user_id
            )
            .group_by(
                DBUser.user_id,
                DBUser.username,
                DBUser.is_admin
            )
            .all()
        )

        return [
            {
                "user_id": row.user_id,
                "username": row.username,
                "password": "",
                "is_admin": row.is_admin,
                "score": row.score
            }
            for row in result
        ]

    # Alle User werden zurückgegeben
    @router.get("/", response_model=list[UserSchema])
    def get_all_users(self):
        return self.db.query(DBUser).all()

    # Einen User erstellen (Registrieren)
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

        hashed_password = bcrypt.hashpw(
            user.password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        new_user = DBUser(
            username=user.username,
            password=hashed_password,
            is_admin=user.is_admin
        )


        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        return new_user

    # Einen User per ID bekommen
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

    # Einen User löschen
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

        self.db.query(DBScore).filter(
            DBScore.user_id == user_id
        ).delete()

        self.db.delete(user)
        self.db.commit()

        return {
            "message": "User gelöscht"
        }

    # Den Punktestand eines Users aktualisieren
    @router.put("/{user_id}/points")
    def update_points(
        self,
        user_id: int,
        data: PointsSchema
    ):
        user = self.db.query(DBUser).filter(
            DBUser.user_id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User nicht gefunden"
            )

        self.db.query(DBScore).filter(
            DBScore.user_id == user_id
        ).delete()

        new_score = DBScore(
            points=data.points,
            user_id=user_id
        )

        self.db.add(new_score)
        self.db.commit()

        return {
            "message": "Punkte geändert"
        }

    # Einen User einloggen und auf Fehler prüfen
    @router.post("/login")
    def login_user(self, login: LoginSchema):

        user = self.db.query(DBUser).filter(
            DBUser.username == login.username
        ).first()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Benutzername oder Passwort falsch"
            )



        if not bcrypt.checkpw(
                login.password.encode("utf-8"),
                user.password.encode("utf-8")
        ):
            raise HTTPException(
                status_code=401,
                detail="Benutzername oder Passwort falsch"
            )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Benutzername oder Passwort falsch"
            )

        return {
            "message": "Login erfolgreich",
            "user_id": user.user_id,
            "username": user.username,
            "is_admin": user.is_admin
        }