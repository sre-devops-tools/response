#!/bin/bash

echo "Apply database migrations"
python manage.py migrate

echo "Collecting statics"
python manage.py collectstatic

# Start server
echo "Starting server"
uwsgi --http "0.0.0.0:8000" --module wsgi --master  --static-map /static=/code/static --enable-threads
