release: bin/release.sh
web: bin/start-pgbouncer gunicorn core.wsgi:application --preload --log-file -
worker: bin/start-pgbouncer dramatiq datasets.tasks -p3 -t3 -v
