#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input --settings=safarismart.settings_production
python manage.py migrate --settings=safarismart.settings_production

# Ensure initial configuration data is loaded (required for wizard to work)
echo "Ensuring initial configuration data..."
python manage.py ensure_initial_data --settings=safarismart.settings_production

# Load destination data
echo "Loading Kenya destinations..."
python manage.py loaddata destinations/fixtures/kenya_destinations.json --settings=safarismart.settings_production || echo "Destinations already loaded"
