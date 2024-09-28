from fastapi import FastAPI

from src.routers import jobs
from src.scheduler import scheduler

app = FastAPI()

scheduler.start()

app.include_router(jobs.router)
