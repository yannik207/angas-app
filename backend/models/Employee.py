from sqlmodel import SQLModel, TIMESTAMP, Column, text, Field, Relationship
from pydantic import EmailStr
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
import uuid
from uuid6 import uuid7
from backend.models.shift_employe_link import ShiftEmployeeLink
from sqlalchemy import func

if TYPE_CHECKING:
    from backend.models.Shift import Shift


class EmployeeType(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid7, primary_key=True)
    # Unique so the DB enforces "no duplicate roles" in a single insert.
    name: str = Field(unique=True, index=True)

    # Relationship to link back to the employees (One-to-Many)
    employees: List["Employee"] = Relationship(back_populates="employee_type")


class EmployeeTypeRequest(SQLModel):
    name: str


class EmployeeBase(SQLModel):
    name: str
    email: EmailStr
    hashed_password: str


class EmployeeRequest(EmployeeBase):
    role: str


class Employee(EmployeeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid7, primary_key=True)
    created_ts: Optional[datetime] = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
    updated_ts: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            onupdate=func.now(),
        ),
    )
    type_id: uuid.UUID | None = Field(default=None, foreign_key="employeetype.id")
    employee_type: Optional[EmployeeType] = Relationship(back_populates="employees")
    shifts: List["Shift"] = Relationship(
        back_populates="employees", link_model=ShiftEmployeeLink
    )


class EmployeeUpdateAttributes(SQLModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None


class EmployeePublic(SQLModel):
    """Employee fields that are safe to expose in API responses (no password)."""

    id: uuid.UUID
    name: str


class EmployeeAvailability(EmployeePublic):
    """An employee plus whether they are available for a particular shift.

    Currently "available" only means the employee is not already assigned to
    the shift; more rules (e.g. overlapping shifts) can be layered on later.
    """

    available: bool
