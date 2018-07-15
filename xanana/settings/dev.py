from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "dlxyutp!=#lx#ocp!+c*^chs1ot^ks$+z4th+s56vw#e4ih&l+"


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS.append("django_extensions")

try:
    from .local import *
except ImportError:
    pass
