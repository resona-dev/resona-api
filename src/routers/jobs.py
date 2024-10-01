from datetime import datetime
from typing import List

from apscheduler.job import Job
from fastapi import APIRouter, HTTPException, status

from src.pydantic_models import JobCreate, ScheduledJob
from src.scheduler import perform_callback, scheduler

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post(
    "",
    operation_id="create_job",
    response_model=ScheduledJob,
    status_code=status.HTTP_201_CREATED,
)
def create_job(job_create: JobCreate):
    if job_create.id and scheduler.get_job(job_create.id):
        raise HTTPException(
            status_code=409, detail=f"Job with id {job_create.id} already exists"
        )

    job_id = job_create.id or uuid4().hex
    trigger = job_create.trigger.create_trigger()
    job_info = ScheduledJob(
        id=job_id,
        name=job_create.name,
        created_at=datetime.now(pytz.utc),
        request=job_create.request,
        status=JobStatus.ACTIVE,
        trigger=parse_trigger(trigger),
    )

    job = scheduler.add_job(
        run_job,
        kwargs={"job_info": job_info},
        id=job_id,
        name=job_create.name,
        trigger=trigger,
    )

    return ScheduledJob.parse_job(job)


@router.get("/{job_id}", response_model=ScheduledJob, operation_id="get_job")
def get_job(job_id: str):
    job = scheduler.get_job(job_id)
    if job:
        return ScheduledJob.parse_job(job)
    raise HTTPException(status_code=404, detail=f"Job {job_id} not found")


@router.get("", response_model=List[ScheduledJob], operation_id="get_all_jobs")
def get_all_jobs():
    jobs: List[Job] = scheduler.get_jobs()
    return [ScheduledJob.parse_job(job) for job in jobs]


@router.delete(
    "/{job_id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="remove_job"
)
def remove_job(job_id: str):
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    job.remove()


@router.post("/{job_id}/pause", response_model=ScheduledJob, operation_id="pause_job")
def pause_job(job_id: str):
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    job.pause()
    modified_job = scheduler.get_job(job_id)
    if not modified_job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return ScheduledJob.parse_job(modified_job)


@router.post("/{job_id}/resume", response_model=ScheduledJob, operation_id="resume_job")
def resume_job(job_id: str):
    job = scheduler.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    job.resume()
    modified_job = scheduler.get_job(job_id)
    if not modified_job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return ScheduledJob.parse_job(modified_job)
