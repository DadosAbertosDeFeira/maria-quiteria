release: bin/release.sh
web: gunicorn web.wsgi:application --preload --log-file -
worker: celery -A web worker -l INFO --without-heartbeat --without-gossip --without-mingle
