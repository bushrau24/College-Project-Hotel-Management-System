# Hotel Horizon - Web-Based Hotel Management System

## Project Overview
This is a full-stack web application built with Django and MongoDB (via Djongo). It features role-based access for Guests, Staff, and Admins.

## Technology Stack
- **Backend:** Django 5.x / Python
- **Database:** MongoDB
- **Frontend:** HTML5, CSS3, Bootstrap 5

## Prerequisites
1.  **Python 3.10+** installed.
2.  **MongoDB** Community Server installed and running locally on default port `27017`.

## Setup Instructions

### 1. Create Virtual Environment (Optional but recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
*Note: If you encounter issues with `djongo` on newer Python versions, try installing `pymongo` explicitly or check compatibility.*

### 3. Database Migration
Ensure MongoDB service is running. Then run:
```bash
python manage.py makemigrations core
python manage.py migrate
```

### 4. Create Admin User
To access the admin panel and manage the system initially:
```bash
python manage.py createsuperuser
```
Follow the prompts. Note that `role` defaults to 'guest' for standard signups, but superuser has admin privileges in Django admin. For the custom logic, you might need to set the role to 'admin' manually via shell or Django admin interface.

**Quick Fix for Admin Role:**
Run this in `python manage.py shell`:
```python
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username='your_superuser_name')
u.role = 'admin'
u.save()
```

### 5. Run the Server
```bash
python manage.py runserver
```
Access the application at: `http://127.0.0.1:8000`

## Features & URLs
- **Home:** `/` - View rooms, filter.
- **Login:** `/login/`
- **Register:** `/register/` (Default role: Guest)
- **Guest Dashboard:** `/my-bookings/`
- **Staff Dashboard:** `/staff/dashboard/`
- **Admin Dashboard:** `/custom-admin/`

## Troubleshooting
- **Djongo Errors**: Ensure you have compatible versions. `sqlparse==0.2.4` is often required for older Djongo versions.
- **MongoDB Connection**: Verify MongoDB is running on `localhost:27017`.
