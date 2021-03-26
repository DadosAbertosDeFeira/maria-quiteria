release: bin/release.sh
web: gunicorn web.wsgi:application --preload --log-file -
worker: dramatiq web.datasets.tasks -p3 -t2 -v
