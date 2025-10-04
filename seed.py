# seed.py
from database import SessionLocal, engine, Base
from models import User, Role

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
db = SessionLocal()

admin_user = User(email='admin@company.com', name='Michael Scott', role=Role.ADMIN)
db.add(admin_user)
db.commit()

employee1 = User(email='dwight@company.com', name='Dwight Schrute', role=Role.EMPLOYEE, manager_id=admin_user.id)
employee2 = User(email='jim@company.com', name='Jim Halpert', role=Role.EMPLOYEE, manager_id=admin_user.id)
db.add(employee1); db.add(employee2); db.commit()

finance_manager = User(email='finance@company.com', name='Angela Martin', role=Role.MANAGER)
db.add(finance_manager); db.commit()

print("Database has been completely reset and seeded!")
db.close()