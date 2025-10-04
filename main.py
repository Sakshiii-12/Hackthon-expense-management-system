# main.py
from fastapi import FastAPI, Depends, HTTPException, Header, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import time
from fastapi.middleware.cors import CORSMiddleware
import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def write_notification(email: str, message: str):
    time.sleep(2)
    with open("notifications.log", mode="a") as log_file: log_file.write(f"Notification for {email}: {message}\n")
    print(f"--- Notification sent to {email} ---")

def get_db():
    db = SessionLocal();
    try: yield db
    finally: db.close()

async def get_current_user_id(x_user_id: int = Header(...)):
    if not x_user_id: raise HTTPException(status_code=401, detail="X-User-ID header is required")
    return x_user_id

def get_admin_user(db: Session, current_user_id: int):
    user = db.query(models.User).filter(models.User.id == current_user_id).first()
    if not user or user.role != models.Role.ADMIN: raise HTTPException(status_code=403, detail="Admin access required")
    return user

@app.get("/users", response_model=List[schemas.User])
def read_users(db: Session = Depends(get_db)): return crud.get_users(db=db)

@app.post("/users", response_model=schemas.User)
def create_new_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    get_admin_user(db, current_user_id)
    if crud.get_user_by_email(db, email=user.email): raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.patch("/users/{user_id}", response_model=schemas.User)
def update_user_details(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    get_admin_user(db, current_user_id)
    return crud.update_user_manager(db=db, user_id=user_id, manager_id=user_update.manager_id)

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    get_admin_user(db, current_user_id)
    return crud.delete_user_by_id(db=db, user_id=user_id)

@app.post("/rules", response_model=schemas.ApprovalRule)
def create_rule(name: str, min_amount: float = 0, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    get_admin_user(db, current_user_id)
    return crud.create_approval_rule(db=db, name=name, min_amount=min_amount)

@app.post("/rules/{rule_id}/steps", response_model=schemas.ApprovalRule)
def add_approver_to_rule(rule_id: int, approver_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    get_admin_user(db, current_user_id)
    return crud.add_step_to_rule(db=db, rule_id=rule_id, approver_id=approver_id)

@app.delete("/rules/{rule_id}")
def delete_approval_rule(rule_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    get_admin_user(db, current_user_id)
    return crud.delete_rule(db=db, rule_id=rule_id)

@app.get("/rules", response_model=List[schemas.ApprovalRule])
def get_rules(db: Session = Depends(get_db)): return crud.get_all_rules(db=db)

@app.post("/expenses/", response_model=schemas.Expense)
def submit_expense(expense: schemas.ExpenseCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    new_expense = crud.create_expense(db=db, expense=expense, user_id=current_user_id)
    background_tasks.add_task(write_notification, "admin@company.com", f"New expense #{new_expense.id} submitted.")
    return new_expense

@app.get("/expenses/my-history/", response_model=List[schemas.Expense])
def read_my_expense_history(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return crud.get_user_expenses(db=db, user_id=current_user_id)

@app.get("/expenses/{expense_id}/history", response_model=List[schemas.ExpenseLog])
def read_expense_log_history(expense_id: int, db: Session = Depends(get_db)):
    return crud.get_expense_logs(db=db, expense_id=expense_id)

@app.get("/approvals/pending/", response_model=List[schemas.Expense])
def read_pending_approvals(db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    return crud.get_pending_approvals(db=db, user_id=current_user_id)

@app.put("/approvals/{expense_id}", response_model=schemas.Expense)
def approve_or_reject_expense(expense_id: int, approval_data: schemas.ApprovalUpdate, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    expense = crud.process_approval(db=db, expense_id=expense_id, approval_data=approval_data, user_id=current_user_id)
    if not expense: raise HTTPException(status_code=404, detail="Expense processing failed")
    return expense