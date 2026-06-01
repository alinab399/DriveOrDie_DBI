from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class DBUser(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(VARCHAR(50), nullable=False, unique=True)
    password = Column(VARCHAR(15), nullable=False)
    is_admin = Column(Boolean, default=False)

    scores = relationship("DBScore", back_populates="user")
    logs = relationship("DBLogging", back_populates="user")
    user_questions = relationship("DBUserQuestion", back_populates="user")


class DBScore(Base):
    __tablename__ = "score"

    score_id = Column(Integer, primary_key=True, index=True)
    points = Column(Integer, nullable=False)

    user_id = Column(Integer, ForeignKey("user.user_id"))

    user = relationship("DBUser", back_populates="scores")


class DBLogging(Base):
    __tablename__ = "logging"

    log_id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    user_id = Column(Integer, ForeignKey("user.user_id"))

    user = relationship("DBUser", back_populates="logs")


class DBQuestion(Base):
    __tablename__ = "question"

    question_id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    question_type = Column(String, nullable=False)
    image_path = Column(String, nullable=True)

    answers = relationship("DBAnswer", back_populates="question")
    user_questions = relationship("DBUserQuestion", back_populates="question")
    action_steps = relationship("DBActionStep", back_populates="question", cascade="all, delete-orphan")

class DBActionStep(Base):
    __tablename__ = "action_steps"

    actionstep_id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer,ForeignKey("question.question_id"))
    text = Column(String)
    correct_order = Column(Integer)

    question = relationship("DBQuestion", back_populates="action_steps")


class DBAnswer(Base):
    __tablename__ = "answer"

    answer_id = Column(Integer, primary_key=True, index=True)
    answer_text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)

    question_id = Column(Integer, ForeignKey("question.question_id"))

    question = relationship("DBQuestion", back_populates="answers")


class DBUserQuestion(Base):
    __tablename__ = "user_question"

    uq_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("user.user_id"))
    question_id = Column(Integer, ForeignKey("question.question_id"))

    user = relationship("DBUser", back_populates="user_questions")
    question = relationship("DBQuestion", back_populates="user_questions")