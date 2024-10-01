from sqlalchemy import Column, DateTime, PickleType, String, Unicode, UnicodeText
from src.database import Base


class CompletedJob(Base):
    __tablename__ = "completed_jobs"

    id = Column(Unicode(191), primary_key=True)
    completed_at = Column(DateTime, nullable=False, primary_key=True)
    name = Column(UnicodeText)
    created_at = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    error_message = Column(String)
    trigger = Column(PickleType, nullable=False)
    request = Column(PickleType, nullable=False)
    response = Column(PickleType, nullable=False)
