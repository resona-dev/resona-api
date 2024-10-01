from sqlalchemy.orm import Session

from . import models, schemas


def get_completed_job(db: Session, job_id: str):
    job = db.query(models.CompletedJob).filter(models.CompletedJob.id == job_id).first()
    if job:
        return schemas.ScheduledJob.parse_db_job(job)


def get_completed_jobs(db: Session, skip: int = 0, limit: int = 100):
    jobs = (
        db.query(models.CompletedJob)
        .order_by(models.CompletedJob.completed_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [schemas.ScheduledJob.parse_db_job(job) for job in jobs]


def create_completed_job(db: Session, job: schemas.ScheduledJob):
    if not job.result:
        raise ValueError("Job result is required to create a completed job")
    db_job = models.CompletedJob(
        id=job.id,
        name=job.name,
        created_at=job.created_at,
        request=job.request.model_dump(),
        status=job.status.value,
        trigger=job.trigger.model_dump(),
        completed_at=job.result.completed_at,
        response=job.result.response.model_dump(),
        error_message=job.result.error_message,
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
