from datetime import datetime

import requests
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from src import database
from src.pydantic_models import APIRequest

scheduler = BackgroundScheduler(
    jobstores={"default": SQLAlchemyJobStore(engine=database.engine, tablename="jobs")},
)


def perform_callback(registered_at: datetime, request: APIRequest):
    try:
        # TODO: Make async and retryable
        # TODO: Use logging instead of print
        response = requests.request(
            request.method, request.url, headers=request.headers, json=request.body
        )
        print(response.json())
        print(f"API called successfully, status: {response.status_code}")
    except Exception as e:
        print(f"Error while calling API: {str(e)}")