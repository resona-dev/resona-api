from datetime import datetime

import pytz
import requests
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from src.crud import create_completed_job
from src.database import SessionLocal, engine
from src.schemas import APIResponse, JobResult, JobStatus, ScheduledJob

scheduler = BackgroundScheduler(
    jobstores={"default": SQLAlchemyJobStore(engine=engine, tablename="jobs")},
)


def run_job(job_info: ScheduledJob):
    status = JobStatus.COMPLETED_REQUEST_ERROR
    error_message = None
    api_response = APIResponse(status_code=500)
    try:
        # TODO: Make async and retryable
        # TODO: Use logging instead of print
        request = job_info.request
        response = requests.request(
            request.method, request.url, headers=request.headers, json=request.body
        )

        api_response = APIResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.json(),
        )

        if response.ok:
            status = JobStatus.COMPLETED_SUCCESSFUL
        else:
            status = JobStatus.COMPLETED_RESPONSE_ERROR
    except Exception as e:
        error_message = str(e)

    job_info.status = status
    job_info.result = JobResult(
        completed_at=datetime.now(pytz.utc),
        error_message=error_message,
        response=api_response,
    )

    try:
        db = SessionLocal()
        create_completed_job(db, job_info)
        db.close()
    except Exception as e:
        print(f"Failed to create completed job: {str(e)}")
