bash:
	docker-compose run --rm web bash

build:
	docker-compose build

collectstatic:
	docker-compose run --rm web python manage.py collectstatic

crawl:
	docker-compose run --rm web python manage.py crawl

createsuperuser:
	docker-compose run --rm web python manage.py createsuperuser

migrate:
	docker-compose run --rm web python manage.py migrate

run:
	docker-compose up -d

tests:
	docker-compose run --rm web pytest
