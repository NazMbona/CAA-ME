from mayan.settings.production import *

# ------------------------------------------------------------
# Extra database for the "matters" app
# "default" is already Mayan's DB (from mayan.settings.production)
# ------------------------------------------------------------
DATABASES["matters_db"] = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "matters_db",
    "USER": "matters_user",
    "PASSWORD": "your_password",
    "HOST": "localhost",
    "PORT": "5432",
}

# ------------------------------------------------------------
# Register the custom app and route it to matters_db
# ------------------------------------------------------------
INSTALLED_APPS += ["matters.apps.MattersConfig"]
DATABASE_ROUTERS = ["app_routing.MattersRouter"]
