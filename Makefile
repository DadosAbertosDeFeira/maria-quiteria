migrate:
	docker-compose exec web ./manage.py migrate

createsuperuser:
	docker-compose exec web ./manage.py createsuperuser

collectstatic:
	docker-compose exec web ./manage.py collectstatic

runtests:
	docker-compose exec web pytest
