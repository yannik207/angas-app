import uuid
from typing import List
from fastapi import HTTPException, Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.utils.central_logging import setup_logger
from backend.depends import base_connection, get_base_servie
from backend.service.base_service import BaseService
from backend.models import Employee, EmployeeAvailability, ShiftRequest, ShiftSummary, ShiftUpdateAttributes
from backend.models.exceptions import ShiftNotFoundError

logger = setup_logger(__name__)

shift_router = APIRouter(tags=["shift"])


@shift_router.post("/login")
async def post_login(
    employee: Employee,
    # form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
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
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info("Receiving new shift...")
    try:
        await service.create_shift(session, shift_request.shifts)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success", "message": "fuck off!"}


@shift_router.get("/shifts", response_model=List[ShiftSummary])
async def get_shifts(
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info("Reading all shifts...")
    try:
        return await service.read_shifts(session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@shift_router.get("/shifts/{shift_id}")
async def get_shift_details(
    shift_id: uuid.UUID,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info("Reading shift details...", extra={"shift_id": str(shift_id)})
    try:
        return await service.read_shift_details(session, shift_id)
    except ShiftNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@shift_router.get(
    "/shifts/{shift_id}/employees/availability",
    response_model=List[EmployeeAvailability],
)
async def get_shift_employee_availability(
    shift_id: uuid.UUID,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info(
        "Reading employee availability for shift...", extra={"shift_id": str(shift_id)}
    )
    try:
        return await service.read_shift_employee_availability(session, shift_id)
    except ShiftNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@shift_router.delete("/shifts/{shift_id}")
async def delete_shift(
    shift_id: uuid.UUID,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info("Deleting shift...", extra={"shift_id": str(shift_id)})
    try:
        await service.delete_shift(session, shift_id)
    except ShiftNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success", "message": "Shift deleted"}


@shift_router.patch("/shifts/{shift_id}")
async def patch_shift(
    shift_id: uuid.UUID,
    shift_to_update: ShiftUpdateAttributes,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info("Receiving shift update...", extra={"shift_id": str(shift_id)})
    try:
        await service.update_shift(session, shift_id, shift_to_update)
    except ShiftNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success", "message": "Shift updated"}


@shift_router.post("/shifts/{shift_id}/employees/{employee_id}")
async def assign_employee_to_shift(
    shift_id: uuid.UUID,
    employee_id: uuid.UUID,
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.get_session),
):
    logger.info(
        "Assigning employee to shift...",
        extra={"shift_id": str(shift_id), "employee_id": str(employee_id)},
    )
    try:
        await service.assign_employee_to_shift(session, shift_id, employee_id)
    except ShiftNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
