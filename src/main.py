from datetime import datetime

from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, HTTPException

from src.pydantic_models import CronJob, OneTimeJob
from src.scheduler import perform_callback, scheduler

app = FastAPI()

scheduler.start()


@app.post("/jobs/one-time")
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


@app.post("/jobs/cron")
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


@app.delete("/jobs/{job_id}")
def remove_job(job_id: str):
    try:
        scheduler.remove_job(job_id)
        return {"message": "Job removed successfully"}
    except Exception as e:
        print(f"Error removing job {job_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error removing job: {job_id}")
