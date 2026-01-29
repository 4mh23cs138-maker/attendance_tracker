from flask import Flask, render_template, request, redirect, url_for
from database import db, Student, Attendance
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    students = Student.query.all()
    return render_template("index.html", students=students)

@app.route("/add_student", methods=["POST"])
def add_student():
    name = request.form.get("name")
    roll_number = request.form.get("roll_number")
    if name and roll_number:
        new_student = Student(name=name, roll_number=roll_number)
        db.session.add(new_student)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    date_str = request.form.get("date")
    date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.utcnow().date()
    
    # Iterate through form data to find attendance status
    for key, value in request.form.items():
        if key.startswith("status_"):
            student_id = int(key.split("_")[1])
            status = value
            
            # Check if attendance already exists for this student and date
            existing = Attendance.query.filter_by(student_id=student_id, date=date).first()
            if existing:
                existing.status = status
            else:
                new_attendance = Attendance(student_id=student_id, date=date, status=status)
                db.session.add(new_attendance)
    
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/report")
def report():
    attendances = Attendance.query.order_by(Attendance.date.desc()).all()
    return render_template("report.html", attendances=attendances)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)