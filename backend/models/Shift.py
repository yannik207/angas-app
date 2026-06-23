import uuid
from uuid6 import uuid7
from backend.models.Employee import Employee
from sqlmodel import SQLModel, Column, text, Field, Relationship
from sqlalchemy.types import TIMESTAMP
from datetime import datetime
from typing import Optional, List
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

class Shift(ShiftBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid7, primary_key=True)
    employees: List[Employee] = Relationship(
        back_populates="shifts", 
        link_model=ShiftEmployeeLink
    )
    created_ts: Optional[datetime] = Field(default=None, sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ))
    updated_ts: Optional[datetime] = Field(default=None, sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    ))
