import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.repository.postgres_repo import BasePostgresRepo
from backend.models import (
    Employee,
    EmployeeAvailability,
    EmployeeRequest,
    EmployeeUpdateAttributes,
    EmployeeType,
    EmployeeTypeRequest,
    ShiftBase,
    ShiftSummary,
    ShiftUpdateAttributes,
    ShiftEmployeeDetails,
)
from backend.models.exceptions import (
    EmployeeNotFoundError,
    ShiftNotFoundError,
    ShiftAlreadyAssignedErrorToEmployee,
)
from backend.utils.central_logging import setup_logger
from backend.utils.security import verify_password, create_access_token
from typing import Any, List
from fastapi import HTTPException, status


class BaseService:
    def __init__(self, postgres_repo: BasePostgresRepo):
        self.repo = postgres_repo
        self.logger = setup_logger(self.__class__.__name__)

    async def login(self, session: AsyncSession, employee_request: Employee):
        try:
            employee_db = await self.read_user(session, email=employee_request.email)
            if not verify_password(
                employee_request.hashed_password, employee_db.hashed_password
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            access_token = create_access_token(data={"sub": str(employee_db.id)})
            return access_token
        except EmployeeNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def read_user(self, session: AsyncSession, **kwargs: Any) -> Employee:
        employee = await self.repo.find_user(session, **kwargs)
        if not employee:
            raise EmployeeNotFoundError("Employee with this setting does not exist.")
        else:
            return employee

    async def read_users(self, session: AsyncSession) -> list[Employee]:
        self.logger.info("reading users data")
        employees = await self.repo.select_all_users(session)
        return employees

    async def create_user(
        self, session: AsyncSession, employee: EmployeeRequest
    ) -> None:
        try:
            await self.read_user(session, email=employee.email)
        except EmployeeNotFoundError:
            employee_type = await self.repo.find_employee_type_by_name(
                session, employee.role
            )
            if employee_type is None:
                raise ValueError(f"Role '{employee.role}' does not exist.")
            await self.repo.insert_user(session, employee, type_id=employee_type.id)

    async def update_user(
        self,
        session: AsyncSession,
        employee_id: int,
        employee_attribute_update: EmployeeUpdateAttributes,
    ) -> None:
        employee = await self.read_user(session, id=employee_id)
        update_data: dict[str, Any] = employee_attribute_update.model_dump(
            exclude_unset=True
        )
        await self.repo.update_user(session, employee, update_data)

    async def read_shifts(self, session: AsyncSession) -> List[ShiftSummary]:
        rows = await self.repo.select_all_shifts_with_assigned_counts(session)
        summaries: List[ShiftSummary] = []
        for shift, assigned_count in rows:
            summary = ShiftSummary.model_validate(shift)
            summary.assigned_employees = assigned_count
            summaries.append(summary)
        return summaries

    async def create_shift(self, session: AsyncSession, shifts: List[ShiftBase]):
        await self.repo.insert_shift(session, shifts)

    async def delete_shift(self, session: AsyncSession, shift_id: uuid.UUID):
        shift = await self.repo.find_by_shift_id(session, shift_id)
        if not shift:
            raise ShiftNotFoundError("Shift with this id does not exist.")
        else:
            await self.repo.delete_shift(session, shift)

    async def update_shift(
        self,
        session: AsyncSession,
        shift_id: uuid.UUID,
        shift_to_update: ShiftUpdateAttributes,
    ):
        shift = await self.repo.find_by_shift_id(session, shift_id)
        if not shift:
            raise ShiftNotFoundError("Shift with this id does not exist.")
        else:
            update_data: dict[str, Any] = shift_to_update.model_dump(exclude_unset=True)
            await self.repo.update_shift(session, shift, update_data)

    async def read_shift_details(
        self, session: AsyncSession, shift_id: uuid.UUID
    ) -> ShiftEmployeeDetails:
        shift = await self.repo.read_shift_details(session, shift_id)
        if not shift:
            raise ShiftNotFoundError("Shift with this id does not exist.")
        return ShiftEmployeeDetails.model_validate(shift)

    async def assign_employee_to_shift(
        self, session: AsyncSession, shift_id: uuid.UUID, employee_id: uuid.UUID
    ):
        if not await self.repo.find_by_shift_id(session, shift_id):
            raise ShiftNotFoundError("Shift with this id does not exist.")
        if not await self.repo.find_by_user_id(session, employee_id):
            raise EmployeeNotFoundError("Employee with this id does not exist.")
        else:
            await self.repo.assign_employee_to_shift(session, shift_id, employee_id)
            return True

    async def read_shift_employee_availability(
        self, session: AsyncSession, shift_id: uuid.UUID
    ) -> List[EmployeeAvailability]:
        if not await self.repo.find_by_shift_id(session, shift_id):
            raise ShiftNotFoundError("Shift with this id does not exist.")
        employees = await self.repo.select_all_users(session)
        assigned_ids = set(
            await self.repo.find_assigned_employee_ids(session, shift_id)
        )
        return [
            EmployeeAvailability(
                id=employee.id,
                name=employee.name,
                available=employee.id not in assigned_ids,
            )
            for employee in employees
        ]

    async def create_employee_type(
        self, session: AsyncSession, employee_type_request: EmployeeTypeRequest
    ):
        employee_type = EmployeeType(name=employee_type_request.name)
        await self.repo.create_employee_type(session, employee_type)

    async def read_employee_types(self, session: AsyncSession) -> List[EmployeeType]:
        employee_types = await self.repo.select_all_employee_types(session)
        return employee_types
