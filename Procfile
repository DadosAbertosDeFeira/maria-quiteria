release: bin/release.sh
web: bin/start-pgbouncer-stunnel gunicorn core.wsgi:application --preload --log-file -
worker: bin/start-pgbouncer-stunnel dramatiq datasets.tasks -p3 -v
