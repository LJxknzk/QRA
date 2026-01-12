"""
Reset instance databases to a fresh state.
- Moves existing .db files under dist/instance to dist/instance/backup_<timestamp>/
- Recreates main `attendance.db` and runs `db.create_all()` to initialize schema
- Creates default `AdminConfig` row

Run: python tools/reset_instance.py
"""
import os
import shutil
from datetime import datetime

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INSTANCE = os.path.join(BASE, 'dist', 'instance')
if not os.path.isdir(INSTANCE):
    print('Instance dir not found, creating:', INSTANCE)
    os.makedirs(INSTANCE, exist_ok=True)

# Backup existing .db files
db_files = [f for f in os.listdir(INSTANCE) if f.endswith('.db')]
if db_files:
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = os.path.join(INSTANCE, f'backup_{ts}')
    os.makedirs(backup_dir, exist_ok=True)
    print(f'Backing up {len(db_files)} .db files to {backup_dir}')
    for f in db_files:
        src = os.path.join(INSTANCE, f)
        dst = os.path.join(backup_dir, f)
        shutil.move(src, dst)
else:
    print('No .db files found to backup in', INSTANCE)

# Recreate main DB schema
print('Recreating main database schema...')
import sys
# Ensure project root on path
sys.path.insert(0, BASE)
from app import app, db, AdminConfig

with app.app_context():
    # Remove any old metadata (should be none since files moved)
    try:
        db.create_all()
        # ensure default admin config exists
        if AdminConfig.query.first() is None:
            cfg = AdminConfig()
            db.session.add(cfg)
            db.session.commit()
            print('Default AdminConfig created')
        else:
            print('AdminConfig already present')
    except Exception as e:
        print('Error creating schema:', e)
        raise

print('Reset complete. Main DB recreated at:', os.path.join(INSTANCE, 'attendance.db'))
print('Teacher DBs will be created automatically when teachers are added via the app.')
