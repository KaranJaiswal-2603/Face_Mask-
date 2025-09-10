from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import secrets

def generate_unique_link():
    return secrets.token_urlsafe(16)

from datetime import datetime


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


from itsdangerous import URLSafeTimedSerializer

serializer = URLSafeTimedSerializer(app.secret_key)

def generate_reset_token(email):
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=3600):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except:
        return None
    return email


# User model for database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='student')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class InstructorGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    # Missing fields below — Add ye fields yahan
    description = db.Column(db.String(255))
    department = db.Column(db.String(100))
    class_name = db.Column(db.String(50))   # 'class' reserved word hai isliye 'class_name'
    section = db.Column(db.String(50))
    instructor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    registration_link = db.Column(db.String(255), unique=True)
    attendance_link = db.Column(db.String(255), unique=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    student_id = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    face_encoding_file = db.Column(db.String(255), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('instructor_group.id'), nullable=False)

    group = db.relationship('InstructorGroup', backref=db.backref('students', lazy=True))   

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='present')

    student = db.relationship('Student', backref=db.backref('attendances', lazy=True))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    # Basic validation
    if not username or not email or not password:
        flash('Please fill out all required fields.')
        return redirect(url_for('auth'))

    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        flash('Email already registered.')
        return redirect(url_for('auth'))

    new_user = User(username=username, email=email, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    flash(f'Successfully signed up as {role}. Please log in.')
    return redirect(url_for('auth'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role

        if user.role == 'instructor':
            return redirect(url_for('instructor_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    else:
        flash('Invalid email or password')
        return redirect(url_for('auth'))

@app.route('/instructor-dashboard')
def instructor_dashboard():
    if 'user_id' not in session or session.get('role') != 'instructor':
        flash('Unauthorized access! Please log in as instructor.')
        return redirect(url_for('auth'))

    username = session.get('username', 'User')
    return render_template('instructor-dashboard.html', username=username)


@app.route('/student-dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        flash('Unauthorized access! Please log in as student.')
        return redirect(url_for('auth'))
    
    username = session.get('username', 'User')  # session se username le lo
    return render_template('student-dashboard.html', username=username)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('auth'))

@app.route('/link-handler')
def link_handler():
    return render_template('link-handler.html')

# Initialize the database (run once)
with app.app_context():
    db.create_all()

    from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'facemaskattendance@gmail.com'
app.config['MAIL_PASSWORD'] = 'tjzk jfwt pyng xewn'  # Gmail ke liye app password banao

mail = Mail(app)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message("Password Reset Request",
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[user.email])
            msg.body = f'Please use the following link to reset your password:\n{reset_url}\nIf you did not request this, please ignore.'
            mail.send(msg)
            flash('Password reset link has been sent to your email.')
        else:
            flash('No account found with that email.')
        return redirect(url_for('auth'))
    return render_template('reset.html')



@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash('Invalid or expired reset link.')
        return redirect(url_for('reset_password_request'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(new_password)  # Password hashing karne wala method
            db.session.commit()
            flash('Your password has been updated. Please log in.')
            return redirect(url_for('auth'))

    return render_template('passwords.html')

@app.route('/create-group', methods=['POST'])
def create_group():
    if 'user_id' not in session or session.get('role') != 'instructor':
        return {'error': 'Unauthorized'}, 403

    data = request.json
    group_name = data.get('name')
    description = data.get('description')
    department = data.get('department')
    class_name = data.get('class')
    section = data.get('section')

    if not group_name or not department or not class_name or not section:
        return {'error': 'Missing required fields'}, 400

    registration_link = generate_unique_link()
    attendance_link = generate_unique_link()

    new_group = InstructorGroup(
    name=group_name,
    description=description,
    department=department,
    class_name=class_name,
    section=section,
    instructor_id=session['user_id'],
    registration_link=registration_link,
    attendance_link=attendance_link
)

    db.session.add(new_group)
    db.session.commit()

    return {'message': 'Group created successfully', 'group_id': new_group.id}
   
@app.route('/get-groups')
def get_groups():
    if 'user_id' not in session or session.get('role') != 'instructor':
        return {'error': 'Unauthorized'}, 403

    groups = InstructorGroup.query.filter_by(instructor_id=session['user_id']).all()
    groups_list = []
    for g in groups:
        student_count = Student.query.filter_by(group_id=g.id).count()  # Dynamic student count
        attendance_count = 0  # Agar attendance data hai toh calculate karo

        groups_list.append({
            'id': g.id,
            'name': g.name,
            'description': g.description,
            'department': g.department,
            'class': g.class_name,
            'section': g.section,
            'registration_link': g.registration_link,
            'attendance_link': g.attendance_link,
            'studentCount': student_count,
            'attendancecount': attendance_count
        })
    return {'groups': groups_list}


import base64, io, os, pickle
from model import get_face_encodings, compare_faces
import face_recognition
from flask import request, jsonify

# Encoding files ke liye folder create karo (agar nahi hai)
if not os.path.exists('encodings'):
    os.makedirs('encodings')

def save_encodings(student_id, encodings):
    filepath = f'encodings/{student_id}_encodings.pkl'
    with open(filepath, 'wb') as f:
        pickle.dump(encodings, f)

def load_encodings(student_id, group_id):
    filepath = f'encodings/{student_id}_{group_id}.pkl'  # Group ID bhi include karo path mein
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'rb') as f:
        return pickle.load(f)

from flask import jsonify
from datetime import datetime

@app.route('/attendance/mark-attendance/<string:attendance_token>', methods=['POST'])
def mark_attendance(attendance_token):
    data = request.json
    student_id = data.get('student_id')
    img_str = data.get('image')

    if not student_id or not img_str:
        return jsonify({'error':'student_id or image missing'}), 400

    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return jsonify({'error':'Student not found'}), 400

    try:
        img_data = base64.b64decode(img_str.split(',')[1])
        image = face_recognition.load_image_file(io.BytesIO(img_data))
        captured_encodings = get_face_encodings(image)
    except Exception as e:
        return jsonify({'error': f'Image processing failed: {str(e)}'}), 400

    if not captured_encodings:
        return jsonify({'error':'No face detected'}), 400

    # Load encoding with student_id AND group_id
    known_encodings = load_encodings(student_id, student.group_id)  

    if not known_encodings:
        return jsonify({'error':'Student not registered or encoding missing'}), 400

    match_results = compare_faces(known_encodings, captured_encodings[0])

    if True in match_results:
        # Attendance marking logic (existing)
        attendance = Attendance(student_id=student.id)
        db.session.add(attendance)
        db.session.commit()
        return jsonify({'message':'Attendance marked successfully'})
    else:
        return jsonify({'error':'Face did not match'}), 400



@app.route('/register/<registration_link>')
def registration_page(registration_link):
    group = InstructorGroup.query.filter_by(registration_link=registration_link).first_or_404()
    return render_template('register.html', registration_link=registration_link, group=group)
 




@app.route('/attendance/<attendance_link>')
def attendance_page(attendance_link):
    group = InstructorGroup.query.filter_by(attendance_link=attendance_link).first_or_404()
    # Group info bhej sakte hain agar chahiye
    return render_template('attendance.html')

@app.route('/attendance/register-face/<registration_link>', methods=['POST'])
def register_face(registration_link):
    group = InstructorGroup.query.filter_by(registration_link=registration_link).first_or_404()
    data = request.json

    name = data.get('name')
    email = data.get('email')
    student_id = data.get('student_id')
    department = data.get('department')
    phone = data.get('phone')
    images = data.get('images')

    # Basic validation
    if not all([name, email, student_id, department, phone, images]):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if already registered
    existing_student = Student.query.filter_by(student_id=student_id, group_id=group.id).first()
    if existing_student:
        return jsonify({'error': 'Student already registered in this group.'}), 400

    encodings = []
    for img_str in images:
        try:
            img_data = base64.b64decode(img_str.split(',')[1])
            image = face_recognition.load_image_file(io.BytesIO(img_data))
            face_encs = get_face_encodings(image)
            if face_encs:
                encodings.append(face_encs[0])
        except Exception as e:
            return jsonify({'error': f'Error processing images: {str(e)}'}), 400

    if not encodings:
        return jsonify({'error': 'No face found in images'}), 400

    filepath = f'encodings/{student_id}_{group.id}.pkl'
    try:
        with open(filepath, 'wb') as f:
            pickle.dump(encodings, f)
    except Exception as e:
        return jsonify({'error': f'Failed to save encodings: {str(e)}'}), 500

    student = Student(
        name=name,
        email=email,
        student_id=student_id,
        department=department,
        phone=phone,
        group_id=group.id,
        face_encoding_file=filepath
    )
    db.session.add(student)
    db.session.commit()

    return jsonify({'message': 'Successfully registered.'})

@app.route('/dashboard-stats')
def dashboard_stats():
    if 'user_id' not in session or session.get('role') != 'instructor':
        return {'error': 'Unauthorized'}, 403

    instructor_id = session['user_id']

    total_groups = InstructorGroup.query.filter_by(instructor_id=instructor_id).count()
    total_students = db.session.query(Student).join(InstructorGroup).filter(InstructorGroup.instructor_id == instructor_id).count()
    # Overall attendance calculation placeholder - actual logic depend karta hai attendance model pe
    overall_attendance = 0
    active_links = InstructorGroup.query.filter_by(instructor_id=instructor_id).count()  # Ya jo criteria ho active links ke liye

    return {
        'totalGroups': total_groups,
        'totalStudents': total_students,
        'overallAttendance': overall_attendance,
        'activeLinks': active_links
    }

@app.route('/identify-student', methods=['POST'])
def identify_student():
    data = request.json
    img_str = data.get('image')

    if not img_str:
        return jsonify({'error':'Image missing'}), 400

    img_data = base64.b64decode(img_str.split(',')[1])
    image = face_recognition.load_image_file(io.BytesIO(img_data))
    captured_encodings = get_face_encodings(image)

    if not captured_encodings:
        return jsonify({'error':'No face detected'}), 400

    captured_encoding = captured_encodings[0]
    all_students = Student.query.all()

    matched_students = []
    for student in all_students:
        known_encodings = load_encodings(student.student_id, student.group_id)  # Fix here
        if known_encodings:
            match_results = compare_faces(known_encodings, captured_encoding)
            if True in match_results:
                matched_students.append({
                    'id': student.id,
                    'student_id': student.student_id,
                    'name': student.name,
                })

    if matched_students:
        return jsonify({'matched_students': matched_students})

    return jsonify({'error':'Face not recognized'}), 400


@app.route('/mark-attendance-confirm', methods=['POST'])
def mark_attendance_confirm():
    data = request.json
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'error': 'student_id missing'}), 400

    student = Student.query.filter_by(student_id=student_id).first()
    if not student:
        return jsonify({'error': 'Student not found'}), 400

    # DB mein attendance record insert ya update karo
    # Example:
    attendance = Attendance(student_id=student.id)
    db.session.add(attendance)
    db.session.commit()

    return jsonify({'message': 'Attendance marked successfully for ' + student.name})

from datetime import datetime, time
from flask import jsonify, session

@app.route('/daily-attendance-report')
def daily_attendance_report():
    if 'user_id' not in session or session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403

    instructor_id = session['user_id']
    groups = InstructorGroup.query.filter_by(instructor_id=instructor_id).all()
    today = datetime.utcnow().date()

    report = []

    for group in groups:
        students = Student.query.filter_by(group_id=group.id).all()
        total_students = len(students)

        present_students = []
        for student in students:
            attendance_today = Attendance.query.filter(
                Attendance.student_id == student.id,
                Attendance.timestamp >= datetime.combine(today, time.min),
                Attendance.timestamp <= datetime.combine(today, time.max),
                Attendance.status == 'present'
            ).first()

            if attendance_today:
                present_students.append({
                    'name': student.name,
                    'student_id': student.student_id,
                    'email': student.email,
                    'phone': student.phone
                })

        report.append({
            'group_name': group.name,
            'total_students': total_students,
            'present_count': len(present_students),
            'present_students': present_students
        })

    return jsonify(report)


if __name__ == '__main__':
    app.run(debug=True)
