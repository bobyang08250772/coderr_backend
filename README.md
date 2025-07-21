# Coderr Project 

This guide explains how to set up and run an existing Django project using a `requirements.txt` file.

---

## 📦 Prerequisites

- Python 3.13+
- pip installed
- (Optional but recommended) Python virtual environment (`venv`)

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/bobyang08250772/kanman.git
```

### 2. Frontend
Notice Frontend and Backend should be runing seperately.
Go to frontend folder, open index.html in Live Server

### 3. Backend
Go to root folder

### 3.1. Create and Activate a Virtual Environment
```bash
python -m venv venv
```

####  Activate on macOS/Linux
```bash
source venv/bin/activate
```

####  Activate on Windows
```bash
venv\Scripts\activate
```

### 3.2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3.3. Run Migrations
```bash
python manage.py migrate
```

### 3.4. Create a Superuser
```bash
python manage.py createsuperuser
```

### 3.5. Run the Development Server
```bash
python manage.py runserver
```
Open in browser: http://127.0.0.1:8000/








