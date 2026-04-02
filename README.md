# 🎟 TicketFlow — Event Booking App

A Django-powered event ticket booking platform with an animated dark UI.

---

## ✨ Features

- 🔍 Browse & search events by title, city, or category
- 🔐 User registration & login
- 🛒 Book tickets with quantity selector
- 📧 Email confirmation on booking (console output in dev)
- 📅 Interactive calendar view (FullCalendar)
- ❌ Cancel bookings
- 🛠 Django Admin for managing events & bookings
- 🎨 Animated dark UI with CSS keyframes & smooth transitions

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run migrations

```bash
cd ticketflow
python manage.py migrate
```

### 3. Seed sample events

```bash
python manage.py seed_events
```

### 4. Create a superuser (for admin panel)

```bash
python manage.py createsuperuser
```

### 5. Start the server

```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000** in your browser.

Admin panel: **http://127.0.0.1:8000/admin/**

---

## 📁 Project Structure

```
ticketflow/
├── manage.py
├── requirements.txt
├── ticketflow/          # Project settings & URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── events/              # Main app
│   ├── models.py        # Event, Booking, Category
│   ├── views.py         # All views
│   ├── urls.py          # App URL routes
│   ├── admin.py         # Admin config
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── seed_events.py
│   └── templates/
│       └── events/
│           ├── home.html
│           ├── event_detail.html
│           ├── my_bookings.html
│           ├── calendar.html
│           └── register.html
└── templates/
    ├── base.html
    └── registration/
        └── login.html
```

---

## 📧 Email Configuration

In `settings.py`, email is set to `console` backend (prints to terminal).  
To send real emails, replace with SMTP:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your@email.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## 🔐 Production Checklist

- Change `SECRET_KEY` in settings.py
- Set `DEBUG = False`
- Configure `ALLOWED_HOSTS`
- Use PostgreSQL instead of SQLite
- Set up real email backend
- Run `python manage.py collectstatic`
