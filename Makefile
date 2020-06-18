migrate:
	docker-compose run -rm web ./manage.py migrate

createsuperuser:
	docker-compose run -rm web ./manage.py createsuperuser

collectstatic:
	docker-compose run -rm web ./manage.py collectstatic

runtests:
	docker-compose run -rm web pytest
