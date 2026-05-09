#!/usr/bin/env python3
"""
Fix broken migration dependency graph for ProposalAI.
Run: cd ~/projects/proposalai && python3 fix_migrations.py
"""

import os
import shutil

PROJECT_ROOT = os.path.expanduser("~/projects/proposalai")
os.chdir(PROJECT_ROOT)

print("=" * 70)
print("FIXING BROKEN MIGRATIONS")
print("=" * 70)

# Step 1: Delete ALL migration files (keep __init__.py)
print("\n[Step 1] Deleting all migration files...")
apps = ['users', 'proposals', 'leads', 'analytics', 'dashboard', 'notifications']

for app in apps:
    migrations_dir = f"{app}/migrations"
    if os.path.exists(migrations_dir):
        for filename in os.listdir(migrations_dir):
            if filename != '__init__.py' and filename.endswith('.py'):
                filepath = os.path.join(migrations_dir, filename)
                os.remove(filepath)
                print(f"  Deleted {app}/migrations/{filename}")
            # Also remove .pyc files
            elif filename.endswith('.pyc'):
                os.remove(os.path.join(migrations_dir, filename))

# Step 2: Delete SQLite database to start completely fresh
print("\n[Step 2] Deleting SQLite database...")
for db_file in ['db.sqlite3', 'db.sqlite3-journal']:
    if os.path.exists(db_file):
        os.remove(db_file)
        print(f"  Deleted {db_file}")

# Step 3: Regenerate migrations
print("\n[Step 3] Regenerating migrations...")
import subprocess
result = subprocess.run(
    ['python3', 'manage.py', 'makemigrations'] + apps,
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr)
    print("\nFixing common issues...")

# Step 4: Migrate
print("\n[Step 4] Running migrate...")
result = subprocess.run(
    ['python3', 'manage.py', 'migrate'],
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr)

print("\n" + "=" * 70)
print("DONE. Try: python3 manage.py runserver")
print("=" * 70)