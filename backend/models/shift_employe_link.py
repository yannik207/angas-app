from sqlmodel import SQLModel, Field
import uuid
from datetime import datetime
from sqlmodel import Column, TIMESTAMP, text
from sqlalchemy import func
from typing import Optional


class ShiftEmployeeLink(SQLModel, table=True):
    # These act as a composite primary key
    shift_id: uuid.UUID = Field(foreign_key="shift.id", primary_key=True)
    employee_id: uuid.UUID = Field(foreign_key="employee.id", primary_key=True)
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