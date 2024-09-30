from datetime import datetime
from typing import List

from apscheduler.job import Job
from apscheduler.triggers.cron import CronTrigger
from fastapi import APIRouter, HTTPException
from src.pydantic_models import CronJob, JobStatus, OneTimeJob, ScheduledJob
from src.scheduler import perform_callback, scheduler

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/one-time", operation_id="create_one_time_job")
def create_one_time_job(one_time_job: OneTimeJob):
    run_date = one_time_job.run_date()

    job = scheduler.add_job(
        perform_callback,
        "date",
        run_date=run_date,
        args=[datetime.now(), one_time_job.request],
        id=one_time_job.id,
    )

    return {
        "message": "API call scheduled successfully",
        "run_date": run_date,
        "id": job.id,
    }


@router.post("/cron")
def create_cron_job(cron_job: CronJob):
    cron_trigger = CronTrigger.from_crontab(cron_job.cron)

    job = scheduler.add_job(
        perform_callback,
        trigger=cron_trigger,
        args=[datetime.now(), cron_job.request],
        id=cron_job.id,
    )

    return {
        "message": "Cron job created successfully",
        "cron expression": cron_job.cron,
        "id": job.id,
    }


def get_next_run_time(job: Job) -> datetime | None:
    return getattr(job, "next_run_time", None)


def get_job_status(job: Job) -> JobStatus:
    if hasattr(job, "next_run_time"):
        return JobStatus.ACTIVE if job.next_run_time else JobStatus.PAUSED
    return JobStatus.PENDING


@router.get("/{job_id}", response_model=ScheduledJob | None)
def get_job(job_id: str):
    job: Job | None = scheduler.get_job(job_id)
    if job:
        return ScheduledJob(
            id=job.id,
            request=job.args[1],
            next_run_time=get_next_run_time(job),
            status=get_job_status(job),
        )
    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")


@router.get("/", response_model=List[ScheduledJob], operation_id="get_all_jobs")
def get_all_jobs():
    jobs: List[Job] = scheduler.get_jobs()
    return [
        ScheduledJob(
            id=job.id,
            request=job.args[1],
            next_run_time=get_next_run_time(job),
            status=get_job_status(job),
        )
        for job in jobs
    ]


@router.delete("/{job_id}")
def remove_job(job_id: str):
    try:
        scheduler.remove_job(job_id)
        return {"message": f"Job {job_id} removed successfully"}
    except Exception as e:
        print(f"Error removing job {job_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error removing job: {job_id}")
