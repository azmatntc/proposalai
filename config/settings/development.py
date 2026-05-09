from .base import *  # noqa
import os

DEBUG = True
ALLOWED_HOSTS = ['*']

# Disable throttling in dev
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []  # noqa

# Use SQLite for local dev without Postgres
if os.environ.get('USE_SQLITE'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'proposalai',
        }
    }

# Email to console in dev
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Celery eager mode for dev
CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_EAGER', 'false').lower() == 'true'

# PostgreSQL connection
DATABASES['default']['USER'] = 'proposalai_user'
DATABASES['default']['PASSWORD'] = 'yourpassword'
DATABASES['default']['HOST'] = 'localhost'
DATABASES['default']['PORT'] = '5432'
