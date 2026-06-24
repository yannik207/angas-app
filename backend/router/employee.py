import uuid
from fastapi import HTTPException, Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.utils.central_logging import setup_logger
from backend.depends import base_connection, get_base_servie
from backend.service.base_service import BaseService
from backend.models import Employee, EmployeeUpdateAttributes
from backend.models.exceptions import UserNotFoundError

logger = setup_logger(__name__)

employee_router = APIRouter(tags=["employee"])


@employee_router.get("employee/{user_id}", response_model=Employee)
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


@employee_router.post("employee")
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


@employee_router.patch("/employee/{employee_id}")
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
