from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from . import db

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    time_in = db.Column(db.Time, default=datetime.utcnow().time)
    status = db.Column(db.String(20), default="Present")
    college = db.relationship('College', backref=db.backref('attendance_records', lazy=True))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    studentid = db.Column(db.Integer, nullable=False, unique=True)
    firstname = db.Column(db.String(100), nullable=False)
    middlename = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    contactnum = db.Column(db.String(20), nullable=False)
    address= db.Column(db.String(100), nullable=False)
    gender= db.Column(db.String(100), nullable=False)
    birthdate= db.Column(db.Integer, nullable=False, unique=True)
    email= db.Column(db.String(100), nullable=False)
    level= db.Column(db.Integer, nullable=False, unique=True)
    face_path = db.Column(db.String(255), nullable=True)

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    professorid = db.Column(db.Integer, nullable=False, unique=True)
    firstname = db.Column(db.String(100), nullable=False)
    middlename = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    contactnum = db.Column(db.String(20), nullable=False)
    graduate = db.Column(db.String(100), nullable=False)
    face_path = db.Column(db.String(255))

class College(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    collegeid = db.Column(db.Integer, nullable=False, unique=True)
    firstname = db.Column(db.String(100), nullable=False)
    middlename = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    contactnum = db.Column(db.String(20), nullable=False)
    graduate = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    courses = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(100), nullable=False)
    birthdate = db.Column(db.String(100), nullable=False)
    birthcert = db.Column(db.String(100), nullable=True)
    transcipt = db.Column(db.String(100), nullable=True)
    goodmoral = db.Column(db.String(100), nullable=True)
    face_path = db.Column(db.String(255), nullable=True)
    face_encoding_id = db.Column(db.String(255), nullable=True)
    def __repr__(self):
        return f'<College {self.firstname} {self.lastname}>'
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(150), nullable=False)
    course = db.Column(db.String(100), nullable=False)  # Link to course
    level = db.Column(db.String(50), nullable=False)  # 1st Year, 2nd Year, etc.
    units = db.Column(db.Integer, nullable=False)
    instructor = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    def __repr__(self):
        return f'<Subject {self.code} - {self.name}>'

