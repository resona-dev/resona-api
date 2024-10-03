from datetime import datetime
from sqlalchemy import (
    Column,
    PickleType,
    String,
    TypeDecorator,
    Unicode,
    UnicodeText,
)
from src.database import Base


class TimestampTZ(TypeDecorator):
    impl = String

    cache_ok = True

    def process_bind_param(self, value: datetime, dialect):
        return value.isoformat()

    def process_result_value(self, value: str, dialect):
        return datetime.fromisoformat(value)


class CompletedJob(Base):
    __tablename__ = "completed_jobs"

    id = Column(Unicode(191), primary_key=True)
    completed_at = Column(TimestampTZ, nullable=False, primary_key=True)
    name = Column(UnicodeText)
    created_at = Column(TimestampTZ, nullable=False)
    status = Column(String, nullable=False)
    error_message = Column(String)
    trigger = Column(PickleType, nullable=False)
    request = Column(PickleType, nullable=False)
    response = Column(PickleType, nullable=False)
