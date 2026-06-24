from fastapi import Depends, APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.utils.central_logging import setup_logger
from backend.depends import base_connection, get_base_servie
from backend.service.base_service import BaseService
from backend.models import Employee
from fastapi import Request

logger = setup_logger(__name__)

central_router = APIRouter(tags=["central"])


@central_router.middleware("http")
async def middleware_logger(request: Request, call_next):
    logger.info(
        "which type of request is this",
        extra={"request_type": request.method, "request_body": request.body},
    )
    response = await call_next(request)
    return response


@central_router.post("/login")
async def post_login(
    employee: Employee,
    # form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: BaseService = Depends(get_base_servie),
    session: AsyncSession = Depends(base_connection.pg_execution),
):
    access_token = await service.login(session, employee)
    return {"access_token": access_token, "token_type": "bearer"}
