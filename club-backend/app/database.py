"""
Подключение к базе данных и определение моделей (SQLAlchemy + PostgreSQL).
"""

import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, JSON
)
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/club_db"
)

# Railway/Render иногда отдают postgres:// — SQLAlchemy 2.x требует postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Lecture(Base):
    """Одна запись в словаре материалов клуба."""
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)   # lesson15
    title = Column(String(300), nullable=False)
    description = Column(Text, default="")
    link = Column(String(500), default="")                                # ссылка в Telegram
    type = Column(String(20), default="lecture")                          # lecture|training|qa|other
    tags = Column(JSON, default=list)                                     # ["возражения","скрипты"]
    topics = Column(JSON, default=list)                                   # ["Тема 1","Тема 2"]
    timecodes = Column(JSON, default=list)                                # [{"time":"0:00","label":"..."}]
    duration_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Создаёт таблицы, если их ещё нет."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency для FastAPI — выдаёт сессию и закрывает её после запроса."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
