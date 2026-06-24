import uuid
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.utils.central_logging import setup_logger
from backend.depends import base_connection, get_base_servie
from backend.service.base_service import BaseService
from contextlib import asynccontextmanager
from backend.models import Employee, EmployeeUpdateAttributes, ShiftRequest
from backend.models.exceptions import UserNotFoundError, ShiftNotFoundError

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up... Creating tables!")
    async with base_connection.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield

    logger.info("Shutting down...")
    await base_connection.engine.dispose()


app = FastAPI(lifespan=lifespan)

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


@app.post("/login")
async def post_login(
    employee: Employee,
    # form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.pg_execution),
):
    access_token = await service.login(session, employee)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("employees", response_model=list[Employee])
async def get_users(
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.pg_execution),
):
    logger.info("reading all users")
    try:
        return await service.read_users(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("employee/{user_id}", response_model=Employee)
async def get_user(
    user_id: uuid.UUID,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.pg_execution),
):
    logger.info("reading user", extra={"user_id": str(user_id)})
    try:
        return await service.read_user(session, id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("employee")
async def post_user(
    user_request: Employee,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.pg_execution),
):
    logger.info("Receiving new user...")

    try:
        await service.create_user(session, user_request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "success", "message": "fuck off!"}


@app.patch("/employee/{employee_id}")
async def patch_user(
    employee_id: int,
    employee_to_update: EmployeeUpdateAttributes,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.pg_execution),
):
    logger.info("Receiving user update...", extra={"employee_id": employee_id})
    try:
        await service.update_user(session, employee_id, employee_to_update)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"successfully updated user X Y Z"}


####################################
# Employee shift#
####################################


@app.post("/shifts")
async def post_shift(
    shift_request: ShiftRequest,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.pg_execution),
):
    logger.info("Receiving new shift...")
    try:
        await service.create_shift(session, shift_request.shifts)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success", "message": "fuck off!"}


@app.get("/shifts")
async def get_shifts(
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.pg_execution),
):
    logger.info("Reading all shifts...")
    try:
        return await service.read_shifts(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/shifts/{shift_id}")
async def delete_shift(
    shift_id: uuid.UUID,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.pg_execution),
):
    logger.info("Deleting shift...", extra={"shift_id": str(shift_id)})
    try:
        await service.delete_shift(session, shift_id)
    except ShiftNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success", "message": "Shift deleted"}