SUBJECTS = {
    'BS Information Technology': {
        '1st Year': [
            {'code': 'IT101', 'name': 'Introduction to Computing', 'units': 3, 'instructor': 'Mr. Santos'},
            {'code': 'IT102', 'name': 'Programming Fundamentals', 'units': 4, 'instructor': 'Ms. Garcia'},
            {'code': 'IT103', 'name': 'Web Design Basics', 'units': 3, 'instructor': 'Mr. Reyes'},
            {'code': 'IT104', 'name': 'Database Fundamentals', 'units': 3, 'instructor': 'Ms. Cruz'},
            {'code': 'IT105', 'name': 'IT Ethics and Security', 'units': 2, 'instructor': 'Mr. Lopez'},
        ],
        '2nd Year': [
            {'code': 'IT201', 'name': 'Object-Oriented Programming', 'units': 4, 'instructor': 'Mr. Santos'},
            {'code': 'IT202', 'name': 'Data Structures', 'units': 4, 'instructor': 'Ms. Garcia'},
            {'code': 'IT203', 'name': 'Web Development', 'units': 4, 'instructor': 'Mr. Reyes'},
            {'code': 'IT204', 'name': 'Database Management', 'units': 3, 'instructor': 'Ms. Cruz'},
            {'code': 'IT205', 'name': 'System Administration', 'units': 3, 'instructor': 'Mr. Lopez'},
        ],
        '3rd Year': [
            {'code': 'IT301', 'name': 'Advanced Web Development', 'units': 4, 'instructor': 'Mr. Santos'},
            {'code': 'IT302', 'name': 'Software Engineering', 'units': 4, 'instructor': 'Ms. Garcia'},
            {'code': 'IT303', 'name': 'Cloud Computing', 'units': 3, 'instructor': 'Mr. Reyes'},
            {'code': 'IT304', 'name': 'Network Administration', 'units': 3, 'instructor': 'Ms. Cruz'},
            {'code': 'IT305', 'name': 'Mobile App Development', 'units': 4, 'instructor': 'Mr. Lopez'},
        ],
        '4th Year': [
            {'code': 'IT401', 'name': 'Capstone Project 1', 'units': 3, 'instructor': 'Mr. Santos'},
            {'code': 'IT402', 'name': 'Capstone Project 2', 'units': 3, 'instructor': 'Ms. Garcia'},
            {'code': 'IT403', 'name': 'IT Project Management', 'units': 3, 'instructor': 'Mr. Reyes'},
            {'code': 'IT404', 'name': 'Cybersecurity Essentials', 'units': 3, 'instructor': 'Ms. Cruz'},
        ],
    },
    'BS Computer Science': {
        '1st Year': [
            {'code': 'CS101', 'name': 'Discrete Mathematics', 'units': 4, 'instructor': 'Dr. Aquino'},
            {'code': 'CS102', 'name': 'Programming Language', 'units': 4, 'instructor': 'Dr. Bautista'},
            {'code': 'CS103', 'name': 'Computer Organization', 'units': 3, 'instructor': 'Dr. Canseco'},
            {'code': 'CS104', 'name': 'Logic Design', 'units': 3, 'instructor': 'Dr. David'},
        ],
        '2nd Year': [
            {'code': 'CS201', 'name': 'Algorithms', 'units': 4, 'instructor': 'Dr. Aquino'},
            {'code': 'CS202', 'name': 'Operating Systems', 'units': 4, 'instructor': 'Dr. Bautista'},
            {'code': 'CS203', 'name': 'Database Systems', 'units': 3, 'instructor': 'Dr. Canseco'},
            {'code': 'CS204', 'name': 'Computer Networks', 'units': 3, 'instructor': 'Dr. David'},
        ],
        '3rd Year': [
            {'code': 'CS301', 'name': 'Artificial Intelligence', 'units': 4, 'instructor': 'Dr. Aquino'},
            {'code': 'CS302', 'name': 'Compiler Design', 'units': 4, 'instructor': 'Dr. Bautista'},
            {'code': 'CS303', 'name': 'Graphics Programming', 'units': 3, 'instructor': 'Dr. Canseco'},
        ],
        '4th Year': [
            {'code': 'CS401', 'name': 'Thesis 1', 'units': 3, 'instructor': 'Dr. Aquino'},
            {'code': 'CS402', 'name': 'Thesis 2', 'units': 3, 'instructor': 'Dr. Bautista'},
        ],
    },
    'BS Accountancy': {
        '1st Year': [
            {'code': 'ACC101', 'name': 'Principles of Accounting', 'units': 3, 'instructor': 'Mr. Torres'},
            {'code': 'ACC102', 'name': 'Financial Accounting', 'units': 3, 'instructor': 'Ms. Villanueva'},
            {'code': 'ACC103', 'name': 'Business Mathematics', 'units': 3, 'instructor': 'Mr. Gonzales'},
            {'code': 'ACC104', 'name': 'Accounting Information Systems', 'units': 3, 'instructor': 'Ms. Ramos'},
        ],
        '2nd Year': [
            {'code': 'ACC201', 'name': 'Intermediate Accounting', 'units': 4, 'instructor': 'Mr. Torres'},
            {'code': 'ACC202', 'name': 'Cost Accounting', 'units': 3, 'instructor': 'Ms. Villanueva'},
            {'code': 'ACC203', 'name': 'Taxation', 'units': 3, 'instructor': 'Mr. Gonzales'},
            {'code': 'ACC204', 'name': 'Auditing Basics', 'units': 3, 'instructor': 'Ms. Ramos'},
        ],
        '3rd Year': [
            {'code': 'ACC301', 'name': 'Advanced Accounting', 'units': 4, 'instructor': 'Mr. Torres'},
            {'code': 'ACC302', 'name': 'Auditing Principles', 'units': 3, 'instructor': 'Ms. Villanueva'},
            {'code': 'ACC303', 'name': 'Management Accounting', 'units': 3, 'instructor': 'Mr. Gonzales'},
        ],
        '4th Year': [
            {'code': 'ACC401', 'name': 'Accounting Practice', 'units': 3, 'instructor': 'Mr. Torres'},
            {'code': 'ACC402', 'name': 'Professional Ethics', 'units': 2, 'instructor': 'Ms. Villanueva'},
        ],
    },
}
class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.Integer, db.ForeignKey('college.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    midterm = db.Column(db.Float, nullable=True)  # Midterm grade
    final = db.Column(db.Float, nullable=True)    # Final exam grade
    assignment = db.Column(db.Float, nullable=True)  # Assignment/Project grade
    participation = db.Column(db.Float, nullable=True)  # Class participation
    final_grade = db.Column(db.Float, nullable=True)  # Final computed grade
    pass_status = db.Column(db.String(20), default='Pending')  # Passed, Failed, Pending
    remarks = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    college = db.relationship('College', backref=db.backref('grades', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('grades', lazy=True))
    
    def calculate_final_grade(self):
        """Calculate final grade based on weighted average"""
        grades = []
        weights = []
        if self.midterm is not None:
            grades.append(self.midterm)
            weights.append(0.25)  # 25%
        if self.final is not None:
            grades.append(self.final)
            weights.append(0.40)  # 40%
        if self.assignment is not None:
            grades.append(self.assignment)
            weights.append(0.20)  # 20%
        if self.participation is not None:
            grades.append(self.participation)
            weights.append(0.15)  # 15%
        if grades and weights:
            total_weight = sum(weights)
            weighted_sum = sum(g * w for g, w in zip(grades, weights))
            return round(weighted_sum / total_weight, 2)
        return None
    
    def get_letter_grade(self):
        """Convert numerical grade to letter grade"""
        if self.final_grade is None:
            return 'N/A'
        if self.final_grade >= 90:
            return 'A'
        elif self.final_grade >= 85:
            return 'B+'
        elif self.final_grade >= 80:
            return 'B'
        elif self.final_grade >= 75:
            return 'C+'
        elif self.final_grade >= 70:
            return 'C'
        elif self.final_grade >= 65:
            return 'D'
        else:
            return 'F'
    
    def update_pass_status(self):
        """Update pass/fail status"""
        if self.final_grade is None:
            self.pass_status = 'Pending'
        elif self.final_grade >= 70:
            self.pass_status = 'Passed'
            self.remarks = f'Grade: {self.final_grade}'
        else:
            self.pass_status = 'Failed'
            self.remarks = f'Grade: {self.final_grade} - Below 70'
    
    def __repr__(self):
        return f'<Grade {self.college_id} - {self.subject_id}>'