#!/bin/bash

cd /code
echo "ENV: " $ENVIROMENT
if ["$ENVIROMENT" = "PRODUCTION"]
then
    echo "Running Django Migrations"
    python3 manage.py migrate --noinput
    echo "Collecting Static Files"
    python3 manage.py collectstatic --noinput
fi
echo "entrypoint.sh finished"