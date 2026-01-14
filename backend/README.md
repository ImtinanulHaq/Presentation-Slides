# Presentation Tools Backend

Django REST Framework backend for Presentation Tools application.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- pip

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Setup Database

```bash
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

### Run Development Server

```bash
python manage.py runserver
```

Server will be available at [http://localhost:8000](http://localhost:8000)

Admin panel: [http://localhost:8000/admin](http://localhost:8000/admin)

API Docs: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

### Technologies Used
- Django 4.2.7
- Django REST Framework 3.14.0
- django-cors-headers 4.3.1
- drf-spectacular 0.26.5
- Pillow 10.1.0
