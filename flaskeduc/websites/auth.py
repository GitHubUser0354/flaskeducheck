from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, College, Admin, Attendance, Subject, Grade
from .camera import capture_face_encoding, recognize_face
from .face_db import get_all_users, add_user
import base64, numpy as np, cv2, face_recognition
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json

UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

auth = Blueprint('auth', __name__)

@auth.route('/')
def home():
    return render_template('frontpage.html')

@auth.route('/professor')
def professor():
    return render_template('professor_frontpage.html')

@auth.route('/college', methods=['GET', 'POST'])
def college_register():
    if request.method == 'POST':
        collegeid = request.form.get('collegeid')
        firstname = request.form.get('firstname')
        middlename = request.form.get('middlename')
        lastname = request.form.get('lastname')
        password = request.form.get('password')
        contactnum = request.form.get('contactnum')
        graduate = request.form.get('lastschools')
        address = request.form.get('address')
        email = request.form.get('email')
        courses = request.form.get('courses')
        level = request.form.get('level')
        birthdate = request.form.get('datebirth')
        gender = request.form.get('gender')
        birthcert = request.files.get('birthcert')
        transcipt = request.files.get('form')
        goodmoral = request.files.get('goodmoral')

        def save_file(file):
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(filepath)
                return filepath
            return None
        birthcert_path = save_file(birthcert)
        transcipt_path = save_file(transcipt)
        goodmoral_path = save_file(goodmoral)
        existing_college = College.query.filter_by(collegeid=collegeid).first()
        if existing_college:
            flash("Student ID already registered!", "danger")
            return redirect(url_for('auth.college_register'))
        hashed_pw = generate_password_hash(password)
        face_encoding_id = f"{firstname}_{lastname}_{collegeid}"
        new_college = College(collegeid=collegeid, firstname=firstname,middlename=middlename, lastname=lastname, password=hashed_pw, contactnum=contactnum,graduate=graduate, address=address, email=email, courses=courses,level=level, birthdate=birthdate,gender=gender, birthcert=birthcert_path,transcipt=transcipt_path, goodmoral=goodmoral_path,face_encoding_id=face_encoding_id)
        db.session.add(new_college)
        db.session.commit()
        if 'face_encoding' in session:
            face_encoding_list = session['face_encoding']
            face_encoding = np.array(face_encoding_list)
            add_user(face_encoding_id, face_encoding)
            session.pop('face_encoding', None)
            flash("Registration successful! Face encoding saved.", "success")
        else:
            flash("Registration successful!", "success")
        return redirect(url_for('auth.logincollege'))
    return render_template('registercollege.html')

@auth.route('/logincollege', methods=['GET', 'POST'])
def logincollege():
    if request.method == 'POST':
        collegeid = request.form.get('collegeid')
        password = request.form.get('password')
        college = College.query.filter_by(collegeid=collegeid).first()
        if college and check_password_hash(college.password, password):
            session['college_id'] = college.id
            flash(f"Welcome back, {college.firstname}!", "success")
            return redirect(url_for('auth.college_dashboard'))
        else:
            flash("Invalid Student ID or Password!", "danger")
            return redirect(url_for('auth.logincollege'))
    return render_template('logincollege.html')

@auth.route('/logout')
def logout():
    session.pop('college_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.logincollege'))

@auth.route('/college/dashboard')
def college_dashboard():
    if 'college_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.logincollege'))
    college = College.query.get(session['college_id'])
    return render_template('dashboard.html', college=college)

@auth.route('/college/profile')
def college_profile():
    if 'college_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.logincollege'))
    college = College.query.get(session['college_id'])
    attendance_records = Attendance.query.filter_by(college_id=college.id).all()
    total_days = len(attendance_records)
    present_days = len([r for r in attendance_records if r.status == "Present"])
    absent_days = total_days - present_days
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    return render_template('profile.html',  college=college,  attendance_records=attendance_records,  total_days=total_days,  present_days=present_days, absent_days=absent_days, attendance_percentage=attendance_percentage)

