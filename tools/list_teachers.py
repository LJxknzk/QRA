import sqlite3
import json
import os
import sys

DB = os.path.join('dist', 'instance', 'attendance.db')

if not os.path.exists(DB):
    print(f"Database not found: {DB}")
    sys.exit(1)

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT id, full_name, email, section, grade_level, db_name, created_at FROM teachers")
rows = cur.fetchall()

teachers = []
for r in rows:
    teachers.append({
        'id': r[0],
        'full_name': r[1],
        'email': r[2],
        'section': r[3],
        'grade_level': r[4],
        'db_name': r[5],
        'created_at': r[6]
    })

print(json.dumps(teachers, indent=2, default=str))
