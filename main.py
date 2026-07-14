import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_tables
from fastapi.middleware.cors import CORSMiddleware
from services.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    create_tables()
    yield


app = FastAPI(
    title="Thumbnail Generation API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)