@auth.route('/college/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if 'college_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.logincollege'))
    college = College.query.get(session['college_id'])
    if request.method == 'POST':
        try:
            college.firstname = request.form.get('firstname', college.firstname)
            college.middlename = request.form.get('middlename', college.middlename)
            college.lastname = request.form.get('lastname', college.lastname)
            college.email = request.form.get('email', college.email)
            college.contactnum = request.form.get('contactnum', college.contactnum)
            college.address = request.form.get('address', college.address)
            college.gender = request.form.get('gender', college.gender)
            college.birthdate = request.form.get('birthdate', college.birthdate)
            new_password = request.form.get('new_password')
            if new_password:
                college.password = generate_password_hash(new_password)
            if 'face_encoding' in session:
                face_encoding_list = session['face_encoding']
                face_encoding = np.array(face_encoding_list)
                face_encoding_id = f"{college.firstname}_{college.lastname}_{college.collegeid}"
                college.face_encoding_id = face_encoding_id
                try:
                    add_user(face_encoding_id, face_encoding)
                    flash("Face encoding updated successfully!", "success")
                except:
                    college.face_encoding_id = face_encoding_id
                session.pop('face_encoding', None)
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('auth.college_profile'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "danger")
            return redirect(url_for('auth.edit_profile'))
    return render_template('edit_profile.html', college=college)

@auth.route('/college/subjects')
def college_subjects():
    if 'college_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.logincollege'))
    college = College.query.get(session['college_id'])
    subjects = Subject.query.filter_by(course=college.courses,level=college.level).all()
    total_units = sum(subject.units for subject in subjects)
    return render_template('subjects.html', college=college, subjects=subjects,total_units=total_units)

@auth.route('/college/grades')
def college_grades():
    if 'college_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.logincollege'))
    college = College.query.get(session['college_id'])
    grades = Grade.query.filter_by(college_id=college.id).all()
    passed = len([g for g in grades if g.pass_status == 'Passed'])
    failed = len([g for g in grades if g.pass_status == 'Failed'])
    pending = len([g for g in grades if g.pass_status == 'Pending'])
    completed_grades = [g.final_grade for g in grades if g.final_grade is not None]
    average_grade = sum(completed_grades) / len(completed_grades) if completed_grades else 0
    total_units = sum([g.subject.units for g in grades if g.subject])
    
    return render_template('grades.html', college=college, grades=grades, passed=passed, failed=failed, pending=pending, average_grade=average_grade,total_units=total_units)

@auth.route('/college/attendance', methods=['GET', 'POST'])
def attendance():
    if 'college_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.logincollege'))
    college = College.query.get(session['college_id'])
    users = get_all_users()
    known_face_encodings = [encoding for _, encoding in users]
    known_face_names = [username for username, _ in users]
    video_capture = cv2.VideoCapture(0)
    recognized = False
    recognized_name = None
    frame_count = 0
    max_frames = 150
    while frame_count < max_frames:
        ret, frame = video_capture.read()
        if not ret:
            flash("Camera not detected!", "danger")
            break
        frame_count += 1
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    recognized_name = known_face_names[best_match_index]
                    recognized = True
                    break
        if recognized:
            break
        cv2.imshow("Facial Attendance - Auto detecting...", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video_capture.release()
    cv2.destroyAllWindows()
    if recognized:
        today = datetime.utcnow().date()
        existing = Attendance.query.filter_by(college_id=college.id, date=today).first()
        if not existing:
            new_record = Attendance(college_id=college.id,date=today,time_in=datetime.utcnow().time(),status="Present")
            db.session.add(new_record)
            db.session.commit()
            flash(f"Face detected - {recognized_name} marked Present!", "success")
        else:
            flash("You already marked attendance today!", "info")
    else:
        flash("Face Absent - No face detected. Try again.", "danger")
    return redirect(url_for('auth.attendance_records'))

@auth.route('/attendance_records')
def attendance_records():
    if 'college_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('auth.logincollege'))
    college = College.query.get(session['college_id'])
    records = Attendance.query.filter_by(college_id=college.id).all()
    return render_template('attendance_records.html', college=college, records=records)

@auth.route('/college/attendance-analysis')
def college_attendance_analysis():
    if 'college_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.logincollege'))
    college = College.query.get(session['college_id'])
    records = Attendance.query.filter_by(college_id=college.id).all()
    total_days = len(records)
    present_days = len([r for r in records if r.status == "Present"])
    absent_days = total_days - present_days
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    monthly_data = {}
    for record in records:
        month_key = record.date.strftime('%B %Y')
        if month_key not in monthly_data:
            monthly_data[month_key] = {'present': 0, 'absent': 0}
        if record.status == "Present":
            monthly_data[month_key]['present'] +=1
        else:
            monthly_data[month_key]['absent'] +=1
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_data = {day: {'present': 0, 'absent': 0} for day in day_names}
    for record in records:
        day_name = day_names[record.date.weekday()]
        if record.status == "Present":
            day_data[day_name]['present'] += 1
        else:
            day_data[day_name]['absent'] += 1
    return render_template('attendance_analysis.html',college=college, records=records, total_days=total_days, present_days=present_days, absent_days=absent_days, attendance_percentage=attendance_percentage, monthly_data=json.dumps(monthly_data),day_data=json.dumps(day_data))

