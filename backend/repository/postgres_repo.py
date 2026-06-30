import uuid
from backend.models import Employee, EmployeeType, Shift, ShiftBase, ShiftEmployeeLink
from backend.models.exceptions import (
    EmployeeTypeAlreadyExistsError,
)
from backend.utils.security import get_password_hash
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from typing import Any, Optional, List


class BasePostgresRepo:
    def __init__(self):
        pass

    async def find_by_user_id(
        self, session: AsyncSession, employee_id: int
    ) -> Optional[Employee]:
        statement = select(Employee).where(Employee.id == employee_id)
        result = await session.exec(statement)
        return result.first()

    async def find_user(
        self, session: AsyncSession, **kwargs: Any
    ) -> Optional[Employee]:
        statement = select(Employee)
        # Iterate over the provided kwargs (e.g., email="test@test.com", id=1)
        for key, value in kwargs.items():
            # Safely get the column attribute from the Employee model
            column = getattr(Employee, key, None)

            if column is None:
                raise ValueError(
                    f"'{key}' is not a valid column on the Employee model."
                )

            # Dynamically build the where clause
            statement = statement.where(column == value)
        result = await session.exec(statement)
        return result.first()

    async def select_all_users(self, session: AsyncSession) -> list[Employee]:
        statement = select(Employee)
        result = await session.exec(statement)
        return result.all()

    async def insert_user(
        self,
        session: AsyncSession,
        employee: Employee,
        type_id: Optional[uuid.UUID] = None,
    ):
        employee_to_register = Employee(
            name=employee.name,
            email=employee.email,
            hashed_password=get_password_hash(employee.hashed_password),
            type_id=type_id,
        )
        session.add(employee_to_register)
        await session.commit()

    async def find_employee_type_by_name(
        self, session: AsyncSession, name: str
    ) -> Optional[EmployeeType]:
        statement = select(EmployeeType).where(EmployeeType.name == name)
        result = await session.exec(statement)
        return result.first()

    async def create_employee_type(
        self, session: AsyncSession, employee_type: EmployeeType
    ) -> EmployeeType:
        session.add(employee_type)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise EmployeeTypeAlreadyExistsError(
                f"Role '{employee_type.name}' already exists."
            )
        await session.refresh(employee_type)
        return employee_type

    async def update_user(
        self, session: AsyncSession, employee, update_data: dict[str, Any]
    ):
        employee.sqlmodel_update(update_data)
        await session.commit()

    #########################################################
    # Shift Repository
    #########################################################

    async def select_all_shifts_with_assigned_counts(
        self, session: AsyncSession
    ) -> List[tuple[Shift, int]]:
        # LEFT JOIN so shifts with zero assignments still come back (count = 0).
        statement = (
            select(Shift, func.count(ShiftEmployeeLink.employee_id))
            .outerjoin(ShiftEmployeeLink, ShiftEmployeeLink.shift_id == Shift.id)
            .group_by(Shift.id)
        )
        result = await session.exec(statement)
        return result.all()

    async def insert_shift(self, session: AsyncSession, shifts: List[ShiftBase]):
        shifts_to_insert = [Shift.model_validate(shift) for shift in shifts]
        session.add_all(shifts_to_insert)
        await session.commit()

    async def find_by_shift_id(
        self, session: AsyncSession, shift_id: uuid.UUID
    ) -> Optional[Shift]:
        statement = select(Shift).where(Shift.id == shift_id)
        result = await session.exec(statement)
        return result.first()

    async def delete_shift(self, session: AsyncSession, shift: Shift):
        await session.delete(shift)
        await session.commit()

    async def update_shift(
        self, session: AsyncSession, shift: Shift, update_data: dict[str, Any]
    ):
        shift.sqlmodel_update(update_data)
        await session.commit()

    async def select_all_employee_types(
        self, session: AsyncSession
    ) -> List[EmployeeType]:
        statement = select(EmployeeType)
        result = await session.exec(statement)
        return result.all()

    async def read_shift_details(
        self, session: AsyncSession, shift_id: uuid.UUID
    ) -> Optional[Shift]:
        statement = (
            select(Shift)
            .where(Shift.id == shift_id)
            .options(selectinload(Shift.employees))
        )
        result = await session.exec(statement)
        return result.first()

    async def assign_employee_to_shift(
        self, session: AsyncSession, shift_id: uuid.UUID, employee_id: uuid.UUID
    ):
        session.add(ShiftEmployeeLink(shift_id=shift_id, employee_id=employee_id))
        await session.commit()

    async def find_assigned_employee_ids(
        self, session: AsyncSession, shift_id: uuid.UUID
    ) -> List[uuid.UUID]:
        statement = select(ShiftEmployeeLink.employee_id).where(
            ShiftEmployeeLink.shift_id == shift_id
        )
        result = await session.exec(statement)
        return result.all()