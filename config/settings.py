import os
import sys
from pathlib import Path
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ADICIONA A PASTA APPS AO PYTHON PATH
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-change-me-in-production-!@#')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# CSRF E PROXY (Para Codespaces/Deploy)
CSRF_TRUSTED_ORIGINS = ['https://*.github.dev', 'https://*.app.github.dev']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition
INSTALLED_APPS = [
    # UNFOLD (Deve vir ANTES do django.contrib.admin)
    "unfold",
    "unfold.contrib.filters",  # Opcional: Filtros bonitos
    "unfold.contrib.forms",    # Opcional: Forms bonitos
    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Nossos Apps
    'apps.common',
    'apps.clientes',
    'apps.backups',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

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
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURAÇÃO VISUAL DO UNFOLD (ADMIN) ---
# --- CONFIGURAÇÃO VISUAL DO UNFOLD (ADMIN) ---
UNFOLD = {
    "SITE_TITLE": "MaiLou Cloud",  # Título da aba do navegador
    "SITE_HEADER": "MaiLou Cloud", # Título GRANDE no topo da Sidebar (Corrigido)
    
    "SITE_URL": None,  
    
    "SITE_ICON": {
        "light": lambda request: static("img/logo-light.svg"),
        "dark": lambda request: static("img/logo-dark.svg"),
    },
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False, 
        "navigation": [
            {
                "title": _("Gestão de Backups"),
                "separator": True,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                    {
                        "title": _("Validações Realizadas"),
                        "icon": "verified",
                        "link": reverse_lazy("admin:backups_validacaobackup_changelist"),
                    },
                    {
                        "title": _("Rotinas de Backup"),
                        "icon": "schedule",
                        "link": reverse_lazy("admin:backups_rotinabackup_changelist"),
                    },
                    {
                        "title": _("Ferramentas"),
                        "icon": "build",
                        "link": reverse_lazy("admin:backups_ferramentabackup_changelist"),
                    },
                ],
            },
            {
                "title": _("Gestão de Clientes"),
                "separator": True,
                "items": [
                    {
                        "title": _("Clientes e Servidores"),
                        "icon": "business",
                        "link": reverse_lazy("admin:clientes_cliente_changelist"),
                    },
                ],
            },
            {
                "title": _("Acesso e Segurança"),
                "separator": True,
                "items": [
                    {
                        "title": _("Usuários"),
                        "icon": "people",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": _("Grupos"),
                        "icon": "lock",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}