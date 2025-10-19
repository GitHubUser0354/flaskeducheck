from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .face_db import create_database

db = SQLAlchemy()


def seed_subjects():
    """Seed the database with subjects"""
    from .models import Subject, db
    
    SUBJECTS = {
        'BS Information Technology': {
            '1st Year': [
                {'code': 'IT101', 'name': 'Introduction to Computing', 'units': 3, 'instructor': 'Mr. Santos'},
                {'code': 'IT102', 'name': 'Programming Fundamentals', 'units': 4, 'instructor': 'Ms. Garcia'},
                {'code': 'IT103', 'name': 'Web Design Basics', 'units': 3, 'instructor': 'Mr. Reyes'},
                {'code': 'IT104', 'name': 'Database Fundamentals', 'units': 3, 'instructor': 'Ms. Cruz'},
            ],
            '2nd Year': [
                {'code': 'IT201', 'name': 'Object-Oriented Programming', 'units': 4, 'instructor': 'Mr. Santos'},
                {'code': 'IT202', 'name': 'Data Structures', 'units': 4, 'instructor': 'Ms. Garcia'},
                {'code': 'IT203', 'name': 'Web Development', 'units': 4, 'instructor': 'Mr. Reyes'},
            ],
            '3rd Year': [
                {'code': 'IT301', 'name': 'Advanced Web Development', 'units': 4, 'instructor': 'Mr. Santos'},
                {'code': 'IT302', 'name': 'Software Engineering', 'units': 4, 'instructor': 'Ms. Garcia'},
                {'code': 'IT303', 'name': 'Cloud Computing', 'units': 3, 'instructor': 'Mr. Reyes'},
            ],
            '4th Year': [
                {'code': 'IT401', 'name': 'Capstone Project 1', 'units': 3, 'instructor': 'Mr. Santos'},
                {'code': 'IT402', 'name': 'Capstone Project 2', 'units': 3, 'instructor': 'Ms. Garcia'},
            ],
        },
        'BS Computer Science': {
            '1st Year': [
                {'code': 'CS101', 'name': 'Discrete Mathematics', 'units': 4, 'instructor': 'Dr. Aquino'},
                {'code': 'CS102', 'name': 'Programming Language', 'units': 4, 'instructor': 'Dr. Bautista'},
                {'code': 'CS103', 'name': 'Computer Organization', 'units': 3, 'instructor': 'Dr. Canseco'},
            ],
            '2nd Year': [
                {'code': 'CS201', 'name': 'Algorithms', 'units': 4, 'instructor': 'Dr. Aquino'},
                {'code': 'CS202', 'name': 'Operating Systems', 'units': 4, 'instructor': 'Dr. Bautista'},
                {'code': 'CS203', 'name': 'Database Systems', 'units': 3, 'instructor': 'Dr. Canseco'},
            ],
            '3rd Year': [
                {'code': 'CS301', 'name': 'Artificial Intelligence', 'units': 4, 'instructor': 'Dr. Aquino'},
                {'code': 'CS302', 'name': 'Compiler Design', 'units': 4, 'instructor': 'Dr. Bautista'},
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
            ],
            '2nd Year': [
                {'code': 'ACC201', 'name': 'Intermediate Accounting', 'units': 4, 'instructor': 'Mr. Torres'},
                {'code': 'ACC202', 'name': 'Cost Accounting', 'units': 3, 'instructor': 'Ms. Villanueva'},
                {'code': 'ACC203', 'name': 'Taxation', 'units': 3, 'instructor': 'Mr. Gonzales'},
            ],
            '3rd Year': [
                {'code': 'ACC301', 'name': 'Advanced Accounting', 'units': 4, 'instructor': 'Mr. Torres'},
                {'code': 'ACC302', 'name': 'Auditing Principles', 'units': 3, 'instructor': 'Ms. Villanueva'},
            ],
            '4th Year': [
                {'code': 'ACC401', 'name': 'Accounting Practice', 'units': 3, 'instructor': 'Mr. Torres'},
                {'code': 'ACC402', 'name': 'Professional Ethics', 'units': 2, 'instructor': 'Ms. Villanueva'},
            ],
        },
    }

    # Check if subjects already exist
    if Subject.query.first():
        print("Subjects already seeded!")
        return

    # Add all subjects
    for course, levels in SUBJECTS.items():
        for level, subject_list in levels.items():
            for subject_data in subject_list:
                subject = Subject(
                    code=subject_data['code'],
                    name=subject_data['name'],
                    course=course,
                    level=level,
                    units=subject_data['units'],
                    instructor=subject_data.get('instructor'),
                )
                db.session.add(subject)
    
    db.session.commit()
    print(f"✅ Seeded {Subject.query.count()} subjects!")
    

def create_app():
    app = Flask(__name__, static_folder='../static', template_folder="../templates")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
    app.config['SECRET_KEY'] = 'thisismysecretkey'
    create_database() 

    db.init_app(app)

    # Import blueprints after db init
    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')

    # Import models here (AFTER db is ready)
    from . import models  

    with app.app_context():
        db.create_all()

    return app
