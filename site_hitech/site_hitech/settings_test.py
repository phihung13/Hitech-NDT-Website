from .settings import *

# Test environment settings
DEBUG = True
ALLOWED_HOSTS = ['*']

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable security for local testing
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
