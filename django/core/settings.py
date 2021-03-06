import os
import environ
import json
import base64

from google.oauth2 import service_account

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env(
    DEBUG=(bool, False),
    DATABASE_URL=(str, ''),
    SECRET_KEY=(str, ''),
    ALLOWED_HOSTS=(list, []),
    SERVER_NAME=(str, ''),
    SOCIAL_AUTH_GITHUB_KEY=(str, ''),
    SOCIAL_AUTH_GITHUB_SECRET=(str, ''),
    PROTOCOL=(str, ''),

    GS_BUCKET_NAME=(str, ''),
    GS_PROJECT_ID=(str, ''),
    GS_CREDENTIALS=(str, ''),
    GS_AUTO_CREATE_BUCKET=(bool, False),
    GS_AUTO_CREATE_ACL=(str, 'publicRead'),
    GS_DEFAULT_ACL=(str, 'publicRead'),
    GS_LOCATION=(str, ''),
    GS_FILE_OVERWRITE=(bool, False),

    DB_CLIENT_CERT=(str, ''),
    DB_CLIENT_KEY=(str, ''),
    DB_SERVER_CA=(str, ''),

    SENTRY_DSN=(str, ''),
)

SENTRY_DSN = env.str("SENTRY_DSN")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )

checkout_dir = environ.Path(__file__) - 2
assert os.path.exists(checkout_dir('manage.py'))

DEBUG = env.bool('DEBUG')

SECRET_KEY = env.str("SECRET_KEY")

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
SERVER_NAME = env.str('SERVER_NAME')


DATABASES = {'default': env.db()}

DB_CLIENT_CERT = env.str("DB_CLIENT_CERT")
DB_CLIENT_KEY = env.str("DB_CLIENT_KEY")
DB_SERVER_CA = env.str("DB_SERVER_CA")


def load_db_certs():
    cert_dir = "/etc/ssl/private/db-certs/"
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)

    mappings = {
        "sslcert": ("client-cert.pem", DB_CLIENT_CERT),
        "sslkey": ("client-key.pem", DB_CLIENT_KEY),
        "sslrootcert": ("server-ca.pem", DB_SERVER_CA),
    }
    cert_options = {}

    for target_parameter, (filename, cert_encoded) in mappings.items():
        if not cert_encoded:
            continue
        target = os.path.join(cert_dir, filename)
        cert = base64.b64decode(cert_encoded).decode("utf-8")
        with open(os.open(target, os.O_CREAT | os.O_WRONLY, 0o600), "w") as certfile:
            certfile.write(cert)

        cert_options[target_parameter] = target

    if "OPTIONS" not in DATABASES["default"]:
        DATABASES["default"]["OPTIONS"] = {}

    if cert_options:
        cert_options["sslmode"] = "verify-ca"

    DATABASES["default"]["OPTIONS"].update(cert_options)


load_db_certs()

# Application definition

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd Party
    'easy_thumbnails',
    'social_django',
    'rest_framework',
    'rest_framework_swagger',

    # Own
    'core',
    'frontend',
    'repository',
    'webhooks',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "var/media/")

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "var/static/")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

# Custom settings

LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'

# REST Framework

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
    )
}

# Cloud Storage

GS_BUCKET_NAME = env.str("GS_BUCKET_NAME")
GS_PROJECT_ID = env.str("GS_PROJECT_ID")

GS_CREDENTIALS = env.str("GS_CREDENTIALS")
if GS_CREDENTIALS:
    GS_CREDENTIALS = json.loads(base64.b64decode(GS_CREDENTIALS).decode("utf-8"))
    GS_CREDENTIALS = service_account.Credentials.from_service_account_info(GS_CREDENTIALS)

GS_AUTO_CREATE_BUCKET = env.str("GS_AUTO_CREATE_BUCKET")
GS_AUTO_CREATE_ACL = env.str("GS_AUTO_CREATE_ACL")
GS_DEFAULT_ACL = env.str("GS_DEFAULT_ACL")
GS_LOCATION = env.str("GS_LOCATION")
GS_FILE_OVERWRITE = env.bool("GS_FILE_OVERWRITE")

if GS_CREDENTIALS and GS_PROJECT_ID and GS_BUCKET_NAME:
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    THUMBNAIL_DEFAULT_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"

# Social auth

SOCIAL_AUTH_POSTGRES_JSONFIELD = True
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']
AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GITHUB_KEY = env.str("SOCIAL_AUTH_GITHUB_KEY")
SOCIAL_AUTH_GITHUB_SECRET = env.str("SOCIAL_AUTH_GITHUB_SECRET")
SOCIAL_AUTH_GITHUB_SCOPE = ["user:email", "read:user", "read:org"]
SOCIAL_AUTH_GITHUB_PROFILE_EXTRA_PARAMS = {
   'fields': 'email'
}

PROTOCOL = env.str("PROTOCOL")
if PROTOCOL == "https://":
    SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_REDIRECT_EXEMPT = ("/healthcheck/")

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
