import uuid
from fastapi import HTTPException, Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.utils.central_logging import setup_logger
from backend.depends import base_connection, get_base_servie
from backend.service.base_service import BaseService
from backend.models import (
    Employee,
    EmployeePublic,
    EmployeeRequest,
    EmployeeUpdateAttributes,
    EmployeeTypeRequest,
    EmployeeType,
)
from backend.models.exceptions import (
    EmployeeNotFoundError,
    EmployeeTypeAlreadyExistsError,
)
from typing import List

logger = setup_logger(__name__)

employee_router = APIRouter(tags=["employee"])


@employee_router.post("/employee/type")
async def post_employee_type(
    employee_type_request: EmployeeTypeRequest,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info("Receiving employee type creation...")
    try:
        await service.create_employee_type(session, employee_type_request)
    except EmployeeTypeAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success", "message": "Employee type created"}


@employee_router.get("/employees", response_model=List[EmployeePublic])
async def get_employees(
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info("Reading all employees...")
    try:
        return await service.read_users(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@employee_router.get("/employee/types", response_model=List[EmployeeType])
async def get_employee_types(
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info("Receiving employee types...")
    try:
        return await service.read_employee_types(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@employee_router.get("/employee/{user_id}", response_model=Employee)
async def get_user(
    user_id: uuid.UUID,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info("reading user", extra={"user_id": str(user_id)})
    try:
        return await service.read_user(session, id=user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@employee_router.post("/employee")
async def post_user(
    user_request: EmployeeRequest,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info("Receiving new user...")

    try:
        await service.create_user(session, user_request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "success", "message": "Employee created"}


@employee_router.patch("/employee/{employee_id}")
async def patch_user(
    employee_id: int,
    employee_to_update: EmployeeUpdateAttributes,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info("Receiving user update...", extra={"employee_id": employee_id})
    try:
        await service.update_user(session, employee_id, employee_to_update)
    except EmployeeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"successfully updated user X Y Z"}
