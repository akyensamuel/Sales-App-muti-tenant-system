# sales_management_project/settings.py

import os
import sys
from pathlib import Path
from decouple import config, Csv, UndefinedValueError
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# SECURITY SETTINGS
# =============================================================================

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)

# Configure ALLOWED_HOSTS with support for tenant subdomains
if DEBUG:
    # In development, allow all localhost subdomains for tenant access
    ALLOWED_HOSTS = [
        'localhost',
        '127.0.0.1',
        '[::1]',
        'testserver',
        '.localhost',  # Allow all subdomains of localhost
        'demo.localhost',
        'test.localhost', 
        'dev.localhost',
        # Add more tenant subdomains as needed
    ]
else:
    # In production, use environment variable
    ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sales_app',
    'accounting_app',
    'core',
    'tenants',  # Multi-tenancy support
    'widget_tweaks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'tenants.middleware.TenantMiddleware',  # Tenant detection and routing
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sales_management_project.urls'
LOGIN_URL = '/sales/login/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sales_management_project.wsgi.application'

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

try:
    database_url = config('DATABASE_URL')
except UndefinedValueError:
    database_url = f'sqlite:///{BASE_DIR / "db.sqlite3"}'

DATABASES = {
    'default': dj_database_url.parse(database_url, conn_max_age=600)
}

# =============================================================================
# MULTI-TENANCY CONFIGURATION
# =============================================================================

# Database router for tenant isolation
DATABASE_ROUTERS = ['tenants.db_router.TenantDatabaseRouter']

# Template for tenant database configuration
TENANT_DATABASE_TEMPLATE = {
    'ENGINE': 'django.db.backends.postgresql',
    'OPTIONS': {
        'charset': 'utf8mb4',
    },
    'TEST': {
        'CHARSET': 'utf8mb4',
    }
}

# No default tenant - all access must be through valid tenant subdomains
DEFAULT_TENANT_SUBDOMAIN = None

# Log active DB (remove or disable in production if needed)
print(f"[ENV DEBUG] Active DB URL: {database_url}", file=sys.stderr)

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC & MEDIA FILES
# =============================================================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'sales_app' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =============================================================================
# DEFAULT AUTO FIELD
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# LOGGING (Optional but useful)
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True