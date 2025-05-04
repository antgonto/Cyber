#!/bin/bash
cd /code

# Ensure the database exists before Django starts
python create_db.py

# Install or upgrade django-cors-headers
pip install django-cors-headers --upgrade

echo "ENV: $ENVIRONMENT"
if [ "$ENVIRONMENT" = "PRODUCTION" ]; then
    echo "Running Django Migrations"
    python manage.py migrate --noinput
    echo "Collecting Static Files"
    python manage.py collectstatic --noinput
else
    echo "Running Django Migrations in development mode"
    python manage.py migrate --noinput
    # Add collectstatic for development too
    echo "Collecting Static Files in development"
    python manage.py collectstatic --noinput
fi

echo "Starting Daphne server"
exec daphne app.asgi:application -b 0.0.0.0 -p 8000