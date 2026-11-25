from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime
from datetime import datetime, timezone
import json
from app.core.config import settings

engine=create_async_engine(settings.database_url)
Session=async_sessionmaker(engine,expire_on_commit=False)
class Base(DeclarativeBase): pass
class Analysis(Base):
    __tablename__='analyses'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    url: Mapped[str]=mapped_column(String(2048),index=True)
    resource_type: Mapped[str]=mapped_column(String(30))
    report_json: Mapped[str]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
class SearchEvent(Base):
    __tablename__="search_events"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    url: Mapped[str]=mapped_column(String(2048),index=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))

class AnalysisAttempt(Base):
    __tablename__='analysis_attempts'
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    day: Mapped[str]=mapped_column(String(10),index=True)

async def init_db():
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
