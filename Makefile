build:
	docker-compose build

run:
	docker-compose up -d

migrate:
	docker-compose run --rm web python manage.py migrate

crawl:
	docker-compose run --rm web python manage.py crawl

createsuperuser:
	docker-compose run --rm web python manage.py createsuperuser

collectstatic:
	docker-compose run --rm web python manage.py collectstatic

tests:
	docker-compose run --rm web pytest
