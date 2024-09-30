from datetime import datetime
from typing import List

from apscheduler.job import Job
from fastapi import APIRouter, HTTPException

from src.pydantic_models import JobCreate, ScheduledJob
from src.scheduler import perform_callback, scheduler

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", operation_id="create_job")
def create_job(job_create: JobCreate):
    job = scheduler.add_job(
        perform_callback,
        trigger=job_create.trigger.create_trigger(),
        args=[datetime.now(), job_create.request],
        id=job_create.id,
    )

    return {
        "message": "Job created successfully",
        "job_id": job.id,
        "next_run_time": job.next_run_time,
    }


@router.get("/{job_id}", response_model=ScheduledJob | None)
def get_job(job_id: str):
    job: Job | None = scheduler.get_job(job_id)
    if job:
        return ScheduledJob.parse_job(job)
    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")


@router.get("/", response_model=List[ScheduledJob], operation_id="get_all_jobs")
def get_all_jobs():
    jobs: List[Job] = scheduler.get_jobs()
    return [ScheduledJob.parse_job(job) for job in jobs]


@router.delete("/{job_id}")
def remove_job(job_id: str):
    try:
        scheduler.remove_job(job_id)
        return {"message": f"Job {job_id} removed successfully"}
    except Exception as e:
        print(f"Error removing job {job_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error removing job: {job_id}")
