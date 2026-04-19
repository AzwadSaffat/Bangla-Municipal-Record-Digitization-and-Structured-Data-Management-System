# Bangla-Municipal-Record-Digitization-and-Structured-Data-Management-System

## BMREMS (Flask + SQLite)

This repository contains a SaaS-style landing website and a working municipal record management web app in:

`municipal-system/`

### Tech stack used

#### Languages
- **Python** for backend logic and routing (`app.py`, `models.py`)
- **HTML (Jinja templates)** for pages in `templates/`
- **CSS** for custom styling in `static/style.css`
- **JavaScript** for small client-side behavior in `static/script.js`
- **SQL (via SQLite)** as the underlying relational storage engine

#### Backend and framework
- **Flask** (web framework)
- **Flask-SQLAlchemy** (ORM + database integration)
- **Werkzeug** utility helpers (e.g., safe uploaded filenames)

#### Database and storage
- **SQLite** database file: `municipal-system/database.db` (local runtime file, ignored by git)
- **Uploads folder**: `municipal-system/uploads/` for uploaded documents

#### Frontend and UI
- **Tailwind CSS (CDN)** for utility-first UI styling
- Custom reusable classes (`btn-primary`, `btn-secondary`, cards, form fields) in `static/style.css`
- Multi-page SaaS-style marketing + app templates (`landing.html`, `dashboard.html`, `upload.html`, etc.)

#### Features implemented
- Landing/marketing website
- Dashboard metrics
- Upload + mocked OCR extraction flow
- Manual data entry
- View/search/filter records
- Edit and delete records
- CSV export
- Duplicate holding number highlighting

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
