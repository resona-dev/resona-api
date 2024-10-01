from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.database import engine
from src.models import Base
from src.routers import jobs
from src.scheduler import scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI()

scheduler.start()


app.include_router(jobs.router)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
