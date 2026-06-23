from sqlmodel import SQLModel, TIMESTAMP, Column, text, Field, Relationship
from pydantic import EmailStr
from datetime import datetime
from enum import Enum
from typing import List, Optional, TYPE_CHECKING
import uuid
from uuid6 import uuid7
from backend.models.shift_employe_link import ShiftEmployeeLink

if TYPE_CHECKING:
    from backend.models.Shift import Shift

class EmployeeType(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid7, primary_key=True)
    name: str  # This will hold the string "Waiter" or "Barkeeper"
    
    # Relationship to link back to the employees (One-to-Many)
    employees: List["Employee"] = Relationship(back_populates="employee_type")
    

class EmployeeBase(SQLModel):
    name: str
    email: EmailStr
    hashed_password: str

class EmployeeRequest(EmployeeBase):
    pass

class Employee(EmployeeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid7, primary_key=True)
    created_ts: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    updated_ts: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    ))
    type_id: uuid.UUID | None = Field(default=None, foreign_key="employeetype.id")
    employee_type: Optional[EmployeeType] = Relationship(back_populates="employees")
    shifts: List["Shift"] = Relationship(
        back_populates="employees",
        link_model=ShiftEmployeeLink
    )
    

class EmployeeRole(str, Enum):
    waiter = "Waiter"
    barkeeper = "Barkeeper"
    manager = "Manager"
    chef = "Chef"

class EmployeeUpdateAttributes(SQLModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None