@auth.route('/capture_face', methods=['POST'])
def capture_face():
    try:
        data = request.get_json()
        image_data = data['image'].split(',')[1]
        image = base64.b64decode(image_data)
        npimg = np.frombuffer(image, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        encoding = capture_face_encoding(frame)
        if encoding is not None:
            session['face_encoding'] = encoding.tolist()
            return jsonify({'message': 'Face captured and encoded successfully!','success': True,'encoding': encoding.tolist()})
        else:
            return jsonify({'message': 'No face detected in the image!','success': False}), 400
    except Exception as e:
        return jsonify({ 'message': f'Error capturing face: {str(e)}','success': False}), 500


@auth.route('/professor/register', methods=['GET', 'POST'])
def professor_register():
    if request.method == 'POST':
        professorid = request.form.get('professorid')
        firstname = request.form.get('firstname')
        middlename = request.form.get('middlename')
        lastname = request.form.get('lastname')
        password = request.form.get('password')
        contactnum = request.form.get('contactnum')
        graduate = request.form.get('graduate')
        existing_prof = Admin.query.filter_by(professorid=professorid).first()
        if existing_prof:
            flash("Professor ID already registered!", "danger")
            return redirect(url_for('auth.professor_register'))
        hashed_pw = generate_password_hash(password)
        new_professor = Admin( professorid=professorid, firstname=firstname, middlename=middlename, lastname=lastname, password=hashed_pw, contactnum=contactnum, graduate=graduate)
        db.session.add(new_professor)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('auth.professor_login'))
    return render_template('professor_register.html')

@auth.route('/professor/login', methods=['GET', 'POST'])
def professor_login():
    if request.method == 'POST':
        professorid = request.form.get('professorid')
        password = request.form.get('password')
        professor = Admin.query.filter_by(professorid=professorid).first()
        if professor and check_password_hash(professor.password, password):
            session['professor_id'] = professor.id
            flash(f"Welcome back, Prof. {professor.firstname}!", "success")
            return redirect(url_for('auth.professor_dashboard'))
        else:
            flash("Invalid Professor ID or Password!", "danger")
            return redirect(url_for('auth.professor_login'))
    return render_template('logincollege.html')

@auth.route('/professor/logout')
def professor_logout():
    session.pop('professor_id', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.professor_login'))

@auth.route('/professor/dashboard')
def professor_dashboard():
    if 'professor_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.professor_login'))
    professor = Admin.query.get(session['professor_id'])
    subjects_teaching = Subject.query.filter_by(instructor=f"{professor.firstname} {professor.lastname}").all()
    total_subjects = len(subjects_teaching)
    all_grades = Grade.query.all()
    total_students_graded = len(set([g.college_id for g in all_grades]))
    return render_template('professor_dashboard.html', professor=professor,total_subjects=total_subjects, total_students_graded=total_students_graded,subjects_teaching=subjects_teaching)

