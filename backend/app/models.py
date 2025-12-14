from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # student, proctor, admin
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ExamSession", back_populates="student")

class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    duration_minutes = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    sessions = relationship("ExamSession", back_populates="exam")

class ExamSession(Base):
    __tablename__ = "exam_sessions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    status = Column(String)  # in_progress, completed, terminated

    exam = relationship("Exam", back_populates="sessions")
    student = relationship("User", back_populates="sessions")
    report = relationship("ExamReport", uselist=False, back_populates="session")

class ExamReport(Base):
    __tablename__ = "exam_reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"))
    overall_risk_score = Column(Float)
    details = Column(JSON)
    generated_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ExamSession", back_populates="report")
