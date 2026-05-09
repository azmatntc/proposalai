#!/usr/bin/env python3
"""
Bulletproof fix for ProposalAI Django configuration issues.
Run: cd ~/projects/proposalai && python3 fix_all.py
"""

import os
import sys

PROJECT_ROOT = os.path.expanduser("~/projects/proposalai")
os.chdir(PROJECT_ROOT)

print("=" * 70)
print("PROPOSALAI BULLETPROOF FIX SCRIPT")
print("=" * 70)

# STEP 1: Fix config package structure
print("\n[STEP 1] Fixing config package structure...")
for path in ["config/__init__.py", "config/settings/__init__.py"]:
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w').close()
        print(f"  Created {path}")
    else:
        print(f"  OK: {path}")

# STEP 2: Detect settings module
print("\n[STEP 2] Detecting settings module...")
settings_dir = "config/settings"
available = [f for f in os.listdir(settings_dir) if f.endswith('.py') and f != '__init__.py']
print(f"  Found: {available}")

selected = None
for priority in ['development.py', 'base.py', 'local.py']:
    if priority in available:
        selected = priority.replace('.py', '')
        break
if not selected and available:
    selected = available[0].replace('.py', '')

if not selected:
    print("  Creating base.py...")
    selected = "base"
    with open(f"{settings_dir}/base.py", 'w') as f:
        f.write("""from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me')
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'users', 'proposals', 'leads', 'analytics', 'dashboard', 'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'
""")

settings_module = f"config.settings.{selected}"
print(f"  Using: {settings_module}")

# Update manage.py, wsgi.py, asgi.py
for filename in ["manage.py", "config/wsgi.py", "config/asgi.py"]:
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            content = f.read()
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if 'DJANGO_SETTINGS_MODULE' in line and 'setdefault' in line:
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + f"os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{settings_module}')")
            else:
                new_lines.append(line)
        with open(filename, 'w') as f:
            f.write('\n'.join(new_lines))
        print(f"  Updated {filename}")

# STEP 3: Fix app packages
print("\n[STEP 3] Fixing app packages...")
for app in ['users', 'proposals', 'leads', 'analytics', 'dashboard', 'notifications']:
    for path in [f"{app}/__init__.py", f"{app}/migrations/__init__.py"]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            open(path, 'w').close()
            print(f"  Created {path}")

# STEP 4: Fix leads/admin.py
print("\n[STEP 4] Fixing leads/admin.py...")
with open('leads/admin.py', 'w') as f:
    f.write("""from django.contrib import admin
from .models import Lead, LeadActivity, LeadScore, LeadProposal

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'company', 'status', 'priority', 'user']
    list_filter = ['status', 'priority', 'source']
    search_fields = ['first_name', 'last_name', 'email', 'company']

@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ['lead', 'activity_type', 'description', 'created_at']
    list_filter = ['activity_type', 'created_at']

@admin.register(LeadScore)
class LeadScoreAdmin(admin.ModelAdmin):
    list_display = ['lead', 'id']

@admin.register(LeadProposal)
class LeadProposalAdmin(admin.ModelAdmin):
    list_display = ['lead', 'proposal', 'status', 'sent_at']
    list_filter = ['status']
""")
print("  Fixed leads/admin.py")

# STEP 5: Test
print("\n[STEP 5] Testing...")
os.environ['DJANGO_SETTINGS_MODULE'] = settings_module
try:
    import django
    django.setup()
    print("  Django loaded OK!")
    print("\nNext: python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py runserver")
except Exception as e:
    print(f"  Error: {e}")