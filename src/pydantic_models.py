from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Optional, Self
from urllib.parse import urlparse

from apscheduler.job import Job
from apscheduler.triggers.cron import BaseTrigger, CronTrigger
from apscheduler.triggers.date import DateTrigger
from pydantic import BaseModel, Field, field_validator, model_validator


class APIRequest(BaseModel):
    url: str = Field(examples=["http://127.0.0.1:8000"])
    method: str = "POST"
    headers: Dict[str, str] = {}
    body: Any = Field(default=None, examples=[{}])

    @field_validator("url")
    @classmethod
    def validate_url(cls, url: str):
        result = urlparse(url)
        if result.scheme in ["http", "https"] and result.netloc:
            return url
        raise ValueError(f"Invalid URL: {url}")


class JobStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"


class TriggerType(Enum):
    ONE_TIME = "one-time"
    CRON = "cron"


class Trigger(BaseModel):
    type: TriggerType
    fields: Any = Field(examples=[{}])


def get_next_run_time(job: Job) -> datetime | None:
    return getattr(job, "next_run_time", None)


def get_job_status(job: Job) -> JobStatus:
    if hasattr(job, "next_run_time"):
        return JobStatus.ACTIVE if job.next_run_time else JobStatus.PAUSED
    return JobStatus.PENDING


class ScheduledJob(BaseModel):
    id: str
    next_run_time: datetime | None
    status: JobStatus
    trigger: Trigger
    request: APIRequest

    @classmethod
    def parse_job(cls, job: Job) -> "ScheduledJob":
        return ScheduledJob(
            id=job.id,
            request=job.args[1],
            next_run_time=get_next_run_time(job),
            status=get_job_status(job),
            trigger=Trigger(
                type=(
                    TriggerType.ONE_TIME
                    if job.trigger is DateTrigger
                    else TriggerType.CRON
                ),
                fields={f.name: str(f) for f in job.trigger.fields if not f.is_default},
            ),
        )


class OneTimeTriggerCreate(BaseModel):
    delay: Optional[int] = None
    date: Optional[datetime] = None

    @model_validator(mode="after")
    def check_delay_or_date_provided(self) -> Self:
        if self.delay is None and self.date is None:
            raise ValueError("Either delay or date must be provided")
        return self

    def run_date(self):
        if self.delay:
            return datetime.now() + timedelta(seconds=self.delay)
        if self.date:
            return self.date
        raise Exception("Either delay or date must be provided")

    def create_trigger(self) -> BaseTrigger:
        return DateTrigger(run_date=self.run_date())


class CronTriggerCreate(BaseModel):
    cron: str = Field(examples=["* * * * *"])

    @field_validator("cron")
    @classmethod
    def validate_cron(cls, cron: str):
        if len(cron.split()) == 5:
            return cron
        raise ValueError(
            "Invalid cron expression. You can check https://crontab.guru/ for help"
        )

    def create_trigger(self) -> BaseTrigger:
        return CronTrigger.from_crontab(self.cron)


class JobCreate(BaseModel):
    id: Optional[str] = Field(default=None, examples=[None])
    request: APIRequest
    trigger: OneTimeTriggerCreate | CronTriggerCreate
