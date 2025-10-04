# schemas.py
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List
from models import Status, Role

# Base Schemas
class UserBase(BaseModel):
    name: str
    email: str

# User Schemas
class User(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    manager_id: int | None = None
    class Config: from_attributes = True

class UserCreate(BaseModel):
    name: str
    email: str
    role: Role
    manager_id: int | None = None

class UserUpdate(BaseModel):
    role: Role | None = None
    manager_id: int | None = None

# Approval Workflow Schemas
class ApprovalStep(BaseModel):
    id: int
    step_number: int
    approver: User
    class Config: from_attributes = True

class ApprovalRule(BaseModel):
    id: int
    name: str
    min_amount: float
    steps: List[ApprovalStep] = []
    class Config: from_attributes = True

# Expense Schemas
class Expense(BaseModel):
    id: int
    amount: float
    currency: str
    category: str
    description: str
    date: datetime
    status: Status
    employee_id: int
    employee: UserBase | None = None
    amount_in_company_currency: float | None = None
    class Config: from_attributes = True

class ExpenseCreate(BaseModel):
    amount: float
    currency: str
    category: str
    description: str
    date: datetime

    @field_validator('amount')
    def amount_must_be_positive(cls, value):
        if value <= 0: raise ValueError('Amount must be a positive number')
        return value

class ApprovalUpdate(BaseModel):
    status: Status
    comment: str | None = None

# Logging Schemas
class ExpenseLog(BaseModel):
    id: int
    user_name: str
    action: str
    comment: str | None = None
    timestamp: datetime
    class Config: from_attributes = True