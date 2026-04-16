# Bangla-Municipal-Record-Digitization-and-Structured-Data-Management-System

## BMREMS (Flask + SQLite)

This repository contains a SaaS-style landing website and a working municipal record management web app in:

`municipal-system/`

### Quick start

```bash
cd municipal-system
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`.

### Important note about `database.db`

The SQLite database file is intentionally **not version-controlled** to avoid git merge conflicts.
It is created automatically on app startup by Flask-SQLAlchemy (`db.create_all()`).