@auth.route('/professor/classes')
def professor_classes():
    if 'professor_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.professor_login'))
    professor = Admin.query.get(session['professor_id'])
    subjects = Subject.query.filter_by(instructor=f"{professor.firstname} {professor.lastname}").all()
    return render_template('professor_classes.html', professor=professor,subjects=subjects)

@auth.route('/professor/class/<int:subject_id>/students')
def professor_class_students(subject_id):
    if 'professor_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.professor_login'))
    professor = Admin.query.get(session['professor_id'])
    subject = Subject.query.get(subject_id)
    if not subject:
        flash("Subject not found!", "danger")
        return redirect(url_for('auth.professor_classes'))
    students = College.query.filter_by(courses=subject.course, level=subject.level).all()
    grades = {}
    for student in students:
        grade = Grade.query.filter_by(college_id=student.id, subject_id=subject.id).first()
        if not grade:
          grade = Grade(college_id=student.id, subject_id=subject.id)
        grades[student.id] = grade
    return render_template('professor_class_students.html', professor=professor, subject=subject,students=students,grades=grades)

@auth.route('/professor/grade/update/<int:grade_id>', methods=['POST'])
def update_grade(grade_id):
    if 'professor_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.professor_login'))

    grade = Grade.query.get(grade_id)
    
    if not grade:
        return jsonify({'success': False, 'message': 'Grade not found'}), 404
    
    try:
        grade.midterm = float(request.form.get('midterm')) if request.form.get('midterm') else None
        grade.final = float(request.form.get('final')) if request.form.get('final') else None
        grade.assignment = float(request.form.get('assignment')) if request.form.get('assignment') else None
        grade.participation = float(request.form.get('participation')) if request.form.get('participation') else None
        
        grade.final_grade = grade.calculate_final_grade()
        grade.update_pass_status()
        
        db.session.commit()
        
        return jsonify({'success': True,'message': 'Grade updated successfully!', 'final_grade': grade.final_grade,'letter_grade': grade.get_letter_grade(),'pass_status': grade.pass_status})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@auth.route('/professor/profile')
def professor_profile():
    if 'professor_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.professor_login'))

    professor = Admin.query.get(session['professor_id'])
    
    subjects_teaching = Subject.query.filter_by(instructor=f"{professor.firstname} {professor.lastname}").all()
    
    return render_template('professor_profile.html',professor=professor,subjects_teaching=subjects_teaching)

@auth.route('/professor/edit-profile', methods=['GET', 'POST'])
def professor_edit_profile():
    if 'professor_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.professor_login'))

    professor = Admin.query.get(session['professor_id'])

    if request.method == 'POST':
        try:
            professor.firstname = request.form.get('firstname', professor.firstname)
            professor.middlename = request.form.get('middlename', professor.middlename)
            professor.lastname = request.form.get('lastname', professor.lastname)
            professor.contactnum = request.form.get('contactnum', professor.contactnum)
            professor.graduate = request.form.get('graduate', professor.graduate)

            new_password = request.form.get('new_password')
            if new_password:
                professor.password = generate_password_hash(new_password)

            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('auth.professor_profile'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "danger")
            return redirect(url_for('auth.professor_edit_profile'))

    return render_template('professor_edit_profile.html', professor=professor)

@auth.route('/professor/attendance-analysis')
def professor_attendance_analysis():
    if 'professor_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.professor_login'))

    professor = Admin.query.get(session['professor_id'])
    
    subjects = Subject.query.filter_by(instructor=f"{professor.firstname} {professor.lastname}").all()
    
    subject_stats = []
    
    for subject in subjects:
        students = College.query.filter_by(courses=subject.course, level=subject.level).all()
        
        total_records = 0
        present_count = 0
        absent_count = 0
        
        for student in students:
            records = Attendance.query.filter_by(college_id=student.id).all()
            total_records += len(records)
            present_count += len([r for r in records if r.status == "Present"])
            absent_count += len([r for r in records if r.status == "Absent"])
        attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
        subject_stats.append({'subject': subject,'total_students': len(students),'total_records': total_records,'present': present_count,'absent': absent_count,'attendance_rate': attendance_rate})
    
    total_present = sum([s['present'] for s in subject_stats])
    total_absent = sum([s['absent'] for s in subject_stats])
    total_records = total_present + total_absent
    overall_rate = (total_present / total_records * 100) if total_records > 0 else 0
    
    return render_template('professor_attendance_analysis.html',professor=professor,subject_stats=subject_stats,total_present=total_present,total_absent=total_absent,total_records=total_records, overall_rate=overall_rate)

