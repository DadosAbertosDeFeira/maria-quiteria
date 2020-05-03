release: bin/release.sh
web: newrelic-admin run-program gunicorn core.wsgi:application --preload --log-file -
worker: newrelic-admin run-program dramatiq datasets.tasks -p3 -t2 -v
