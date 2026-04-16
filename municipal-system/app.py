import csv
import hashlib
import os
from datetime import datetime, date
from io import StringIO

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from werkzeug.utils import secure_filename

from models import Record, db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev-secret-key-change-me"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)


with app.app_context():
    db.create_all()


def extract_data_from_image(image_path: str):
    """
    This simulates OCR extraction and can be replaced with real Bangla OCR.
    """
    mock_profiles = [
        {"moholla_name": "Shulok Bohor", "owner_name": "Zakir Hossain", "father_name": "Mrito Osman Ali"},
        {"moholla_name": "Patharghata", "owner_name": "Nasima Akter", "father_name": "Abdul Karim"},
        {"moholla_name": "Anderkilla", "owner_name": "Rahim Uddin", "father_name": "Anwar Hossain"},
        {"moholla_name": "Kotwali", "owner_name": "Shahnaz Begum", "father_name": "Nurul Amin"},
        {"moholla_name": "Halishahar", "owner_name": "Sohel Rana", "father_name": "Abdus Sattar"},
    ]

    with open(image_path, "rb") as img:
        digest = hashlib.sha256(img.read()).hexdigest()

    seed = int(digest[:8], 16)
    profile = mock_profiles[seed % len(mock_profiles)]

    ward_no = f"{(seed % 20) + 1:02d}"
    circle_no = f"{(seed % 5) + 1:02d}"
    holding_main = (seed % 899) + 100
    holding_sub = ((seed // 17) % 400) + 1

    return {
        "holding_no": f"{holding_main}/{holding_sub}",
        "ward_no": ward_no,
        "circle_no": circle_no,
        "moholla_name": profile["moholla_name"],
        "owner_name": profile["owner_name"],
        "father_name": profile["father_name"],
    }


def save_record_from_form(form):
    record = Record(
        holding_no=form.get("holding_no", "").strip(),
        ward_no=form.get("ward_no", "").strip(),
        circle_no=form.get("circle_no", "").strip(),
        moholla_name=form.get("moholla_name", "").strip(),
        owner_name=form.get("owner_name", "").strip(),
        father_name=form.get("father_name", "").strip(),
        address=form.get("address", "").strip(),
        mobile=form.get("mobile", "").strip(),
    )
    db.session.add(record)
    db.session.commit()
    return record


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/dashboard")
def dashboard():
    records = Record.query.all()
    total_records = len(records)
    today = date.today()
    added_today = sum(1 for r in records if r.created_at.date() == today)
    missing_data_count = sum(r.missing_required_count() for r in records)

    duplicate_holding_count = (
        db.session.query(Record.holding_no)
        .filter(Record.holding_no.isnot(None), Record.holding_no != "")
        .group_by(Record.holding_no)
        .having(db.func.count(Record.holding_no) > 1)
        .count()
    )

    return render_template(
        "dashboard.html",
        total_records=total_records,
        added_today=added_today,
        missing_data_count=missing_data_count,
        duplicate_holding_count=duplicate_holding_count,
    )


@app.route("/upload", methods=["GET", "POST"])
def upload_document():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "extract":
            file = request.files.get("document")
            if not file or file.filename == "":
                flash("Please upload a document image first.", "error")
                return redirect(url_for("upload_document"))

            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            extracted = extract_data_from_image(file_path)
            flash("Data extracted successfully. Verify and save.", "success")
            return render_template(
                "upload.html",
                extracted_data=extracted,
                uploaded_filename=filename,
            )

        if action == "save":
            required = ["holding_no", "ward_no", "circle_no", "moholla_name", "owner_name", "father_name"]
            missing = [field for field in required if not request.form.get(field, "").strip()]
            if missing:
                flash("Please fill all required fields before saving.", "error")
                return render_template("upload.html", extracted_data=request.form)

            save_record_from_form(request.form)
            flash("Record saved from extracted data.", "success")
            return redirect(url_for("view_records"))

    return render_template("upload.html", extracted_data=None)


@app.route("/add", methods=["GET", "POST"])
def add_record():
    if request.method == "POST":
        required = ["holding_no", "ward_no", "circle_no", "moholla_name", "owner_name", "father_name"]
        missing = [field for field in required if not request.form.get(field, "").strip()]
        if missing:
            flash("Please complete all required fields.", "error")
            return render_template("add_record.html", form_data=request.form)

        save_record_from_form(request.form)
        flash("Record added successfully.", "success")
        return redirect(url_for("view_records"))

    return render_template("add_record.html", form_data={})


@app.route("/records")
def view_records():
    search = request.args.get("search", "").strip()
    ward_filter = request.args.get("ward", "").strip()
    moholla_filter = request.args.get("moholla", "").strip()

    query = Record.query

    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Record.holding_no.ilike(like),
                Record.owner_name.ilike(like),
                Record.father_name.ilike(like),
                Record.moholla_name.ilike(like),
            )
        )

    if ward_filter:
        query = query.filter(Record.ward_no == ward_filter)

    if moholla_filter:
        query = query.filter(Record.moholla_name.ilike(f"%{moholla_filter}%"))

    records = query.order_by(Record.created_at.desc()).all()

    duplicate_rows = (
        db.session.query(Record.holding_no)
        .group_by(Record.holding_no)
        .having(db.func.count(Record.id) > 1)
        .all()
    )
    duplicate_holding_numbers = {row[0] for row in duplicate_rows if row[0]}

    ward_options = [x[0] for x in db.session.query(Record.ward_no).distinct().order_by(Record.ward_no).all() if x[0]]

    return render_template(
        "view_records.html",
        records=records,
        search=search,
        ward_filter=ward_filter,
        moholla_filter=moholla_filter,
        ward_options=ward_options,
        duplicate_holding_numbers=duplicate_holding_numbers,
    )


