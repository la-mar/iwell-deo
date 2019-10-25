

redis-start:
	docker run -d --name redis -p 6379:6379 redis

init-db:
	poetry run iwell db init

migrate:
	# poetry run iwell db stamp head
	poetry run iwell db migrate

revision:
	poetry run iwell db revision

upgrade:
	poetry run iwell db upgrade

celery-worker:
	celery -E -A iwell.celery_queue.worker:celery worker --loglevel=INFO --purge

celery-beat:
	celery -A iwell.celery_queue.worker:celery beat --loglevel=DEBUG

celery-flower:
	celery -A iwell.celery_queue.worker:celery flower --loglevel=DEBUG --purge

app-start:
	poetry run iwell ipython

build:
	docker build . -t iwell-deo