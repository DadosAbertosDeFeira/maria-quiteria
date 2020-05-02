release: bin/release.sh
web: gunicorn core.wsgi:application --preload --log-file -
worker: dramatiq datasets.tasks -p3 -t3 -v
