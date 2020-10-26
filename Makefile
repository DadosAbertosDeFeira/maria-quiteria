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

makemigrations:
	docker-compose run --rm web python manage.py makemigrations

migrate:
	docker-compose run --rm web python manage.py migrate

run:
	docker-compose up -d

runspider:
	docker-compose run --rm web scrapy crawl $(SPIDER) -a start_from_date=$(START_DATE)

tests:
	docker-compose run --rm web pytest
