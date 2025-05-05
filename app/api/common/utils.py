import psycopg

from django.conf import settings

def get_connection():
    return psycopg.connect(
        dbname=settings.DATABASES['default']["NAME"],
        user=settings.DATABASES['default']["USER"],
        password=settings.DATABASES['default']["PASSWORD"],
        host=settings.DATABASES['default']["HOST"],
        port=settings.DATABASES['default']["PORT"],
    )