# crud.py
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
import models, schemas

# --- User Management ---
def get_user_by_email(db: Session, email: str): return db.query(models.User).filter(models.User.email == email).first()
def get_users(db: Session): return db.query(models.User).all()
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email, role=user.role, manager_id=user.manager_id)
    db.add(db_user); db.commit(); db.refresh(db_user); return db_user
def update_user_manager(db: Session, user_id: int, manager_id: int | None):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user: raise HTTPException(status_code=404, detail="User not found")
    db_user.manager_id = manager_id; db.commit(); db.refresh(db_user); return db_user
def delete_user_by_id(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user: raise HTTPException(status_code=404, detail="User not found")
    if db_user.role == models.Role.ADMIN: raise HTTPException(status_code=400, detail="Cannot delete the admin user")
    db.delete(db_user); db.commit(); return {"ok": True}

# --- Approval Rule Management ---
def create_approval_rule(db: Session, name: str, min_amount: float):
    db_rule = models.ApprovalRule(name=name, min_amount=min_amount); db.add(db_rule); db.commit(); db.refresh(db_rule); return db_rule
def add_step_to_rule(db: Session, rule_id: int, approver_id: int):
    rule = db.query(models.ApprovalRule).filter(models.ApprovalRule.id == rule_id).first()
    if not rule: raise HTTPException(status_code=404, detail="Rule not found")
    next_step_number = len(rule.steps) + 1
    db_step = models.ApprovalStep(rule_id=rule_id, approver_id=approver_id, step_number=next_step_number)
    db.add(db_step); db.commit(); db.refresh(rule); return rule
def get_all_rules(db: Session): return db.query(models.ApprovalRule).options(joinedload(models.ApprovalRule.steps).joinedload(models.ApprovalStep.approver)).all()
def delete_rule(db: Session, rule_id: int):
    steps_in_rule = db.query(models.ApprovalStep.id).filter(models.ApprovalStep.rule_id == rule_id).subquery()
    active_use = db.query(models.ActiveApproval).filter(models.ActiveApproval.current_step_id.in_(steps_in_rule)).first()
    if active_use: raise HTTPException(status_code=400, detail="Cannot delete rule: it is in use by an active expense.")
    db_rule = db.query(models.ApprovalRule).filter(models.ApprovalRule.id == rule_id).first()
    if not db_rule: raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(db_rule); db.commit(); return {"ok": True}

# --- Expense and Workflow Logic ---
def create_expense(db: Session, expense: schemas.ExpenseCreate, user_id: int):
    db_expense = models.Expense(**expense.dict(), employee_id=user_id, status=models.Status.PENDING)
    db.add(db_expense); db.commit(); db.refresh(db_expense)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    log_entry = models.ExpenseLog(expense_id=db_expense.id, user_name=user.name, action="SUBMITTED")
    db.add(log_entry)
    
    applicable_rule = db.query(models.ApprovalRule).filter(models.ApprovalRule.min_amount <= db_expense.amount).order_by(models.ApprovalRule.min_amount.desc()).first()
    if applicable_rule and applicable_rule.steps:
        first_step = applicable_rule.steps[0]
        active_approval = models.ActiveApproval(expense_id=db_expense.id, current_step_id=first_step.id)
        db.add(active_approval)
    else:
        db_expense.status = models.Status.APPROVED
        log_entry = models.ExpenseLog(expense_id=db_expense.id, user_name="System", action="AUTO-APPROVED", comment="No approval rule matched.")
        db.add(log_entry)
    db.commit(); return db_expense

def get_pending_approvals(db: Session, user_id: int):
    active_approvals = db.query(models.ActiveApproval).join(models.ApprovalStep).filter(models.ApprovalStep.approver_id == user_id).all()
    expense_ids = [approval.expense_id for approval in active_approvals]
    if not expense_ids: return []
    pending_expenses = db.query(models.Expense).options(joinedload(models.Expense.employee)).filter(models.Expense.id.in_(expense_ids)).all()
    
    COMPANY_CURRENCY = "INR"; CONVERSION_RATES = {"USD": 83.50, "EUR": 90.25}
    for expense in pending_expenses:
        if expense.currency != COMPANY_CURRENCY and expense.currency in CONVERSION_RATES:
            expense.amount_in_company_currency = expense.amount * CONVERSION_RATES[expense.currency]
        else: expense.amount_in_company_currency = expense.amount
    return pending_expenses

def process_approval(db: Session, expense_id: int, approval_data: schemas.ApprovalUpdate, user_id: int):
    active_approval = db.query(models.ActiveApproval).filter(models.ActiveApproval.expense_id == expense_id).first()
    if not active_approval or active_approval.current_step.approver_id != user_id:
        raise HTTPException(status_code=403, detail="Not your turn to approve or expense not found")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    log_entry = models.ExpenseLog(expense_id=expense_id, user_name=user.name, action=approval_data.status.value, comment=approval_data.comment)
    db.add(log_entry)

    if approval_data.status == models.Status.REJECTED:
        active_approval.expense.status = models.Status.REJECTED
        db.delete(active_approval); db.commit(); return active_approval.expense
        
    current_rule = active_approval.current_step.rule
    current_step_number = active_approval.current_step.step_number
    next_step = next((step for step in current_rule.steps if step.step_number == current_step_number + 1), None)

    if next_step:
        active_approval.current_step_id = next_step.id
    else:
        active_approval.expense.status = models.Status.APPROVED
        db.delete(active_approval)
    db.commit(); return active_approval.expense

def get_user_expenses(db: Session, user_id: int): return db.query(models.Expense).filter(models.Expense.employee_id == user_id).order_by(models.Expense.date.desc()).all()
def get_expense_logs(db: Session, expense_id: int): return db.query(models.ExpenseLog).filter(models.ExpenseLog.expense_id == expense_id).order_by(models.ExpenseLog.timestamp.asc()).all()