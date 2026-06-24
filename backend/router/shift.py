import uuid
from fastapi import HTTPException, Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.utils.central_logging import setup_logger
from backend.depends import base_connection, get_base_servie
from backend.service.base_service import BaseService
from backend.models import Employee, ShiftRequest
from backend.models.exceptions import ShiftNotFoundError

logger = setup_logger(__name__)

shift_router = APIRouter(tags=["shift"])


@shift_router.post("/login")
async def post_login(
    employee: Employee,
    # form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.pg_execution),
):
    access_token = await service.login(session, employee)
    return {"access_token": access_token, "token_type": "bearer"}


####################################
# Employee shift#
####################################


@shift_router.post("/shifts")
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


@shift_router.get("/shifts")
async def get_shifts(
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.pg_execution),
):
    logger.info("Reading all shifts...")
    try:
        return await service.read_shifts(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@shift_router.delete("/shifts/{shift_id}")
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
