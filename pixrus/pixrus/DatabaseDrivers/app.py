# pixrus/DatabaseDrivers/apps.py
from django.apps import AppConfig

class DatabaseDriversConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pixrus.DatabaseDrivers'  # Ensure this matches the folder structure exactly
