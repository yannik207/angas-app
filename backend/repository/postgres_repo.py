from backend.models import Employee, Employee, Shift, ShiftBase
from backend.utils.security import get_password_hash
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from typing import Any, Optional, List


class BasePostgresRepo():
    def __init__(self):
        pass

    async def find_by_user_id(self, session: AsyncSession, employee_id: int) -> Optional[Employee]:
        statement = select(Employee).where(Employee.id == employee_id)
        result = await session.exec(statement)
        return result.first()
    
    async def find_user(self, session: AsyncSession, **kwargs: Any) -> Optional[Employee]:
        statement = select(Employee)
        # Iterate over the provided kwargs (e.g., email="test@test.com", id=1)
        for key, value in kwargs.items():
            # Safely get the column attribute from the Employee model
            column = getattr(Employee, key, None)
            
            if column is None:
                raise ValueError(f"'{key}' is not a valid column on the Employee model.")
            
            # Dynamically build the where clause
            statement = statement.where(column == value)
        result = await session.exec(statement)
        return result.first()

    async def select_all_users(self, session: AsyncSession) -> list[Employee]:
        statement = select(Employee)
        result = await session.exec(statement)
        return result.all()

    async def insert_user(self, session: AsyncSession, employee: Employee):
        employee_to_register = Employee(name=employee.name, email=employee.email, hashed_password=get_password_hash(employee.hashed_password))
        session.add(employee_to_register)
        await session.commit()

    async def update_user(self, session: AsyncSession, employee, update_data: dict[str, Any]):
        employee.sqlmodel_update(update_data)
        await session.commit()
    
    #########################################################
    # Shift Repository
    #########################################################

    async def select_all_shifts(self, session: AsyncSession) -> List[Shift]:
        statement = select(Shift)
        result = await session.exec(statement)
        return result.all()

    async def insert_shift(self, session: AsyncSession, shifts: List[ShiftBase]):
        shifts_to_insert = [Shift.model_validate(shift) for shift in shifts]
        session.add_all(shifts_to_insert)
        await session.commit()