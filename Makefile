migrate:
	docker-compose run --rm web python manage.py migrate

createsuperuser:
	docker-compose run --rm web python ./manage.py createsuperuser

runtests:
	docker-compose run --rm web pytest

collectstatic:
	docker-compose run --rm web python manage.py collectstatic