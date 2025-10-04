# Expense Management System
**Submission for the Odoo x Amalthea IIT Gandhinagar Hackathon 2025**

This project provides a robust, scalable, and modern solution to the inefficiencies and lack of transparency in traditional expense reimbursement processes. It replaces manual workflows with a dynamic, rule-based web application featuring an administrator-configurable approval engine.


## 1. Problem Domain

Organizations often face significant challenges with traditional expense reimbursement systems, including:

* **Inflexible Approval Logic:** Difficulty adapting workflows to business-specific rules (e.g., additional oversight for high-value claims).
* **Rigid Hierarchies:** Inability to model real organizational structures (e.g., Manager → Finance Head → Admin).
* **Lack of Transparency:** Employees often have no clear visibility into their reimbursement status.
* **High Administrative Overhead:** Managing users, roles, and reporting lines is manual and error-prone.


## 2. Our Solution: A Rule-Based Approach

The **Expense Management System** is a full-stack web application designed to streamline the reimbursement process for all stakeholders:

* **Employees:** Submit expense claims in multiple currencies and track their approval status in real-time.
* **Managers/Approvers:** Review and act upon pending expense requests efficiently through a dedicated dashboard.
* **Administrators:** Configure the entire system—users, roles, reporting lines, and multi-level approval workflows—without writing a single line of code.

This system follows the principle of **configuration over code**, enabling organizations to adapt workflows dynamically to their internal policies.


## 3. Core Features

### Full User and Role Management (Admin)

* Create and manage users with roles such as *Employee* or *Manager*.
* Define reporting structures by assigning managers to employees.
* Delete users safely with automatic data integrity handling.

### Dynamic Multi-Level Approval Workflow (Admin)

* Create **custom approval rules** (e.g., “Standard Expenses,” “High-Value Expenditure”).
* Configure **minimum expense amounts** to trigger different approval chains.
* Define **sequential approval steps** involving multiple approvers.

### Intelligent Expense Routing Engine

* Automatically select appropriate approval rules based on expense amount.
* Route each expense to the **first approver** in the sequence.
* Progress through approvers step-by-step until completion or rejection.

### Complete Expense Lifecycle Management

* Submit expenses in **multiple currencies**.
* View expenses in the **company’s base currency (INR)** for uniform evaluation.
* Approvers can **approve or reject** with optional comments stored in an audit log.

### Audit Trail and Transparency

* Every submission, approval, or rejection is recorded immutably.
* Employees can view detailed logs of their expenses, including actions, timestamps, and comments.

### Advanced System Utilities

* **Data Validation:** Pydantic ensures consistent and clean data handling.
* **Asynchronous Processing:** Background tasks simulate non-blocking notifications using FastAPI.


## 4. Tech Stack and Architecture

### Technologies Used

* **Backend:** Python (FastAPI, SQLAlchemy, SQLite)
* **Frontend:** HTML, CSS, JavaScript

### Architecture Overview

A decoupled **client-server** architecture enables scalability and maintainability.

```
Client (JS + HTML)  <-->  API Server (FastAPI)  <-->  Business Logic (CRUD)  <-->  Database (SQLite)
```

### Database Schema Overview

| Model              | Purpose                                                   |
| ------------------ | --------------------------------------------------------- |
| **User**           | Stores user details and roles (Admin, Manager, Employee). |
| **Expense**        | Tracks expense claims and associated data.                |
| **ApprovalRule**   | Defines approval logic and minimum expense triggers.      |
| **ApprovalStep**   | Represents individual steps in an approval sequence.      |
| **ActiveApproval** | Tracks the current approval state of each expense.        |

This design allows flexible, hierarchical, and reusable approval flows without hardcoding business logic.


## 5. How to Run the Project

This project consists of a Python backend and a JavaScript frontend. You will need to run both simultaneously in two separate terminals.

### Prerequisites

* [Python](https://www.python.org/) (3.8+).
* A modern web browser (like Chrome, Firefox, or Edge).

### Backend Setup

1. Navigate into the `expense-backend-py` directory.
2. Create and activate a Python virtual environment:

   ```bash
   # For Windows
   python -m venv venv
   venv\Scripts\activate

   # For macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required Python packages:

   ```bash
   pip install "fastapi[all]" sqlalchemy
   ```
4. Run the seed script to create and populate a fresh database. This script will automatically reset the database on every run.

   ```bash
   python seed.py
   ```
5. Start the backend server:

   ```bash
   uvicorn main:app --reload
   ```

   The backend will now be running at `http://127.0.0.1:8000`. Keep this terminal open.

### Frontend Setup

1. In a **separate terminal** or your file explorer, navigate to the folder containing `login.html` and `dashboard.html`.
2. **Open the `login.html` file directly in your web browser.**

   * You can do this by double-clicking the file or right-clicking and selecting "Open with..." your preferred browser.

The application is now running. You can log in as different users to test the functionality.


## 6. Future Improvements

1. **OCR for Receipts:**
   Integrate OCR to extract details like amount, date, and vendor from uploaded receipts.

2. **Live Currency Conversion:**
   Fetch real-time exchange rates using APIs like *exchangerate-api.com*.

3. **Advanced Conditional Rules:**
   Support percentage-based or role-specific approval conditions.

4. **Real-Time Notifications:**
   Implement WebSockets or email services for instant updates on approval status.


## 7. Contributors

* [Sakshi Makwana](https://github.com/Sakshiii-12) – Frontend Development
* [Jayal Shah](https://github.com/014-Jayal) – Backend Development
* [Mayank Jangid](https://github.com/Mayankjangid89) – Frontend Development


## 8. Acknowledgments

This project was built as part of the **Odoo x Amalthea Hackathon 2025**, demonstrating modern, configurable enterprise expense management using a dynamic approval logic model.
