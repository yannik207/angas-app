from sqlmodel import SQLModel, Field
import uuid


class ShiftEmployeeLink(SQLModel, table=True):
    # These act as a composite primary key
    shift_id: uuid.UUID = Field(foreign_key="shift.id", primary_key=True)
    employee_id: uuid.UUID = Field(foreign_key="employee.id", primary_key=True)
