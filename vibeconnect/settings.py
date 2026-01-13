"""
Django settings for vibeconnect project.
Production-ready for Render Deployment.
"""

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================
# SECURITY
# ============================
# ✅ Use environment variable in production
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-this")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
]


# ============================
# APPS
# ============================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # ✅ Channels
    "channels",

    # ✅ Your app
    "chat",
]


# ============================
# MIDDLEWARE
# ============================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # ✅ Whitenoise (static file serving in production)
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "vibeconnect.urls"


# ============================
# TEMPLATES
# ============================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        # ✅ You use templates folder
        "DIRS": [BASE_DIR / "templates"],

        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ============================
# ASGI / WSGI
# ============================
# ✅ Channels uses ASGI
ASGI_APPLICATION = "vibeconnect.asgi.application"
WSGI_APPLICATION = "vibeconnect.wsgi.application"


# ============================
# DATABASE
# ============================
# ✅ Render free uses sqlite unless you add postgres.
# Keep sqlite for now. We'll upgrade later.
import dj_database_url

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=True
    )
}

# ============================
# PASSWORD VALIDATORS
# ============================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ============================
# INTERNATIONALIZATION
# ============================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# ============================
# STATIC FILES
# ============================
STATIC_URL = "/static/"

# ✅ In dev: use BASE_DIR/static
STATICFILES_DIRS = [BASE_DIR / "static"]

# ✅ In production: collectstatic output
STATIC_ROOT = BASE_DIR / "staticfiles"

# ✅ best storage for whitenoise
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ============================
# DEFAULT PK
# ============================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================
# CHANNELS (WebSockets)
# ============================
# ✅ Use Redis in production, fallback to InMemory in local
REDIS_URL = os.getenv("REDIS_URL", "")

if REDIS_URL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
            },
        }
    }
else:
    # local dev
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        }
    }
