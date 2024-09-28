from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Self
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, model_validator


class APIRequest(BaseModel):
    url: str = Field(examples=["http://127.0.0.1:8000"])
    method: str = "POST"
    headers: Dict[str, str] = {}
    body: Any = Field(examples=[{}])

    @field_validator("url")
    @classmethod
    def validate_url(cls, url: str):
        result = urlparse(url)
        if result.scheme in ["http", "https"] and result.netloc:
            return url
        raise ValueError(f"Invalid URL: {url}")


class Callback(BaseModel):
    id: Optional[str] = Field(examples=[None])
    request: APIRequest


class OneTimeJob(Callback):
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


class CronJob(Callback):
    cron: str = Field(examples=["* * * * *"])

    @field_validator("cron")
    @classmethod
    def validate_cron(cls, cron: str):
        if len(cron.split()) == 5:
            return cron
        raise ValueError(
            "Invalid cron expression. You can check https://crontab.guru/ for help"
        )