@app.route("/edit/<int:record_id>", methods=["GET", "POST"])
def edit_record(record_id):
    record = Record.query.get_or_404(record_id)

    if request.method == "POST":
        required = ["holding_no", "ward_no", "circle_no", "moholla_name", "owner_name", "father_name"]
        missing = [field for field in required if not request.form.get(field, "").strip()]
        if missing:
            flash("Please complete all required fields.", "error")
            return render_template("edit_record.html", record=record)

        record.holding_no = request.form.get("holding_no", "").strip()
        record.ward_no = request.form.get("ward_no", "").strip()
        record.circle_no = request.form.get("circle_no", "").strip()
        record.moholla_name = request.form.get("moholla_name", "").strip()
        record.owner_name = request.form.get("owner_name", "").strip()
        record.father_name = request.form.get("father_name", "").strip()
        record.address = request.form.get("address", "").strip()
        record.mobile = request.form.get("mobile", "").strip()

        db.session.commit()
        flash("Record updated successfully.", "success")
        return redirect(url_for("view_records"))

    return render_template("edit_record.html", record=record)


@app.post("/delete/<int:record_id>")
def delete_record(record_id):
    record = Record.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    flash("Record deleted successfully.", "success")
    return redirect(url_for("view_records"))


@app.route("/records/export")
def export_records_csv():
    records = Record.query.order_by(Record.id.asc()).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID",
        "Holding No",
        "Ward No",
        "Circle No",
        "Moholla Name",
        "Owner Name",
        "Father/Husband Name",
        "Address",
        "Mobile",
        "Created At",
    ])

    for r in records:
        writer.writerow([
            r.id,
            r.holding_no,
            r.ward_no,
            r.circle_no,
            r.moholla_name,
            r.owner_name,
            r.father_name,
            r.address,
            r.mobile,
            r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        ])

    output.seek(0)
    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"municipal_records_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
    )


if __name__ == "__main__":
    app.run(debug=True)
