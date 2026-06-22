from sqlmodel.ext.asyncio.session import AsyncSession
from backend.repository.postgres_repo import BasePostgresRepo
from backend.models.database import Employee, EmployeeUpdateAttributes
from backend.models.exceptions import UserNotFoundError
from backend.utils.central_logging import setup_logger
from backend.utils.security import verify_password, create_access_token
from typing import Any
from fastapi import HTTPException, status

class BaseService():
    def __init__(self, postgres_repo: BasePostgresRepo):
        self.repo = postgres_repo
        self.logger = setup_logger(self.__class__.__name__)

    async def read_user(self, session: AsyncSession, **kwargs: Any) -> Employee:
        employee = await self.repo.find_user(session, **kwargs)
        if not employee:
            raise UserNotFoundError(f"Employee with this setting does not exist.")
        else:
            return employee

    async def read_users(self, session: AsyncSession) -> list[Employee]:
        self.logger.info("reading users data")
        employees = await self.repo.select_all_users(session)
        return employees

    async def login(self, session: AsyncSession, employee_request: Employee):
        try:
            employee_db = await self.read_user(session, email=employee_request.email)
            if not verify_password(employee_request.hashed_password, employee_db.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token = create_access_token(data={"sub": str(employee_db.id)})
            return access_token
        except UserNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def create_user(self, session: AsyncSession, employee: Employee) -> None:
        try:
            await self.read_user(session, email=employee.email)
        except UserNotFoundError as e:
            await self.repo.insert_user(session, employee)

    async def update_user(self, session: AsyncSession, employee_id: int, employee_attribute_update: EmployeeUpdateAttributes) -> None:
        employee = await self.read_user(session, id=employee_id)
        update_data: dict[str, Any] = employee_attribute_update.model_dump(exclude_unset=True)
        await self.repo.update_user(session, employee, update_data)