@auth.route('/professor/attendance-analysis/class/<int:subject_id>')
def professor_class_attendance(subject_id):
    if 'professor_id' not in session:
        flash("Please log in first!", "warning")
        return redirect(url_for('auth.professor_login'))

    professor = Admin.query.get(session['professor_id'])
    
    subject = Subject.query.get(subject_id)
    if not subject:
        flash("Subject not found!", "danger")
        return redirect(url_for('auth.professor_attendance_analysis'))
    
    students = College.query.filter_by(courses=subject.course, level=subject.level).all()
    
    student_attendance = []
    
    for student in students:
        records = Attendance.query.filter_by(college_id=student.id).all()
        total = len(records)
        present = len([r for r in records if r.status == "Present"])
        absent = total - present
        percentage = (present / total * 100) if total > 0 else 0
        student_attendance.append({'student': student,'total': total,'present': present,'absent': absent,'percentage': percentage,'records': records })
        student_attendance.sort(key=lambda x: x['percentage'], reverse=True)
    monthly_data = {}
    for student_data in student_attendance:
        for record in student_data['records']:
            month_key = record.date.strftime('%B %Y')
        if month_key not in monthly_data:
            monthly_data[month_key] = {'present': 0, 'absent': 0}

        if record.status == "Present":
                monthly_data[month_key]['present'] += 1
        else:
                monthly_data[month_key]['absent'] += 1
    
    return render_template('professor_class_attendance.html', professor=professor, subject=subject, student_attendance=student_attendance, monthly_data=json.dumps(monthly_data))

@auth.route('/students')
def students():
    return render_template('students.html')

@auth.route('/facialrecognition')
def facialrecognition():
    return render_template('facialrecognition.html')

@auth.route('/register', methods=['GET', 'POST'])
def registerbasiceduc():
    if request.method == 'POST':
        studentid = request.form.get('studentid')
        firstname = request.form.get('firstname')
        middlename = request.form.get('middlename')
        lastname = request.form.get('lastname')
        password = request.form.get('password')
        contactnum = request.form.get('contactnum')
        address = request.form.get('address')
        gender = request.form.get('gender')
        birthdate = request.form.get('birthDate')
        email = request.form.get('email')
        level = request.form.get('level')
        face_path = request.form.get('facepath')

        existing_user = User.query.filter_by(studentid=studentid).first()
        if existing_user:
            flash("Student ID already registered!", "danger")
            return redirect(url_for('auth.registerbasiceduc'))

      
        hashed_pw = generate_password_hash(password)

    new_user = User(studentid=studentid, firstname=firstname, middlename=middlename, lastname=lastname,password=hashed_pw, contactnum=contactnum, address=address, gender=gender, birthdate=birthdate, email=email, level=level, face_path=face_path,)
    db.session.add(new_user)
    db.session.commit()

    flash("Registration successful! Please log in.", "success")
    return redirect(url_for('auth.basiceduclogin'))

    return render_template('register.html')


@auth.route('/basiceduclogin', methods=['GET', 'POST'])
def basiceduclogin():
    if request.method == 'POST':
        studentid = request.form.get('studentid')
        password = request.form.get('password')
        user = User.query.filter_by(studentid=studentid).first()
        if user and check_password_hash(user.password, password):
            session['student_id'] = user.id
            flash(f"Welcome back, {user.firstname}!", "success")
            return redirect(url_for('auth.basic_dashboard')) 
        else:
            flash("Invalid Student ID or Password!", "danger")
            return redirect(url_for('auth.basiceduclogin'))
    return render_template('login.html')
