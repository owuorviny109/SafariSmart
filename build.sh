#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input --settings=safarismart.settings_production
python manage.py migrate --settings=safarismart.settings_production

# Load initial data if database is empty
python manage.py loaddata destinations/fixtures/kenya_destinations.json --settings=safarismart.settings_production || true
python manage.py loaddata core/fixtures/initial_configuration.json --settings=safarismart.settings_production || true
