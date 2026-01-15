#!/bin/bash
set -o errexit

pip install --upgrade pip
pip install --no-cache-dir -c constraints.txt -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python setup_token.py

echo "✓ Backend setup complete"

