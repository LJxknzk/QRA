from app import app, db, Teacher
from db_manager import create_teacher_database, get_teacher_db_path, get_teacher_db_session
from flask_bcrypt import Bcrypt
from sqlalchemy import text
import os

bcrypt = Bcrypt(app)

with app.app_context():
    teachers = Teacher.query.all()
    if not teachers:
        print('No teachers found in main DB')
    for t in teachers:
        print('---')
        print(f'Teacher id={t.id} name={t.full_name} email={t.email} db_name={t.db_name}')
        # Ensure db_name exists
        if not t.db_name:
            # Provide defaults if missing
            grade = t.grade_level or '11'
            section = t.section or f'section_{t.id}'
            db_name = create_teacher_database(t.id, grade, section)
            t.db_name = db_name
            db.session.commit()
            print(f'Created teacher DB: {db_name}')
        # Check teacher password hash looks like bcrypt
        ph = t.password_hash or ''
        if not ph.startswith('$2'):
            new_pass = 'changeme'
            t.password_hash = bcrypt.generate_password_hash(new_pass).decode('utf-8')
            db.session.commit()
            print(f"Replaced weak teacher password with temporary password: {new_pass} (email: {t.email})")
        else:
            print('Teacher password appears bcrypt-hashed')
        # Check teacher DB students
        if t.db_name:
            db_path = get_teacher_db_path(t.db_name)
            print('Teacher DB path:', db_path, 'exists=', os.path.exists(db_path))
            Session = get_teacher_db_session(t.db_name)
            sess = Session()
            try:
                students = sess.execute(text("SELECT id, full_name, email, password_hash FROM students")).fetchall()
                print(f'Students in teacher DB: {len(students)}')
                for s in students:
                    sid, name, email, ph = s
                    weak = 'YES' if not (ph and ph.startswith('$2')) else 'NO'
                    print(f' - {sid}: {name} ({email}) weak_password={weak}')
                    if weak:
                        newp = 'changeme_student'
                        sess.execute(text("UPDATE students SET password_hash = :ph WHERE id = :id"), {
                            'ph': bcrypt.generate_password_hash(newp).decode('utf-8'),
                            'id': sid
                        })
                        print(f'   -> set temporary student password: {newp}')
                sess.commit()
            finally:
                sess.close()
    # Summary list
    print('---')
    print('Final teacher list:')
    for t in Teacher.query.all():
        print(f'id={t.id} email={t.email} db_name={t.db_name}')
