import uuid
from uuid6 import uuid7
from backend.models.Employee import Employee, EmployeePublic
from sqlmodel import SQLModel, Column, text, Field, Relationship
from sqlalchemy import func
from sqlalchemy.types import TIMESTAMP
from datetime import datetime
from typing import Optional, List
from pydantic import computed_field
from backend.models.shift_employe_link import ShiftEmployeeLink


class ShiftBase(SQLModel):
    start_time: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True)))
    end_time: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True)))

    shift_type: str
    shift_status: str
    shift_notes: str
    necessary_employees: int


class ShiftRequest(SQLModel):
    shifts: List[ShiftBase]


class ShiftUpdateAttributes(SQLModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    shift_type: Optional[str] = None
    shift_status: Optional[str] = None
    shift_notes: Optional[str] = None
    necessary_employees: Optional[int] = None


class Shift(ShiftBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid7, primary_key=True)
    employees: List[Employee] = Relationship(
        back_populates="shifts", link_model=ShiftEmployeeLink
    )
    created_ts: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        ),
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


class ShiftEmployeeDetails(ShiftBase):
    """A shift together with its assigned employees and how many are still missing."""

    id: uuid.UUID
    created_ts: Optional[datetime] = None
    updated_ts: Optional[datetime] = None
    employees: List[EmployeePublic] = []

    @computed_field
    @property
    def assigned_employees(self) -> int:
        return len(self.employees)

    @computed_field
    @property
    def missing_employees(self) -> int:
        return self.necessary_employees - len(self.employees)


class ShiftSummary(ShiftBase):
    """A shift plus a lightweight staffing summary for list/calendar views.

    Carries how many employees are needed vs. already assigned so the UI can
    colour-code shifts that still need staff without fetching full details.
    """

    id: uuid.UUID
    created_ts: Optional[datetime] = None
    updated_ts: Optional[datetime] = None
    assigned_employees: int = 0

    @computed_field
    @property
    def missing_employees(self) -> int:
        return max(self.necessary_employees - self.assigned_employees, 0)

    @computed_field
    @property
    def staffing_status(self) -> str:
        """'full' when fully staffed, 'empty' when nobody is assigned yet,
        otherwise 'partial'. Drives the calendar colour indicator."""
        if self.assigned_employees >= self.necessary_employees:
            return "full"
        if self.assigned_employees == 0:
            return "empty"
        return "partial"
