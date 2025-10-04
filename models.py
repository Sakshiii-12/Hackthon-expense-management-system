# models.py
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base

class Role(str, enum.Enum):
    EMPLOYEE = "EMPLOYEE"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"

class Status(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    role = Column(Enum(Role), default=Role.EMPLOYEE)
    manager_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    reports = relationship("User", backref=backref("manager", remote_side=[id]))
    expenses = relationship("Expense", back_populates="employee", cascade="all, delete-orphan")

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    currency = Column(String, default="USD")
    category = Column(String)
    description = Column(String)
    date = Column(DateTime)
    status = Column(Enum(Status), default=Status.PENDING)
    employee_id = Column(Integer, ForeignKey("users.id"))
    employee = relationship("User", back_populates="expenses")

class ExpenseLog(Base):
    __tablename__ = "expense_logs"
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"))
    user_name = Column(String)
    action = Column(String)
    comment = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ApprovalRule(Base):
    __tablename__ = "approval_rules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    min_amount = Column(Float, default=0.0)
    steps = relationship("ApprovalStep", back_populates="rule", cascade="all, delete-orphan", order_by="ApprovalStep.step_number")

class ApprovalStep(Base):
    __tablename__ = "approval_steps"
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("approval_rules.id"))
    
    # --- THIS IS THE FIX ---
    # If the user linked here is deleted, this approval step will be automatically deleted too.
    approver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE")) 
    
    step_number = Column(Integer)
    rule = relationship("ApprovalRule", back_populates="steps")
    approver = relationship("User")

class ActiveApproval(Base):
    __tablename__ = "active_approvals"
    id = Column(Integer, primary_key=True, index=True)
    expense_id = Column(Integer, ForeignKey("expenses.id"))
    current_step_id = Column(Integer, ForeignKey("approval_steps.id"))
    expense = relationship("Expense")
    current_step = relationship("ApprovalStep")

