release: bin/release.sh
web: gunicorn web.wsgi:application --preload --log-file -
worker: python manage.py rundramatiq_dc
