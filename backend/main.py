from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from backend.utils.central_logging import setup_logger
from backend.depends import base_connection
from contextlib import asynccontextmanager
from backend.router.shift import shift_router
from backend.router.employee import employee_router
from backend.router.central import central_router

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up... Creating tables!")
    async with base_connection.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield

    logger.info("Shutting down...")
    await base_connection.engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title="Shift Scheduler API",
    description="API for the Shift Scheduler application",
    version="0.1.0",
)

app.include_router(shift_router)
app.include_router(employee_router)
app.include_router(central_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def middleware_logger(request: Request, call_next):
    logger.info(
        "which type of request is this",
        extra={"request_type": request.method, "request_body": request.body},
    )
    response = await call_next(request)
    return response
