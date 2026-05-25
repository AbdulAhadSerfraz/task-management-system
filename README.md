# Task Management System

A web-based Task Management System built with Flask, SQLite, and Bootstrap.

## Features

- User Registration & Login
- Task CRUD (Create, Read, Update, Delete)
- Mark Tasks as Complete/Pending
- Responsive Dashboard
- SQLite Database
- Input Validation
- Unit Testing with PyTest

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS, Bootstrap
- **Testing:** PyTest
- **Version Control:** Git & GitHub

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/task-management-system.git
   cd task-management-system
   ```

2. Install dependencies:
   ```bash
   pip install flask flask-sqlalchemy flask-login werkzeug
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and go to `http://127.0.0.1:5000`

## Running Tests

```bash
pytest tests/
```

## Project Structure

```
task-management-system/
├── app.py              # Application entry point
├── config.py           # Configuration settings
├── models/
│   ├── __init__.py
│   ├── user.py         # User model
│   └── task.py         # Task model
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py  # Authentication routes
│   └── task_routes.py  # Task CRUD routes
├── templates/
│   ├── base.html       # Base template
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   ├── dashboard.html  # Task dashboard
│   ├── create_task.html # Create task form
│   └── edit_task.html  # Edit task form
├── static/
│   └── css/
│       └── style.css   # Custom styles
├── tests/
│   ├── __init__.py
│   └── test_app.py     # Unit tests
└── README.md
```

## Team Members

- **Abdul Ahad** - Project Lead
- **Abubakar** - Authentication Module
- **Rehan** - Task CRUD Module
- **Hassan Adeel** - UI + Testing + Documentation
