from sqlmodel import SQLModel, TIMESTAMP, Column, text, Field, Relationship
from pydantic import EmailStr
from datetime import datetime
from enum import Enum
from typing import List, Optional

class EmployeeBase(SQLModel):
    name: str
    email: EmailStr

class EmployeeRequest(EmployeeBase):
    pass

class EmployeeType(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str  # This will hold the string "Waiter" or "Barkeeper"
    
    # Relationship to link back to the employees (One-to-Many)
    employees: List["Employee"] = Relationship(back_populates="employee_type")

class Employee(EmployeeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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
    hashed_password: str
    type_id: int | None = Field(default=None, foreign_key="employeetype.id")
    employee_type: Optional[EmployeeType] = Relationship(back_populates="employees")
    

class EmployeeRole(str, Enum):
    waiter = "Waiter"
    barkeeper = "Barkeeper"
    manager = "Manager"
    chef = "Chef"

class EmployeeUpdateAttributes(SQLModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None